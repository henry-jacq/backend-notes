---
title: "Common Bottlenecks and Testing"
part: 1
part_title: "Foundations"
chapter: 4
summary: "No summary available"
---
# Common Bottlenecks and Testing

## Common performance bottlenecks

### Database queries

Symptoms:
- Database CPU at 100%
- Slow query log filling up
- Query latency increasing with load

Causes:
- Missing indexes (full table scans)
- N+1 queries (one query triggers many follow-up queries)
- Inefficient join order
- Lack of query result caching
- Locks on frequently updated rows

Investigation:
- Enable query logging
- Look at execution plans
- Count queries per request
- Measure query latency

Fix order:
1. Add indexes
2. Remove N+1 queries
3. Cache query results
4. Redesign the schema

### Memory allocation and garbage collection

Symptoms:
- Memory usage grows over time
- Latency spikes periodically (garbage collection pauses)
- Out-of-memory errors

Causes:
- Objects created unnecessarily (allocations in hot loops)
- Memory leaks (references held longer than needed)
- Large objects kept in memory
- Inefficient data structures

Investigation:
- Heap dumps
- Allocation profilers
- Garbage collection logs

Fix:
- Reduce object allocation
- Release references explicitly
- Use efficient data structures
- Consider object pooling

### Lock contention

Symptoms:
- High CPU usage but throughput does not increase
- Latency increases with concurrent load
- Thread count high but threads waiting

Causes:
- Too many threads competing for locks
- Holding locks too long
- Coarse-grained locking (locking entire table instead of row)

Investigation:
- Thread dumps (show which threads are waiting)
- Lock statistics (if available)
- Contention profilers

Fix:
- Fine-grained locking (lock smaller data)
- Reduce time locks are held
- Use lock-free data structures
- Partition data to reduce contention

### Network I/O

Symptoms:
- Network bandwidth near limit
- Requests that cross data centers are slow
- Latency correlated with request size

Causes:
- Large response sizes
- Inefficient serialization (JSON vs binary)
- Chatty protocols (many round trips for one logical operation)

Investigation:
- Network packet capture
- Request size distribution
- Bandwidth utilization

Fix:
- Compress responses
- Filter unnecessary data
- Use binary serialization
- Batch operations

### Disk I/O

Symptoms:
- Disk utilization high but CPU/memory low
- Response times variable and unpredictable
- Latency correlated with disk activity

Causes:
- Sequential reads instead of random
- Inefficient caching (disk thrashing)
- Fsync on every write (unnecessary durability guarantees)
- Insufficient RAM for working set

Investigation:
- Disk I/O monitoring
- File access patterns

Fix:
- Reduce fsync frequency (batch writes)
- Increase RAM or cache size
- Prefetch data
- Use SSD instead of HDD

## Amdahl's Law and diminishing returns

Amdahl's Law describes why optimizing one component stops helping at some point.

If a system spends 70% of time in component A and 30% in component B:

- Optimizing A by 50% saves 35% overall
- Optimizing A by 99% saves 69.3% overall (approaching limit)
- Optimizing B saves almost nothing initially

Once you optimize the bottleneck, a different component becomes the bottleneck.

This is why profiling before optimization matters. Without profiling, developers often optimize the wrong thing and see no improvement.

## Caching decisions

Caching helps when:
- Same data is read repeatedly
- Working set fits in available memory
- Cache hit rate is high (> 80%)
- Data doesn't change too frequently

Caching hurts when:
- Cache hit rate is low (< 30%)
- Data changes constantly (cache invalidation complexity)
- Memory is limited and cache causes eviction of other data
- Stale data causes bugs

**Cache effectiveness:**
- Hit rate below 50%: probably not worth the complexity
- Hit rate 50-80%: helps but monitor carefully
- Hit rate above 80%: definitely worthwhile

Many developers add caching reactively ("it's slow, add cache!"). Better approach: measure whether queries are repeated. If yes, cache helps. If no, cache adds complexity without benefit.

## Premature optimization trap

The most common performance mistake: optimizing before understanding requirements.

Examples:
- Adding Redis before measuring database latency
- Implementing connection pooling in application before checking if database is the bottleneck
- Rewriting code in a faster language before profiling
- Adding async processing for work that is already fast

All these add complexity.

**When to optimize:**
1. Requirements are clear (response time target exists)
2. Current system doesn't meet them (measured)
3. Bottleneck is identified (profiled)
4. Simple optimizations tried first (indexes, caching, code)
5. Impact is measured (before/after comparison)

## Performance testing

Performance requirements only matter if you verify the system meets them under load.

**Types:**

- **Load test** — does system meet requirements at target load?
- **Stress test** — at what load does system fail?
- **Soak test** — does system degrade over time? (memory leaks, file descriptor leaks)
- **Spike test** — does system handle sudden traffic increases?

**Load testing pitfalls:**

- Using synthetic traffic that doesn't match real requests
- Testing from a machine too close to the system (network latency not realistic)
- Testing with too few concurrent users (doesn't stress database connection pool)
- Testing with unrealistic think time between requests
- Not measuring percentile latencies (just averaging hides tail latency)

Good load testing matches production traffic patterns: request distribution, think times, data patterns.

## Monitoring and alerting

Performance degradation must be detected early.

**Metrics to monitor:**

- Response latency (p50, p95, p99)
- Throughput (requests per second)
- Error rate
- Resource usage (CPU, memory, disk, network)
- Database metrics (query latency, slow queries)
- Cache metrics (hit rate, eviction rate)

**Alert thresholds:**

- p99 latency > 500ms
- Error rate > 0.1%
- Queue depth > 10,000 jobs
- Database CPU > 80%
- Disk usage > 90%

Without alerts, performance degradation goes unnoticed until users complain.

## Questions to think about

- How do you know if your system is slow?
- What metric is most important: p50, p95, or p99 latency?
- If a query takes 1 second but only happens once per day, does it matter?
- How do you prove that adding cache will actually help?
- What happens if the bottleneck is network I/O in a data center you don't control?
- If you optimize the database query from 700ms to 100ms, and response time improves by only 50%, what else is slow?
- When is premature optimization actually a good idea?
- How do you differentiate between performance problem and scalability problem?

## Summary

Performance engineering is about understanding systems deeply, measuring accurately, and optimizing the real bottleneck.

Most performance problems are not about choosing faster technologies. They are about:

1. Knowing what acceptable performance is
2. Measuring current performance accurately
3. Finding the real bottleneck (profiling, not guessing)
4. Fixing the bottleneck (simple fixes first)
5. Verifying the fix worked (before/after measurement)
6. Repeating as new bottlenecks emerge

The best performance engineers are careful before they are clever. They measure before they code.
