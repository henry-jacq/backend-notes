---
title: "Redis at Scale"
part: 2
part_title: "Data Storage"
chapter: 7
summary: "Explains in-memory caching theory, comparing Redis against Memcached, detailing persistence and eviction policies under memory pressure and exploring common caching mistakes."
---
# Redis at Scale

Adding an in-memory cache is a common response to database read bottlenecks. However, running a cache tier in production introduces new architectural concerns: eventual consistency, memory limits, eviction behaviours and persistence trade-offs.

## In-Memory Caching Theory

### The Read Bottleneck
Traditional relational databases are optimised for durability and consistent query plans. They read indexes and records from disk, which introduces random I/O latency (~10–20ms per query). 

When the same read query is executed thousands of times per second (e.g. fetching a popular product page or configuration setting), the database spends redundant CPU and I/O cycles recalculating the exact same result. serving these repeated reads from RAM (latency <1ms) drops database load dramatically.

### Cache Hit Rate
A cache only improves system performance if it actually serves requests. This is measured by the **Cache Hit Rate**:

```
Cache Hit Rate = (Cache Hits / (Cache Hits + Cache Misses)) * 100
```

-   **High Hit Rate (>70%):** The cache effectively absorbs reads, shielding the database.
-   **Low Hit Rate (<50%):** The cache misses frequently. The application must perform a double lookup (querying the cache, missing, then querying the database), which adds latency and operational complexity without reducing database load.



## Redis vs Memcached

Both are high-performance, in-memory key-value stores, but they represent different design philosophies:

| Aspect | Redis | Memcached |
| :--- | :--- | :--- |
| **Data Types** | Rich structures (Hashes, Lists, Sets, Zsets) | Simple strings/objects only |
| **Persistence** | Optional disk writes (RDB/AOF) | Purely transient (data lost on restart) |
| **Replication** | Native primary-replica clusters | Third-party client-side hashing |
| **Complexity** | Higher operational footprint | Low, lightweight footprint |

Choose **Memcached** for simple, static key-value caching where simplicity is paramount. Choose **Redis** when you need complex data structures (like lists for queues or sorted sets for real-time leaderboards) or basic persistence.



## Memory Limits and System Operations

Because RAM is finite and expensive, caching tiers must be designed to handle resource constraints.

### 1. Key Eviction Policies
When Redis memory fills up, it evicts keys based on configured rules:

-   **No Eviction (default):** Rejects new writes with an error when memory limit is reached. Safe for primary database workloads but breaks cache pipelines.
-   **Allkeys-LRU / Volatile-LRU:** Evicts the *Least Recently Used* keys across all keys or only keys with an active TTL.
-   **Allkeys-LFU / Volatile-LFU:** Evicts the *Least Frequently Used* keys.
-   **Volatile-TTL:** Evicts keys with an active expiration that are closest to expiring.

### 2. Persistence Trade-offs
To recover from crashes, Redis offers optional disk persistence:

-   **RDB (Redis Database) snapshots:** Point-in-time snapshots of memory dumped to disk at intervals. It is highly performant but risks losing several minutes of writes if a crash occurs between snapshots.
-   **AOF (Append-Only File) logs:** Appends every write command to a disk log. Safe but writes introduce I/O latency, which can starve the single event loop.



## Common Caching Mistakes and Anti-patterns

### 1. serving Stale Data (Missing Invalidation)
Serving stale database records because cache values are not invalidated on updates.

-   **Fix:** Explicitly delete or update the cache key whenever the corresponding database row is modified, or use short key expirations (TTL) if absolute real-time accuracy is not required.

### 2. Cache Stampede (Thundering Herd)
When a high-traffic cache key expires, thousands of concurrent threads detect the cache miss and query the database simultaneously, overwhelming it.

-   **Fix:** Pre-compute key expirations in the background, or use distributed locking to ensure only one thread queries the database to repopulate the cache.

### 3. Starving the Single Event Loop
Running slow, complex commands (like `KEYS *` or huge `HGETALL` operations) blocks the single event loop, causing all other concurrent client commands to queue up and time out.

-   **Fix:** Use non-blocking commands like `SCAN` instead of `KEYS` and keep collections small.

### 4. Unbatched Network Roundtrips
Requesting dozens of cache keys sequentially in a loop, creating significant network round-trip overhead.

-   **Fix:** Use pipelining or multi-key commands (`MGET`, `HMGET`) to fetch multiple values in a single network trip.
