---
title: "API State Management"
part: 6
part_title: "API Design"
chapter: 5
summary: "Statelessness is the most misunderstood concept in API design. Engineers say \"REST is stateless\" without..."
---
# API State Management

Statelessness is the most misunderstood concept in API design. Engineers say "REST is stateless" without understanding what that means or why it matters. State doesn't disappear — it moves. The question is where it lives and who manages it.

## What stateless actually means

A stateless API means the server does not store any information about previous requests. Every request contains everything the server needs to process it.

```
Stateless:
  Request 1: GET /users/123, Authorization: Bearer token-abc
  Request 2: GET /users/123, Authorization: Bearer token-abc
  -> Server processes each independently. No memory of Request 1.

Stateful:
  Request 1: POST /login { "user": "alice", "pass": "..." }
  -> Server creates session, returns session_id
  Request 2: GET /users/123, Cookie: session_id=xyz
  -> Server looks up session_id in memory to identify user
```

## Why statelessness matters for APIs

### Scaling

```
Stateful server:
  User Alice -> Server 1 (session stored in Server 1's memory)
  User Alice -> Server 2 (session not here -> fails)
  -> Sticky sessions required (load balancer must route Alice to Server 1)

Stateless server:
  User Alice -> Server 1 (token in request, server validates)
  User Alice -> Server 2 (same token, server validates)
  -> Any server can handle any request
```

Statelessness enables horizontal scaling. Add servers, remove servers — no session migration needed.

### Reliability

```
Stateful:
  Server 1 crashes -> all sessions on Server 1 are lost
  Users must re-authenticate

Stateless:
  Server 1 crashes -> load balancer routes to Server 2
  Token still valid -> user continues without interruption
```

### Caching

```
Stateless request:
  GET /products?category=electronics
  -> Response depends only on the request
  -> Cache by URL, serve to any user

Stateful request:
  GET /my-products
  -> Response depends on session (who is "my"?)
  -> Cannot cache without user context
```

## Where state lives

State doesn't vanish in a stateless API. It moves to one of these places:

### 1. Client-side (tokens)

The client carries its own state in every request.

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**JWT (JSON Web Token):**
```
Header:   { "alg": "RS256", "typ": "JWT" }
Payload:  { "sub": "123", "name": "Alice", "role": "admin", "exp": 1700000000 }
Signature: HMAC(header + payload, secret)
```

The token contains the user's identity and permissions. The server validates the signature without looking anything up.

**Advantages:**
- Server doesn't store session data
- Any server can validate the token
- No database lookup per request

**Disadvantages:**
- Cannot revoke individual tokens (token is valid until expiry)
- Token size grows with claims (every request carries the payload)
- Sensitive data in token is visible (base64 encoded, not encrypted)

### 2. Server-side (session store)

Server stores session data in a shared store.

```
Client sends:
  Cookie: session_id=abc123

Server does:
  session = redis.get("session:abc123")
  user_id = session.user_id
  role = session.role
```

**Session in shared store (Redis):**
```
Server 1 -> Redis <- Server 2
         ↗      ↖
Server 3          Server 4

Any server can look up any session.
```

**Advantages:**
- Can revoke sessions instantly (delete from store)
- Session data stays server-side (not visible to client)
- Token is small (just an opaque ID)

**Disadvantages:**
- Every request requires a store lookup (added latency)
- Session store becomes a single point of failure
- Session store must scale with user count

### 3. Database

Long-lived state (user preferences, settings, API keys) lives in the database.

```
Request: GET /users/123/preferences
Server: SELECT preferences FROM users WHERE id = 123
-> No session needed, state in database
```

This is standard data retrieval, not session state.

## Token types

### JWT (JSON Web Token)

Self-contained token. Server can validate without any lookup.

```
Structure: header.payload.signature

Flow:
1. Client authenticates -> server creates JWT, signs it
2. Client stores JWT (localStorage, cookie, memory)
3. Client sends JWT with every request
4. Server validates signature -> trusts the claims

Validation:
  verify(token.signature, server_secret) -> valid/invalid
  check(token.exp > now) -> not expired
  -> No database query needed
```

**When JWT works:**
- Microservices (each service validates independently)
- Short-lived tokens (minutes to hours)
- Claims rarely change during token lifetime

**When JWT doesn't work:**
- Need to revoke tokens immediately (logout, compromised account)
- Large number of claims (token becomes too large)
- Token data changes frequently

### Opaque tokens

Random string. Requires server-side lookup.

```
Token: f47ac10b-58cc-4372-a567-0e02b2c3d479

Flow:
1. Client authenticates -> server creates random token, stores in Redis
2. Client sends token with every request
3. Server looks up token in Redis -> gets user data
4. If not found -> invalid/expired
```

**When opaque tokens work:**
- Need instant revocation (delete from store)
- Sensitive data should not be in the token
- Server-side control over sessions is required

**When opaque tokens don't work:**
- Thousands of services (each lookup adds latency)
- Token store availability is a concern

### Hybrid approach

Use both. Short-lived JWT for routine requests, opaque refresh token for renewing JWTs.

```
Access token (JWT):
  - Short lived (15 minutes)
  - Self-contained (no lookup)
  - Used for API requests

Refresh token (opaque):
  - Long lived (30 days)
  - Stored in server-side store
  - Used only to get new access tokens
  - Can be revoked instantly

Flow:
1. Login -> receive access token (JWT) + refresh token (opaque)
2. API requests -> use access token
3. Access token expires -> send refresh token to /token/refresh
4. Server validates refresh token in store -> issues new access token
5. Logout -> delete refresh token from store
```

## Cookies vs headers

### Cookies

```
Server response:
  Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Strict

Subsequent requests (automatic):
  Cookie: session_id=abc123
```

**Advantages:**
- Browser sends automatically (no client code needed)
- `HttpOnly` prevents JavaScript access (XSS protection)
- `Secure` ensures HTTPS only
- `SameSite` prevents CSRF

**Disadvantages:**
- Not suitable for non-browser clients (mobile apps, other services)
- CORS complications for cross-domain APIs
- Cookie size limits (~4KB)

### Authorization header

```
Authorization: Bearer eyJhbG...
```

**Advantages:**
- Works with any client (browser, mobile, service)
- No CORS cookie complications
- Explicit — developer controls when to send it

**Disadvantages:**
- Client must store token (localStorage vulnerable to XSS)
- Client must attach to every request manually
- No automatic browser handling

**Recommendation:**
- Browser-only apps -> cookies with `HttpOnly`, `Secure`, `SameSite`
- APIs consumed by multiple clients -> Authorization header
- Service-to-service -> mTLS or Authorization header

## State in distributed systems

### Sticky sessions

```
Load balancer routes user to the same server:

User Alice -> always -> Server 1
User Bob   -> always -> Server 2

If Server 1 dies -> Alice's session is lost
```

**Problems:**
- Uneven load distribution (one server may get all active users)
- Server failure loses sessions
- Scaling requires session migration

**When sticky sessions are acceptable:**
- WebSocket connections (must maintain connection to same server)
- In-memory caches that are expensive to rebuild
- Legacy systems that can't be refactored

### Session replication

```
Server 1 writes session -> replicates to Server 2, Server 3

Any server can handle any request.
```

**Problems:**
- Replication delay (stale reads possible)
- Network bandwidth for replication
- Complexity grows with server count

### External session store

```
All servers -> shared Redis/Memcached

Server 1 writes session -> Redis
Server 2 reads session -> Redis
```

**This is the standard approach for production systems.** Redis provides sub-millisecond lookups, replication for availability, and TTL for automatic expiry.

## Common state management mistakes

1. **Storing everything in JWT** — JWT grows large, sent with every request. Keep claims minimal
2. **No token expiry** — tokens valid forever are a security risk
3. **Session in application memory** — dies with the process, breaks scaling
4. **Mixing session and application state** — shopping carts in sessions. Use database for business data
5. **No refresh token rotation** — reusing refresh tokens allows stolen tokens to work indefinitely
6. **Ignoring token size** — large JWTs add latency to every request (headers have size limits in some proxies)

State management determines how your API handles identity across requests. But APIs also change over time, and managing that change is equally critical. See [5_API_Versioning.md](file:///d:/Playground/Backend%20Notes/6_API_Design/5_API_Versioning.md).
