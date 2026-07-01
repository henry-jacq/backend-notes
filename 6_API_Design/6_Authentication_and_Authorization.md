# Authentication and Authorization

Every production API must answer two questions: **who is calling?** (authentication) and **what are they allowed to do?** (authorization). These are different concerns with different mechanisms. Conflating them is one of the most common API security mistakes.

## Authentication vs authorization

```
Authentication (authn):
  "Who are you?"
  → Verify identity
  → Input: credentials (password, token, certificate)
  → Output: identity (user ID, service name)

Authorization (authz):
  "What can you do?"
  → Verify permissions
  → Input: identity + requested action
  → Output: allow or deny
```

**Example:**
```
Request: DELETE /users/456
Authentication: Token belongs to user 123 (identity verified)
Authorization: Does user 123 have permission to delete user 456? (permission checked)
```

Authentication happens first. Authorization depends on authentication.

## API keys

The simplest authentication mechanism. A long, random string identifies the caller.

```
Request:
  GET /api/weather?city=london
  X-API-Key: sk_live_abc123def456ghi789
```

**How API keys work:**
```
1. Developer registers → server generates API key
2. Developer includes key in requests
3. Server looks up key → finds associated account
4. Server checks key permissions → allows or denies
```

**When API keys work:**
- Server-to-server communication
- Public APIs with usage tracking (rate limiting per key)
- Low-security scenarios (read-only public data)

**When API keys don't work:**
- User-facing authentication (API keys identify applications, not users)
- High-security scenarios (keys are long-lived, hard to rotate)
- Delegated access (user grants limited access to a third party)

**API key security:**
- Never embed in client-side code (visible in browser)
- Transmit only over HTTPS
- Store hashed on server side (like passwords)
- Support rotation (issue new key, deprecate old one)
- Scope keys (read-only vs read-write, per-resource)

## OAuth 2.0

OAuth 2.0 is the standard for **delegated authorization**. It allows a user to grant a third-party application limited access to their resources without sharing their password.

### The problem OAuth solves

```
Without OAuth:
  User gives their Google password to a third-party app
  App can access everything (email, drive, contacts, payments)
  User can't revoke access without changing password
  Password shared with multiple apps = single breach compromises all

With OAuth:
  User authorizes specific permissions (read email only)
  App gets a token, not the password
  User revokes token without changing password
  Token has limited scope and lifetime
```

### OAuth 2.0 roles

```
Resource Owner  → The user who owns the data
Client          → The application requesting access
Authorization Server → Issues tokens after user consent (Google, GitHub, etc.)
Resource Server → The API that holds the user's data
```

### Authorization Code flow (most secure, server-side apps)

This is the recommended flow for web applications with a backend server.

```
Step 1: Client redirects user to authorization server
  → https://auth.example.com/authorize?
      response_type=code
      &client_id=my-app
      &redirect_uri=https://myapp.com/callback
      &scope=read:profile read:email
      &state=random-csrf-token

Step 2: User authenticates and consents
  → User sees: "My App wants to access your profile and email"
  → User clicks "Allow"

Step 3: Authorization server redirects back with code
  → https://myapp.com/callback?code=AUTH_CODE_123&state=random-csrf-token

Step 4: Client exchanges code for tokens (server-to-server)
  POST https://auth.example.com/token
  Body: {
    grant_type: "authorization_code",
    code: "AUTH_CODE_123",
    client_id: "my-app",
    client_secret: "SECRET",
    redirect_uri: "https://myapp.com/callback"
  }

Step 5: Authorization server responds with tokens
  {
    "access_token": "eyJhbG...",
    "refresh_token": "dGhpcyBpcyBh...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "read:profile read:email"
  }

Step 6: Client uses access token to call API
  GET https://api.example.com/user/profile
  Authorization: Bearer eyJhbG...
```

**Why the code exchange exists (Step 4):**
The authorization code is exchanged server-to-server. The access token never passes through the browser. This prevents token theft via browser history, referrer headers, or JavaScript.

### Authorization Code flow with PKCE (public clients)

PKCE (Proof Key for Code Exchange) secures the flow for clients that can't keep a secret (mobile apps, SPAs).

```
Step 1: Client generates code_verifier (random string) and code_challenge
  code_verifier = random(43-128 characters)
  code_challenge = BASE64URL(SHA256(code_verifier))

Step 2: Client sends code_challenge with authorization request
  → /authorize?...&code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw&code_challenge_method=S256

Step 3: User authenticates, server returns authorization code

Step 4: Client sends code_verifier with token request
  POST /token
  Body: { code: "AUTH_CODE", code_verifier: "original_random_string" }

Step 5: Server verifies SHA256(code_verifier) == code_challenge
  → If match, issues tokens
  → If no match, rejects (attacker intercepted code but doesn't have verifier)
```

**Why PKCE matters:**
Without PKCE, an attacker who intercepts the authorization code (via malicious app on same device) can exchange it for tokens. With PKCE, they also need the code_verifier, which never left the original client.

### Client Credentials flow (service-to-service)

No user involved. One service authenticates to another.

```
POST https://auth.example.com/token
Body: {
  grant_type: "client_credentials",
  client_id: "order-service",
  client_secret: "SERVICE_SECRET",
  scope: "inventory:read inventory:update"
}

Response:
{
  "access_token": "eyJhbG...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Use when:**
- Microservice A calls microservice B
- Background jobs accessing APIs
- No user context needed

### Implicit flow (deprecated)

```
Token returned directly in URL fragment:
  https://myapp.com/callback#access_token=eyJhbG...

Problems:
  - Token visible in browser history
  - Token visible in server logs (if referrer leaks)
  - No refresh token
  - Cannot verify client identity

Status: DEPRECATED. Use Authorization Code + PKCE instead.
```

## JWT (JSON Web Token) in depth

JWT is the most common token format for API authentication. It carries claims (identity and permissions) in a self-contained, verifiable format.

### JWT structure

```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjMiLCJuYW1lIjoiQWxpY2UiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3MDAwMDAwMDAsImV4cCI6MTcwMDAwMzYwMH0.
signature_bytes_here

Three parts, base64url-encoded, separated by dots:
  Header.Payload.Signature
```

**Header:**
```json
{
  "alg": "RS256",     // signing algorithm
  "typ": "JWT",       // token type
  "kid": "key-id-1"   // key identifier (for key rotation)
}
```

**Payload (claims):**
```json
{
  "sub": "123",              // subject (user ID)
  "name": "Alice",           // custom claim
  "role": "admin",           // custom claim
  "iat": 1700000000,         // issued at (Unix timestamp)
  "exp": 1700003600,         // expiration (1 hour later)
  "iss": "https://auth.example.com",  // issuer
  "aud": "https://api.example.com",   // audience
  "scope": "read:users write:users"   // permissions
}
```

**Registered claims:**
```
sub  → Subject (who the token is about)
iss  → Issuer (who created the token)
aud  → Audience (who the token is for)
exp  → Expiration time
iat  → Issued at
nbf  → Not before (token not valid before this time)
jti  → JWT ID (unique identifier for this token)
```

### Signing algorithms

**Symmetric (HMAC):**
```
HMAC-SHA256: Same secret to sign and verify

Sign:   HMAC(header + payload, shared_secret) → signature
Verify: HMAC(header + payload, shared_secret) == signature?

Problem: Every service that verifies needs the secret.
         If any service is compromised, attacker can forge tokens.
```

**Asymmetric (RSA/ECDSA):**
```
RS256: Private key signs, public key verifies

Sign:   RSA_SIGN(header + payload, private_key) → signature
Verify: RSA_VERIFY(header + payload, public_key, signature) → valid?

Advantage: Only auth server has private key.
           Any service can verify with public key.
           Compromised service cannot forge tokens.
```

**Use asymmetric signing in production.** Symmetric is acceptable only when one service both signs and verifies.

### JWT validation checklist

```
Every service must validate:

1. Signature valid?     → verify(token, public_key)
2. Not expired?         → exp > current_time
3. Not used too early?  → nbf <= current_time (if present)
4. Correct issuer?      → iss == expected_issuer
5. Correct audience?    → aud == this_service
6. Required claims?     → sub, scope present
7. Sufficient scope?    → token scope covers requested action
```

**Never skip validation steps.** A common mistake is verifying the signature but ignoring expiration or audience.

### JWT security pitfalls

```
1. alg: "none" attack
   Attacker sends JWT with algorithm "none" (no signature)
   Vulnerable server accepts it without verification
   Fix: Always validate algorithm matches expected value

2. Key confusion attack
   Server expects RS256 (asymmetric)
   Attacker sends HS256 JWT signed with the public key
   Server uses public key as HMAC secret → signature matches
   Fix: Enforce expected algorithm, never accept "alg" from token

3. No expiration
   Token valid forever → stolen token = permanent access
   Fix: Always set exp, keep access tokens short-lived (15-60 min)

4. Sensitive data in payload
   JWT payload is base64-encoded, NOT encrypted
   Anyone can decode it: base64decode(payload) → readable JSON
   Fix: Never put passwords, credit cards, or secrets in JWT
```

## Refresh tokens

Refresh tokens solve the conflict between security (short-lived tokens) and usability (don't make users re-authenticate constantly).

### How refresh tokens work

```
Login:
  → Access token (JWT, 15 min expiry)
  → Refresh token (opaque, 30 day expiry, stored server-side)

Normal API calls:
  Authorization: Bearer <access_token>
  → Server validates JWT (no database lookup)

Access token expires:
  POST /auth/token/refresh
  Body: { "refresh_token": "rt_abc123..." }

  Server:
    1. Look up refresh token in database
    2. Verify not revoked or expired
    3. Issue new access token
    4. (Optionally) issue new refresh token (rotation)

  Response:
  {
    "access_token": "new_jwt...",
    "refresh_token": "rt_def456...",   // rotated
    "expires_in": 900
  }
```

### Refresh token rotation

```
Without rotation:
  Refresh token: rt_abc123
  Used at time 1 → new access token (refresh token unchanged)
  Used at time 2 → new access token (same refresh token)
  If stolen, attacker can use it indefinitely until expiry

With rotation:
  Refresh token: rt_abc123
  Used at time 1 → new access token + new refresh token rt_def456
  Old rt_abc123 is invalidated

  If attacker stole rt_abc123 and tries to use it:
  → Server detects reuse of invalidated token
  → Revokes entire token family (all refresh tokens for this user)
  → User must re-authenticate
```

**Refresh token rotation detects theft.** When a revoked refresh token is used, it means either the legitimate user or an attacker is using a stale token. Revoking the entire family forces re-authentication, which is the safe choice.

### Refresh token storage

```
Server-side (database/Redis):
  Key: hash(refresh_token)
  Value: { user_id, created_at, expires_at, family_id, revoked }

Client-side:
  Browser: HttpOnly, Secure cookie (not localStorage)
  Mobile: Secure storage (Keychain on iOS, Keystore on Android)
  Server: Environment variable or secrets manager

NEVER store refresh tokens in:
  - localStorage (accessible to XSS)
  - sessionStorage (lost on tab close)
  - URL parameters (visible in logs)
  - Plain text files
```

## Scopes and permissions

Scopes define what a token is allowed to do.

```
Scope examples:
  read:users        → can read user data
  write:users       → can create/update users
  delete:users      → can delete users
  admin:all         → full access

Token with limited scope:
  { "scope": "read:users read:orders" }

Request: DELETE /users/123
Check: "delete:users" in token.scope? → No → 403 Forbidden
```

**Scope design principles:**
- Use resource:action format (`read:users`, `write:orders`)
- Start with least privilege (minimal scopes by default)
- Allow scope combination (`read:users write:users`)
- Document all available scopes

## RBAC vs ABAC

### RBAC (Role-Based Access Control)

Permissions assigned to roles, roles assigned to users.

```
Roles:
  viewer  → can read
  editor  → can read + write
  admin   → can read + write + delete + manage users

User Alice → role: editor
User Bob   → role: viewer

Request from Alice: PUT /articles/123
Check: editor role allows write → 200 OK

Request from Bob: PUT /articles/123
Check: viewer role allows read only → 403 Forbidden
```

**When RBAC works:**
- Small number of well-defined roles
- Permissions are role-based, not context-dependent
- Organization structure maps to roles

**When RBAC doesn't work:**
- "Alice can edit articles she authored but not others"
- "Users can access data in their region only"
- Complex, attribute-dependent rules

### ABAC (Attribute-Based Access Control)

Permissions based on attributes of user, resource, and environment.

```
Policy: "Users can edit articles they authored"

Attributes:
  User: { id: 123, role: editor, department: engineering }
  Resource: { type: article, author_id: 123, status: published }
  Environment: { time: business_hours, ip: internal_network }

Evaluation:
  user.id == resource.author_id? → Yes
  user.role == "editor"? → Yes
  → Allow
```

**When ABAC works:**
- Fine-grained, context-dependent permissions
- Multi-tenant systems (tenant isolation)
- Regulatory requirements (data residency, time-based access)

**Trade-off:** ABAC is more powerful but more complex to implement and debug than RBAC.

## Service-to-service authentication

### mTLS (Mutual TLS)

Both client and server present certificates. The strongest form of service-to-service authentication.

```
Standard TLS:
  Client verifies server certificate → "I trust this server"

Mutual TLS:
  Client verifies server certificate → "I trust this server"
  Server verifies client certificate → "I trust this client"
```

```
Service A → Service B

1. Service A presents its certificate
2. Service B validates:
   - Certificate signed by trusted CA
   - Certificate not expired
   - Certificate identity matches expected service
3. Service B presents its certificate
4. Service A validates similarly
5. Encrypted communication begins
```

**When mTLS works:**
- Zero-trust networks (verify every connection)
- Service mesh environments (Istio, Linkerd manage certificates)
- High-security environments (financial, healthcare)

**Challenges:**
- Certificate management (issuance, rotation, revocation)
- Certificate authority infrastructure
- Debugging encrypted traffic is harder

### Service tokens

Services authenticate with tokens issued by a central authority.

```
Service A needs to call Service B:
1. Service A authenticates to auth server (client credentials flow)
2. Auth server issues access token for Service A
3. Service A calls Service B with token
4. Service B validates token (checks scope, audience)
```

Simpler than mTLS but less secure (tokens can be stolen).

## Common authentication mistakes

1. **Storing passwords in plain text** — always hash with bcrypt, scrypt, or argon2
2. **Rolling your own auth** — use proven libraries and protocols (OAuth 2.0, OpenID Connect)
3. **Long-lived access tokens** — 24-hour JWTs are a security risk. Use 15-60 minute access tokens with refresh tokens
4. **No token revocation strategy** — JWTs can't be revoked individually without a blocklist. Plan for this
5. **Hardcoded secrets** — API keys and client secrets in source code. Use environment variables or secret managers
6. **Not validating JWT audience** — token meant for Service A accepted by Service B
7. **Transmitting tokens over HTTP** — always use HTTPS. Tokens in plain HTTP are visible to anyone on the network

Authentication verifies identity. Authorization checks permissions. But APIs also need protection against abuse, attacks, and misuse at the network level. See [7_API_Security_and_Rate_Limiting.md](file:///d:/Playground/Backend%20Notes/6_API_Design/7_API_Security_and_Rate_Limiting.md).
