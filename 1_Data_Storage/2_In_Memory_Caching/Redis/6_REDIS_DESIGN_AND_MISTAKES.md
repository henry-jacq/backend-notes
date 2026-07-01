---
title: "Redis: Design Choices and Common Mistakes"
part: 2
part_title: "Data Storage"
chapter: 11
summary: "Covers Redis breaking points, its single-threaded architecture, eviction policies, persistence..."
---
# Redis: Design Choices and Common Mistakes

Covers Redis breaking points, its single-threaded architecture, eviction policies, persistence options and common caching mistakes.

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
- Predictable behaviour (LRU is familiar)
- Doesn't require application changes (no out-of-memory errors)

**Trade-off of eviction:**

- Unknown data is evicted (could be important)
- Cache hit rate drops when memory is full
- Unpredictable behaviour (which key is evicted?)

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
   - Fix: shard Redis (multiple instances), optimise commands, use pipeline batching

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
