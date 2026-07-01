---
title: "API Versioning"
part: 6
part_title: "API Design"
chapter: 6
summary: "APIs are contracts. When you change a contract, you break everyone relying on it. Versioning is how you evolve APIs..."
---
# API Versioning

APIs are contracts. When you change a contract, you break everyone relying on it. Versioning is how you evolve APIs without destroying trust.

The hardest part of API design is not building the first version. It is changing the API without breaking existing consumers.

## Why APIs break

### Breaking changes

A breaking change is any change that causes existing clients to fail without modifying their code.

```
Breaking changes:
  - Removing a field from a response
  - Renaming a field
  - Changing a field's type (string -> integer)
  - Removing an endpoint
  - Changing required parameters
  - Changing the meaning of a status code
  - Changing authentication requirements
  - Changing error response format
```

### Non-breaking changes

```
Non-breaking changes:
  - Adding a new field to a response (clients ignore unknown fields)
  - Adding a new endpoint
  - Adding an optional parameter
  - Adding a new enum value (if client handles unknown values)
  - Improving error messages (without changing error codes)
  - Adding new HTTP methods to existing resources
```

**The key rule:** additions are safe, modifications and removals are breaking.

### Why breaking changes happen

```
Version 1:
  GET /users/123
  Response: { "name": "Alice Smith" }

Product requirement: separate first and last name.

Version 2 (breaking):
  GET /users/123
  Response: { "first_name": "Alice", "last_name": "Smith" }
  -> "name" field removed -> all clients parsing "name" break

Version 2 (non-breaking):
  GET /users/123
  Response: { "name": "Alice Smith", "first_name": "Alice", "last_name": "Smith" }
  -> "name" kept for backward compatibility -> no clients break
```

## Versioning strategies

### 1. URI versioning

Version in the URL path.

```
GET /v1/users/123
GET /v2/users/123
```

**Advantages:**
- Obvious and explicit
- Easy to test (change URL, see different behavior)
- Easy to route (load balancer, API gateway)
- Cache-friendly (different URL = different cache entry)

**Disadvantages:**
- URL changes for every version bump
- Clients must update URLs
- Resource identity changes (/v1/users/123 ≠ /v2/users/123, but they're the same user)
- Proliferation of versioned endpoints

**Implementation:**
```
Router:
  /v1/* -> handler_v1
  /v2/* -> handler_v2

Or:
  /v1/* -> same handler, behavior flag = v1
  /v2/* -> same handler, behavior flag = v2
```

**This is the most common approach.** Simple, widely understood, easy to implement.

### 2. Header versioning

Version in a custom header.

```
GET /users/123
Accept-Version: v2

Or:
GET /users/123
X-API-Version: 2
```

**Advantages:**
- Clean URLs (resource identity doesn't change)
- Can default to latest version if header missing
- Separates versioning from resource identification

**Disadvantages:**
- Not visible in URL (harder to debug, share, bookmark)
- Requires header inspection for routing
- Clients must set headers correctly
- Can't test by just changing URL

### 3. Query parameter versioning

```
GET /users/123?version=2
GET /users/123?api-version=2024-01-15
```

**Advantages:**
- URL-visible (can share, bookmark)
- Optional (default to latest if not specified)
- Easy to add to existing APIs

**Disadvantages:**
- Pollutes query parameters (mixes versioning with filtering)
- Inconsistent with query parameter semantics (version is metadata, not a filter)

### 4. Content negotiation (media type versioning)

Version in the Accept header using vendor media types.

```
GET /users/123
Accept: application/vnd.myapi.v2+json

Response:
Content-Type: application/vnd.myapi.v2+json
```

**Advantages:**
- RESTful (uses HTTP content negotiation as intended)
- Fine-grained (can version individual resources)
- Clean URLs

**Disadvantages:**
- Complex to implement and test
- Not widely understood by developers
- Tooling support is limited
- Hard to debug

### Which strategy to use

```
Strategy           | Visibility | Simplicity | RESTfulness | Adoption
URI (/v1/...)      | High       | High       | Low         | Most common
Header             | Low        | Medium     | Medium      | Common in enterprise
Query param        | Medium     | High       | Low         | Less common
Content negotiation| Low        | Low        | High        | Rare
```

**Recommendation:** Use URI versioning unless you have a specific reason not to. It's the most widely understood and easiest to implement.

## Date-based versioning

Some APIs use dates instead of numbers.

```
GET /users/123
api-version: 2024-01-15

Each date represents a snapshot of the API behavior.
```

**Used by:** Stripe, Azure

**How it works:**
```
Client sets api-version: 2023-06-01
-> Server returns response format as of June 1, 2023

Client sets api-version: 2024-01-15
-> Server returns response format as of January 15, 2024
```

**Advantages:**
- No arbitrary version numbers
- Clear timeline of changes
- Client pins to a date and migrates when ready

**Disadvantages:**
- Many versions to maintain (every date is potentially different)
- Complex server-side logic to handle date ranges
- Must document what changed on each date

## Semantic versioning for APIs

```
MAJOR.MINOR.PATCH
  2.1.3

MAJOR -> breaking changes (v1 -> v2)
MINOR -> new features, backward compatible (v2.0 -> v2.1)
PATCH -> bug fixes (v2.1.0 -> v2.1.1)
```

**In practice for APIs:**
- Only MAJOR version appears in URL: `/v1/`, `/v2/`
- MINOR and PATCH are internal (documented in changelog)
- Clients care about MAJOR (determines compatibility)

## Deprecation workflow

Deprecation is how you tell consumers to stop using an old version.

### The timeline

```
Phase 1: Announce deprecation
  - Document that v1 will be deprecated
  - Add Deprecation header to v1 responses
  - Communicate timeline (email, docs, dashboard)

Phase 2: Sunset period
  - v1 still works
  - v2 is the recommended version
  - v1 responses include Sunset header with date
  - Log which clients still use v1

Phase 3: End of life
  - v1 returns 410 Gone
  - Clients that didn't migrate break
  - Support available for migration assistance
```

### Deprecation headers

```
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 01 Jun 2025 00:00:00 GMT
Link: <https://api.example.com/v2/docs>; rel="successor-version"
```

- `Deprecation: true` — this version is deprecated
- `Sunset` — date when this version stops working
- `Link` — pointer to the replacement

### Migration support

```
Good deprecation:
  1. Announce 6+ months in advance
  2. Provide migration guide (v1 field -> v2 field mapping)
  3. Offer both versions simultaneously
  4. Log usage of deprecated endpoints
  5. Contact heavy users directly
  6. Provide migration tools or scripts

Bad deprecation:
  1. Remove endpoint without notice
  2. Change behavior silently
  3. Give 2 weeks notice for a breaking change
```

## Backward compatibility strategies

### Additive changes only

The safest approach: never remove or rename fields.

```
v1: { "name": "Alice Smith" }
v2: { "name": "Alice Smith", "first_name": "Alice", "last_name": "Smith" }
v3: { "name": "Alice Smith", "first_name": "Alice", "last_name": "Smith", "display_name": "Alice S." }

Each version adds fields. Old clients work with every version.
```

**Trade-off:** Response payload grows over time with legacy fields.

### Tolerant reader pattern

Clients should ignore fields they don't understand.

```
Client code:
  user = response.json()
  name = user["name"]       // use known fields
  // ignore any unknown fields

Not:
  assert set(user.keys()) == {"id", "name", "email"}  // breaks if new field added
```

**Rule for clients:** Parse what you need, ignore what you don't.

**Rule for servers:** Never remove fields without a version bump.

### Expand-contract pattern

For database-backed changes that affect the API:

```
Step 1 (expand): Add new field, populate from old field
  DB: name + first_name + last_name
  API: returns all three

Step 2 (migrate): Update all clients to use new fields

Step 3 (contract): Remove old field
  DB: first_name + last_name only
  API v2: returns first_name, last_name only
```

## Versioning in GraphQL

GraphQL takes a different approach: **no versioning**.

```
Instead of versions, evolve the schema:
  1. Add new fields (non-breaking)
  2. Deprecate old fields (mark with @deprecated)
  3. Remove deprecated fields after migration period

type User {
  name: String @deprecated(reason: "Use firstName and lastName")
  firstName: String
  lastName: String
}
```

Because clients request specific fields, adding new fields never breaks existing queries. Deprecated fields continue to work until explicitly removed.

## Versioning in gRPC

Protocol Buffers have built-in backward compatibility rules:

```protobuf
// v1
message User {
  int64 id = 1;
  string name = 2;
}

// v2 (backward compatible)
message User {
  int64 id = 1;
  string name = 2;        // kept
  string first_name = 3;  // new field, new number
  string last_name = 4;   // new field, new number
}
```

**Rules:**
- Never change field numbers
- Never change field types
- Use `reserved` for removed fields
- Add new fields with new numbers

Old clients reading v2 messages ignore unknown fields. New clients reading v1 messages get default values for missing fields.

## Common versioning mistakes

1. **No versioning from day one** — adding versioning later requires migrating all consumers simultaneously
2. **Too many versions** — maintaining 5+ active versions is unsustainable
3. **Silent breaking changes** — changing behavior without bumping version
4. **No deprecation period** — removing versions without warning
5. **Versioning internal APIs like public APIs** — internal APIs can afford faster deprecation cycles
6. **Coupling version to deployment** — version represents the contract, not the release

Versioning protects the API contract over time. But the API also needs to verify who is calling it and what they're allowed to do. See [6_Authentication_and_Authorization.md](file:///d:/Playground/Backend%20Notes/6_API_Design/6_Authentication_and_Authorization.md).
