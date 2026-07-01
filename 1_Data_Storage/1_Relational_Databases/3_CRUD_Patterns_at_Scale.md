---
title: "CRUD Patterns at Scale"
part: 2
part_title: "Data Storage"
chapter: 4
summary: "This document covers CRUD scaling patterns, common performance mistakes like N+1 queries, and strategies for..."
---
# CRUD Patterns at Scale

This document covers CRUD scaling patterns, common performance mistakes like N+1 queries, and strategies for diagnosing CRUD performance issues in production.

## CRUD patterns at scale

### INSERT heavy

**Scenario:** log events, create millions of records per second.

**Challenges:**

- Indexes slow down writes
- Disk I/O bottleneck
- Index fragmentation

**Solutions:**

- Batch inserts
- Use partitions (write to one partition at a time)
- Disable indexes temporarily during bulk load
- Denormalize to reduce writes

### SELECT heavy

**Scenario:** user dashboard, millions of reads per second.

**Challenges:**

- Indexes help but add disk space
- Query optimisation matters
- Cache hits critical

**Solutions:**

- Read replicas (distribute read load)
- Caching (Redis for hot data)
- Denormalization (avoid joins)
- Materialized views (precomputed results)

### UPDATE heavy

**Scenario:** real-time counters, status updates.

**Challenges:**

- Lock contention on hot rows
- Index updates expensive
- Cascading updates slow

**Solutions:**

- Counter tables (separate high-frequency updates)
- Batch updates (collect changes, update periodically)
- Denormalization (store aggregate instead of updating)

### DELETE heavy

**Scenario:** retention policies, archive old data.

**Challenges:**

- Cascade deletes are slow
- Index cleanup expensive
- Disk reclamation slow

**Solutions:**

- Soft deletes (mark as deleted)
- Partition by time (drop entire partition)
- Archive to separate table
- Background cleanup jobs

## Common CRUD mistakes

### 1. N+1 queries

**Mistake:**
```python
users = db.query("SELECT * FROM users LIMIT 100")
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user.id)
    # Process orders
```

**Result:** 1 query (get users) + 100 queries (get each user's orders) = 101 queries.

**Better:** single JOIN query.

```sql
SELECT users.*, orders.*
FROM users
JOIN orders ON users.id = orders.user_id
LIMIT 100 users
```

### 2. Missing indexes

**Mistake:** frequently query by email but no index on email column.

```sql
SELECT * FROM users WHERE email = 'alice@example.com'
```

**Result:** full table scan every time, slow.

**Better:** create index.

```sql
CREATE INDEX idx_users_email ON users(email)
```

### 3. Too many indexes

**Mistake:** create index on every column "just in case".

**Result:**

- Every INSERT updates all indexes (slow)
- Storage bloated
- Query planner confused (chooses wrong index)

**Better:** only index columns that are queried frequently.

### 4. Not batching deletes

**Mistake:** delete all old data in one query.

```sql
DELETE FROM logs WHERE date < '2020-01-01'
-- 1 billion rows deleted
```

**Result:**

- Database locked
- All other queries blocked
- Hours of downtime

**Better:** batch delete.

```python
while True:
    db.execute("DELETE FROM logs WHERE date < '2020-01-01' LIMIT 10000")
    time.sleep(1)  # Let other queries run
```

### 5. Denormalization without reason

**Mistake:** duplicate data to avoid joins, but joins not the bottleneck.

**Result:**

- Data inconsistency (update one copy, miss other)
- Storage bloated
- UPDATE queries complex

**Better:** denormalize only if JOIN is measured bottleneck.

## Investigation: CRUD performance issues

**Slow INSERTs:**

- Check: are indexes being updated?
- Check: are constraints being validated?
- Check: is disk I/O the bottleneck?

**Slow SELECTs:**

- Check: are indexes being used?
- Check: is query doing full table scan?
- Check: is query plan optimal?

**Slow UPDATEs:**

- Check: are rows locked?
- Check: is lock contention high?
- Check: are indexes being updated?

**Slow DELETEs:**

- Check: are cascade deletes triggered?
- Check: are indexes being cleaned up?
- Check: is disk full (impacts delete performance)?

## Questions to think about

- Why does an index slow down inserts but speed up selects?
- What is N+1 query problem and why is it bad?
- If you delete 1 user but it takes 10 minutes, what might be happening?
- Why would batching 1000 inserts be faster than 1000 individual inserts?
- What happens if you update a row that 100 other transactions are trying to read?
- Why would you use soft deletes instead of hard deletes?
- If SELECT is your bottleneck, what should you optimise first: indexes or caching?
- What's the difference between full table scan and index scan?

## Summary

CRUD operations are the fundamental database interactions. But they don't operate in isolation. Scaling CRUD requires understanding:

- Indexes (what they solve, what they cost)
- Queries (optimisation, joins)
- Locking (contention, performance)
- Patterns (batching, denormalization)

The best engineers think about CRUD efficiency early. Add indexes before production, batch operations, and measure before optimising.
