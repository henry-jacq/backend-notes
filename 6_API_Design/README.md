---
title: "API Design: Contracts Between Systems"
part: 6
part_title: "API Design"
type: "part_intro"
summary: "This section covers how systems communicate through APIs. An API is the contract between a client and a server. Get..."
---
# API Design: Contracts Between Systems

This section covers how systems communicate through APIs. An API is the contract between a client and a server. Get it wrong and every consumer of that API suffers. Get it right and the system is intuitive, evolvable and resilient.

## Why API design matters

Most backend engineers can build an endpoint. Few design APIs that remain stable under growth, are intuitive to consumers and don't create operational nightmares.

A well-designed API:

- Is predictable (consumers know what to expect)
- Is evolvable (changes don't break existing consumers)
- Is secure (authentication, authorisation, rate limiting)
- Matches the communication pattern (request-response, streaming, pub-sub)

A poorly designed API:

- Breaks consumers on every release
- Leaks internal implementation details
- Creates performance problems (over-fetching, chatty calls)
- Becomes the bottleneck that limits the entire system

## Learning path

**[Communication Protocols Overview](file:///d:/Playground/Backend%20Notes/6_API_Design/0_API_Communication_Protocols.md)**

- Synchronous vs asynchronous communication
- Request-response, streaming, pub-sub patterns
- HTTP/1.1 vs HTTP/2 vs HTTP/3
- WebSockets and Server-Sent Events
- Protocol selection criteria

**[RESTful API Design](file:///d:/Playground/Backend%20Notes/6_API_Design/1_REST_API_Design.md)**

- Resource modelling and URI design
- HTTP methods and status codes
- Pagination, filtering, sorting
- Content negotiation and idempotency
- REST maturity model

**[GraphQL](file:///d:/Playground/Backend%20Notes/6_API_Design/2_GraphQL.md)**

- Schema-first design and type system
- Queries, mutations, subscriptions
- N+1 problem and DataLoader
- When GraphQL beats REST and when it doesn't

**[gRPC](file:///d:/Playground/Backend%20Notes/6_API_Design/3_gRPC.md)**

- Protocol Buffers and service definitions
- Streaming types (unary, server, client, bidirectional)
- Code generation and strong typing
- Performance characteristics and when to use gRPC

**[Statelessness and State](file:///d:/Playground/Backend%20Notes/6_API_Design/4_API_State_Management.md)**

- Stateless vs stateful APIs
- Session management strategies
- Tokens (JWT, opaque) and cookies
- State in distributed systems

**[API Versioning](file:///d:/Playground/Backend%20Notes/6_API_Design/5_API_Versioning.md)**

- Why APIs break
- Versioning strategies (URI, header, query param)
- Breaking vs non-breaking changes
- Deprecation workflows and backward compatibility

**[Authentication and Authorisation](file:///d:/Playground/Backend%20Notes/6_API_Design/6_Authentication_and_Authorization.md)**

- API keys, OAuth 2.0, JWT
- RBAC vs ABAC
- Service-to-service auth (mTLS)
- Common auth mistakes

**[API Security and Rate Limiting](file:///d:/Playground/Backend%20Notes/6_API_Design/7_API_Security_and_Rate_Limiting.md)**

- Rate limiting algorithms (token bucket, sliding window)
- Input validation, CORS, CSRF
- DDoS protection
- OWASP API Top 10

**[API Gateway and Load Balancing](file:///d:/Playground/Backend%20Notes/6_API_Design/8_API_Gateway_and_Load_Balancing.md)**

- API gateway patterns and responsibilities
- Backend for Frontend (BFF)
- Load balancing algorithms (round robin, least connections, consistent hashing)
- L4 vs L7 load balancing, health checks
- Service mesh overview

Read these in order. Protocols come first because you must choose how systems communicate before designing the API contract. REST, GraphQL and gRPC are the three dominant paradigms. State, versioning, auth, security and gateway/load balancing are cross-cutting concerns that apply to all of them.

## Key concepts

- Protocol selection (matching communication pattern to protocol)
- Resource modelling (designing intuitive, consistent APIs)
- Contract stability (versioning, backward compatibility)
- Security layers (authentication, authorisation, rate limiting)
- Performance trade-offs (over-fetching, under-fetching, streaming)

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

## Next sections

After understanding API design:

- **Operations** — monitoring, debugging and incident response for API-driven systems
- **Foundations** — revisit system evolution with API design context
