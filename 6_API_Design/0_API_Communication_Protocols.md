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

## Polling Patterns

When real-time updates are required but persistent push protocols are unavailable, clients fall back to polling models using standard HTTP request-response.

### Short Polling
Short polling is a client-driven pull mechanism where requests are repeatedly sent at fixed intervals.

-   **Traffic Flow:** Client -> HTTP GET -> Server. The server immediately responds with either new data or an empty payload.
-   **How it works:** A browser timer triggers an AJAX request at a fixed frequency (e.g. every 5 seconds). The server queries the database or cache and immediately sends a response.
-   **When to use:** Non-critical background syncs or administrative dashboards where immediate latency is not required and traffic volumes are low.
-   **Limitations:** High resource waste. If data only updates once an hour, the client sends thousands of unnecessary requests, generating high database CPU utilization and network overhead.

### Long Polling
Long polling is a hybrid pull-push mechanism where the server delays its response until new data is available.

-   **Traffic Flow:** Client -> HTTP GET -> Server (Holds connection open) -> (Data arrives) -> Server responds -> Client receives and immediately restarts loop.
-   **How it works:** The client initiates an HTTP request. If no updates exist, the server halts the response thread (or uses asynchronous request processing) and keeps the connection open. Once the backend records an update or the request reaches a timeout (e.g. 30 seconds), the server returns the response. The client immediately opens a new long-poll request.
-   **When to use:** Simple notification feeds or chat triggers when WebSocket infrastructure cannot be deployed.
-   **Limitations:** Connection exhaustion. Keeping thousands of requests open consumes web server worker threads or file descriptors, requiring asynchronous event loops (like Node.js or Netty) to scale.

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

## Webhooks

Webhooks are event-driven HTTP POST callbacks triggered by server-to-server updates.

```text
Webhook Event Flow

  [Provider Server] --- HTTP POST (JSON Payload) ---> [Consumer Server]
          ^                                                   |
    Event Triggered                                    Processes payload &
    (e.g., payment.paid)                               returns 200 OK
```

-   **How it works:**
    1.  The consumer registers a public URL (webhook endpoint) in the provider's system dashboard.
    2.  An event occurs in the provider's platform (e.g. a payment successfully completes).
    3.  The provider's background job queue triggers an HTTP POST request containing the event payload to the consumer's registered URL.
    4.  The consumer processes the payload and returns a `200 OK` response to acknowledge receipt.
-   **When to use:** Integrating third-party APIs (e.g. Stripe payment notifications, GitHub commit hooks or Twilio SMS status updates).
-   **Security Defenses:** Since webhook endpoints are publicly accessible, attackers can spoof requests. Providers generate cryptographic signatures using a shared secret and attach them in headers (e.g. `X-Signature`). Consumers must compute the HMAC hash of the raw request body and compare it with the header signature before processing.


## Real-Time Protocol Comparison

| Mechanism | Direction | Protocol Base | Connection Type | Resource Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Short Polling** | Client to Server | HTTP | Short-lived | High (polling) |
| **Long Polling** | Client to Server | HTTP | Long-lived | Medium |
| **SSE** | Server to Client | HTTP | Persistent | Low |
| **WebSocket** | Bidirectional | WebSocket (HTTP Upgrade) | Persistent | Low |
| **Webhooks** | Server to Server | HTTP (POST Request) | Short-lived | Lowest (event-driven) |

## Protocol Selection Guide

-   **Use HTTP/1.1 + REST when:** Building standard CRUD APIs where request volumes are moderate and compatibility is the primary concern.
-   **Use HTTP/2 + REST or gRPC when:** Low-latency service-to-service communication requires multiple concurrent requests multiplexed over a single connection.
-   **Use Short Polling when:** Implementing basic, non-critical background updates where latency is not a concern and traffic volume is low.
-   **Use Long Polling when:** The client needs real-time event alerts but WebSockets or SSE are blocked by corporate firewall proxies or infra limitations.
-   **Use WebSockets when:** Bidirectional, low-latency, real-time message streams are required (e.g. chat systems, collaborative whiteboards or online multiplayer games).
-   **Use SSE when:** The server must push events or data streams (like news feeds, stock tickers or progress indicators) directly to clients over standard HTTP channels.
-   **Use Webhooks when:** Designing server-to-server integrations where a provider system must notify an external consumer system asynchronously about event states.
-   **Use Message Brokers (Kafka, RabbitMQ) when:** Decoupling internal backend microservices with asynchronous, high-throughput message publishing, replayability and durability guarantees.

## Key Trade-Offs Summary

| Mechanism | Latency | Complexity | Statefulness | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Short Polling** | High | Low | Stateless | Low-frequency data pulls |
| **Long Polling** | Medium | Medium | Stateful* | Simple notifications (no WebSocket support) |
| **WebSocket** | Lowest | High | Stateful | Bidirectional chat, games, collaborative boards |
| **SSE** | Low | Low | Stateful | Real-time dashboard feeds, ticker updates |
| **Webhooks** | Low | Medium | Stateless | Server-to-server event integrations |

*Long polling requests are stateless on HTTP, but the server must manage socket handles or thread reservations during the hang window.

Choosing the right protocol is the first design decision. Everything else builds on it.
