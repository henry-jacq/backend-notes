---
title: "gRPC"
part: 6
part_title: "API Design"
chapter: 4
summary: "gRPC is a high-performance RPC (Remote Procedure Call) framework developed by Google. It uses Protocol Buffers for..."
---
# gRPC

gRPC is a high-performance RPC (Remote Procedure Call) framework developed by Google. It uses Protocol Buffers for serialization and HTTP/2 for transport. Where REST is resource-oriented ("give me this thing"), gRPC is action-oriented ("do this operation").

gRPC exists because REST has overhead that matters at scale: text-based serialization, no built-in streaming, and loose contracts. When services call each other thousands of times per second, that overhead becomes measurable.

## Why gRPC exists

### The REST overhead problem

```
REST request:
  POST /api/orders HTTP/1.1
  Content-Type: application/json
  Authorization: Bearer eyJ...

  {"user_id": 123, "item_id": 456, "quantity": 1}

REST response:
  HTTP/1.1 201 Created
  Content-Type: application/json

  {"id": 789, "status": "created", "created_at": "2024-01-01T00:00:00Z"}
```

**Overhead:**
- JSON parsing: ~10-100x slower than binary serialization
- Text headers: repeated on every request
- No streaming: long-running operations need polling
- Loose contract: JSON has no schema enforcement at transport level

### gRPC equivalent

```protobuf
service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (OrderResponse);
}

message CreateOrderRequest {
  int64 user_id = 1;
  int64 item_id = 2;
  int32 quantity = 3;
}

message OrderResponse {
  int64 id = 1;
  string status = 2;
  google.protobuf.Timestamp created_at = 3;
}
```

The binary payload is typically 5-10x smaller than JSON. Serialization is 10-100x faster. The contract is enforced at compile time.

## Protocol Buffers (protobuf)

Protocol Buffers are gRPC's serialization format. You define message structures in `.proto` files, and a compiler generates code for your language.

### Message definition

```protobuf
syntax = "proto3";

package ecommerce;

message User {
  int64 id = 1;            // field number, not default value
  string name = 2;
  string email = 3;
  repeated string tags = 4; // list
  Address address = 5;      // nested message
  UserRole role = 6;        // enum
}

message Address {
  string street = 1;
  string city = 2;
  string country = 3;
  string zip = 4;
}

enum UserRole {
  VIEWER = 0;               // 0 must be default
  EDITOR = 1;
  ADMIN = 2;
}
```

### Field numbers matter

```protobuf
message User {
  int64 id = 1;     // field number 1
  string name = 2;  // field number 2
}
```

Field numbers are how protobuf identifies fields in binary format. **Never reuse or change field numbers** — this breaks backward compatibility.

```
Adding a field (safe):
  message User {
    int64 id = 1;
    string name = 2;
    string phone = 3;     // new field, new number
  }

Removing a field (unsafe without reservation):
  message User {
    int64 id = 1;
    // name removed, but field number 2 must never be reused
    reserved 2;
    reserved "name";
    string phone = 3;
  }
```

### Why protobuf is fast

```
JSON:
  {"id": 123, "name": "Alice"}
  = 30 bytes, requires parsing key names as strings

Protobuf binary:
  [field 1, varint, 123][field 2, string, 5, "Alice"]
  = ~12 bytes, no key names, direct field number lookup
```

- No field names in binary (just field numbers)
- Variable-length integer encoding (small numbers use fewer bytes)
- No parsing quotes, colons, or brackets
- Schema-driven: both sides know the structure at compile time

## Service definitions

gRPC services are defined in `.proto` files alongside messages.

```protobuf
service UserService {
  // Unary: one request, one response
  rpc GetUser(GetUserRequest) returns (User);

  // Server streaming: one request, stream of responses
  rpc ListUsers(ListUsersRequest) returns (stream User);

  // Client streaming: stream of requests, one response
  rpc UploadUserPhotos(stream Photo) returns (UploadResult);

  // Bidirectional streaming: stream in both directions
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}
```

## Four streaming types

### 1. Unary RPC

Standard request-response. Most similar to REST.

```
Client ---request---> Server
Client <--response--- Server
```

**Use when:** Simple operations (get user, create order, update status)

### 2. Server streaming

Server sends multiple responses to a single request.

```
Client ---request----------> Server
Client <--response 1-------- Server
Client <--response 2-------- Server
Client <--response 3-------- Server
Client <--end of stream----- Server
```

**Use when:**
- Returning large datasets in chunks
- Real-time updates (stock prices, sensor data)
- Progress updates for long-running operations

**Example:**
```protobuf
rpc WatchOrderStatus(OrderId) returns (stream OrderStatusUpdate);
```

Client requests order tracking, server pushes status changes as they happen.

### 3. Client streaming

Client sends multiple requests, server responds once after receiving all of them.

```
Client ---request 1-------> Server
Client ---request 2-------> Server
Client ---request 3-------> Server
Client ---end of stream---> Server
Client <--response--------- Server
```

**Use when:**
- Uploading large files in chunks
- Batch operations (client sends many items, server processes all at once)
- Aggregation (client sends data points, server returns summary)

**Example:**
```protobuf
rpc UploadLog(stream LogEntry) returns (UploadSummary);
```

### 4. Bidirectional streaming

Both sides send streams of messages simultaneously.

```
Client ---message 1-------> Server
Client <--message A--------- Server
Client ---message 2-------> Server
Client ---message 3-------> Server
Client <--message B--------- Server
Client <--message C--------- Server
```

Messages are independent — neither side waits for the other.

**Use when:**
- Chat applications
- Real-time collaboration
- Interactive workflows (client sends data, server sends feedback continuously)

**Example:**
```protobuf
rpc InteractiveSearch(stream SearchQuery) returns (stream SearchResult);
```

User types a search query character by character, server returns results as they refine.

## Code generation

The protobuf compiler (`protoc`) generates client and server code from `.proto` files.

```
user.proto
    |
    v
protoc compiler
    |
    +---> user_pb2.py (Python)
    +---> user.pb.go (Go)
    +---> User.java (Java)
    +---> user_pb.ts (TypeScript)
```

**What gets generated:**
- Message classes with serialization/deserialization
- Client stubs (call remote methods as if local)
- Server interfaces (implement methods, framework handles transport)

```
Generated client usage (conceptual):

client = UserServiceClient(channel)
user = client.GetUser(GetUserRequest(id=123))
print(user.name)  # "Alice"
```

The generated client handles:
- Serialization (object -> protobuf binary)
- HTTP/2 framing
- Connection management
- Deserialization (protobuf binary -> object)

The developer writes business logic. gRPC handles the plumbing.

## HTTP/2 foundation

gRPC requires HTTP/2. This is not optional.

```
Why HTTP/2 matters for gRPC:

Multiplexing:
  Stream 1: GetUser(123) -> response
  Stream 2: GetUser(456) -> response (concurrent, same connection)
  Stream 3: ListOrders() -> response 1, response 2, ... (streaming)

All on a single TCP connection.
```

**Benefits:**
- Multiple RPCs on one connection (no connection-per-request overhead)
- Streaming is built into the protocol
- Header compression reduces overhead for repeated calls
- Flow control prevents fast senders from overwhelming slow receivers

**Limitation:**
- Browser support is limited (browsers don't expose HTTP/2 framing directly)
- gRPC-Web exists as a workaround (proxy translates HTTP/1.1 -> HTTP/2)

## gRPC vs REST — when to use which

```
Criteria            | REST                    | gRPC
--------------------|-------------------------|---------------------------
Serialization       | JSON (text)             | Protobuf (binary)
Contract            | OpenAPI (optional)      | Proto files (required)
Streaming           | Not built-in            | Four streaming types
Browser support     | Native                  | Requires gRPC-Web proxy
Human readability   | High (JSON, text)       | Low (binary)
Performance         | Good                    | Excellent
Code generation     | Optional                | Built-in
Learning curve      | Low                     | Medium
Debugging           | Easy (curl, browser)    | Harder (need gRPC tools)
Ecosystem           | Massive                 | Growing
```

**Use gRPC when:**
- Service-to-service communication (microservices)
- Performance matters (high throughput, low latency)
- Streaming is needed (real-time data, long-running ops)
- Strong contracts are desired (compile-time safety)
- Polyglot environment (many languages need the same API)

**Use REST when:**
- Public APIs (browser clients, third-party integrations)
- Simple CRUD operations
- Human debugging is important (curl, Postman)
- Team is not familiar with protobuf
- Browser is the primary client

## gRPC error handling

gRPC uses status codes (similar to but different from HTTP).

```
OK                  -> Success
CANCELLED           -> Operation cancelled by client
INVALID_ARGUMENT    -> Client sent invalid data (like 400)
NOT_FOUND           -> Resource not found (like 404)
ALREADY_EXISTS      -> Conflict (like 409)
PERMISSION_DENIED   -> Not authorized (like 403)
UNAUTHENTICATED     -> Not authenticated (like 401)
RESOURCE_EXHAUSTED  -> Rate limit or quota exceeded (like 429)
UNAVAILABLE         -> Service temporarily unavailable (like 503)
INTERNAL            -> Internal server error (like 500)
DEADLINE_EXCEEDED   -> Operation timed out (like 504)
```

**Deadlines:** gRPC has built-in deadline propagation. A client sets a deadline, and every service in the call chain respects it.

```
Client sets deadline: 5 seconds

Client -> Service A (2 seconds used)
         Service A -> Service B (remaining deadline: 3 seconds)
                     Service B -> Service C (remaining deadline: 1 second)
                                 Service C exceeds deadline -> DEADLINE_EXCEEDED
```

This prevents cascading timeouts. Every service knows how much time is left.

## gRPC in practice

### Load balancing

```
REST (simple):
  Load balancer at L7 (HTTP) routes by URL path

gRPC (more complex):
  Load balancer must understand HTTP/2 frames
  Options:
    - L7 proxy (Envoy, nginx with gRPC support)
    - Client-side load balancing (client knows all server addresses)
    - Service mesh (Istio, Linkerd)
```

### Health checking

gRPC has a standard health checking protocol:

```protobuf
service Health {
  rpc Check(HealthCheckRequest) returns (HealthCheckResponse);
  rpc Watch(HealthCheckRequest) returns (stream HealthCheckResponse);
}
```

Load balancers use this to route traffic away from unhealthy instances.

### Interceptors (middleware)

```
Client interceptors:
  Logging -> Auth -> Retry -> [send request]

Server interceptors:
  [receive request] -> Auth -> Logging -> Rate Limit -> [handle request]
```

Interceptors add cross-cutting concerns without modifying business logic. Similar to middleware in REST frameworks.

## Common gRPC mistakes

1. **Not setting deadlines** — requests hang forever if downstream is slow
2. **Ignoring backpressure** — streaming without flow control overwhelms receivers
3. **Large messages** — protobuf messages have a default 4MB limit. Stream large data instead of sending one huge message
4. **Not versioning proto files** — breaking changes in proto files break all clients
5. **Using gRPC for browser clients** — need gRPC-Web proxy, adds complexity

gRPC solves the performance and contract problem for service-to-service communication. But regardless of which protocol you choose (REST, GraphQL, gRPC), you need to manage state correctly. See [4_API_State_Management.md](file:///d:/Playground/Backend%20Notes/6_API_Design/4_API_State_Management.md).
