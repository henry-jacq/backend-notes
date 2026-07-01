---
title: "REST API Design"
part: 6
part_title: "API Design"
chapter: 2
summary: "REST (Representational State Transfer) is the dominant paradigm for web APIs. Most APIs you interact with are REST..."
---
# REST API Design

REST (Representational State Transfer) is the dominant paradigm for web APIs. Most APIs you interact with are REST APIs. But most REST APIs are poorly designed — they expose database tables as endpoints, ignore HTTP semantics, and break consumers with every release.

Good REST design treats the API as a product with clear contracts, predictable behaviour, and graceful evolution.

## What REST actually means

REST is an architectural style, not a specification. It was defined by Roy Fielding in his 2000 dissertation. The core constraints:

1. **Client-server** — client and server are separate, evolve independently
2. **Stateless** — each request contains all information needed to process it
3. **Cacheable** — responses must declare whether they are cacheable
4. **Uniform interface** — consistent way to interact with resources
5. **Layered system** — client doesn't know if it talks to the server directly or through intermediaries
6. **Code on demand (optional)** — server can send executable code to client

Most "REST" APIs only follow the first two constraints. That's fine for most use cases.

## Resource modelling

The core concept of REST: everything is a resource. A resource is a noun, not a verb.

**Good resource design:**
```
/users              -> collection of users
/users/123          -> specific user
/users/123/orders   -> orders belonging to user 123
/orders/456         -> specific order
```

**Bad resource design:**
```
/getUser?id=123          -> verb in URL
/createOrder             -> verb in URL
/user/123/getOrders      -> verb in URL
/api/v1/fetchAllProducts -> verb in URL
```

**The rule:** URLs identify resources (nouns). HTTP methods define actions (verbs).

### Nested vs flat resources

**Nested (shows relationship):**
```
GET /users/123/orders          -> orders for user 123
GET /users/123/orders/456      -> specific order for user 123
```

**Flat (independent access):**
```
GET /orders?user_id=123        -> orders filtered by user
GET /orders/456                -> specific order
```

**When to nest:**

- Resource only exists in context of parent (comments on a post)
- Parent-child relationship is the primary access pattern
- Nesting depth ≤ 2 (deeper nesting becomes unwieldy)

**When to keep flat:**

- Resource has its own identity (orders exist independently of users)
- Multiple access patterns exist (orders by user, by date, by status)
- Deep nesting would create long URLs

## HTTP methods

Each method has specific semantics. Using them correctly makes the API predictable.

```
Method  | Action           | Idempotent | Safe | Request Body
--------|------------------|------------|------|-------------
GET     | Read resource    | Yes        | Yes  | No
POST    | Create resource  | No         | No   | Yes
PUT     | Replace resource | Yes        | No   | Yes
PATCH   | Partial update   | No*        | No   | Yes
DELETE  | Remove resource  | Yes        | No   | No
```

*PATCH can be made idempotent with proper design.

**Safe** means the method doesn't modify server state. **Idempotent** means calling it multiple times has the same effect as calling it once.

### Why idempotency matters

```
Scenario: Client sends POST /orders to create an order.
Network fails after server processes request but before client gets response.

Without idempotency:
  Client retries POST /orders -> duplicate order created

With idempotency key:
  Client sends POST /orders with Idempotency-Key: abc-123
  Client retries POST /orders with Idempotency-Key: abc-123
  Server recognizes key, returns original response -> no duplicate
```

Idempotency is critical for any operation involving money, inventory, or state changes.

**PUT is naturally idempotent:**
```
PUT /users/123 { "name": "Alice", "email": "alice@example.com" }
PUT /users/123 { "name": "Alice", "email": "alice@example.com" }
-> Same result regardless of how many times called
```

**POST is not naturally idempotent:**
```
POST /orders { "item": "laptop", "qty": 1 }
POST /orders { "item": "laptop", "qty": 1 }
-> Two orders created (not the same result)
```

## HTTP status codes

Use status codes correctly. They tell the client what happened without parsing the body.

### Success codes (2xx)

```
200 OK              -> Request succeeded (GET, PUT, PATCH, DELETE)
201 Created         -> Resource created (POST)
202 Accepted        -> Request accepted for async processing
204 No Content      -> Success, no body returned (DELETE)
```

### Client error codes (4xx)

```
400 Bad Request     -> Malformed request (invalid JSON, missing field)
401 Unauthorized    -> Authentication required or failed
403 Forbidden       -> Authenticated but not authorized
404 Not Found       -> Resource doesn't exist
405 Method Not Allowed -> HTTP method not supported for this resource
409 Conflict        -> Request conflicts with current state (duplicate)
422 Unprocessable   -> Request is valid but semantically incorrect
429 Too Many Requests -> Rate limit exceeded
```

### Server error codes (5xx)

```
500 Internal Server Error -> Unhandled server error
502 Bad Gateway          -> Upstream service returned invalid response
503 Service Unavailable  -> Server is overloaded or in maintenance
504 Gateway Timeout      -> Upstream service timed out
```

**Common mistakes:**

- Returning `200` with an error in the body (client thinks it succeeded)
- Using `404` for authorisation failures (leaks resource existence)
- Returning `500` for all errors (client can't distinguish retryable vs non-retryable)

## URI design principles

**Use plural nouns:**
```
GET /users          -> collection
GET /users/123      -> single resource
Not: GET /user/123
```

**Use lowercase with hyphens:**
```
GET /order-items/456
Not: GET /orderItems/456
Not: GET /order_items/456
```

**Don't expose implementation details:**
```
GET /users/123
Not: GET /mysql/users/table/row/123
Not: GET /api/UserController/findById/123
```

**Use query parameters for filtering, not path segments:**
```
GET /orders?status=shipped&created_after=2024-01-01
Not: GET /orders/shipped/2024-01-01
```

## Pagination

Any endpoint that returns a collection must support pagination. Returning thousands of records in one response is a performance and usability failure.

### Offset-based pagination

```
GET /users?offset=0&limit=20    -> first 20 users
GET /users?offset=20&limit=20   -> next 20 users
GET /users?offset=40&limit=20   -> next 20 users
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "total": 1000,
    "offset": 20,
    "limit": 20
  }
}
```

**Problem:** Offset pagination breaks with real-time data. If a new record is inserted at position 0, all offsets shift. The client may see duplicates or miss records.

**When offset works:**

- Data is relatively static
- Users navigate by page number
- Total count is needed

### Cursor-based pagination

```
GET /users?limit=20                          -> first 20 users
GET /users?limit=20&cursor=eyJpZCI6MjB9     -> next 20 after cursor
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6NDB9",
    "has_more": true
  }
}
```

**How it works:** The cursor encodes a position (usually the last item's ID). The server queries `WHERE id > cursor_id LIMIT 20`. Inserts don't shift the window.

**When cursor works:**

- Data changes frequently (social feeds, event logs)
- Infinite scroll UIs
- Large datasets where `COUNT(*)` is expensive

**Trade-off:** No "jump to page 5" — cursor pagination is sequential only.

## Filtering and sorting

**Filtering:**
```
GET /orders?status=shipped
GET /orders?status=shipped&customer_id=123
GET /orders?created_after=2024-01-01&created_before=2024-12-31
```

**Sorting:**
```
GET /orders?sort=created_at&order=desc
GET /orders?sort=-created_at                 -> prefix notation (- means desc)
GET /orders?sort=status,created_at           -> multi-field sort
```

**Searching:**
```
GET /users?q=alice                           -> full-text search
GET /products?search=laptop&category=electronics
```

Keep filter parameter names consistent across all endpoints.

## Content negotiation

```
Client sends:
Accept: application/json

Server responds:
Content-Type: application/json
```

**Multiple format support:**
```
Accept: application/json    -> JSON response
Accept: application/xml     -> XML response
Accept: text/csv            -> CSV response
```

Most modern APIs only support JSON. That's fine. But set `Content-Type` correctly.

## Error response format

Standardise error responses across the entire API.

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "must be a valid email address"
      },
      {
        "field": "age",
        "message": "must be a positive integer"
      }
    ]
  }
}
```

**Requirements:**

- Machine-readable error code (not just the HTTP status)
- Human-readable message
- Field-level details for validation errors
- Consistent structure for all error responses

**Never expose:**

- Stack traces
- Database error messages
- Internal service names
- File paths

## REST maturity model (Richardson)

**Level 0 — The swamp of POX:**
```
POST /api
Body: { "action": "getUser", "id": 123 }
```
One endpoint, actions in the body. This is RPC over HTTP, not REST.

**Level 1 — Resources:**
```
POST /users/123
Body: { "action": "get" }
```
Multiple endpoints for resources, but still using POST for everything.

**Level 2 — HTTP verbs:**
```
GET /users/123
POST /users
PUT /users/123
DELETE /users/123
```
Correct use of HTTP methods and status codes. **Most production APIs are here.**

**Level 3 — Hypermedia (HATEOAS):**
```json
{
  "id": 123,
  "name": "Alice",
  "links": {
    "self": "/users/123",
    "orders": "/users/123/orders",
    "update": "/users/123"
  }
}
```
Responses include links to related actions. Client discovers the API by following links. **Rarely implemented in practice** but useful for discoverability.

## Common REST design mistakes

1. **Verbs in URLs** — `POST /createUser` instead of `POST /users`
2. **Ignoring HTTP methods** — using POST for everything
3. **Exposing database schema** — `/user_table/row/123` instead of `/users/123`
4. **No pagination** — returning all records in one response
5. **Inconsistent naming** — `/users` in one place, `/user` in another
6. **200 for errors** — returning `200 OK` with error details in body
7. **No versioning** — breaking changes hit all consumers simultaneously
8. **Chatty APIs** — requiring 10 requests to load one page

REST is the right choice for most public APIs and simple service-to-service communication. But when clients need flexible queries or when over-fetching becomes a real problem, consider GraphQL. See [2_GraphQL.md](file:///d:/Playground/Backend%20Notes/6_API_Design/2_GraphQL.md).
