---
title: "Data Storage: Persisting and Querying Data"
part: 2
part_title: "Data Storage"
type: "part_intro"
summary: "This section covers how to store data durably and retrieve it efficiently."
---
# Data Storage: Persisting and Querying Data

This section covers how to store data durably and retrieve it efficiently.

## Learning path

### 0_Basics/
Start here if you're new to databases or need a refresher on fundamental concepts.

### 1_Relational_Databases/ (SQL Databases)

**[0_Database_Bottlenecks_and_Replication.md](file:///d:/Playground/Backend%20Notes/1_Data_Storage/1_Relational_Databases/0_Database_Bottlenecks_and_Replication.md)** — Single Database Bottlenecks

- Limits of a single database (CPU, memory, disk I/O, network, connection limits)
- Write bottleneck symptoms and read bottlenecks
- Replication concepts and its limits for write workloads

**[1_Database_Sharding_and_Strategies.md](file:///d:/Playground/Backend%20Notes/1_Data_Storage/1_Relational_Databases/1_Database_Sharding_and_Strategies.md)** — Database Sharding

- Sharding as a read/write scaling solution
- Hash-based, range-based, and directory-based sharding strategies
- Hot shard problem and load imbalances
- Investigation and common scaling mistakes

**[2_CRUD_Operations_and_Performance.md](file:///d:/Playground/Backend%20Notes/1_Data_Storage/1_Relational_Databases/2_CRUD_Operations_and_Performance.md)** — Core CRUD Performance

- Execution costs of single vs bulk INSERTs
- Full table scans vs index scans under SELECT
- UPDATE/DELETE costs and database row-level locking

**[3_CRUD_Patterns_at_Scale.md](file:///d:/Playground/Backend%20Notes/1_Data_Storage/1_Relational_Databases/3_CRUD_Patterns_at_Scale.md)** — CRUD at Scale

- INSERT-heavy, SELECT-heavy, UPDATE-heavy, and DELETE-heavy scenarios
- Common CRUD mistakes (N+1 query problem, duplicate indexes, unbatched deletes)
- Systematic CRUD performance diagnosis and investigation

Read these in order. First understand the limits of single databases, then understand sharding, and then understand how CRUD operations interact with those limits.

### 2_In_Memory_Caching/Redis/

**0_INTRO.md** through **6_REDIS_DESIGN_AND_MISTAKES.md**

Redis is the solution to repeated expensive queries. This progression explains:

- Why Redis exists (database bottleneck solution)
- How Redis works (data structures, commands)
- When Redis helps (cache hit rate matters)
- When Redis hurts (memory limitations, stale data)
- Redis design trade-offs (single-threading, eviction, persistence, Pub/Sub)
- Common caching mistakes

## How these connect

1. **Database_Bottlenecks_and_Replication** explains single database limits and replication limits.
2. **Database_Sharding_and_Strategies** explains horizontal partitioning to scale writes.
3. **CRUD_Operations_and_Performance** & **CRUD_Patterns_at_Scale** explain how operations interact with databases.
4. **Redis** explains how to cache to reduce database load.

Understanding these gives you the mental model: databases are the original bottleneck, CRUD operations interact with scaling limits, caching and sharding help but introduce new challenges.

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
