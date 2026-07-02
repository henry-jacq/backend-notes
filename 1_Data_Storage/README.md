---
title: "Data Storage: Persisting and Querying Data"
part: 2
part_title: "Data Storage"
type: "part_intro"
summary: "This section covers how to store data durably and retrieve it efficiently."
---
# Data Storage: Persisting and Querying Data

This section covers how to store data durably and retrieve it efficiently.

## Chapters

**Single Database Bottlenecks**

- Limits of a single database (CPU, memory, disk I/O, network, connection limits)
- Write bottleneck symptoms and read bottlenecks
- Replication concepts and its limits for write workloads

**Database Sharding**

- Sharding as a read/write scaling solution
- Hash-based, range-based and directory-based sharding strategies
- Hot shard problem and load imbalances
- Investigation and common scaling mistakes

**Core CRUD Performance**

- Execution costs of single vs bulk INSERTs
- Full table scans vs index scans under SELECT
- UPDATE/DELETE costs and database row-level locking

**CRUD at Scale**

- INSERT-heavy, SELECT-heavy, UPDATE-heavy and DELETE-heavy scenarios
- Common CRUD mistakes (N+1 query problem, duplicate indexes, unbatched deletes)
- Systematic CRUD performance diagnosis and investigation

**Geospatial Indexing and Proximity Search**

- Challenge of multi-dimensional indexing (1D B-Tree limitations)
- Custom spatial trees (Quadtrees, KD-trees, R-trees, R*-trees) and design choices
- Encoded key space-filling curves (Geohash, Google S2, Uber H3)
- Range scanning, boundary artifacts (3x3 grid trick) and multi-resolution zoom

**Redis Fundamentals**

- Core architecture (in-memory, single-threaded execution model)
- Supported data types (Strings, Hashes, Lists, Sets, Sorted Sets) and core commands
- Key expirations and lightweight Pub/Sub messaging

**Redis at Scale**

- Caching theory (read bottlenecks and cache hit rate metrics)
- Memory limits and key eviction policies (LRU, LFU)
- Disk persistence trade-offs (RDB snapshots vs AOF logs)
- Caching anti-patterns and common design mistakes

## How these connect

1. **Database bottlenecks and replication** explains single database limits and replication limits.
2. **Database sharding and strategies** explains horizontal partitioning to scale writes.
3. **CRUD operations and performance** & **CRUD patterns at scale** explain how operations interact with databases.
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

