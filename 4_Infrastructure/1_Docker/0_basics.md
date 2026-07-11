---
title: "Docker Fundamentals"
part: 5
part_title: "Infrastructure"
chapter: 5
summary: "Introduces the concept of containerisation, comparing containers with virtual machines and explores the Docker platform architecture, layered image designs and basic networking principles."
---
# Docker Fundamentals

Modern application deployment requires consistency across environments, from a developer's laptop to production servers. Traditionally, this was achieved using Virtual Machines (VMs). Today, containerisation is the standard for packaging and running services.

## What is a Container?

A container is a lightweight, isolated user-space environment that packages an application and all its dependencies (libraries, configuration files and runtimes) so that it runs reliably across different computing environments. 

Unlike older virtualisation methods, a container does not run a separate guest operating system. Instead, it runs as an isolated process directly on the host operating system, sharing the host's kernel.

## What is Docker?

Docker is not the container technology itself, but a highly popular platform and product built to manage containers. 

While container primitives (such as Linux namespaces and cgroups) existed in the Linux kernel long before Docker's launch in 2013, they were notoriously complex to configure manually. Docker solved this usability problem by introducing:

- **A standard image format:** Packaging the application and its dependencies into a single immutable artifact.
- **Developer-friendly CLI tooling:** Making it trivial to build, run and distribute containers with commands like `docker build` and `docker run`.
- **A centralized registry system:** Making it easy to share images via Docker Hub.

As a result of this developer experience optimization, Docker achieved massive industry adoption and defined the modern standards for container runtimes.

Originally, Docker leveraged LinuX Containers (LXC) as its execution driver, but later transitioned to its own custom runtime library (`libcontainer`) to manage kernel namespaces directly. This interface was subsequently standardized as the Open Container Initiative (OCI) specification, ensuring cross-runtime interoperability. Additionally, because containers require a Linux host kernel, Docker on macOS or Windows hosts executes containers inside a lightweight Linux virtual machine running in the background.



## Containers vs Virtual Machines

The fundamental difference between a container and a virtual machine lies in the level of abstraction and what resource is shared.

```
Virtual Machine Architecture          Container Architecture
+------------------------+          +------------------------+
| App A   | App B   | .. |          | App A   | App B   | .. |
+---------+---------+----+          +---------+---------+----+
| Guest OS| Guest OS| .. |          | Container Runtime (Dk) |
+---------+---------+----+          +------------------------+
|   Hypervisor (ESXi)    |          |   Host OS (Linux)      |
+------------------------+          +------------------------+
|   Host OS / Hardware   |          |      Hardware          |
+------------------------+          +------------------------+
```

### Virtual Machines (Hardware-level Virtualisation)
A Virtual Machine runs a complete guest operating system on top of physical hardware. This is managed by a **hypervisor** (e.g. VMware ESXi, VirtualBox or KVM):

- **Overhead:** Each VM requires its own guest operating system kernel, virtual device drivers and memory allocation. This results in significant overhead, requiring gigabytes of RAM and disk space even for simple applications.
- **Startup Latency:** Booting a VM requires initializing a full OS kernel, running system startup scripts and starting background services. This boot process typically takes minutes.
- **Resource Allocation:** Resources (RAM, CPU) are statically allocated to the VM at boot time, making dynamic scaling inefficient.

### Containers (OS-level Virtualisation)
A container is a lightweight, isolated execution environment that shares the host operating system's kernel. Instead of virtualising hardware, it virtualises the operating system:

- **Overhead:** Because containers share the host kernel, they do not require a guest OS. A container is simply a standard Linux process running under specific restrictions. The memory overhead is minimal, limited to the memory consumed by the application process itself.
- **Startup Latency:** Starting a container is as fast as starting a normal OS process, taking milliseconds rather than minutes.
- **Resource Allocation:** Resources can be allocated dynamically, allowing containers to consume only what they need up to a configured threshold.



## The Docker Architecture

Docker is based on a client-server model. The Docker client communicates with the Docker Daemon, which builds, runs and manages containers. They communicate through a REST API via UNIX sockets or a network interface.

```
+------------------+         REST API         +--------------------------------------+
|  Docker Client   | <======================> |             Docker Host              |
|                  |  (Sockets / TCP)         |                                      |
|  docker run      |                          |  +--------------------------------+  |
|  docker build    |                          |  |      Docker Daemon (dockerd)   |  |
|  docker pull     |                          |  +--------------------------------+  |
+------------------+                          |                  |                   |
                                              |                  v (Manage Objects)  |
                                              |  +------------+  +----------------+  |
                                              |  |  Images    |  | Containers     |  |
                                              |  |  (ubuntu)  |  | (nginx-web)    |  |
                                              |  |  (nginx)   |  | (redis-db)     |  |
                                              |  +------------+  +----------------+  |
                                              |                  |                   |
                                              |                  v (Direct execution)|
                                              |         [containerd / runc]          |
                                              +--------------------------------------+
                                                                 ^
                                                                 |
                                                                 | (Pulls / Pushes)
                                                                 v
                                                      +--------------------+
                                                      |  Docker Registry   |
                                                      | (Docker Hub / ECR) |
                                                      +--------------------+
```

### The Core Architectural Components

-   **Docker Client:** The primary interface for users. When you execute commands such as `docker run`, `docker build` or `docker pull`, the client translates them into REST API requests and transmits them to the Docker Daemon.
-   **Docker Host:** The physical or virtual machine that runs the Docker Daemon (`dockerd`) and provides the complete environment to execute and run containers. It comprises the operating system kernel, the daemon, pulled or built images, active containers, networks and storage components.
-   **Docker Registry:** A stateless, scalable storage and distribution system for Docker images.
    -   *Public Registry:* The default public registry is Docker Hub, which hosts a vast collection of community and official images.
    -   *Private Registries:* Organisations frequently run private registries (such as AWS ECR, Google Artifact Registry or Harbor) to store proprietary images for security and compliance.



## Docker Objects

When working with Docker, you create and configure images, containers, networks, volumes and other virtualised objects.

### 1. Images

An image is a read-only, inert template containing instructions for creating a Docker container. Think of it as a blueprint or a class in object-oriented programming:

-   **Dockerfile assembly:** It is built from a `Dockerfile`, a simple text file defining the steps to assemble the environment.
-   **Layered storage:** Images are constructed in immutable layers using a union filesystem (such as OverlayFS) where each instruction (base OS, installed packages, runtime dependencies, application code) represents a discrete layer.
-   **Deduplication:** This layered design enables different images to share identical base layers on the host disk, drastically reducing registry download times and physical storage consumption.

### 2. Containers

A container is a runnable, live instance of an image. If an image is the blueprint, a container is the physical house built from it:

-   **Lifecycle actions:** You can create, start, stop, move or delete containers using the Docker CLI or API.
-   **Thin writable layer:** When a container launches, the runtime stacks a thin read-write layer (the container layer) on top of the immutable image layers. Any runtime modifications (such as log files or temp databases) are written here.
-   **Isolation boundaries:** Each container operates within its own namespace and cgroup boundaries, preventing processes from interfering with the host OS or other containers.
-   **Multi-instantiation:** A single image can be instantiated into multiple running containers concurrently, each maintaining its own separate runtime state.

### 3. Storage

Because a container's write layer is ephemeral and tied to its lifecycle, Docker uses a storage driver to manage image layers while exposing persistent storage mechanisms:

-   **Volumes:** Managed entirely by Docker and stored in a designated area on the host filesystem (e.g. `/var/lib/docker/volumes/` on Linux). This isolates volume data from the container lifecycle and storage driver overhead.
-   **Bind Mounts:** Directly maps a path on the host machine to a directory inside the container. This is primarily used in development to share source code or hot-reload configurations instantly.
-   **tmpfs Mounts:** Writes data directly to host system memory rather than disk, ensuring fast execution for temporary files and preventing sensitive secrets from persisting.

### 4. Networking

Docker networking isolates and virtualises networking interfaces, assigning distinct interfaces to containers using Linux namespace primitives:

-   **Virtual interfaces:** Each container is allocated an isolated network namespace with its own IP address, routing table and virtual Ethernet (`veth`) pair connected to the host's virtual bridge interface.
-   **Network Drivers:**
    -   **Bridge:** The default network driver. It acts as a software switch allowing containers connected to the same bridge network to communicate.
    -   **Host:** Removes network isolation between the container and the host, allowing the container to bind directly to host port addresses.
    -   **Overlay:** Enables container-to-container communication across multiple host daemons (commonly used in Docker Swarm clusters).
    -   **macvlan:** Assigns a unique MAC address to a container, making it appear as a physical hardware device connected directly to the local network.
    -   **None:** Disables all network connectivity for the container.



## Step-by-Step Execution of a Docker Command

To understand how all these components coordinate, let's trace a standard run command:

```bash
docker run -d -p 80:80 nginx
```

1.  **Client:** The Docker Client translates the CLI command into a REST API request and transmits it to the Docker Daemon on the host.
2.  **Daemon:** The Daemon receives the request and checks if the `nginx` image exists in the host's local cache.
3.  **Registry (Pull):** If the image is not found locally, the Daemon contacts the configured Registry (Docker Hub by default) to pull the image layers.
4.  **Runtime (containerd):** Once the image layers are assembled, the Daemon passes the image metadata and run-configuration to `containerd` via gRPC.
5.  **Runtime (runc):** `containerd` spawns a shim process and calls the low-level OCI tool `runc`. `runc` interfaces with the Linux kernel to create isolated namespaces (PID, mount, net) and apply resource limits using cgroups.
6.  **Execution:** The container begins execution. Docker maps port 80 of the host machine to port 80 inside the container using `iptables` NAT rules and the Nginx web server starts as PID 1.



## Layered Filesystem Architecture

One of Docker's key innovations is the use of a layered, read-only filesystem for container images.

When you write a `Dockerfile`, each instruction (e.g. `FROM`, `RUN`, `COPY`) creates a new read-only layer in the image. These layers are stacked on top of each other:

```
+-----------------------------------+
| Container Writable Layer (Read/Write) |  <-- Created when container runs
+-----------------------------------+
| Application Code (Read-Only)      |  <-- COPY . /app
+-----------------------------------+
| Installed Packages (Read-Only)    |  <-- RUN apt-get install
+-----------------------------------+
| Base OS Layer (Read-Only)         |  <-- FROM debian:stable
+-----------------------------------+
```

- **Read-Only Layers:** The lower layers of an image are immutable. Once built, they cannot be changed. This immutability guarantees that an image behaves identically in development and production.
- **Container Writable Layer:** When a container is started, a thin writable layer is added on top of the read-only stack. Any modifications made by the running application (e.g. writing logs, temp files) occur in this layer.
- **Efficient Layer Sharing:** If two different images share the same base layer (e.g. `debian:stable`), Docker does not download or store that layer twice. Both images share the same physical blocks on disk.

<div class="takeaway-box">
    <strong>Key Takeaway:</strong> Containers provide fast startup times, low resource overhead and reliable environment reproducibility by virtualising the operating system rather than the underlying hardware. Sharing the host OS kernel makes containers highly efficient but links containerised processes to the host OS kernel version.
</div>
