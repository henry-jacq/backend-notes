---
title: "Redis Fundamentals"
part: 2
part_title: "Data Storage"
chapter: 5
summary: "Covers the core architecture of Remote Dictionary Server (Redis), including its single-threaded in-memory model, supported data types, basic commands and lightweight Pub/Sub messaging."
---
# Redis Fundamentals

Redis (Remote Dictionary Server) is an open-source, in-memory data structure store used as a database, cache and message broker. Because it stores data directly in RAM, it provides sub-millisecond latencies and high throughput for read- and write-heavy workloads.

## Core Architectural Concepts

-   **In-Memory Storage:** Unlike traditional databases that write to disk first, Redis resides primarily in memory. Data can be persisted asynchronously to disk via RDB (Redis Database) snapshots or AOF (Append-Only File) logs for durability.
-   **Single-Threaded Command Execution:** Redis executes commands using a single event loop. This architecture simplifies concurrency by eliminating race conditions and lock contention, ensuring command execution latency remains highly predictable.
-   **Key-Value Model:** Redis behaves like a remote dictionary. Keys are binary-safe strings (up to 512 MB). Values are structured data types that define which specialized operations can be run on them.
-   **Key Expirations:** Redis supports a Time-to-Live (TTL) expiration on any key. When the TTL expires, the key is automatically evicted.



## Supported Data Types and Core Commands

Redis supports structured data types natively rather than storing everything as raw strings. The most common data types and their standard commands include:

### 1. Strings
-   **Concept:** A binary-safe sequence of bytes (up to 512 MB). Useful for caching HTML, JSON payloads or session tokens.
-   **Key Commands:**
    -   `SET key value` / `GET key` — Store and retrieve a string value.
    -   `DEL key` — Remove a key.
    -   `SETEX key seconds value` — Set a value with a TTL expiration in one atomic step.
    -   `SETNX key value` — Set a value only if the key does not already exist (useful for lock implementations).
    -   `INCR key` / `DECR key` — Atomically increment or decrement integer string values.

### 2. Hashes
-   **Concept:** A collection of field-value pairs under a single key. Useful for storing objects or records.
-   **Key Commands:**
    -   `HSET key field value` / `HGET key field` — Set and get a single field value.
    -   `HGETALL key` — Retrieve all fields and values in the hash.
    -   `HDEL key field` — Delete a field.

### 3. Lists
-   **Concept:** An ordered sequence of strings, sorted by insertion order. Useful for task queues or recent activity feeds.
-   **Key Commands:**
    -   `LPUSH key value` / `RPUSH key value` — Push elements onto the head or tail of the list.
    -   `LPOP key` / `RPOP key` — Pop elements off the head or tail.
    -   `LRANGE key start stop` — Fetch a slice of the list by index.

### 4. Sets
-   **Concept:** An unordered collection of unique strings. Useful for membership testing or tags.
-   **Key Commands:**
    -   `SADD key member` / `SREM key member` — Add or remove a member.
    -   `SISMEMBER key member` — Check membership.
    -   `SMEMBERS key` — Return all members of the set.

### 5. Sorted Sets (Zsets)
-   **Concept:** A collection of unique members, where each member is associated with a floating-point score. Members are kept sorted by score. Useful for real-time leaderboards.
-   **Key Commands:**
    -   `ZADD key score member` — Add a member with a score.
    -   `ZRANGE key start stop [WITHSCORES]` — Retrieve members by index range.

### 6. Specialised Data Types
-   **Bitmaps:** Perform bitwise operations on strings.
-   **HyperLogLogs:** Estimate cardinality (unique item count) in constant memory space.
-   **Streams:** A append-only log structure for event streaming.



## Key Management and Pub/Sub Messaging

### Key Administration Commands
-   `EXISTS key` — Checks if a key exists in the database.
-   `EXPIRE key seconds` — Sets a TTL expiration on an existing key.
-   `TTL key` — Returns the remaining TTL in seconds (-1 if no expiration is set).
-   `FLUSHDB` / `FLUSHALL` — Deletes all keys in the current database or all databases.
-   `KEYS pattern` — Lists keys matching a pattern. (Caution: blocks the main thread on large databases; use `SCAN` instead in production).

### Redis Pub/Sub (Publish/Subscribe)
Redis includes lightweight publish/subscribe functionality for real-time, fire-and-forget message routing:

-   **Channels:** Named message pathways. Messages are forwarded directly to connected clients.
-   **No Durability:** Redis Pub/Sub does not store messages. If a subscriber is offline, published messages are discarded immediately.
-   **Key Commands:**
    -   `SUBSCRIBE channel` — Subscribe to a channel to listen for messages.
    -   `PUBLISH channel message` — Send a message to a channel.
