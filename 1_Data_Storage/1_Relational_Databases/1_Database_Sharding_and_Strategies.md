---
title: "Database Sharding and Strategies"
part: 2
part_title: "Data Storage"
chapter: 2
summary: "Covers database sharding—the distribution of data across multiple database servers to scale both reads..."
---
# Database Sharding and Strategies

Covers database sharding—the distribution of data across multiple database servers to scale both reads and writes.

## Sharding: solves both read and write scaling

Sharding is splitting data across multiple databases.

```
Data split by user ID:

- Shard 1: users 1-1,000,000
- Shard 2: users 1,000,001-2,000,000
- Shard 3: users 2,000,001-3,000,000

Request for user 500,000 -> goes to Shard 1
Request for user 1,500,000 -> goes to Shard 2
Request for user 2,500,000 -> goes to Shard 3

Load distributed across shards.
```

**Benefits:**

- Write load distributed
- Read load distributed
- Each shard smaller (fits more in memory)
- Each shard can grow independently

**Trade-offs of sharding:**

### 1. Operational complexity

**Before sharding:**

- One database server
- Simple deployment

**After sharding:**

- Multiple database servers
- Backup must shard too
- Failover must happen per shard
- Monitoring per shard
- Migration of shards requires planning

### 2. Application complexity

**Before sharding:**
```python
user = database.query("SELECT * FROM users WHERE id = 5")
```

**After sharding:**
```python
shard_id = consistent_hash(user_id) % num_shards
shard = shards[shard_id]
user = shard.query("SELECT * FROM users WHERE id = 5")
```

Every query now includes shard determination.

### 3. Cross-shard queries become expensive

**Example:** find all orders from user 500,000 (in Shard 1) with product 999,999 (product data maybe in Shard 3)

**Query:**
```sql
SELECT * FROM orders
WHERE user_id = 500000 AND product_id = 999999
```

**Execution:**

- Query Shard 1 for user's orders
- For each order, query Shard 3 for product
- Aggregate results

This is slow (many network round trips).

**Solutions:**

- Denormalize (store product info in shard 1 too)
- Accept the complexity
- Use different architecture for cross-shard queries

### 4. Transactions across shards fail

**Example:** transfer money between two users in different shards

```
User A (Shard 1): decrease balance by $100
User B (Shard 2): increase balance by $100
```

If User A's update succeeds but Shard 2 is down, User B never gets the money.

**Solutions:**

- Avoid cross-shard transactions
- Use saga pattern (eventual consistency)
- Accept data loss risk

### 5. Rebalancing is complex

**Problem:** add a new shard

```
Old: 3 shards, each holding users 1-3,000,000
New: 4 shards, each should hold users 1-2,250,000

Requires moving data from shards 1-3 to shards 1-4.
```

During rebalancing:

- System unavailable for affected data
- Or complex dual-write logic
- Risk of data loss or duplication

## Sharding strategies

### Hash-based sharding

```
shard_id = hash(user_id) % num_shards
```

**Pros:**

- Even distribution (if hash is good)
- Deterministic (same user always in same shard)

**Cons:**

- Adding shards requires rebalancing all data
- Queries that don't know user_id need to scan all shards

### Range-based sharding

```
user_id 1-1,000,000 -> Shard 1
user_id 1,000,001-2,000,000 -> Shard 2
user_id 2,000,001-3,000,000 -> Shard 3
```

**Pros:**

- Range queries easier (users 1-500,000 in Shard 1)
- Adding shards doesn't require rebalancing (new shard for new range)

**Cons:**

- Uneven distribution (if user IDs not uniform)
- Hot shards (if range has more active users)

### Directory-based sharding

```
Directory:
user_id 5 -> Shard 2
user_id 100 -> Shard 1
user_id 500 -> Shard 3
```

**Pros:**

- Flexible rebalancing (directory updated, no data move)
- Can adapt to load (hot shards migrated)

**Cons:**

- Directory lookup overhead
- Directory is single point of failure
- Complex to implement

## Hot shards and uneven load

**Problem:** not all shards get equal load

```
Shard 1 (users 1-1,000,000): 90% of traffic
Shard 2 (users 1,000,001-2,000,000): 5% of traffic
Shard 3 (users 2,000,001-3,000,000): 5% of traffic
```

Shard 1 becomes bottleneck.

**Causes:**

- Data is not uniform (some users much more popular)
- Access patterns are not uniform (some regions active, others dormant)

**Solutions:**

- Sub-shard (Shard 1 split into 1a, 1b)
- Denormalize (cache popular data elsewhere)
- Rebalance based on load (move some users to other shards)

## When to shard

**Symptoms that sharding is needed:**

1. **Write throughput exceeds single database**
   - Database writes at 10,000/sec
   - Application needs 50,000/sec
   - Single database insufficient

2. **Data size exceeds server memory**
   - Database size 2TB
   - Server memory 256GB
   - Cannot fit working set in memory

3. **Read replicas are saturated**
   - Replicas are bottleneck
   - Adding more replicas doesn't help (all saturated)

4. **Geographic distribution needed**
   - Users in multiple continents
   - Latency to central database too high
   - Local shard in each region needed

**Symptoms that sharding is NOT needed:**

- Data size fits in server memory
- Write throughput is moderate
- Read replication sufficient
- System is not experiencing actual bottlenecks

Sharding adds immense complexity. Use only when necessary.

## Investigation: identifying database bottlenecks

**How to know if database is the problem:**

1. **High database CPU**
   - Database CPU at 100%
   - Application CPU at 20%
   - Database is the bottleneck

2. **Slow queries**
   - Enable slow query log
   - Check query execution plans
   - Identify queries doing full scans

3. **Lock waits**
   - Lock statistics show contention
   - Threads waiting on locks
   - Deadlock logs indicate conflicts

4. **Disk I/O saturation**
   - Disk I/O at 100%
   - Despite adequate memory
   - Working set doesn't fit in cache

5. **Connection exhaustion**
   - Connection count at max
   - New connections rejected
   - Increasing pool size fails

## Common database scaling mistakes

### 1. Adding indexes for every query

**Mistake:** create 50 indexes for 50 slow queries

**Result:**

- Write performance degrades (every write updates 50 indexes)
- Storage bloats
- Query planner confused (chooses wrong index)

**Better:** identify expensive queries, create indexes for the most expensive.

### 2. Sharding too early

**Mistake:** shard after 1 year, before data requires it

**Result:**

- Cross-shard queries immediately needed
- Transactions fail
- Operational complexity not justified

**Better:** optimise single database first, shard only when necessary.

### 3. No query analysis

**Mistake:** add indexes blindly without understanding queries

**Result:**

- Indexes don't help (wrong columns)
- Write performance suffers
- Unused indexes consume storage

**Better:** analyze slow query log, understand query patterns.

### 4. Ignoring replica lag

**Mistake:** read from replica without checking lag

**Result:**

- Stale data returned
- Users see inconsistent state
- Application bugs from stale reads

**Better:** check replica lag, use master for critical reads, accept stale reads for non-critical data.

### 5. Shard without monitoring

**Mistake:** deploy sharding without metrics on per-shard load

**Result:**

- Hot shard emerges silently
- Days pass before noticed
- Affects users in that shard

**Better:** monitor each shard independently, alert on uneven distribution.

## Trade-offs summary

| Approach | Pros | Cons |
|----------|------|------|
| Single database | Simple, consistent | Limited by one server |
| Replication | Read scaling, HA | Writes still bottleneck |
| Sharding | Read+write scaling | Complex, cross-shard queries hard |
| Denormalization | Faster reads | Consistency complexity |
| Caching (Redis) | Fast reads | Stale data risk |

The best system often uses multiple layers:

- Single database for small workload
- Replication for high read volume
- Caching for hot data
- Sharding for very large datasets
- Denormalization for specific queries

## Questions to think about

- How do you know if your database is the bottleneck versus your application?
- If you add a database replica, why might query performance not improve?
- Why is adding an index expensive at write time?
- What queries become hard after sharding by user ID?
- If you shard by user but need to aggregate across all users, what must you do?
- How would you detect a hot shard?
- If replication lag is 10 seconds, what data consistency issues arise?
- Why is shard rebalancing dangerous?
- If a shard fails, what should the system do?
- At what data size does sharding become necessary?

## Summary

Database scaling is not one-size-fits-all. Each approach (replication, caching, sharding, denormalization) solves specific problems and introduces new ones.

The best engineers understand:

- When single database is insufficient (measure, don't guess)
- What each scaling technique solves (write bottleneck, read bottleneck, memory limit)
- What trade-offs each introduces (complexity, consistency, cross-shard queries)
- How to implement incrementally (cache first, replicate second, shard last)

The worst mistake is applying advanced techniques too early. The best systems start simple and evolve only when actual bottlenecks appear.
