---
title: "System Evolution"
part: 1
part_title: "Foundations"
chapter: 1
summary: "No summary available"
---
# System Evolution

## Why systems evolve

A backend system starts simple: a single application server, a single database, maybe a cache. Developers ship it, users arrive, traffic grows. At some point, the system stops meeting requirements. Not because it was poorly designed, but because the problem changed.

System evolution is not a failure of planning. It is a consequence of success.

Engineers design systems to solve today's problem efficiently. As the problem grows, the design becomes a bottleneck. The next phase requires rethinking the architecture.

Understanding why systems evolve teaches you why each technology exists. Kafka doesn't exist because databases are bad. Redis doesn't exist because all data must be on disk. Microservices don't exist because monoliths are evil. Each emerged as a solution to a specific breaking point.

## The single-server system

Start here:

```
Clients
  |
  v
Application Server (handles requests, runs logic, connects to database)
  |
  v
Database (stores data)
```

This works for thousands of users. The application server handles requests sequentially or with a thread pool. The database handles reads and writes.

Metrics that matter at this stage:

- Request latency
- Database query time
- CPU and memory usage on the server
- Database storage size

## When a single server breaks

A single application server fails when it runs out of capacity. This manifests as:

**Symptoms:**
- CPU usage approaches 100%
- Memory usage grows constantly
- Requests start timing out
- Database connection pool exhausted
- Response times degrade unpredictably

**Why it happens:**
Each request consumes CPU, memory, and database connections. A server has finite resources. When request rate exceeds what one server can process, requests queue up. If they queue too long, clients give up or retry, making it worse.

**Breaking point:**
The server cannot handle concurrent requests. Scaling means adding more servers.

## Horizontal scaling: multiple servers

Next step:

```
Load Balancer
  |
  +---> Server 1
  +---> Server 2
  +---> Server 3
  |
  v
Database (still single)
```

A load balancer distributes requests across multiple servers. This solves CPU bottleneck: traffic spreads across more instances.

But a problem emerges: all servers write to the same database. The database becomes the bottleneck.

**Symptoms of database bottleneck:**
- CPU on database server is at 100%
- Slow queries pile up in query queue
- Connection pool fills up
- Lock contention on frequently updated rows
- Disk I/O is consistently high
- Response times for all requests degrade together

The database cannot write faster than one disk can write. Multiple application servers queuing writes to one database creates contention.

## Caching as a scaling tool

Problem: reads hit the database repeatedly for the same data.

Solution: cache frequently read data in memory, closer to the application.

```
Load Balancer
  |
  +---> Server 1 --> Cache
  +---> Server 2 --> Cache
  +---> Server 3 --> Cache
  |
  v
Database
```

**Why this works:**
A cache server (Redis, Memcached) holds data in RAM. RAM is orders of magnitude faster than disk. Reads that would hit the database for 10ms now hit cache for 0.1ms.

**Symptoms that caching helps:**
- Database CPU is high because of repeated reads
- Same queries run thousands of times per second
- Read latency is the dominant factor in response time
- Database connections are exhausted by readers

**Symptoms that caching doesn't help:**
- Most queries are unique (cache hit rate low)
- Writes dominate over reads
- Data changes constantly (cache stale)
- Working set larger than available RAM

Caching is not magic. It only helps when the working set fits in memory and reads are repetitive.

## Write scaling and persistence

Problem: caching helps reads, but writes still hit one database.

Example: an e-commerce system gets 1,000 orders per second. Each order is a write. One database server's disk can only write so fast.

**Symptoms:**
- Write latency increases as load increases
- Database CPU is 100% but mostly doing writes
- Disk I/O is maxed out
- Queue of pending write requests grows
- Users see "transaction timeout" errors

**Options:**

1. **Vertical scaling** — bigger disk, faster CPU, more RAM. Eventually hits hard limits. Expensive.

2. **Database replication** — replicate reads to secondary databases, all writes to one primary. Solves read scaling, not write scaling.

3. **Sharding** — split data across multiple databases by a key (user ID, order ID, etc.). Each shard is a separate database. Write load distributes.

```
Write request
  |
  v
Hash function (determine shard)
  |
  +---> Shard 1 (database)
  +---> Shard 2 (database)
  +---> Shard 3 (database)
```

Sharding solves write scaling but introduces new problems:

- Cross-shard queries become expensive
- Transactions that span shards require distributed coordination
- Rebalancing data when adding shards is complex
- Application code becomes more complex

For handling heavy workloads and coordination across services that sharding or synchronous flows cannot easily handle, systems evolve to use asynchronous processing and distributed messaging. See [1_Asynchronous_Processing.md](file:///d:/Playground/Backend%20Notes/0_Foundations/1_Asynchronous_Processing.md) to continue.
