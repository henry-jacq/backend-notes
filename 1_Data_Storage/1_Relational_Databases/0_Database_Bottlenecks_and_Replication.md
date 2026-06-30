# Database Bottlenecks and Replication

This document explains why databases fail as systems grow, focusing on single database bottlenecks and how replication is used to scale read workloads.

## The database bottleneck

A single database server is finite. It has:
- CPU cores (limited parallel query execution)
- Memory (buffer pool size, working set limit)
- Disk I/O bandwidth (read/write throughput)
- Network bandwidth (query throughput, replication)
- Connection count (concurrent connections)

At some scale, all of these are exhausted.

## Single database breaking points

### Write bottleneck

**Problem:** all writes go to one server

```
Multiple application servers
  |
  +---> Database (single server)
```

Each write must:
1. Reach the database
2. Acquire a lock
3. Modify the data
4. Write to disk
5. Update indexes
6. Write to log (durability)
7. Return success

At high write volume, the database becomes the bottleneck.

**Symptoms:**
- Write latency increasing with load
- Lock waits in slow query log
- Disk I/O at 100%
- Write queue building up

**Example:**
```
Database can write 10,000 events/second
Application generates 100,000 events/second
Gap grows: events accumulate, latency increases
```

### Read bottleneck

**Problem:** reads require index lookups and disk I/O

Even with replication (replicas for read offload), replicas themselves become saturated.

**Symptoms:**
- Read latency increasing
- Query queue building
- Replica lag growing (replicas cannot keep up with writes)

### Memory bottleneck

**Problem:** buffer pool (database cache) has fixed size

```
Database working set (unique data accessed) = 500GB
Buffer pool size = 100GB

Only 20% of queries hit cache.
80% require disk I/O.
```

Without enough buffer pool, most queries hit disk (slow).

**Solutions:**
- Add more memory (limited by hardware)
- Reduce working set (delete old data)
- Improve caching (application caching with Redis)

### Connection limit

**Problem:** database has maximum concurrent connections

```
Max connections configured: 1000

When 1000 connections active, new connections rejected.
Applications see "too many connections" errors.
```

At high traffic, connection pool exhausted.

## Replication: solves read scaling, not write scaling

Replication copies data to multiple servers.

```
Master (handles writes)
  |
  +---> Replica 1 (handles reads)
  +---> Replica 2 (handles reads)
  +---> Replica 3 (handles reads)
```

**Benefits:**
- Reads distribute across replicas
- Read throughput increases
- High availability (if master fails, replica becomes master)

**Limitations:**
- All writes still go to master (write bottleneck remains)
- Replication lag (replicas lag behind master by milliseconds to seconds)
- Consistency issue (replicas may see different state than master during lag)

**Symptoms of replication not helping:**
- Replica lag growing (replicas cannot keep up)
- Master still saturated (writes still the bottleneck)
- Inconsistency bugs (read from replica, gets stale data)

Replication solves read scaling. It does not solve write scaling.

To learn how sharding and other architectural strategies are used to scale both reads and writes, see [1_Database_Sharding_and_Strategies.md](file:///d:/Playground/Backend%20Notes/1_Data_Storage/1_Relational_Databases/1_Database_Sharding_and_Strategies.md).
