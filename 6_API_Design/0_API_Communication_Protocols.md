---
title: "API Communication Protocols"
part: 6
part_title: "API Design"
chapter: 1
summary: "Before designing an API, you must choose how systems communicate. The protocol determines what is possible. Pick the..."
---
# API Communication Protocols

Before designing an API, you must choose how systems communicate. The protocol determines what is possible. Pick the wrong protocol and you fight it forever. Pick the right one and the API design flows naturally.

## Why protocol choice matters

Every API runs on a communication protocol. The protocol defines:

- How data is encoded and transmitted
- Whether communication is synchronous or asynchronous
- Whether data flows one-way or both ways
- How connections are established and maintained
- What performance characteristics are possible

Choosing a protocol is not a cosmetic decision. It constrains everything that follows.

## Communication patterns

### Request-response

The simplest pattern. Client sends a request, server sends a response.

```
Client ---request---> Server
Client <--response--- Server
```

Used by: REST, GraphQL, gRPC (unary calls)

**When it works:**

- Client needs data and can wait for it
- Operations have clear inputs and outputs
- Latency is acceptable (typically <500ms)

**When it breaks:**

- Client needs continuous updates (polling wastes resources)
- Server processing takes minutes or hours
- High-frequency updates would create too many requests

### Streaming

Data flows continuously in one or both directions over a persistent connection.

```
Server streaming:
Client ---request---> Server
Client <--data-------- Server
Client <--data-------- Server
Client <--data-------- Server

Client streaming:
Client ---data-------> Server
Client ---data-------> Server
Client ---data-------> Server
Client <--response--- Server

Bidirectional streaming:
Client <---data------> Server
Client <---data------> Server
```

Used by: WebSockets, SSE (server-only), gRPC streaming

**When it works:**

- Real-time updates (stock prices, chat messages, live feeds)
- Large data uploads in chunks
- Long-running operations with progress updates

**When it breaks:**

- Simple CRUD operations (overhead of maintaining connections)
- Stateless architectures (streaming requires connection state)
- High fan-out to many clients (each connection consumes server resources)

### Pub-sub (publish-subscribe)

Publishers emit events. Subscribers receive them. Neither knows about the other.

```
Publisher --event--> Broker --event--> Subscriber A
                           --event--> Subscriber B
                           --event--> Subscriber C
```

Used by: Message brokers (Kafka, RabbitMQ), webhooks

**When it works:**

- Multiple consumers need the same event
- Producers and consumers scale independently
- Loose coupling between services

**When it breaks:**

- Client needs immediate response (pub-sub is asynchronous)
- Ordering guarantees are critical (depends on broker)
- Simple point-to-point communication (pub-sub adds complexity)

## HTTP protocol versions

Most APIs use HTTP. The version matters for performance.

### HTTP/1.1

The workhorse of the web for two decades.

```
Connection 1: GET /users     -> response
Connection 2: GET /orders    -> response
Connection 3: GET /products  -> response
```

**Characteristics:**

- One request per connection at a time (head-of-line blocking)
- Text-based headers (human-readable but verbose)
- Persistent connections (keep-alive) reuse TCP connections
- Browsers open 6-8 parallel connections per domain

**Head-of-line blocking problem:**
```
Connection 1: GET /slow-query (takes 5 seconds)
              GET /fast-query (blocked, waiting for slow-query)
```

The second request waits even though the server could handle it immediately.

### HTTP/2

Solves HTTP/1.1's performance problems.

```
Single connection:
  Stream 1: GET /users     -> response
  Stream 2: GET /orders    -> response (concurrent)
  Stream 3: GET /products  -> response (concurrent)
```

**Key improvements:**

- **Multiplexing** — multiple requests on one connection, no head-of-line blocking at HTTP level
- **Binary framing** — binary protocol, more efficient parsing
- **Header compression (HPACK)** — reduces repeated header overhead
- **Server push** — server can send resources before client requests them
- **Stream prioritization** — client can prioritize important requests

**Why it matters for APIs:**

- gRPC requires HTTP/2 (streaming depends on multiplexing)
- Reduces latency for chatty APIs (many small requests)
- Single connection reduces TCP handshake overhead

**Trade-off:**

- TCP-level head-of-line blocking still exists (a lost packet blocks all streams)
- More complex to debug (binary protocol, not human-readable in transit)

### HTTP/3

Replaces TCP with QUIC (UDP-based).

**Key improvements:**

- **No TCP head-of-line blocking** — lost packet only blocks its stream, not all streams
- **Faster connection establishment** — 0-RTT or 1-RTT (TCP + TLS requires 2-3 RTT)
- **Connection migration** — survives network changes (Wi-Fi to cellular)

**When HTTP/3 matters:**

- Mobile clients with unreliable networks
- High-latency connections (fewer round trips)
- Applications where TCP head-of-line blocking is measurable

**Current state:**

- Supported by major CDNs and browsers
- Not yet universal for API-to-API communication
- Most backend services still use HTTP/2

## WebSockets

A full-duplex communication protocol over a single TCP connection.

```
HTTP upgrade handshake:
Client ---GET /chat (Upgrade: websocket)---> Server
Client <--101 Switching Protocols----------- Server

Bidirectional communication:
Client <--------messages---------> Server
```

**How it works:**

1. Client initiates HTTP request with `Upgrade: websocket` header
2. Server responds with `101 Switching Protocols`
3. Connection upgrades from HTTP to WebSocket
4. Both sides can send messages at any time

**When WebSockets work:**

- Real-time chat applications
- Live collaboration (Google Docs-style)
- Gaming with low-latency requirements
- Financial data feeds

**When WebSockets don't work:**

- Simple request-response APIs (unnecessary complexity)
- Stateless server architectures (WebSockets require connection state)
- Behind proxies or load balancers that don't support WebSocket upgrade
- When clients are behind restrictive firewalls

**Trade-offs:**

- Each connection consumes server memory (connection state)
- Scaling requires sticky sessions or connection-aware load balancing
- No built-in request-response semantics (you must implement your own)
- Reconnection logic is the client's responsibility

## Server-Sent Events (SSE)

Server pushes data to client over a standard HTTP connection. One-way only.

```
Client ---GET /events---> Server
Client <--event: update--- Server
Client <--event: update--- Server
Client <--event: update--- Server
```

**How it works:**

- Client opens HTTP connection with `Accept: text/event-stream`
- Server keeps connection open, sends events as they occur
- Built-in reconnection (browser handles it automatically)
- Uses standard HTTP (works with existing infrastructure)

**When SSE works:**

- Live notifications and feeds
- Dashboard updates
- Progress indicators for long-running operations
- Any scenario where server pushes to client (not bidirectional)

**When SSE doesn't work:**

- Client needs to send frequent messages to server (SSE is server-to-client only)
- Binary data (SSE is text-based)
- High-frequency updates where HTTP overhead matters

**SSE vs WebSockets:**

```
Feature          | SSE                  | WebSocket
Direction        | Server -> Client      | Bidirectional
Protocol         | HTTP                 | WebSocket (upgraded HTTP)
Reconnection     | Automatic            | Manual
Binary data      | No (text only)       | Yes
Complexity       | Simple               | Complex
Infrastructure   | Standard HTTP        | Requires WebSocket support
```

## Protocol selection guide

**Use HTTP/1.1 + REST when:**

- Building standard CRUD APIs
- Simplicity and compatibility matter most
- Request volumes are moderate

**Use HTTP/2 + REST or gRPC when:**

- Many concurrent requests to the same server
- Low latency matters
- Service-to-service communication

**Use WebSockets when:**

- Bidirectional real-time communication is required
- Low latency in both directions is critical
- Both client and server initiate messages

**Use SSE when:**

- Server needs to push updates to clients
- Standard HTTP infrastructure must be used
- Simplicity is preferred over WebSocket complexity

**Use message brokers (Kafka, RabbitMQ) when:**

- Asynchronous, decoupled communication
- Multiple consumers need the same events
- Durability and replay matter

## Key trade-offs summary

```
Protocol     | Latency | Complexity | Statefulness | Direction
HTTP/1.1     | Medium  | Low        | Stateless    | Request-response
HTTP/2       | Low     | Medium     | Stateless    | Multiplexed req-resp
HTTP/3       | Lowest  | High       | Stateless    | Multiplexed req-resp
WebSocket    | Low     | High       | Stateful     | Bidirectional
SSE          | Medium  | Low        | Stateful     | Server -> Client
gRPC (HTTP/2)| Low     | Medium     | Stateless*   | All streaming types
```

*gRPC connections are persistent but the protocol itself is designed for stateless services.

Choosing the right protocol is the first design decision. Everything else builds on it. To understand how REST uses HTTP for resource-oriented APIs, see [REST API Design](file:///d:/Playground/Backend%20Notes/6_API_Design/1_REST_API_Design.md).
