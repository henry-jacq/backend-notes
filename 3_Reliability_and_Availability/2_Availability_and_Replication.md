---
title: "Availability and Replication"
part: 4
part_title: "Reliability and Availability"
chapter: 3
summary: "This document explains availability metrics and data replication strategies as the foundation for building..."
---
# Availability and Replication

This document explains availability metrics and data replication strategies as the foundation for building fault-tolerant systems.

## The availability problem

A single server is a single point of failure.

```
Request -> Server -> Database

Server crashes:
  No response
  System unavailable
  Users affected
```

To be always available (or close to it), you need redundancy.

## Measuring availability

Availability is expressed as uptime percentage.

| Availability | Downtime per year | Downtime per month |
|--------------|-------------------|-------------------|
| 99% (two nines) | 3.65 days | 7.2 hours |
| 99.9% (three nines) | 8.76 hours | 43 minutes |
| 99.99% (four nines) | 52 minutes | 4.3 minutes |
| 99.999% (five nines) | 5.26 minutes | 26 seconds |

**Reality check:**
- 99% (two nines) is achievable with basic redundancy
- 99.9% (three nines) requires solid engineering
- 99.99% (four nines) is very difficult
- 99.999% (five nines) is exceptionally rare

Most critical systems target 99.9% (three nines).

## Replication: the foundation

Replication copies data to multiple servers.

```
Master: handles reads and writes
Replica 1: copy of master (reads only)
Replica 2: copy of master (reads only)
```

**Benefits:**
- Read distribution (scale read throughput)
- High availability (if master fails, replica takes over)
- Data durability (multiple copies)

**Types of replication:**

### 1. Synchronous replication

```
Write to master:
  1. Master receives write
  2. Master applies write
  3. Master waits for replicas to acknowledge
  4. Master confirms write to client

All replicas have the write before acknowledging.
Consistent but slower.
```

**Pros:** strong consistency (all servers have same data)
**Cons:** slower (wait for slowest replica), if any replica down, writes block

### 2. Asynchronous replication

```
Write to master:
  1. Master receives write
  2. Master applies write
  3. Master confirms write to client
  4. Master sends write to replicas (in background)

Master doesn't wait for replicas.
Fast but replication delay.
```

**Pros:** fast writes
**Cons:** replicas lag (may not have latest data), if master fails before replicating, data is lost

**Trade-off:**
Synchronous = consistency, slower.
Asynchronous = performance, eventual consistency.

Most systems use asynchronous with monitoring (alert if lag too high).

To learn about database failover mechanisms, multi-region deployments, and how to avoid split-brain issues, see [3_Failover_and_Multi_Region.md](file:///d:/Playground/Backend%20Notes/3_Reliability_and_Availability/3_Failover_and_Multi_Region.md).
