---
title: "Infrastructure: Servers and Networks That Run Systems"
part: 5
part_title: "Infrastructure"
type: "part_intro"
summary: "This section covers the physical and virtual infrastructure that runs backend systems."
---
# Infrastructure: Servers and Networks That Run Systems

This section covers the physical and virtual infrastructure that runs backend systems.

## Chapters

**Under the Hood**

- HTTP protocol (requests, responses)
- TCP foundation (reliable delivery)
- Request/response cycle
- Web server operation
- Database connectivity
- Connection pooling

**Web Server Overview**

- Server types and characteristics
- Operating system considerations
- Configuration and performance tuning
- Security and hardening
- Backup and disaster recovery
- Automation and CI/CD
- Monitoring and alerting

**Load Balancing**

- Traffic distribution algorithms (Round Robin, Least Connection, Consistent Hashing).
- Active health checks vs passive monitoring.
- Resilience clustering models (Active-Passive Virtual IPs vs Active-Active DNS).
- Production patterns (TLS offloading, connection draining).

**Content Delivery Networks**

-   Points of Presence (PoPs) and Geo-routing mechanics (Geo-DNS vs. Anycast).
-   Caching pull/push models and HTTP Cache-Control header control.
-   Cache invalidation techniques (TTL, purge APIs and version busting).
-   Edge acceleration (SSL termination, warm TCP pools) and edge firewalls.

**Docker Fundamentals**

- VM vs Container architecture and overhead differences
- Docker CLI, Daemon and registry roles
- Image layers and read-only immutability
- Container writable layers and storage efficiency

**Docker Under the Hood**

- Linux namespaces (PID, Mount, Network) and process isolation
- Control groups (cgroups) resource limits and OOM-killer policies
- OverlayFS layers (LowerDir, UpperDir, MergedDir) and copy-on-write costs
- OCI runtimes (containerd, runc) and virtual networking bridge routes

## Key concepts

- HTTP protocol structure
- TCP reliability (3-way handshake, retransmission)
- Connection pooling (reusing connections)
- Thread models (blocking, non-blocking)
- Load balancing
- Reverse proxies
- SSL/TLS encryption
- DNS resolution
- Network latency
