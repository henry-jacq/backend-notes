# Data Storage: Persisting and Querying Data

This section covers how to store data durably and retrieve it efficiently.

## Learning path

### 0_Basics/
Start here if you're new to databases or need a refresher on fundamental concepts.

### 1_Relational_Databases/ (SQL Databases)

**0_Database_Design_for_Scale.md** — Why databases fail and how to fix it
- Single database bottlenecks (write bottleneck, read bottleneck, memory limits)
- Replication (solves read scaling, not write scaling)
- Sharding (solves write scaling, introduces complexity)
- Hot shard problem and load imbalance
- When each approach is necessary

**1_CRUD_Operations.md** — Create, Read, Update, Delete operations
- How each operation works at the database level
- Indexes (what they solve, what they cost)
- Common patterns (bulk insert, JOIN optimization)
- N+1 query problem
- Locking and contention
- Investigation and optimization

Read these in order. First understand the limits of single databases, then understand how operations interact with those limits.

### 2_In_Memory_Caching/Redis/

**0_INTRO.md** through **5_SYSTEMS_PERSPECTIVE.md**

Redis is the solution to repeated expensive queries. This progression explains:
- Why Redis exists (database bottleneck solution)
- How Redis works (data structures, commands)
- When Redis helps (cache hit rate matters)
- When Redis hurts (memory limitations, stale data)

## How these connect

1. **Database_Design_for_Scale** explains why databases fail at scale
2. **CRUD_Operations** explains how operations interact with databases
3. **Redis** explains how to cache to reduce database load

Understanding all three gives you the mental model: databases are the original bottleneck, CRUD operations interact with scaling limits, caching helps but introduces new problems.

## Key concepts

- Vertical vs horizontal scaling
- Indexes (trade-offs)
- Replication (async/sync)
- Sharding (hot shards, cross-shard queries)
- Caching (hit rate, eviction, consistency)
- CRUD patterns (N+1, batching, locking)

## When to use each

**Relational databases alone:**
- Starting out, small scale
- Strong consistency critical
- Complex queries needed

**Relational + Replication:**
- High read volume
- Some availability improvement
- Write bottleneck still exists

**Relational + Sharding:**
- Very large datasets
- Write scaling needed
- Willing to accept eventual consistency

**Relational + Caching (Redis):**
- Same queries repeated many times
- Working set fits in memory
- Some staleness acceptable

## Common mistakes to avoid

- Sharding too early (before single database is saturated)
- Caching before measuring (cache hit rate matters)
- Denormalizing without reason (consistency costs increase)
- Creating indexes for every query (write performance suffers)
- Ignoring database limits until system fails

## Next sections

After mastering data storage:
- **Async and Events** — handle work asynchronously to reduce database write load
- **Reliability** — ensure data isn't lost during failures
