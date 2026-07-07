---
title: "API Authentication and Authorization"
part: 6
part_title: "API Design"
chapter: 7
summary: "Every production API must answer two questions: **who is calling?** (authentication) and **what are they allowed to..."
---
# API Authentication and Authorization

Every production API must answer two questions: **who is calling?** (authentication) and **what are they allowed to do?** (authorization). These are different concerns with different mechanisms. Conflating them is one of the most common API security mistakes.

## Authentication vs authorization

-   **Authentication (AuthN)** verifies identity by asking *"Who are you?"*. It checks credentials (like passwords, tokens or certificates) to confirm the client is who they claim to be, outputting a verified identity.
-   **Authorization (AuthZ)** verifies permissions by asking *"What are you allowed to do?"*. It checks the verified identity against permission policies to allow or deny specific actions (like reading or deleting a resource).

Authentication must always happen first; authorization depends on a verified identity.

## Common Authentication Methods

Before implementing session or token-based architectures, it is important to understand the traditional authentication standards:

-   **Basic Authentication:** Transmits credentials as a Base64-encoded string (e.g. `username:password`) in the `Authorization` header. It is stateless and simple, but highly insecure because the string can be easily decoded; thus, it must always be used over encrypted HTTPS channels.
-   **Digest Authentication:** A challenge-response protocol where the server sends a unique nonce and the client replies with an MD5 hash of the username, password, nonce and request URI. This avoids sending passwords in plain text, making it more secure than Basic Auth, but it is considered legacy and outdated in modern web/API environments.

## Stateful vs Stateless Authentication

When designing an API authentication system, developers must choose between maintaining session state on the server or delegating authentication state entirely to the client.

### Stateful Authentication (Session-Based)
Session-based authentication stores the user's login state centrally on the server (e.g. in a database or Redis cache) and transmits a unique session ID cookie to the client. Every subsequent request requires the server to query its storage to validate the session and retrieve the user's identity.

-   **High-Security Use Cases (e.g. Online Banking):** Stateful sessions allow immediate revocation. If a bank portal detects suspicious activity or a user logs out, the server can instantly delete the session from its cache to block access. In contrast, stateless tokens are stored on the client and validated locally, meaning they cannot be revoked on demand until they naturally expire.

Why Session-Based Auth Fails to Scale:

-   **Multi-Server Complexity:** In distributed systems or microservices, subsequent requests from a single client may route to different servers. This requires a centralized cache (like Redis) so that if a user's subsequent request hits a different server, it can still access their session.
-   **Memory Overhead:** The server must allocate memory for every single active session, which can become prohibitively expensive as your user base grows.

### Stateless Authentication (Token-Based)
Stateless authentication delegates state tracking entirely to the client. Instead of storing session records on the server, the server issues a digitally signed, cryptographically verifiable token (such as a JWT) to the client upon successful login.

How Stateless Auth Works:

1.  **Issue:** The user authenticates with their credentials. The server creates a token containing user information (payload), signs it using a secret key or private key and returns it to the client.
2.  **Request:** The client stores the token (e.g. in secure storage or a Secure cookie) and transmits it in the `Authorization: Bearer <token>` header on every request.
3.  **Verify:** Because the token is self-contained and carries a cryptographic signature, any server in the network can verify its authenticity and read the payload claims using the key without performing a database trip or session lookup.


## Architectural Comparison: Stateful Sessions vs Stateless Tokens

-   **Statelessness:** Since the token contains all necessary user data, the server doesn't need to store session records. Any server in your network can verify the token using the secret key without making a database trip.
-   **Horizontal Scalability:** Because no server-side session state exists, you can spin up as many backend servers as needed without coordinating session sharing.
-   **Microservices-Friendly:** Microservices can independently verify the signature of a JWT without constantly querying a central authentication service.
-   **Vulnerability to Hijacking:** Stateful sessions transmit a long-lived session cookie that is vulnerable to hijacking attacks (such as session fixation, XSS or cookie sniffing). To defend stateful systems, developers must implement client fingerprinting validation (e.g. hashing the client's User-Agent or IP address during login and validating the incoming request hash on every call). By contrast, stateless tokens carry short-lived access periods and rotate refresh tokens to automatically bound hijacking exposure windows.

*Note:* While JWTs are excellent for scaling, they have one major drawback—they cannot be easily invalidated before they expire. Because of this, developers often use Access Token and Refresh Token Strategies or maintain a blacklist to revoke compromised tokens.

Ultimately, no pattern is always secure by default. Security is an ongoing engineering process where developers must proactively plan, analyze threat profiles and design active defenses to keep resources safe.

## JSON Web Token in depth

JSON Web Token (JWT) is a compact and secure method for transmitting information between parties as a JSON object. It is commonly used for authentication and authorization in web applications, allowing users to access protected resources without repeatedly providing credentials.

Key features include:

-   **Stateless Authentication:** Stores user information in a token, reducing the need for server-side session storage.
-   **Secure Data Exchange:** Uses digital signatures to verify that the token has not been altered.
-   **Compact Format:** Consists of three parts—Header, Payload and Signature—encoded into a single string.
-   **Widely Supported:** Works across different programming languages and platforms.

### JWT Structure
A JWT mainly consists of 3 components, separated by dots (`Header.Payload.Signature`):

#### 1. Header
The header contains metadata about the token, including the signing algorithm and token type.

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

where,

-   `alg`: The algorithm used for signing (e.g. HS256 or RS256).
-   `typ`: Token type, always "JWT".

Example base64url-encoded header:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
```

#### 2. Payload
The payload contains the information about the user, also known as claims and some additional information including the timestamp at which it was issued and the expiry time of the token.

```json
{
  "userId": 123,
  "role": "admin",
  "exp": 1672531199
}
```

Common claim types:

-   `iss` (Issuer): Identifies who issued the token.
-   `sub` (Subject): Represents the user or entity the token is about.
-   `aud` (Audience): Specifies the intended recipient.
-   `exp` (Expiration): Defines when the token expires.
-   `iat` (Issued At): Timestamp when the token was created.
-   `nbf` (Not Before): Specifies when the token becomes valid.

Example base64url-encoded payload:
```
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNzA4MzQ1MTIzLCJleHAiOjE3MDgzNTUxMjN9
```

#### 3. Signature
The signature ensures token integrity and is generated using the header, payload and a secret key:

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

Example base64url-encoded signature:
```
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

#### Final JWT Token
After all these steps, the final JWT token is generated by joining the Header, Payload and Signature via a dot:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNzA4MzQ1MTIzLCJleHAiOjE3MDgzNTUxMjN9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Security Considerations
When working with JWTs, keep these best practices in mind to ensure safe and reliable authentication:

-   **Use HTTPS:** Prevent man-in-the-middle attacks by transmitting JWTs over HTTPS, which sends the token in encrypted form instead of plain text.
-   **Set Expiration Time:** Prevent long-lived tokens that can be exploited. Set a fixed time after which the token will automatically be invalidated.
-   **Use Secure Storage:** Store JWTs securely. For example, use HttpOnly cookies instead of local storage.
-   **Verify Signature:** Always validate the token's signature before trusting its content.

### Common Issues During Development
-   **JWT Rejected:** The server could not verify the token. This can happen if the token has expired, the signature is invalid or the claims do not match the expected details.
-   **Token Does Not Support Required Scope:** The token does not include the permissions needed for the action. For example, it may allow only reading data, but the app requires write access.
-   **JWT Decode Failed:** The token is not in the correct format or not properly encoded, so the client cannot read it.

## Refresh tokens

Refresh tokens solve the conflict between security (short-lived tokens) and usability (don't make users re-authenticate constantly).

### How refresh tokens work

```
Login:
  -> Access token (JWT, 15 min expiry)
  -> Refresh token (opaque, 30 day expiry, stored server-side)

Normal API calls:
  Authorization: Bearer <access_token>
  -> Server validates JWT (no database lookup)

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
  Used at time 1 -> new access token (refresh token unchanged)
  Used at time 2 -> new access token (same refresh token)
  If stolen, attacker can use it indefinitely until expiry

With rotation:
  Refresh token: rt_abc123
  Used at time 1 -> new access token + new refresh token rt_def456
  Old rt_abc123 is invalidated

  If attacker stole rt_abc123 and tries to use it:
  -> Server detects reuse of invalidated token
  -> Revokes entire token family (all refresh tokens for this user)
  -> User must re-authenticate
```

**Refresh token rotation detects theft.** When a revoked refresh token is used, it means either the legitimate user or an attacker is using a stale token. Revoking the entire family forces re-authentication, which is the safe choice.

### Refresh token storage

Refresh tokens are long-lived and highly sensitive, requiring strict server and client security standards:

-   **Server-Side Storage:** Store refresh tokens in a database or Redis cache using their cryptographic hash (e.g. SHA-256) as the lookup key to protect them from direct database leakage.
-   **Browser Storage:** Store tokens in the browser using `HttpOnly` and `Secure` cookies to prevent client-side Javascript from accessing them via cross-site scripting (XSS) attacks.
-   **Mobile App Storage:** Use platform-provided secure containers (such as iOS Keychain or Android Keystore) rather than unencrypted database or preference files.
-   **Server-to-Server Storage:** Keep keys secured in environment variables or cloud secrets managers (like HashiCorp Vault or AWS Secrets Manager).
-   **Forbidden Storage Areas:** Never store tokens in browser localStorage, sessionStorage, plain text files or URL query parameters due to XSS and log-sniffing exposures.
-   **BFF Proxy Defense:** For browser applications, use a Backend-for-Frontend (BFF) proxy layer to manage tokens on the server side entirely, sending only session cookies to the client.

*Note on Protocols:* Modern token-based authentication relies on OAuth 2.0. The older OAuth 1.0 protocol is deprecated and unusable for modern APIs because it requires complex cryptographic signature calculations on every request and lacks built-in support for bearer token lifecycles.


## API Keys

API keys are the simplest authentication mechanism, represented by a long, cryptographically random string that identifies the calling application.

```
Request:
  GET /api/weather?city=london
  X-API-Key: sk_live_abc123def456ghi789
```

### Why API Keys are Used
API keys establish programmatic identity between two systems. For example, to integrate Stripe payments or SendGrid email services into a custom application, a developer generates an API key in that service's portal. Copied into their own application's backend configuration, this key acts as a delegated credential, allowing their application to query data from the third-party API on the user's behalf without sharing passwords. This allows automated background tasks to query data continuously without manual browser login prompts.

### Lifecycle and Verification Flow
1.  **Generation & Transit:** The API provider generates a random, high-entropy key (e.g. `sk_live_...`), which the client transmits in HTTP headers (like `X-API-Key`).
2.  **AuthN & AuthZ:** The API server hashes the incoming key, looks it up in a database cache to identify the developer account and validates that the key has appropriate access scopes before allowing the request.

### Usability and Limitations
-   **Where They Work:** Programmatic server-to-server calls and public tracking endpoints (to enforce rate limits, billing tiers or call quotas).
-   **Where They Fail:** User-facing identity tracking (keys identify systems, not individuals), client-side applications (SPA/mobile binaries where keys can be extracted) and fine-grained access authorization.

### Security Best Practices
-   **Server-Side Isolation:** Keep keys in environment variables; never compile them into browser or client-side application code.
-   **Secure Storage & Transit:** Transmit keys strictly over HTTPS and store them hashed (using SHA-256) server-side to prevent database compromise leaks.
-   **Scopes and Rotation:** Restrict keys to read-only scopes or specific white-listed IP addresses and support dual-key windows for rotation without downtime.

## OAuth 2.0

OAuth 2.0 is the industry-standard framework for **delegated authorization**. It allows a third-party application to obtain limited access to a service on behalf of a resource owner by coordinating user consent, or by allowing the application to act on its own behalf.

Key concepts of this standard include:

-   **Token-Based Delegation:** Instead of passing credentials (such as passwords) to the third-party app, the client application is issued a limited-use access token.
-   **Separation of Authorization:** The system decouples credential validation (handled by the authorization server) from data hosting (handled by the resource server), allowing independent security scaling.

### The problem OAuth solves

**Without OAuth:**

-   A user gives their Google password directly to a third-party application.
-   The application gains full, unrestricted access to the user's entire account (including email, drive, contacts and payments).
-   The user cannot revoke access to a single app without changing their master password.
-   If any third-party application is compromised, the shared password is leaked, compromising all other services using it.

**With OAuth:**

-   The user authorizes specific, limited permissions (such as read-only access to email).
-   The application receives a scoped token instead of the user's password.
-   The user can revoke the token at any time without changing their password.
-   Tokens have a limited lifecycle and scope, bounding exposure if a single application is breached.

### OAuth 2.0 Roles

The framework defines core roles that interact to orchestrate secure token delegation:

-   **Resource Owner:** The user who owns the account data and has the authority to grant access to it.
-   **Client:** The third-party application requesting access to the resource owner's account (e.g. a calendar app).
-   **Authorization Server:** The system that authenticates the resource owner, obtains their consent and issues access tokens (e.g. Google or GitHub auth servers).
-   **Resource Server:** The API hosting the protected user data, which validates incoming access tokens and serves the requested resources.
-   **User Agent:** The intermediary client interface (such as a web browser) used by the resource owner to interact with the client application and handle authorization server redirects.

### Authorization Code Flow (most secure, server-side apps)

This is the recommended flow for web applications with a backend server.

```
Step 1: Client redirects user to authorization server
  -> https://auth.example.com/authorize?
      response_type=code
      &client_id=my-app
      &redirect_uri=https://myapp.com/callback
      &scope=read:profile read:email
      &state=random-csrf-token

Step 2: User authenticates and consents
  -> User sees: "My App wants to access your profile and email"
  -> User clicks "Allow"

Step 3: Authorization server redirects back with code
  -> https://myapp.com/callback?code=AUTH_CODE_123&state=random-csrf-token

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
  -> /authorize?...&code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw&code_challenge_method=S256

Step 3: User authenticates, server returns authorization code

Step 4: Client sends code_verifier with token request
  POST /token
  Body: { code: "AUTH_CODE", code_verifier: "original_random_string" }

Step 5: Server verifies SHA256(code_verifier) == code_challenge
  -> If match, issues tokens
  -> If no match, rejects (attacker intercepted code but doesn't have verifier)
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

## Single Sign-On (SSO) and OpenID Connect (OIDC)

Developers frequently confuse Single Sign-On (SSO), OAuth 2.0 and OpenID Connect (OIDC) because modern systems often combine them to build identity solutions.

| Feature | Single Sign-On (SSO) | OAuth 2.0 | OpenID Connect (OIDC) |
| :--- | :--- | :--- | :--- |
| **Purpose** | Single login credential set across multiple distinct applications | Delegation framework for third-party API resource access | Identity and authentication protocol extension layer |
| **Primary Focus** | User experience and centralized authentication | API authorization and secure resource scopes | Identity verification and profile metadata sharing |
| **User Flow** | Signs in once to access email, HR tools and internal chat | Grants permission to an application without password sharing | Receives an identity token during authentication handshake |
| **Example** | Corporate workforce sign-in via Microsoft Entra ID | Third-party photo app accessing files in Google Drive | "Sign in with Google" button verifying user email |

### What is Single Sign-On (SSO)?
SSO is a centralized user authentication experience enabling a person to log in once and gain access to multiple applications without re-authenticating. SSO is commonly implemented using protocols such as:

-   **SAML 2.0 (Security Assertion Markup Language):** XML-based standard used to pass identity and authorization data between an Identity Provider (IdP) and a Service Provider (SP).
-   **OpenID Connect (OIDC):** A JSON/REST-friendly authentication layer built directly on top of OAuth 2.0.
-   **Kerberos:** A ticket-based network authentication protocol used primarily in traditional Windows enterprise environments.

### What is OpenID Connect (OIDC)?
OpenID Connect (OIDC) is an identity and authentication protocol built directly as an extension layer on top of OAuth 2.0. While OAuth 2.0 was designed solely for delegated authorization, OIDC standardizes user authentication and profile metadata delivery, making it the industry standard for single sign-on (SSO), mobile logins and social auth integrations.

```
OIDC Layered Model
+-------------------------------------------------------+
|  OIDC Authentication Layer (ID Token / Claims)        |
+-------------------------------------------------------+
|  OAuth 2.0 Authorization Base (Access/Refresh Tokens) |
+-------------------------------------------------------+
```

Unlike plain OAuth 2.0, which only issues an Access Token for API access, OIDC introduces an **ID Token** (a JWT signed by the provider) to verify the user's identity.

Key benefits extending this standard include:

-   **Federated Identity Interoperability:** Because OIDC standardizes discovery endpoints and token signatures, any compliant application can integrate with any compliant Identity Provider (IdP) (like Google, Microsoft, Okta or Auth0) using the same code, avoiding vendor lock-in.

A standard OIDC handshake flow proceeds as follows:

1.  **Request:** The user clicks "Sign in with Google/Okta". The client redirects the user to the Identity Provider (IdP).
2.  **Authenticate:** The IdP authenticates the user and obtains consent.
3.  **Callback:** The IdP redirects back to the client, delivering an authorization code.
4.  **Exchange:** The client exchanges the code at the IdP token endpoint to receive an **ID Token** alongside standard Access and Refresh Tokens.

### Core Components of OIDC
-   **ID Token:** A signed JSON Web Token (JWT) containing identity claims about the authenticated user (e.g. issuer, subject ID, name, email and locale).
-   **UserInfo Endpoint:** A protected API endpoint where clients can present the Access Token to retrieve additional profile claims.
-   **Standard Claims:** Defines standardized profile claims—such as `sub` (subject ID), `name`, `email`, `picture` and `locale`—to ensure consistent user representations across different identity providers.



## Scopes and permissions

Scopes define what a token is allowed to do.

```
Scope examples:
  read:users        -> can read user data
  write:users       -> can create/update users
  delete:users      -> can delete users
  admin:all         -> full access

Token with limited scope:
  { "scope": "read:users read:orders" }

Request: DELETE /users/123
Check: "delete:users" in token.scope? -> No -> 403 Forbidden
```

**Scope design principles:**

- Use resource:action format (`read:users`, `write:orders`)
- Start with least privilege (minimal scopes by default)
- Allow scope combination (`read:users write:users`)
- Document all available scopes

## Access Control and Identity Management (IAM)

An authorization system determines what resources an authenticated user or application can access and what actions they are permitted to perform. It enforces security boundaries—such as allowing managers to approve budgets while restricting regular employees—ensuring the principle of least privilege.

In cloud environments, Identity and Access Management (IAM) authorization systems determine what authenticated users can do. They enforce security policies by granting or denying permissions to specific data, applications and tools based on access control models like Role-Based Access Control (RBAC) or Attribute-Based Access Control (ABAC).

### Common IAM Frameworks and Standards
-   **OAuth 2.0:** The industry-standard protocol that allows apps to securely access resources on behalf of a user without sharing credentials.
-   **SAML 2.0:** Commonly used to pass identity and authorization data between an identity provider and a service provider.
-   **JWT (JSON Web Tokens):** An open standard used to securely transmit compact and self-contained authorization claims between parties.

### Access Control Lists (ACL)
Permissions are assigned directly to individual users on a per-resource basis. This is a highly granular, object-level model:

```
Resource: document_123.docx
Access List:
  user_alice   -> read, write
  user_bob     -> read only
  user_charlie -> deny all
```

-   **When ACL works:** Perfect for user-shared document collaboration systems (like Google Drive or Dropbox) where access is decided by resource owners for specific files.
-   **Trade-off:** Hard to manage at scale. If an organization has millions of resources and users, querying and auditing ACLs on every request can cause database bottlenecks.

### Role-Based Access Control (RBAC)
Permissions are assigned to logical roles and roles are assigned to users:

```
Roles:
  viewer  -> can read
  editor  -> can read + write
  admin   -> can read + write + delete + manage users

User Alice -> role: editor
User Bob   -> role: viewer

Request from Alice: PUT /articles/123
Check: editor role allows write -> 200 OK

Request from Bob: PUT /articles/123
Check: viewer role allows read only -> 403 Forbidden
```

-   **When RBAC works:** Small numbers of well-defined roles, organizations where job titles map to strict permissions and scenarios where permission rules are not context-dependent.
-   **When RBAC fails:** Fine-grained requirements (e.g. "Alice can edit only articles she authored") or dynamic variables (e.g. "users can access data only in their region").

### Attribute-Based Access Control (ABAC)
Permissions are evaluated dynamically using a policy engine that parses attributes of the user, the resource and the environment:

```
Policy: "Users can edit articles they authored during business hours from the internal network"

Attributes:
  User: { id: 123, role: editor, department: engineering }
  Resource: { type: article, author_id: 123, status: published }
  Environment: { time: business_hours, ip: internal_network }

Evaluation:
  user.id == resource.author_id (True)
  environment.time == business_hours (True)
  environment.ip == internal_network (True)
  -> Allow
```

-   **When ABAC works:** Fine-grained, context-dependent permissions, multi-tenant architectures and compliance-heavy environments (data residency or time-based access control).
-   **Trade-off:** ABAC is extremely powerful but introduces higher processing overhead and configuration complexity than RBAC.

### Popular Platforms
To implement IAM solutions in your ecosystem, explore major enterprise offerings and tools:

-   **Cloud-Native IAM:** Enterprise cloud providers offer built-in IAM solutions (such as AWS IAM or Microsoft Entra ID) to enforce security boundaries across infrastructure resources and organizational databases.
-   **Workforce and Customer Identity:** Identity-as-a-Service (IDaaS) platforms (such as Okta or Auth0) manage user registration, Single Sign-On integrations and token exchange handshakes.
-   **Decoupled Policy Engines:** Modern architectures decouple authorization logic from application code using platforms like **Cerbos**, which manages access rules through declarative, version-controlled policies.

## Service-to-service authentication

### mTLS (Mutual TLS)

Both client and server present certificates. The strongest form of service-to-service authentication.

```
Standard TLS:
  Client verifies server certificate -> "I trust this server"

Mutual TLS:
  Client verifies server certificate -> "I trust this server"
  Server verifies client certificate -> "I trust this client"
```

```
Service A -> Service B

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

Authentication verifies identity. Authorization checks permissions. But APIs also need protection against abuse, attacks and misuse at the network level. See [API Security and Rate Limiting](file:///d:/Playground/Backend%20Notes/6_API_Design/7_API_Security_and_Rate_Limiting.md).
