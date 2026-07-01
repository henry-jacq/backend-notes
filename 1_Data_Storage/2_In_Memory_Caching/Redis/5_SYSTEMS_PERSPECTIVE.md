---
title: "Redis: Why It Exists"
part: 2
part_title: "Data Storage"
chapter: 10
summary: "This document explains Redis not as a cache to learn, but as a solution to specific performance bottlenecks that..."
---
# Redis: Why It Exists

This document explains Redis not as a cache to learn, but as a solution to specific performance bottlenecks that databases cannot solve alone.

## The database performance problem that redis solves

Before Redis, caching existed (Memcached, in-memory stores). The problem was not that caching didn't work. The problem was that databases got slower as systems scaled.

A typical database:

- Stores data on disk (durable but slow)
- Answers queries by finding data on disk (I/O required)
- Uses indexes to speed up lookups (but index lookups still require disk I/O)
- Can answer thousands of queries per second at best

At scale (millions of requests per day), a single expensive query repeated millions of times becomes a bottleneck.

## Why databases become the bottleneck

### The read bottleneck

**Scenario:** a product catalog system

```
User requests:  GET /product/id/12345

Database execution:

1. Parse query
2. Check query plan
3. Find index entry for product 12345
4. Read index from disk (random I/O, ~10ms)
5. Follow pointer to data row
6. Read row from disk (another random I/O, ~10ms)
7. Return result

Total: ~20ms per request
```

One request takes 20ms. At 1,000 concurrent users, database is handling 1,000 * (1 / 0.020) = **50,000 requests per second**.

But here is the problem: **the same product is requested repeatedly**.

```
Request 1: GET /product/12345 (database hit)
Request 2: GET /product/12345 (database hit again)
Request 3: GET /product/12345 (database hit again)
...
Request 1000: GET /product/12345 (database hit again)
```

The database performs the same work 1000 times.

**Symptoms of this bottleneck:**

- Database query log shows same queries over and over
- Database CPU is high despite moderate request rate
- Response time varies (sometimes 20ms, sometimes 100ms if query queue builds)
- Disk I/O is constant

### Why the problem exists

Databases are optimised for durability and consistency, not repeated read performance. They must:

- Check query plan
- Verify authorisation
- Check for locks
- Read from disk

All of this is necessary, but wasteful when the same query repeats thousands of times per second.

## Caching: the performance solution

Caching moves frequently accessed data from disk to RAM.

```
Before caching:
User request -> Database (disk I/O, 20ms)

After caching:
User request -> Cache (RAM access, 0.1ms) -> Return immediately
                        |
                        | (cache miss, only on first request)
                        v
                    Database (disk I/O, 20ms) -> Cache stores result
```

**Why this works:**

- RAM is orders of magnitude faster than disk (100x)
- Same data served from RAM, not disk
- Database load drops dramatically

**When caching helps:**

- Same data requested repeatedly (cache hit rate > 70%)
- Response time is dominated by database query
- Working set fits in available memory
- Data doesn't change too frequently

**Symptoms that caching will help:**

- Same queries in slow query log
- Database query latency is high (> 10ms per request)
- Query volume is high (thousands/second) but unique queries are low
- CPU metrics: database CPU is high but application CPU is low (database is the bottleneck, not application logic)

## Redis vs Memcached: why Redis

Both Redis and Memcached are in-memory stores. They are similar at first glance but made different choices.

### Memcached design

**Design:** key-value store in RAM, distributed, simple

**What worked:**

- Very simple to use
- Very fast
- Low memory overhead

**Breaking points:**

- No persistence (crash = loss)
- Limited data structures (only key-value)
- No expiration management (keys kept forever or manually evicted)
- No pub/sub
- Clients must handle distribution (not the server)

**Example Memcached use case:**
```
Cache user session:
key: session:12345
value: { userId: 1, username: "alice", loginTime: 123456 }

Fetch: GET session:12345
Result: user session data
```

### Redis design

**Design:** in-memory data structure store, more features, richer capabilities

**What worked better:**

- Multiple data structures (strings, hashes, lists, sets, sorted sets)
- Built-in expiration (keys expire automatically)
- Persistence to disk (optional)
- Pub/Sub messaging
- Replication
- Server handles distribution (cluster mode)

**Why more features:**

Redis added features not because they are nice to have, but because caching at scale requires them.

**Strings for caching:**
```
User profile:
key: user:12345
value: { name: "Alice", email: "alice@example.com" }
Expiration: 1 hour
```

**Hashes for structured data:**
```
Shopping cart:
key: cart:12345
fields: product:1 -> quantity:5
        product:2 -> quantity:3
        product:3 -> quantity:1
```

**Lists for ordered events:**
```
User activity feed:
key: feed:12345
values: [event1, event2, event3, ...]
```

**Sets for deduplication:**
```
Trending topics:
key: trending
values: { topic1, topic2, topic3, ... }
```

**Sorted sets for rankings:**
```
Leaderboard:
key: leaderboard
values: { user1: 1000, user2: 950, user3: 900 }
```

Caching complex queries with Redis is easier when you can store hashes, lists, and sets directly, instead of serialising JSON to Memcached.

## When Redis becomes necessary

Redis was built at Antirez to cache complex queries and enable real-time features that a database alone could not support.

**Symptoms that Redis is needed:**

1. **Repeated expensive queries**
   - Database query takes 50ms
   - Query runs 10,000 times per second
   - Total database time: 500 seconds per second (impossible)
   - Solution: cache result for 10 seconds, 500 cache hits save 9,500 database queries

2. **Session storage**
   - User session data (login, preferences, permissions)
   - Read on every request (very high frequency)
   - Database query for every request is wasteful
   - Redis caches per user

3. **Real-time counters**
   - Page views, impressions, clicks
   - Database updates are slow (write lock, index updates)
   - Redis counter is atomic and fast
   - Batch update to database periodically

4. **Leaderboards and rankings**
   - Sorted set of users by score
   - Database sorting is expensive
   - Redis sorted sets are optimised for this
   - Queries are fast and updateable

5. **Rate limiting**
   - Limit requests per user (100/minute)
   - Must be checked on every request
   - Database check is too slow
   - Redis keeps counter, increments, expires after minute

To learn about Redis design choices (such as its single-threaded model, eviction policies, and persistence) and common caching mistakes, see [6_REDIS_DESIGN_AND_MISTAKES.md](file:///d:/Playground/Backend%20Notes/1_Data_Storage/2_In_Memory_Caching/Redis/6_REDIS_DESIGN_AND_MISTAKES.md).
