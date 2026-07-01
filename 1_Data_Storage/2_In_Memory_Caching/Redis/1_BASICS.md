---
title: "Redis Basics"
part: 2
part_title: "Data Storage"
chapter: 6
summary: "Redis is an in-memory data structure store. It is often used as a cache, message broker, session store, and database..."
---
# Redis Basics

Redis is an in-memory data structure store. It is often used as a cache, message broker, session store, and database for workloads that require low latency and high throughput.

Key points:

- Redis stores data in memory for fast access. Data can also be persisted to disk using RDB snapshots, AOF logs, or both.
- Redis keys and values are binary-safe, which means they can contain any data, not only printable text.
- Redis is single-threaded for command execution, which simplifies concurrency and keeps command latency predictable.
- Redis supports expiration on keys. A key with a time-to-live (TTL) is removed automatically when the TTL expires.
- Redis can operate as a standalone server, with replication, or as a clustered setup for scaling.

Core features:

- data structures: strings, hashes, lists, sets, sorted sets
- key expiration and eviction policies
- persistence: RDB, AOF, or no persistence
- replication and high availability
- Pub/Sub messaging

Redis command format:

Redis commands are typically written as `COMMAND key [arguments]`.
Redis returns different types of replies, such as strings, integers, arrays, and errors.
