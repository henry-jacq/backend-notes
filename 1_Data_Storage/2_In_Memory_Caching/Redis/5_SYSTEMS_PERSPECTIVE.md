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

Databases are optimized for durability and consistency, not repeated read performance. They must:
- Check query plan
- Verify authorization
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

Caching complex queries with Redis is easier when you can store hashes, lists, and sets directly, instead of serializing JSON to Memcached.

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
   - Redis sorted sets are optimized for this
   - Queries are fast and updateable

5. **Rate limiting**
   - Limit requests per user (100/minute)
   - Must be checked on every request
   - Database check is too slow
   - Redis keeps counter, increments, expires after minute

## Breaking points: why Redis design choices exist

### Single-threaded architecture

**Problem:** Redis is single-threaded. Commands execute one at a time.

**Why this works despite single-threaded:**
- In-memory operations are fast (no I/O waits)
- Blocking on I/O (disk, network) is not necessary
- No lock contention (no concurrent reads/writes)
- Predictable latency (no garbage collection pauses)

**Breaking point of single-threaded:**
- Very high command rate (millions/second)
- Complex operations that require multiple commands
- Network I/O becomes bottleneck (single network interface)

**How scaling happens:**
- Multiple Redis instances (sharding by key)
- Each instance handles subset of keys
- Client determines which instance for each key

### Memory limits and eviction

**Problem:** memory is finite. After memory fills, what happens?

**Options:**

1. **Eviction policies** (Redis default)
   - Keep most useful data
   - Evict least recently used (LRU)
   - Evict randomly
   - Evict with TTL closest to expiry

2. **No eviction**
   - Reject new writes when memory full
   - Application must handle errors

3. **Spill to disk**
   - Not supported in standard Redis
   - Other systems support this

**Why Redis chose eviction:**
- Simple to implement
- Predictable behavior (LRU is familiar)
- Doesn't require application changes (no out-of-memory errors)

**Trade-off of eviction:**
- Unknown data is evicted (could be important)
- Cache hit rate drops when memory is full
- Unpredictable behavior (which key is evicted?)

**When eviction breaks:**
- Working set larger than memory
- Eviction policy doesn't match data importance
- Important data keeps getting evicted

### Persistence options

**Problem:** Redis is in-memory. Power loss or crash = data loss.

**Options:**

1. **No persistence** (fastest, data lost on crash)
2. **RDB snapshots** (periodic disk writes, some data loss if crash between snapshots)
3. **AOF log** (write-ahead log, all operations logged, slower but safer)
4. **Both** (RDB for speed, AOF for safety)

**Why different options:**
- Caching doesn't require persistence (data can be regenerated)
- Session storage needs persistence (losing user sessions is bad)
- Real-time counters can tolerate some loss (cache miss)

**Trade-off of persistence:**
- More persistence = slower (disk I/O required)
- No persistence = faster but riskier

### Expiration and cleanup

**Problem:** keys accumulate. Memory fills with stale data.

**Solution:** each key can have TTL (time-to-live)

```
SET cache:user:12345 "{...}" EX 3600
// Expires after 1 hour
```

**Benefits:**
- Stale data removed automatically
- Memory pressure relieved
- No manual cleanup needed

**Trade-off:**
- TTL must be set correctly (too short = cache misses, too long = memory filled)
- Expiration process (background task) uses CPU

### Pub/Sub messaging

**Problem:** multiple consumers need notifications

Redis added Pub/Sub:
```
Producer publishes: event "user:login" 
Subscriber 1 receives: "user:login"
Subscriber 2 receives: "user:login"
Subscriber 3 receives: "user:login"
```

**Why in a cache store:**
- Real-time notifications are common in web apps
- Message brokers add operational complexity
- Redis is already running (reuse infrastructure)
- Low latency important (in-memory)

**Trade-off of Redis Pub/Sub vs Kafka:**
- Redis: fast, in-memory, no persistence
- Kafka: persisted, replay-able, multiple independent consumers

Different design choices for different problems.

## Investigation: how engineers identify caching problems

**When caching doesn't help, what do you see?**

1. **Low cache hit rate (< 50%)**
   - Cache getting misses constantly
   - Database still under load
   - Caching not helping
   - Reason: unique queries every time, or working set too large
   - Fix: identify what queries are actually repeated before caching

2. **Memory pressure**
   - Redis memory at 90%
   - Eviction happening constantly
   - Hit rate degrading
   - Reason: working set larger than memory, or TTL too long
   - Fix: reduce TTL, remove unnecessary data, increase memory, shard

3. **Stale data bugs**
   - Cache returns old value
   - Application sees inconsistency
   - Users complain of wrong data
   - Reason: cache not invalidated when database changed
   - Fix: invalidate cache on write, or use shorter TTL

4. **Single-threaded bottleneck**
   - Redis CPU at 100%
   - Response times high
   - Commands queuing up
   - Reason: very high command rate, complex operations
   - Fix: shard Redis (multiple instances), optimize commands, use pipeline batching

5. **Persistence overhead**
   - Redis slow, tail latency high
   - AOF fsync causing delays
   - Reason: persistence overhead
   - Fix: disable AOF for pure cache, use RDB only, or separate persistence tier

## Common Redis mistakes

### 1. Caching without checking if it helps

**Mistake:** add Redis without measuring database query time

**Result:**
- Cache hit rate low
- Added operational complexity
- Little performance improvement

**Better:** measure query latency first, check if same queries repeat, then add caching.

### 2. TTL too long

**Mistake:** set cache TTL to 1 hour for frequently changing data

**Result:**
- Stale data served to users
- Users see inconsistent state
- Cache bugs

**Better:** set TTL short for changing data, long for stable data.

### 3. No cache invalidation on writes

**Mistake:** cache a user profile but don't invalidate when user updates it

**Result:**
- User updates profile
- Cache still has old data
- User sees their old profile

**Better:** invalidate cache key when database record changes.

### 4. Complex operations without pipelining

**Mistake:** send 1000 individual Redis commands for 1000 keys

```
GET key1
GET key2
GET key3
...
GET key1000
```

**Result:**
- 1000 network round trips
- Very slow
- Redis single-thread starved

**Better:** pipeline commands

```
PIPELINE [
  GET key1,
  GET key2,
  ...
  GET key1000
]
// Single network round trip
```

### 5. No monitoring

**Mistake:** no alerts on Redis memory or hit rate

**Result:**
- Memory fills silently
- Eviction happens
- Hit rate drops
- Days pass before anyone notices

**Better:** monitor memory usage, hit rate, eviction count, alerts.

## Trade-offs: Redis vs alternatives

### Redis vs memcached

| Aspect | Redis | Memcached |
|--------|-------|-----------|
| Data structures | Rich (strings, hashes, lists, sets, sorted sets) | Only key-value |
| Persistence | Optional (RDB, AOF) | None |
| Pub/Sub | Built-in | Not built-in |
| Replication | Built-in cluster | Not built-in |
| Complexity | Higher | Lower |
| Speed | Fast | Slightly faster |

**Choose Memcached when:**
- Simple key-value caching only
- Operational simplicity critical
- No persistence needed

**Choose Redis when:**
- Complex data structures needed
- Persistence important
- Pub/Sub messaging wanted

### Redis vs database caching

| Aspect | Redis | Database |
|--------|-------|----------|
| Speed | Very fast (0.1ms) | Slow (10-100ms) |
| Complexity | Additional component | Already exists |
| Consistency | Eventually consistent | Strong consistency |
| Memory usage | High | Low |

**Choose database caching (indexes) when:**
- Working set fits in database buffer pool
- Consistency critical

**Choose Redis when:**
- Performance critical
- Cache miss acceptable
- Working set larger than database buffer pool

## Questions to think about

- If only 5% of queries repeat, does caching help?
- Why is Redis single-threaded when modern systems have multiple cores?
- What happens to performance if cache hit rate drops from 90% to 50%?
- If you set cache TTL to 1 second but data changes every 100 milliseconds, what is the impact?
- Why does Redis require explicit key eviction instead of automatic?
- If you need to cache 10GB of data but only have 4GB of RAM available, what happens?
- How would you detect if cache is actually improving performance?
- Why would you use Redis Pub/Sub instead of a message queue?
- What happens if you cache user permissions but user's role changes?
- At what command rate does single-threaded Redis become a bottleneck?

## Summary

Redis exists because databases alone cannot meet performance requirements at scale when same data is requested repeatedly.

Redis's design (in-memory, rich data structures, expiration, persistence options) is not arbitrary. Each choice responds to specific production requirements that simple caching could not handle.

The key insight: caching is not magic. It helps when:
1. Same data requested repeatedly (high hit rate)
2. Working set fits in memory
3. Stale data is acceptable
4. Data doesn't change constantly

Without these conditions, caching adds complexity without benefit. The best engineers understand when caching helps and when it is waste.
