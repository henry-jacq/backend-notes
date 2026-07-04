---
title: "API Gateway and Load Balancing"
part: 6
part_title: "API Design"
chapter: 9
summary: "As systems grow from one service to many, a critical question emerges: where do cross-cutting concerns live?..."
---
# API Gateway and Load Balancing

As systems grow from one service to many, a critical question emerges: where do cross-cutting concerns live? Authentication, rate limiting, routing, logging — if every service implements these independently, you get inconsistency, duplication and operational nightmares. API gateways and load balancers centralize these concerns.

## The problem with direct client-to-service communication

```
Without gateway:

Client -> User Service    (port 8001, auth check, rate limit, logging)
Client -> Order Service   (port 8002, auth check, rate limit, logging)
Client -> Product Service (port 8003, auth check, rate limit, logging)
Client -> Payment Service (port 8004, auth check, rate limit, logging)

Problems:

  - Client knows about every service (tight coupling)
  - Each service implements auth, rate limiting, logging (duplication)
  - Adding a service requires updating all clients
  - No single point for monitoring all API traffic
  - Internal service addresses exposed to clients
```

```
With gateway:

Client -> API Gateway -> User Service
                     -> Order Service
                     -> Product Service
                     -> Payment Service

Gateway handles:

  - Authentication (once, before routing)
  - Rate limiting (centralized)
  - Routing (client calls one endpoint)
  - Logging (all traffic in one place)
  - SSL termination
```

## API Gateway

An API gateway is a reverse proxy that sits between clients and backend services. It is the single entry point for all API traffic.

### Core responsibilities

#### 1. Request routing

```
Client request:
  GET /api/users/123

Gateway routing rules:
  /api/users/*    -> user-service:8080
  /api/orders/*   -> order-service:8080
  /api/products/* -> product-service:8080

Gateway forwards:
  GET /users/123 -> user-service:8080
```

The client doesn't know which service handles the request. The gateway maps public URLs to internal services.

#### 2. Authentication offloading

```
Without gateway auth:
  Client -> Service A (validates token)
  Client -> Service B (validates token)
  Client -> Service C (validates token)
  -> Every service implements token validation

With gateway auth:
  Client -> Gateway (validates token) -> Service A (trusts gateway)
                                     -> Service B (trusts gateway)
                                     -> Service C (trusts gateway)
  -> Token validated once at the gateway
  -> Services receive verified identity (e.g., X-User-Id header)
```

```
Gateway auth flow:

  1. Client sends: Authorization: Bearer eyJhbG...
  2. Gateway validates JWT (signature, expiry, audience)
  3. Gateway adds internal headers:
       X-User-Id: 123
       X-User-Role: admin
       X-Request-Id: uuid-abc

  4. Gateway forwards to backend service
  5. Backend trusts headers (internal network only)
```

**Security requirement:** Backend services must reject direct external requests. Only the gateway should be publicly accessible.

#### 3. Rate limiting at the edge

```
Gateway rate limiting:

  Per API key:
    key_free:    100 req/hour
    key_pro:     10,000 req/hour
    key_enterprise: unlimited

  Per endpoint:
    GET  /products -> 1000 req/min (cheap reads)
    POST /orders   -> 50 req/min (expensive writes)

  Per user:
    user_123 -> 100 req/min across all endpoints
```

Rate limiting at the gateway protects all backend services without each service implementing its own.

#### 4. Request and response transformation

```
Client sends:
  GET /api/v2/users/123
  Accept: application/json

Gateway transforms:
  -> Rewrites URL: GET /users/123 (internal format)
  -> Adds headers: X-Request-Id, X-Forwarded-For
  -> Forwards to user-service

Service responds:
  { "user_id": 123, "full_name": "Alice" }

Gateway transforms response:
  -> Renames fields for v2 format: { "id": 123, "name": "Alice" }
  -> Adds CORS headers
  -> Adds security headers
  -> Returns to client
```

This enables API versioning at the gateway level — backend services don't need to know about API versions.

#### 5. API composition pattern (response aggregation)

In a microservices architecture, data is distributed across independent databases. Because SQL joins across separate databases are impossible, the system must compose data at the API level. An API Composer (or Aggregator) queries multiple microservices to build a unified response.

##### Implementation topologies

Where the composition logic runs changes the system's performance and coupling characteristics:

- **Client-Side Composition:** The client (e.g. web browser or mobile app) makes separate requests to each backend service and merges the data locally.
  - **Trade-off:** High latency due to multiple network round trips over public cellular or Wi-Fi networks. Increases battery drain and data usage on mobile devices.
- **API Gateway Composition:** The API Gateway acts as the composer. It exposes a single endpoint, fetches data from the backend services over the low-latency internal network, aggregates the JSON responses and returns them to the client.
  - **Trade-off:** Couples the API Gateway to backend data schemas and domain logic, violating the gateway's goal of being a simple routing layer.
- **Backend-for-Frontend (BFF) Composition:** A dedicated BFF service (e.g. mobile-BFF or web-BFF) handles the aggregation. This keeps the API Gateway stateless and ensures the composed payload is customised to the specific client's screen layout.
- **Dedicated Aggregator Service:** A custom internal microservice acts as the composer. This is useful when the aggregation involves complex business logic or data transformation before returning it to the API Gateway.

##### Execution strategies

- **Parallel Fetching:** The composer fetches independent resources simultaneously using asynchronous concurrency primitives (e.g. `CompletableFuture` in Java, `Promise.all` in JavaScript or goroutines in Go). The total request latency is bounded by the slowest backend service.
- **Sequential Fetching:** Used when subsequent queries depend on initial results (e.g. fetching the `user-service` record to retrieve a list of order IDs before querying the `order-service`). Sequential execution doubles the network latency.

##### Technical challenges and breaking points

- **Cascading Failures and Latency Amplification:** The composer is only as fast as the slowest dependency. If one downstream service experiences high latency, the composer's connection pool can saturate, cascading the failure upstream. You must implement strict timeouts, circuit breakers and fallback responses (e.g. returning the user profile with empty order details if the order service fails).
- **The Microservice N+1 Query Problem:** If a composer fetches a list of 50 orders and then makes 50 individual calls to a user service to retrieve profile details for each order, it creates massive network overhead. Composers should use bulk-query endpoints (e.g. `GET /users?ids=1,2,3...`) to batch requests.
- **Lack of Transactional Consistency:** API composition reads data across independent databases without distributed transactions. The returned aggregated payload represents eventual consistency and might contain out-of-sync data (e.g. showing a user profile that was deleted a millisecond after the orders list was retrieved).
- **Memory Overhead:** Holding and merging large JSON payloads from multiple upstream services in the composer's memory before writing the response stream can lead to high heap usage and garbage collection pauses under high concurrency.

#### 6. SSL/TLS termination

```
Client <-—HTTPS—-> Gateway <-—HTTP—-> Backend services
                 (decrypts)      (internal network, no TLS overhead)

Or for zero-trust:
Client <-—HTTPS—-> Gateway <-—mTLS—-> Backend services
                 (decrypts,       (re-encrypts with internal certs)
                  re-encrypts)
```

Terminating TLS at the gateway simplifies certificate management. One certificate to manage instead of one per service.

### Gateway patterns

#### Single gateway

```
All clients -> one gateway -> all services

Simple. Works for small to medium systems.
Risk: single point of failure, one team owns everything.
```

#### Backend for Frontend (BFF)

```
Web client    -> Web BFF gateway    -> services
Mobile client -> Mobile BFF gateway -> services
Partner API   -> Partner gateway    -> services
```

Each client type gets its own gateway optimized for its needs.

**Why BFF exists:**

- Mobile needs different response shapes (smaller payloads, fewer fields)
- Web needs different authentication (cookies vs tokens)
- Partners need different rate limits and versioning
- Different teams can own different BFFs

**Trade-off:** More gateways to maintain. But each is simpler and optimized.

### Popular API gateways

```
Gateway        | Type          | Use case
Kong           | Open source   | Plugin ecosystem, Lua/Go plugins
AWS API Gateway| Cloud managed | AWS-native, Lambda integration
Envoy          | Proxy         | Service mesh, high performance
NGINX          | Web server    | Lightweight, widely deployed
Traefik        | Cloud-native  | Docker/Kubernetes native
Apigee         | Enterprise    | Full API management platform
```

## Load balancing

Load balancers distribute incoming requests across multiple instances of a service. They ensure no single instance is overwhelmed while others are idle.

### Why load balancing matters

```
Without load balancing:
  All traffic -> Server 1 (overloaded, crashes)
  Server 2 (idle)
  Server 3 (idle)

With load balancing:
  Traffic -> Load Balancer -> Server 1 (33%)
                          -> Server 2 (33%)
                          -> Server 3 (33%)
```

### Load balancing algorithms

#### Round robin

```
Request 1 -> Server 1
Request 2 -> Server 2
Request 3 -> Server 3
Request 4 -> Server 1 (cycle repeats)
```

Simple, fair distribution. Doesn't consider server load or request complexity.

**Problem:** If Server 1 is handling a slow query, it still gets the next request.

#### Weighted round robin

```
Server 1 (8 CPU)  -> weight 4 -> gets 4 of every 7 requests
Server 2 (4 CPU)  -> weight 2 -> gets 2 of every 7 requests
Server 3 (2 CPU)  -> weight 1 -> gets 1 of every 7 requests
```

Accounts for different server capacities. Doesn't account for real-time load.

#### Least connections

```
Server 1: 15 active connections
Server 2: 8 active connections   <- next request goes here
Server 3: 12 active connections
```

Routes to the server with fewest active connections. Better for long-lived requests (WebSockets, streaming).

#### Least response time

```
Server 1: avg response 50ms
Server 2: avg response 120ms
Server 3: avg response 30ms    <- next request goes here
```

Routes to the fastest server. Adapts to real-time performance.

#### IP hash

```
hash(client_ip) % num_servers = server_index

Client 1.2.3.4 -> always -> Server 2
Client 5.6.7.8 -> always -> Server 3
```

Same client always reaches the same server. Useful for sticky sessions but creates uneven distribution.

#### Consistent hashing

```
Servers and requests mapped to a hash ring:

        Server A
       /        \
  Request X      Server B
       \        /
        Server C

Request X routes to the next server clockwise on the ring.
Adding/removing a server only affects adjacent requests.
```

Minimizes redistribution when servers are added or removed. Used by distributed caches and databases.

### L4 vs L7 load balancing

```
L4 (Transport layer):
  Routes based on: IP address, TCP port
  Cannot inspect: HTTP headers, URL path, cookies
  Performance: Very fast (no content parsing)
  Use case: TCP load balancing, non-HTTP protocols

L7 (Application layer):
  Routes based on: URL path, headers, cookies, body content
  Can inspect: Everything in the HTTP request
  Performance: Slower (must parse HTTP)
  Use case: API routing, A/B testing, canary deployments
```

```
L7 routing example:
  /api/users/*    -> user-service cluster
  /api/orders/*   -> order-service cluster
  /api/v2/*       -> v2 service cluster
  Header: X-Canary: true -> canary cluster
```

**API gateways operate at L7.** They need to inspect URLs, headers and sometimes bodies to make routing decisions.

### Health checks

```
Load balancer periodically checks each server:

Active health check:
  Every 10 seconds: GET /health -> 200 OK?
  If 3 consecutive failures -> remove from pool
  If healthy again -> add back to pool

Passive health check:
  Monitor actual request responses
  If error rate > threshold -> remove from pool
```

```
Health check response:
  GET /health

  200 OK:
  {
    "status": "healthy",
    "database": "connected",
    "cache": "connected",
    "uptime": 86400
  }

  503 Service Unavailable:
  {
    "status": "unhealthy",
    "database": "disconnected"
  }
```

### Session persistence (sticky sessions)

```
Without sticky sessions:
  Request 1 from Alice -> Server 1 (session created)
  Request 2 from Alice -> Server 3 (session not found!)

With sticky sessions:
  Request 1 from Alice -> Server 1 (session created)
  Request 2 from Alice -> Server 1 (load balancer remembers)
```

**Implementation:**
```
Cookie-based:
  Server sets: Set-Cookie: SERVERID=server1
  Load balancer reads cookie -> routes to server1

IP-based:
  hash(client_ip) -> always same server
```

**Trade-off:** Sticky sessions break horizontal scaling benefits. Prefer stateless APIs with external session stores (Redis). Use sticky sessions only for WebSocket connections or legacy applications.

## Gateway vs load balancer

```
Feature              | Load Balancer        | API Gateway
Traffic distribution | Yes                  | Yes
Health checks        | Yes                  | Yes
SSL termination      | Yes                  | Yes
Authentication       | No                   | Yes
Rate limiting        | Basic                | Advanced
Request routing      | L4/L7 basic          | L7 advanced (path, header)
Transformation       | No                   | Yes (request/response)
API versioning       | No                   | Yes
Monitoring/Analytics | Basic                | Detailed per-endpoint
Protocol translation | No                   | Yes (REST↔gRPC, etc.)
```

**In practice, use both:**
```
Internet -> Cloud Load Balancer -> API Gateway cluster -> Service Load Balancer -> Service instances
           (L4, distributes       (L7, auth, rate      (L4/L7, distributes
            to gateway instances)  limit, routing)       to service instances)
```

## Service mesh

For large microservice architectures, a service mesh handles service-to-service communication.

```
Without service mesh:
  Service A -> (manual load balancing, auth, retry logic) -> Service B

With service mesh (sidecar proxy):
  Service A -> Sidecar Proxy A -> Sidecar Proxy B -> Service B
              (handles: mTLS, load balancing, retries, observability)
```

**Key components:**
```
Data plane:   Sidecar proxies (Envoy) deployed alongside each service
Control plane: Configuration server (Istio, Linkerd) that manages proxies

Service A Pod:
  [Service A] <--> [Envoy Proxy] <--> network <--> [Envoy Proxy] <--> [Service B]
```

**What a service mesh provides:**

- mTLS between all services (automatic)
- Load balancing with circuit breakers
- Distributed tracing
- Traffic splitting (canary deployments)
- Retry policies

**When you need a service mesh:**

- 20+ microservices
- Need consistent security policies across all services
- Need observability without modifying application code
- Complex traffic management (canary, blue-green, A/B)

**When you don't:**

- Fewer than 10 services
- Monolith or small number of services
- Team doesn't have expertise to operate mesh infrastructure
- Added latency from proxy hops is unacceptable

## Common gateway and load balancing mistakes

1. **Gateway as single point of failure** — deploy multiple gateway instances behind a load balancer
2. **Too much logic in gateway** — gateway should handle cross-cutting concerns, not business logic
3. **No health checks** — routing to dead instances causes user-visible errors
4. **Sticky sessions by default** — prefer stateless design; use sticky only when necessary
5. **Not monitoring gateway latency** — gateway adds latency to every request. Monitor it
6. **Ignoring cold starts** — new instances need warm-up time before receiving full traffic. Use gradual ramp-up
7. **No circuit breaker** — gateway continues sending traffic to failing services, cascading the failure

This concludes the API Design section. APIs are the contracts through which systems communicate. Designing them well — choosing the right protocol, structuring resources correctly, managing state, evolving versions, securing access and centralizing cross-cutting concerns — is what separates systems that scale from systems that collapse under their own complexity.
