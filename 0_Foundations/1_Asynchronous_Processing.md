---
title: "Asynchronous Processing"
part: 1
part_title: "Foundations"
chapter: 2
summary: "No summary available"
---
# Asynchronous Processing

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

**Premature optimisation:**
Adding caching, sharding, or async processing before the system actually needs it. Code becomes complex. Problems that don't exist yet are now real problems to debug.

**Scaling horizontally too early:**
Load balancing adds complexity. Before scaling horizontally, try:

1. Optimise database queries (indexes)
2. Add caching
3. Optimise application code (remove inefficiencies)
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

The best engineers know when to scale and when to optimise. They can look at metrics and see where the next bottleneck will emerge before it becomes critical.
