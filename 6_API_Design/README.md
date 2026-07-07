---
title: "API Design: Contracts Between Systems"
part: 6
part_title: "API Design"
type: "part_intro"
summary: "This section covers how systems communicate through APIs. An API serves as the formal contract between a client and a server. A well-designed API ensures the system remains intuitive, evolvable and resilient."
---
# API Design: Contracts Between Systems

This section covers how systems communicate through APIs. An API serves as the formal contract between a client and a server. A well-designed API ensures the system remains intuitive, evolvable and resilient under changing requirements.

## Why API design matters

Most backend engineers can build an endpoint. Few design APIs that remain stable under growth, are intuitive to consumers and don't create operational nightmares.

A well-designed API:

- Is predictable (consumers know what to expect)
- Is evolvable (changes don't break existing consumers)
- Is secure (authentication, authorization, rate limiting)
- Matches the communication pattern (request-response, streaming, pub-sub)

A poorly designed API:

- Breaks consumers on every release
- Leaks internal implementation details
- Creates performance problems (over-fetching, chatty calls)
- Becomes the bottleneck that limits the entire system

## Chapters

**Communication Protocols Overview**

- Synchronous vs asynchronous communication
- Request-response, streaming, pub-sub patterns
- HTTP/1.1 vs HTTP/2 vs HTTP/3
- WebSockets and Server-Sent Events
- Protocol selection criteria

**RESTful API Design**

- Resource modeling and URI design
- HTTP methods and status codes
- Pagination, filtering, sorting
- Content negotiation and idempotency
- REST maturity model

**GraphQL**

- Schema-first design and type system
- Queries, mutations, subscriptions
- N+1 problem and DataLoader
- When GraphQL beats REST and when it doesn't

**gRPC**

- Protocol Buffers and service definitions
- Streaming types (unary, server, client, bidirectional)
- Code generation and strong typing
- Performance characteristics and when to use gRPC

**Statelessness and State**

- Stateless vs stateful APIs
- Session management strategies
- Tokens (JWT, opaque) and cookies
- State in distributed systems

**API Versioning**

- Why APIs break
- Versioning strategies (URI, header, query param)
- Breaking vs non-breaking changes
- Deprecation workflows and backward compatibility

**Authentication and Authorization**

- API keys, OAuth 2.0, JWT
- RBAC vs ABAC
- Service-to-service auth (mTLS)
- Common auth mistakes

**API Security and Rate Limiting**

- Rate limiting algorithms (token bucket, sliding window)
- Input validation, CORS, CSRF
- DDoS protection
- OWASP API Top 10

**API Gateway and Load Balancing**

- API gateway patterns and responsibilities
- Backend for Frontend (BFF) and API composition
- Load balancing algorithms (round robin, least connections, consistent hashing)
- L4 vs L7 load balancing, health checks
- Service mesh overview

Read these in order. Protocols come first because you must choose how systems communicate before designing the API contract. REST, GraphQL and gRPC are the three dominant paradigms. State, versioning, auth, security and gateway/load balancing are cross-cutting concerns that apply to all of them.

## Key concepts

- Protocol selection (matching communication pattern to protocol)
- Resource modeling (designing intuitive, consistent APIs)
- Contract stability (versioning, backward compatibility)
- Security layers (authentication, authorization, rate limiting)
- Performance trade-offs (over-fetching, under-fetching, streaming)

## The API Lifecycle

Designing an API is not a single event but a structured lifecycle that spans multiple stages:

-   **Requirement Gathering:** Identifying business use cases, data domains, client consumers (web, mobile, IoT) and performance/security SLA boundaries.
-   **Design & Contract Specification:** Creating the formal interface definition (such as OpenAPI/Swagger, GraphQL Schema or Protocol Buffers) before writing code, enabling parallel front-end and back-end development.
-   **Development & Testing:** Implementing the API endpoints, enforcing validation rules, building mock servers and running automated functional, integration and load tests.
-   **Deployment & Release:** Releasing the API endpoints into staging and production, implementing rate limits, setting up API gateways and using canary or blue-green releases.
-   **Maintenance & Observability:** Monitoring traffic patterns, capturing performance metrics (latency, errors, volume) and logging exceptions while maintaining backward compatibility.
-   **Deprecation:** Marking specific API endpoints, fields or versions as deprecated, providing headers (like `Sunset` or `Warning`) and communicating deprecation timelines to consumers.
-   **Retirement:** Gracefully shutting down old endpoints or versions after all client traffic has migrated off them, avoiding downstream client breaks.

## Connection to other sections

**API Design + Foundations:**

- System evolution drives API evolution (monolith APIs -> microservice APIs)
- Performance engineering applies to API latency and throughput

**API Design + Data Storage:**

- API pagination maps to database query patterns
- GraphQL resolvers translate to database queries (N+1 problem)
- Caching strategies interact with API state management

**API Design + Async and Events:**

- Webhooks as asynchronous API callbacks
- gRPC streaming vs message queue patterns
- Event-driven APIs vs request-response APIs

**API Design + Reliability:**

- Retries require idempotent API design
- Circuit breakers protect API consumers
- Rate limiting preserves API availability

**API Design + Infrastructure:**

- HTTP protocol fundamentals underpin REST and GraphQL
- Load balancers route API traffic
- API gateways handle cross-cutting concerns

**API Design + Operations:**

- API metrics (latency, error rate, throughput)
- Debugging API issues with distributed tracing
- Monitoring API versioning and deprecation
