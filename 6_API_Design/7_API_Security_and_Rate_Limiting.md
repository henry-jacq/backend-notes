---
title: "API Security and Rate Limiting"
part: 6
part_title: "API Design"
chapter: 8
summary: "An API is an attack surface. Every public endpoint is an invitation for abuse. Security is not optional — it is a..."
---
# API Security and Rate Limiting

An API is an attack surface. Every public endpoint is an invitation for abuse. Security is not optional — it is a prerequisite for operating an API in production. Rate limiting is not just about fairness — it is about keeping the system alive.

## Why API security is different

Traditional web security focuses on browsers: cookies, HTML injection, form submissions. API security focuses on programmatic access: tokens, JSON payloads, automated requests.

```
Web application attack:
  Attacker -> browser -> HTML form -> server

API attack:
  Attacker -> script -> HTTP request -> server
  No browser. No forms. No CAPTCHA. Just raw requests.
```

APIs are easier to attack because:

- Automated tools can send thousands of requests per second
- No browser rendering step to slow down attackers
- API documentation tells attackers exactly how to call endpoints
- Consistent JSON responses make parsing easy

## Rate limiting

Rate limiting controls how many requests a client can make in a time window. Without it, a single client can consume all server resources.

### Why rate limiting matters

```
Without rate limiting:
  Normal users: 10 requests/second
  Attacker: 10,000 requests/second
  -> Server overwhelmed -> all users affected

With rate limiting:
  Each client: max 100 requests/minute
  Attacker exceeds limit -> gets 429 Too Many Requests
  Normal users unaffected
```

### Rate limiting algorithms

#### Fixed window

```
Window: 1 minute
Limit: 100 requests

00:00 - 00:59 -> count requests -> allow up to 100
01:00 - 01:59 -> counter resets -> allow up to 100

Problem: boundary burst
  00:59 -> 100 requests (allowed)
  01:00 -> 100 requests (allowed, counter reset)
  -> 200 requests in 2 seconds
```

Simple to implement but allows burst at window boundaries.

#### Sliding window log

```
Track timestamp of every request.
For each new request:
  Count requests in last 60 seconds
  If count < limit -> allow
  If count >= limit -> reject

No boundary problem. But stores every request timestamp (memory-intensive).
```

#### Sliding window counter

```
Combine fixed windows with weighted counting:

Current window: 40 requests (30 seconds elapsed)
Previous window: 80 requests

Weighted count = (previous × remaining%) + current
               = (80 × 0.5) + 40
               = 80

If limit is 100 -> allow (80 < 100)
```

Good balance between accuracy and memory usage.

#### Token bucket

```
Bucket holds tokens (max capacity: 100)
Tokens added at fixed rate (10 per second)
Each request consumes 1 token
No tokens left -> request rejected

State:
  tokens: 100 (starts full)
  refill_rate: 10/second

Request at t=0: tokens = 99 -> allowed
Request at t=0: tokens = 98 -> allowed
...
100 requests at t=0: tokens = 0 -> reject subsequent
After 1 second: tokens = 10 (refilled)
```

**Advantages:**

- Allows controlled bursts (up to bucket capacity)
- Smooth rate limiting over time
- Simple to implement and understand

**Used by:** AWS, Stripe, most production APIs

#### Leaky bucket

```
Requests enter a queue (bucket).
Queue processes at a fixed rate.
If queue is full, new requests are dropped.

Incoming:   [req][req][req][req][req]
                    ↓
Queue:      [req][req][req] (max size 3)
                    ↓
Processing: [req] -> process -> [req] -> process (fixed rate)
```

**Difference from token bucket:**

- Token bucket allows bursts up to capacity
- Leaky bucket processes at a constant rate (smooths bursts)

### Rate limit headers

Standard headers inform clients about their rate limit status:

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100        -> max requests per window
X-RateLimit-Remaining: 45     -> requests left in current window
X-RateLimit-Reset: 1700003600 -> Unix timestamp when window resets
Retry-After: 30               -> seconds to wait (on 429 response)

HTTP/1.1 429 Too Many Requests
Retry-After: 30
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 30 seconds.",
    "retry_after": 30
  }
}
```

### Rate limiting dimensions

```
By IP address:
  192.168.1.1 -> 100 req/min
  -> Simple but shared IPs (corporate, NAT) punish legitimate users

By API key:
  key_abc -> 1000 req/min
  key_def -> 100 req/min
  -> Per-customer limits, different tiers

By user:
  user_123 -> 100 req/min
  -> Requires authentication first

By endpoint:
  POST /orders -> 10 req/min (expensive operation)
  GET /products -> 1000 req/min (cheap read)
  -> Different limits for different costs

By combination:
  user_123 + POST /orders -> 10 req/min
  -> Most precise but most complex
```

## Input validation

Every input from every client is potentially malicious. Validate everything.

### Validation layers

```
Layer 1: Transport
  -> HTTPS only (reject HTTP)
  -> Content-Type header matches body

Layer 2: Syntax
  -> Valid JSON/XML/protobuf
  -> Required fields present
  -> Field types correct (string, integer, etc.)

Layer 3: Semantics
  -> Values within expected ranges
  -> Email format valid
  -> Date is not in the past
  -> Quantity > 0

Layer 4: Business rules
  -> User exists
  -> Sufficient inventory
  -> Account not suspended
```

### Common injection attacks

```
SQL injection:
  Input: { "username": "admin'; DROP TABLE users;--" }
  Fix: Parameterized queries, never concatenate input into SQL

NoSQL injection:
  Input: { "username": { "$gt": "" } }
  Fix: Validate input types, reject object where string expected

Command injection:
  Input: { "filename": "report.pdf; rm -rf /" }
  Fix: Never pass user input to shell commands

Path traversal:
  Input: { "file": "../../../etc/passwd" }
  Fix: Validate and sanitize file paths, use allowlists
```

### Request size limits

```
Protect against:

  - 10GB JSON payload -> server runs out of memory parsing
  - Deeply nested JSON -> stack overflow during parsing
  - Millions of array elements -> processing takes forever

Limits to set:

  - Max request body size: 1MB (adjust per endpoint)
  - Max JSON depth: 20 levels
  - Max array length: 1000 elements
  - Max string length: 10,000 characters
```

## CORS (Cross-Origin Resource Sharing)

CORS controls which websites can call your API from a browser.

```
Without CORS:
  malicious-site.com loads JavaScript that calls your API
  Browser sends user's cookies automatically
  API processes request thinking it's from legitimate user

With CORS:
  Browser checks: "Is malicious-site.com allowed to call this API?"
  Server responds with allowed origins
  Browser blocks request if origin not allowed
```

### CORS headers

```
Request from https://myapp.com:
  Origin: https://myapp.com

Server response:
  Access-Control-Allow-Origin: https://myapp.com
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE
  Access-Control-Allow-Headers: Authorization, Content-Type
  Access-Control-Max-Age: 86400
```

### Preflight requests

```
Browser sends OPTIONS request before actual request:

OPTIONS /api/users
Origin: https://myapp.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Authorization

Server responds:
Access-Control-Allow-Origin: https://myapp.com
Access-Control-Allow-Methods: POST
Access-Control-Allow-Headers: Authorization

Browser: origin is allowed -> send actual POST request
```

**Common CORS mistakes:**

- `Access-Control-Allow-Origin: *` with credentials (browsers reject this)
- Not handling OPTIONS preflight (requests fail silently)
- Allowing all origins in production (defeats the purpose)

## CSRF protection for APIs

CSRF (Cross-Site Request Forgery) tricks a user's browser into making requests to your API.

```
Attack:
  User is logged into bank.com (has session cookie)
  User visits malicious-site.com
  Malicious site has: <form action="https://bank.com/transfer" method="POST">
  Form submits automatically -> browser sends bank.com cookies
  -> Money transferred without user's knowledge
```

### CSRF protection strategies

```
1. SameSite cookies:
   Set-Cookie: session=abc; SameSite=Strict
   -> Browser won't send cookie from cross-site requests

2. CSRF tokens:
   Server generates random token per session
   Client includes token in request header: X-CSRF-Token: random123
   Server validates token matches session

3. Check Origin/Referer header:
   If Origin != expected domain -> reject

4. Use Authorization header instead of cookies:
   Bearer tokens are not sent automatically by browser
   -> CSRF attacks don't work (attacker can't read the token)
```

**For APIs:** If you use `Authorization: Bearer` tokens (not cookies), CSRF is not a concern. CSRF exploits automatic cookie sending.

## Security headers

```
Response headers for API security:

Strict-Transport-Security: max-age=31536000; includeSubDomains
-> Force HTTPS for 1 year

X-Content-Type-Options: nosniff
-> Prevent MIME type sniffing

X-Frame-Options: DENY
-> Prevent embedding in iframes

Cache-Control: no-store
-> Prevent caching sensitive responses

Content-Security-Policy: default-src 'none'
-> Restrict resource loading (mainly for HTML responses)
```

## OWASP API Security Top 10

The most common API security vulnerabilities:

```
1. Broken Object Level Authorization (BOLA)
   GET /api/users/456/orders -> returns orders for user 456
   But caller is user 123 -> should be denied
   Fix: Always check if the authenticated user owns the requested resource

2. Broken Authentication
   Weak passwords, no rate limiting on login, credential stuffing
   Fix: Strong auth, MFA, account lockout, rate limiting

3. Broken Object Property Level Authorization
   PUT /api/users/123 { "role": "admin" }
   Server blindly updates all fields -> user becomes admin
   Fix: Whitelist allowed fields per role, ignore unauthorized fields

4. Unrestricted Resource Consumption
   No rate limiting, no pagination limits, no request size limits
   Fix: Rate limit, paginate, set size limits

5. Broken Function Level Authorization
   Regular user calls: DELETE /api/admin/users/456
   Server doesn't check admin role -> user deleted
   Fix: Authorization check on every endpoint

6. Unrestricted Access to Sensitive Business Flows
   Bot buys all concert tickets, scrapes pricing data
   Fix: Rate limiting, CAPTCHA, business logic validation

7. Server-Side Request Forgery (SSRF)
   Input: { "webhook_url": "http://internal-service:8080/admin" }
   Server makes request to internal service on behalf of attacker
   Fix: Validate and allowlist URLs, block internal IPs

8. Security Misconfiguration
   Debug mode in production, default credentials, verbose errors
   Fix: Security hardening checklist, automated scanning

9. Improper Inventory Management
   Old API versions still running, undocumented endpoints
   Fix: API inventory, deprecation workflow, remove unused endpoints

10. Unsafe Consumption of APIs
    Your service trusts responses from third-party APIs without validation
    Fix: Validate all external data, treat third-party responses as untrusted
```

## DDoS protection for APIs

```
DDoS (Distributed Denial of Service):
  Thousands of machines -> flood API with requests -> service unavailable

Protection layers:

Layer 1: Network (ISP/CDN)
  -> Absorb volumetric attacks (terabits of traffic)
  -> Cloudflare, AWS Shield, Akamai

Layer 2: API Gateway
  -> Rate limiting per IP/key
  -> Geographic blocking
  -> Request filtering

Layer 3: Application
  -> Request validation (reject malformed early)
  -> Circuit breakers on downstream calls
  -> Graceful degradation (serve cached responses)
```

## Common API security mistakes

1. **No rate limiting** — single client can take down the API
2. **Trusting client input** — not validating types, ranges, formats
3. **Verbose error messages** — stack traces, SQL errors, internal paths in responses
4. **No HTTPS** — tokens and data visible to network sniffers
5. **Wildcard CORS** — any website can call the API with user credentials
6. **Not logging security events** — can't detect or investigate breaches
7. **Hardcoded secrets in code** — API keys, database passwords in source control
8. **No request size limits** — 1GB JSON payload crashes the server

Rate limiting protects availability. Authentication protects identity. But in a microservices architecture, these concerns multiply across every service. API gateways and load balancers centralise these cross-cutting concerns. See [API Gateway and Load Balancing](file:///d:/Playground/Backend%20Notes/6_API_Design/8_API_Gateway_and_Load_Balancing.md).
