# System Evolution and Scalability

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

## Asynchronous processing and queues

Problem: not all work must finish in the request-response cycle.

Example: user uploads a photo. Application must:

1. Store the photo file
2. Resize the photo
3. Generate thumbnail
4. Update database
5. Send notification

If all this happens synchronously in the request, response takes 5 seconds. Users see a slow request.

Solution: queue the work asynchronously.

```
Request
  |
  v
Application (store file, queue resize job, queue notification)
  |
  v
Return response (fast)

Meanwhile:
Worker processes resize job
Worker processes notification
```

**Why this works:**
- Request completes immediately
- Users see fast response
- Heavy work happens later
- Work is retryable if it fails

**Symptoms that async helps:**
- Some request steps are slow (file processing, API calls to external services)
- Work can be done later without affecting user
- Same work is repeated across requests (batch it)

**New problems introduced:**
- Jobs may fail. Need retries.
- Jobs may process out of order. Need idempotency.
- Multiple workers might process the same job. Need locking or deduplication.
- Monitoring becomes harder (no immediate feedback)
- Debugging delayed failures is complex

## Event streaming and distributed messaging

Problem: multiple services need to react to the same event.

Example: when an order is created:
- Inventory service must decrease stock
- Billing service must charge payment
- Notification service must send email
- Analytics service must log the order

If the application calls each service directly:

```
Order service
  |
  +---> Inventory service
  +---> Billing service
  +---> Notification service
  +---> Analytics service
```

Problems:
- Order service must know about all downstream services
- If one service is slow, the whole request is slow
- If one service is down, the order fails
- Adding a new service requires changing order service code
- Retry logic and failure handling get complex

Solution: publish events to a message broker.

```
Order service publishes: "OrderCreated" event
  |
  v
Message broker (Kafka, RabbitMQ)
  |
  +---> Inventory service subscribes
  +---> Billing service subscribes
  +---> Notification service subscribes
  +---> Analytics service subscribes
```

Services subscribe to events they care about. Order service doesn't know about them.

**Why this works:**
- Decoupling. Services don't directly call each other.
- Resilience. If billing service is slow, order is still created and stored.
- Scalability. New services can subscribe without changing order service.
- Replay. If a service goes down, it can catch up by replaying events.

**New problems introduced:**
- Distributed transactions no longer work (two-phase commit across message broker doesn't help)
- Eventual consistency. Billing might happen 5 minutes after order.
- Duplicate events. Message broker might deliver the same event twice. Services must be idempotent.
- Event schema evolution. If you change the event format, old consumers might break.
- Ordering guarantees. Events for the same order must be processed in order. Requires partitioning.

## Breaking points and metrics

Understanding when to scale requires knowing what to measure:

**Single server scaling limit:**
- CPU usage of application server
- Memory usage of application server
- Request queue depth
- Response latency percentiles (p50, p95, p99)
- Requests per second at different latencies

**Database scaling limit:**
- CPU usage of database server
- Disk I/O utilization
- Query latency
- Lock contention (row locks, table locks)
- Connection pool usage

**Cache effectiveness:**
- Cache hit rate
- Cache eviction rate
- Memory usage

**Queue processing:**
- Queue depth (how many jobs waiting)
- Job processing time
- Job failure rate
- Worker utilization

## Common scaling mistakes

**Premature optimization:**
Adding caching, sharding, or async processing before the system actually needs it. Code becomes complex. Problems that don't exist yet are now real problems to debug.

**Scaling horizontally too early:**
Load balancing adds complexity. Before scaling horizontally, try:
1. Optimize database queries (indexes)
2. Add caching
3. Optimize application code (remove inefficiencies)
4. Upgrade server hardware

**Ignoring the database:**
Many developers scale application servers but ignore database tuning. The database is often the real bottleneck.

**Async everywhere:**
Treating async processing as magic. It trades immediate feedback for later problems. Complex to debug. Use it for actual async work, not as a performance hack.

**Cache without considering staleness:**
Caching stale data sometimes causes bugs. Users see inconsistent state. Worse than no cache.

**Sharding without a plan:**
Sharding is easy to add, hard to remove. Data rebalancing is complex. Hot shards (shards with much more data or traffic) become new bottlenecks.

## Questions to think about

- At what traffic level does a single server become the bottleneck?
- Which is the bottleneck first: CPU, memory, or disk I/O?
- How do you know the database is the problem and not the application?
- What metrics indicate it is time to add caching?
- What happens to cache effectiveness if the working set is larger than available RAM?
- If you shard by user ID but queries often need to aggregate across all users, what breaks?
- Why would a system use both caching and a message queue?
- If async processing is added, how do you ensure jobs actually complete?
- What happens if a worker crashes in the middle of processing a job?
- How do you know when horizontal scaling actually helps versus just adds complexity?

## Summary

Systems evolve because success creates new bottlenecks. Each technology (caching, sharding, async queues, message brokers) emerges as a solution to a specific breaking point.

Scaling is not about using cool technologies. It is about:

1. Measuring the system accurately
2. Identifying the real bottleneck
3. Understanding trade-offs of each solution
4. Choosing the minimal change that solves the problem
5. Monitoring what breaks next
6. Repeating as the system evolves

The best engineers know when to scale and when to optimize. They can look at metrics and see where the next bottleneck will emerge before it becomes critical.
