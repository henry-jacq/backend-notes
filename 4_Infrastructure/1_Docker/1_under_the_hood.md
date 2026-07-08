---
title: "Docker Under the Hood"
part: 5
part_title: "Infrastructure"
chapter: 5
summary: "Explores the low-level Linux kernel features powering containerisation, including namespaces, control groups (cgroups), OverlayFS layers, container runtime components (containerd, runc) and virtual networking."
---
# Docker Under the Hood

While Docker provides a user-friendly abstraction, it does not invent virtualisation primitives. Under the hood, containers are standard Linux processes running inside boundaries enforced by the host Linux kernel.

Understanding these kernel-level mechanisms is critical for troubleshooting performance anomalies, security concerns and container lifecycle events.



## 1. Namespaces: Process Isolation

Linux **namespaces** partition kernel resources so that a group of processes sees one set of resources while another group sees a different set. Namespaces isolate what a containerized process is allowed to *see*.

```
Host OS Kernel (Shared)
  |
  +---> [Network Namespace] ---> Virtual eth0, isolated ports
  +---> [PID Namespace]     ---> Container PID 1 (Host PID 45290)
  +---> [Mount Namespace]   ---> pivot_root isolated file tree
  +---> [UTS Namespace]     ---> Independent hostname
```

The kernel implements several namespaces to achieve complete process isolation:

-   **PID Namespace (Process ID):** Isolates the process ID space. Inside a container, the main application process runs as PID 1 (the init process). On the host, this same process is mapped to a standard high-numbered PID (e.g. PID 45290). This prevents containers from seeing or interacting with host processes.
-   **Mount Namespace (mnt):** Isolates filesystem mount points. Combined with the `pivot_root` system call, it allows a container to have its own root directory structure independent of the host filesystem.
-   **Network Namespace (net):** Isolates network devices, IP routing tables, port mappings and firewall rules. A container gets its own virtual network loopback and interface cards.
-   **UTS Namespace (Unix Timesharing System):** Allows a container to define its own hostname and domain name.
-   **IPC Namespace (Inter-Process Communication):** Isolates system IPC resources (System V IPC, POSIX message queues), preventing processes in different containers from communicating via memory segments.
-   **User Namespace:** Maps root inside a container (UID 0) to a non-privileged user on the host. This restricts the security impact if a process escapes container boundaries.



## 2. Control Groups (cgroups): Resource Constraints

While namespaces restrict what a process can *see*, **control groups (cgroups)** restrict what a process can *use*. Cgroups prevent a single container from consuming all host resources (the "noisy neighbour" problem). By grouping processes into a unified tree hierarchy, the kernel is able to enforce strict limits on CPU shares, memory allocation, active PID counts and disk I/O throughput. This granular resource metering guarantees host stability by preventing any individual containerised process from exhausting the host thread table or triggering system-wide starvation.

```
cgroups Limits:
[CPU Shares / Quota]  ======> Throttle CPU via CFS Scheduler when quota exceeded
[Memory Hard Limits]  ======> Triggers OOM-Killer if exceeded (no swap space default)
[Block I/O Throttling] ======> Limit disk Read/Write operations per second (IOPS)
```

-   **CPU Limits:** Managed using the kernel's Completely Fair Scheduler (CFS). Docker allows setting fractional CPU limits (e.g. `cpus=1.5`). The kernel translates this into CPU period and quota parameters, throttling the containerised process when its allocated time slice is exceeded. Specifically, the CFS scheduler tracks CPU consumption in fixed time windows (usually 100 milliseconds) and if a container's CPU quota is exhausted within that window, its threads are suspended until the next period.
-   **Memory Limits:** Defines hard and soft memory limits. If a container exceeds its hard memory limit, the kernel's **Out-Of-Memory (OOM) Killer** immediately terminates the process (typically resulting in an exit code 137). Before termination, the kernel attempts to reclaim page cache memory; if this reclaim is insufficient, the OOM killer selects the process with the highest OOM score for termination.
-   **Block I/O Limits (blkio):** Sets limits on read and write throughput (bytes/second) or operations (IOPS) on physical disk blocks, preventing disk starvation on shared hardware hosts. These limits are enforced at the block layer using token-bucket rate limiting, protecting host storage controllers from write saturation.
-   **cgroups v2:** Modern Linux distributions use cgroups v2, which provides a unified hierarchy system. This makes resource tracking (especially memory combined with I/O) significantly more accurate than cgroups v1. In v1, separate hierarchies made it impossible to trace resource-dependent costs like memory-backed page cache writebacks, a limitation resolved by v2's single unified tree.



## 3. Union Filesystems and OverlayFS

Docker images leverage Union Filesystems to stack multiple read-only layers. In modern systems, **OverlayFS** is the default storage driver.

OverlayFS merges two directories into a unified virtual directory view:

```
OverlayFS Mount Structure:
+-----------------------------------+
| MergedDir (Unified Container View)| <-- What the application sees
+-----------------------------------+
| UpperDir  (Writable Layer)        | <-- Created at container runtime
+-----------------------------------+
| LowerDir  (Read-Only Image Layers)| <-- Docker base image layers
+-----------------------------------+
```

-   **LowerDir:** Read-only layers comprising the base operating system and application files.
-   **UpperDir:** The writable layer allocated when the container starts. Any new files created or existing files modified are stored here.
-   **MergedDir:** The unified mount point where the kernel merges `LowerDir` and `UpperDir`. The container application interacts exclusively with this view.
-   **Copy-on-Write (CoW) Performance Cost:** When an application modifies an existing file residing in the read-only `LowerDir`, OverlayFS must copy the entire file from the lower layer to the writable `UpperDir` before applying changes. For high-write databases or logs, this copy overhead causes severe performance degradation. This is why high-I/O applications must use **Docker Volumes** to write directly to the host filesystem, bypassing OverlayFS.



## 4. Container Runtime Architecture

The Docker platform is composed of decoupled components matching Open Container Initiative (OCI) specifications:

```
+------------+       gRPC       +------------+       fork/exec       +-------+
|   dockerd  | ---------------> | containerd | --------------------> | runc  |
+------------+                  +------------+                       +-------+
                                      |                                  |
                                      v                                  v
                             +-----------------+                +-----------------+
                             | containerd-shim |                | App Process     |
                             +-----------------+                +-----------------+
```

1.  **dockerd (Daemon):** Provides high-level features such as CLI commands, image management, volume setups and network configuration APIs.
2.  **containerd:** A CNCF graduated daemon that manages the container lifecycle (starting, stopping, pausing, downloading images). It is agnostic of high-level Docker features.
3.  **containerd-shim:** A lightweight daemon that monitors the container process once it is running. It handles standard I/O streams and records the container exit status, preventing `containerd` from keeping files open or crashing if the main Docker daemon restarts.
4.  **runc:** A low-level OCI command-line tool. It queries the kernel to set up namespaces, configure cgroup boundaries, pivot the root filesystem and run the containerised entrypoint. Once the process is active, `runc` exits.



## 5. Container Networking

Docker virtualises networking using Linux bridges and network namespaces:

```
Container Net Namespace             Host OS Network Namespace
+-----------------------+           +-----------------------+
|                       |           |                       |
|         eth0          | <=======> |      vethXXXXX        | (Virtual Cable)
|      (172.17.0.2)     |           |                       |
+-----------------------+           +-----------------------+
                                                |
                                    +-----------------------+
                                    |     docker0 Bridge    |
                                    +-----------------------+
                                                |
                                    +-----------------------+
                                    |     iptables NAT      | (Port Map)
                                    +-----------------------+
```

-   **Virtual Ethernet Pairs (veth):** A virtual network cable with two ends. The kernel places one end inside the container's network namespace (as `eth0`) and attaches the other end to a bridge device in the host's namespace.
-   **The `docker0` Bridge:** A virtual switch on the host. All container namespaces attach to this switch, allowing them to communicate with each other using internal IP addresses (e.g. `172.17.x.x`).
-   **Port Forwarding via iptables:** Because container IPs are internal, external traffic cannot reach them directly. When you expose a port (e.g. `-p 8080:80`), the Docker daemon configures Network Address Translation (NAT) rules via `iptables` in the host kernel. This intercepts incoming traffic on host port 8080 and forwards the packets directly to port 80 inside the container's namespace.

<div class="takeaway-box">
    <strong>Key Takeaway:</strong> Under the hood, a Docker container is not a sandbox VM. It is a standard Linux process isolated by namespaces, resource-restricted by cgroups and operating on an OverlayFS layered filesystem. Managing high-performance containers requires understanding the overhead of Copy-on-Write and the kernel mechanisms regulating network address translation.
</div>
