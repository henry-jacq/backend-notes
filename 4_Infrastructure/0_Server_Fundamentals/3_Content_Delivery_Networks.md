---
title: "Content Delivery Networks"
part: 5
part_title: "Infrastructure"
chapter: 4
summary: "An in-depth guide to Content Delivery Networks (CDNs), covering edge caching, request routing, cache invalidation and edge-security architectures."
---
# Content Delivery Networks

A Content Delivery Network (CDN) is a geographically distributed group of servers that cooperate to provide fast, reliable delivery of internet content. By caching static assets and accelerating dynamic requests closer to end users, a CDN reduces latency, offloads origin server traffic and mitigates distributed denial-of-service (DDoS) attacks.

```text
High-Level CDN Request Routing

           [ Client (Tokyo) ]
                   |
             Queries geo-DNS
                   v
         [ Tokyo PoP Node (Edge) ]
                   |
            Cache Hit?
            /        \
         (Yes)       (No)
          /            \
  Returns asset     Fetches from
  instantly         [ Origin Server (London) ]
```

Without a CDN, every user request (whether for an image, stylesheet, script or dynamic API response) must travel directly to the origin server. This introduces three critical issues:

-   **Geographical Latency:** If the origin server is in London and the client is in Tokyo, network packets must traverse physical fiber-optic lines across continents, adding hundreds of milliseconds of round-trip time (RTT).
-   **Origin Server Exhaustion:** Serving thousands of requests for static files consumes thread capacity, memory resources and network bandwidth on the origin web server.
-   **Vulnerability to DDoS:** Large traffic spikes target the origin server directly, overwhelming its network interface cards (NICs) and causing service outages.



## Under the Hood Operations

A CDN intercepts user requests at the edge of the network before they reach the main system infrastructure.

### Edge Nodes and Points of Presence (PoPs)
CDNs deploy server clusters in data centers across the globe. These physical locations are called Points of Presence (PoPs).

-   **Edge Servers:** Inside each PoP, multiple edge servers host cached copies of files.
-   **Origin Server:** The central server hosting the master version of the application code and data.

### Request Routing Mechanics
When a user requests a file from a CDN-enabled domain, the request is dynamically routed to the nearest PoP using one of two routing methods:

#### 1. Geo-DNS Resolution
The DNS provider detects the client's location based on their local DNS resolver IP address. It then returns the IP address of the closest CDN PoP.

#### 2. Anycast Routing
Multiple CDN edge servers across different PoPs share the same IP address. Routers on the internet use Border Gateway Protocol (BGP) routing tables to automatically send network packets along the path with the fewest network hops, routing the client to the closest node.



## Caching Models and Management

To maintain consistency without serving stale data, CDNs utilize specific caching and invalidation models.

### Pull CDNs vs. Push CDNs
-   **Pull CDNs:** The origin server remains the source of truth. When a user requests an asset, the edge node checks its local cache. If the asset is missing (cache miss), the edge node fetches it from the origin server, returns it to the client and caches it locally for subsequent requests.
-   **Push CDNs:** The application actively uploads (pushes) assets to the CDN storage space whenever content changes (e.g. during a build deployment). This eliminates initial cache-miss latency but adds orchestration overhead to deployment pipelines.

### Cache Control Headers
The origin server defines how long CDNs and client browsers should cache files using HTTP headers:

-   **`Cache-Control: public, max-age=3600, s-maxage=86400`**
    -   `public` permits both browser caches and shared CDN edge caches to store the response.
    -   `max-age` directs the client browser to cache the file for 3600 seconds (1 hour).
    -   `s-maxage` overrides `max-age` specifically for shared CDN caches, directing them to store the file for 86400 seconds (24 hours).
-   **`Cache-Control: no-cache`**
    -   Instructs the browser or CDN that it must validate the resource with the origin server (using ETags or last-modified checks) before using the cached version.
-   **`ETag` (Entity Tag):** A unique cryptographic hash representing the resource state. If the client has a cached resource, it sends the hash in the `If-None-Match` header. If the hash matches the origin's current version, the server returns a `304 Not Modified` status, saving bandwidth.

### Invalidation Strategies
When files change on the origin, the CDN cache must be updated immediately to prevent serving outdated assets:

-   **Time-to-Live (TTL):** The simplest strategy. Files expire automatically after a set duration. This is not suitable for files that update unpredictably.
-   **Purging:** An API call triggers the CDN to delete cached copies of specific URLs or wildcards. Purging can take seconds to propagate globally but incurs API lookup overhead.
-   **Cache Busting (Query or File Versioning):** The application changes the asset path or filename when the file updates (e.g. renaming `main.js` to `main.v2.js` or compiling to `main.[hash].js`). Since the path is entirely new, it triggers an automatic cache miss and pulls the new file, bypassing invalidation propagation delays entirely.



## Edge Acceleration and Security

Beyond static caching, modern CDNs perform logic at the edge:

### Dynamic Content Acceleration
For dynamic database-driven APIs that cannot be cached, CDNs speed up response times via:

-   **TCP Connection Pooling:** The CDN maintains persistent, warm TCP connections between its edge PoPs and the origin server. This eliminates the latency of the TCP 3-way handshake and TLS negotiation over the long distance back to the origin.
-   **SSL/TLS Termination at the Edge:** Clients perform the TLS handshake with the closest edge node. The CDN then routes requests back to the origin over pre-established, secure tunnels.

### Web Application Firewalls (WAF) and DDoS Shielding
-   **DDoS Mitigation:** CDNs absorb massive volumetric attacks (like SYN floods or UDP amplification) at the edge because their distributed network bandwidth is far larger than any single origin data center.
-   **WAF Rule Enforcement:** Edge servers inspect HTTP request headers and query strings, blocking malicious patterns (such as SQL injection or cross-site scripting) before they reach internal application pools.



## Common Pitfalls and Best Practices

-   **Caching Sensitive Data:** Accidentally caching private user dashboard payloads. Always set `Cache-Control: private, no-store` on authenticated API endpoints.
-   **Missing CORS Configurations:** CDNs cache response headers. If a file is cached without proper Cross-Origin Resource Sharing (CORS) headers, browsers requesting the file from other subdomains will block the resource.
-   **Double Caching Overhead:** Having long TTLs on the browser and CDN without versioning. If the origin updates, users may see broken layouts because their browser continues to use old cached assets. Use short browser TTLs combined with versioned file paths.
