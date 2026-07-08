---
title: "Load Balancing"
part: 5
part_title: "Infrastructure"
chapter: 3
summary: "An in-depth analysis of load balancing strategies, routing algorithms, health checks, resilience patterns and best practices in distributed backend architectures."
---
# Load Balancing

Load balancing is central to designing robust, high-performance distributed systems. It acts as a traffic controller, distributing incoming client requests or workloads across a pool of backend servers. This prevents any single machine from becoming a bottleneck, ensuring high availability, horizontal scalability and optimal resource utilization.

```text
High-Level Load Balancing

         +---------+
         |  Client |
         +----+----+
              |
      HTTP/TCP Requests
              v
        +-----+------+
        | Load       |
        | Balancer   |
        +-----+------+
              |
      Distributes requests
              v
  +-----------+-----------+
  |    Server 1 (S1)      |
  +-----------+-----------+
  |    Server 2 (S2)      |
  +-----------+-----------+
  |    Server 3 (S3)      |
  +-----------+-----------+
```

Without a load balancer, client requests query a single server directly. This setup introduces severe limitations:

-   **Single Point of Failure:** If the single server goes down, the entire application becomes completely unavailable.
-   **Overloaded Servers:** As request volumes grow, a single machine eventually exhausts its hardware capacity (CPU, memory, disk I/O and network sockets), causing high latencies or crashes.
-   **Lack of Scalability:** Adding more servers is ineffective because there is no automated gateway to distribute traffic across them.

By contrast, client requests resolve to the load balancer, which presents a single stable entry point, abstracts the server pool and coordinates request distribution.



## Under the Hood Operations

A load balancer sits between clients and servers, evaluating routing policies, monitoring server health and executing failovers.

### Request Flow Mechanics
1.  **Client Request:** The client queries a hostname (e.g. `app.example.com`).
2.  **DNS Resolution:** DNS resolves the hostname to the load balancer's public IP address.
3.  **Routing Decision:** The load balancer intercepts the request, runs its configured routing algorithm and selects a healthy backend server.
4.  **Upstream Execution:** The load balancer forwards the request to the chosen server.
5.  **Client Response:** The server processes the request and sends the response back to the client via the load balancer.

### Server Health Monitoring
To ensure traffic is only routed to responsive servers, load balancers continuously monitor backend status:

#### 1. Active Health Checks (Heartbeats)
The load balancer periodically sends test queries (such as TCP handshakes, HTTP GET requests or ICMP pings) to designated health endpoints on each backend server:
```http
GET /health HTTP/1.1
Host: server-1.internal
```
A typical health endpoint returns database connection status and local resource metrics:
```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected"
}
```
If a server fails multiple consecutive active checks, the load balancer marks it as unhealthy and stops routing client traffic to it. Once the server passes the required check threshold, the load balancer automatically restores it to the active pool.

#### 2. Passive Health Checks (Traffic Monitoring)
Rather than generating test traffic, passive checks monitor live client connections. If a backend server consistently returns TCP connection timeouts, DNS resolve issues or HTTP 5xx errors to real users, the load balancer marks the server as down and initiates failover protocols.



## Traffic Distribution Techniques

Selecting the appropriate load-balancing algorithm depends on the application state, request profiles and hardware capabilities.

### 1. Round Robin & Weighted Round Robin
-   **Round Robin:** Distributes requests sequentially across the server pool. Request 1 goes to Server 1, Request 2 to Server 2, Request 3 to Server 3 and Request 4 loops back to Server 1. This works well when backend servers have identical hardware and requests have uniform processing costs.
-   **Weighted Round Robin:** Assigns a traffic weight to each server based on capacity. A server with a weight of 2 receives double the requests of a server with a weight of 1:
    ```text
    Server 1 (Weight: 1), Server 2 (Weight: 2), Server 3 (Weight: 1)
    Pattern: S1 -> S2 -> S2 -> S3 -> S1 -> S2 -> S2 -> S3
    ```

### 2. Least Connection
Sends new requests to the server with the lowest count of active connections.
```json
{
  "server-1": { "activeConnections": 120 },
  "server-2": { "activeConnections": 45 },
  "server-3": { "activeConnections": 80 }
}
// Decision: Selected server-2 (fewest active connections)
```
This is ideal for systems where requests have highly variable execution times (e.g. databases, file transfers, WebSockets and long-polling connections).

### 3. Least Response Time
Monitors both active connection counts and average response latencies, routing requests to the server likely to respond fastest.
```json
{
  "server-1": { "activeConnections": 40, "averageResponseTimeMs": 180 },
  "server-2": { "activeConnections": 55, "averageResponseTimeMs": 90 }
}
// Decision: Selected server-2 (best latency-to-connection ratio)
```
This protects servers that are slowing down due to high CPU pressure, memory swapping or database locking.

### 4. Least Bandwidth
Routes new connections to the server currently consuming the lowest network throughput (measured in Mbps). This is useful for content delivery networks (CDNs), video streams and heavy file download servers.

### 5. IP Hashing & Consistent Hashing
-   **IP Hashing:** Hashes the client's IP address to map them consistently to the same backend server. While this ensures session persistence (sticky sessions), it can create uneven traffic spikes if many users connect from the same network gateway or corporate NAT.
-   **Consistent Hashing:** Maps request keys (such as user IDs or cache keys) and server nodes onto a circular hash ring. Clients are routed to the nearest server node on the ring. When servers are added or removed, only a small fraction of keys are remapped, preserving cache locality and session data across the remaining servers.

### 6. Layer 4 vs. Layer 7 Load Balancing
Load balancers operate at different layers of the OSI model:

-   **Layer 4 (Transport Layer):** Operates using packet headers (IP addresses and TCP/UDP ports) without inspecting the underlying payload. It is highly performant and requires low CPU utilization, but cannot route traffic based on URL paths or cookie headers.
-   **Layer 7 (Application Layer):** Inspects application-level protocol data (HTTP headers, URL paths, cookies and query parameters). This enables content-aware routing:
    ```text
    Path: /static/* -> static-server-pool
    Path: /api/*    -> api-server-pool
    Host: shop.com  -> checkout-server-pool
    ```
    While Layer 7 routing is highly flexible, it incurs higher CPU and latency overhead due to packet decryption and parsing.



## Load Balancer Resilience

A single load balancer represents a high-risk single point of failure (SPOF). To avoid this, production environments run load balancers in redundant clusters:

### 1. Active-Passive Clustering (Virtual IPs)
An active load balancer handles all traffic, while a passive clone sits on standby, constantly monitoring the active node via heartbeat checks. Both nodes share a Virtual IP address (VIP). If the active node crashes, the passive node takes over the VIP within milliseconds, resuming traffic routing transparently.

### 2. Active-Active Clustering (DNS Round Robin)
Multiple load balancers run concurrently. Public DNS registers multiple IP addresses for the hostname, distributing traffic across all active load balancers:
```text
DNS query for app.example.com resolves to:

- 203.0.113.10 (Load Balancer 1)
- 203.0.113.11 (Load Balancer 2)
```



## Best Practices and Production Patterns

-   **TLS Offloading (SSL Termination):** Decrypt HTTPS traffic at the load balancer level and pass unencrypted HTTP traffic to backend servers over private networks. This offloads resource-heavy cryptographic work from application workers.
-   **Session Persistence (Sticky Sessions):** If backend servers store session state locally, use cookie-based persistence to pin clients to the same server. Alternatively, store sessions in a shared Redis cluster to allow stateless backend routing.
-   **Connection Draining (Graceful Shutdown):** When scaling down or deploying updates, instruct the load balancer to block new requests from reaching target servers while permitting existing connections to complete safely before removal.
-   **Rate Limiting & DDoS Shielding:** Configure rate limits at the load balancer level to reject malicious traffic spikes before they reach internal application pools.
