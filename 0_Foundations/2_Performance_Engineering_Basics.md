---
title: "Performance Engineering Basics"
part: 1
part_title: "Foundations"
chapter: 3
summary: "Performance engineering is not about making things faster. It is about understanding what slow means, proving where..."
---
# Performance Engineering Basics

Performance engineering is not about making things faster. It is about understanding what slow means, proving where slowness lives, and choosing what to optimise.

Many developers equate performance with speed. That is imprecise. Performance engineering is about matching system behaviour to requirements under realistic conditions.

## Performance versus scalability

They are different problems.

**Scalability:** can the system handle more load? Add more servers, distribute work, handle growth.

**Performance:** does it meet latency requirements at the current load? Optimise queries, reduce allocations, cache hot data.

A scalable system that is slow is still slow. A fast system that doesn't scale still breaks at peak load.

Performance work should start only after understanding what "slow" means in your system.

## Defining performance requirements

Before optimising, establish what acceptable performance is.

Without this, optimisation is guesswork.

**Questions to answer:**

- What is the target response time for each request type?
- What is the acceptable tail latency (p95, p99)?
- How many requests per second must the system handle?
- What is the acceptable error rate?
- What resource constraints exist (memory, CPU, bandwidth)?

Example requirements:

```
API endpoint: /api/products/{id}

- p50 latency: < 50ms
- p95 latency: < 200ms
- p99 latency: < 500ms
- SLA: 99.9% uptime
- Traffic: 10,000 requests/second
```

Without these numbers, optimisation is meaningless. One developer might target 100ms, another 10ms. The effort differs by 100x.

## Why the baseline matters

Before optimising anything, measure the current system.

**Why:**

- Optimisation without baseline is guesswork
- Changes might not matter (optimise the wrong thing)
- Regressions might go unnoticed
- You cannot prove improvement

**Baseline measurement includes:**

- Request latency distribution (p50, p95, p99)
- Throughput (requests/second)
- Resource usage (CPU, memory, disk I/O, network)
- Error rate
- Database query latency
- Cache hit rate (if caching exists)
- Queue depth (if async work exists)

Measure under realistic load, not synthetic traffic.

## Finding the bottleneck

A bottleneck is the component that limits overall performance.

If CPU is at 100% but memory is 30%, CPU is the bottleneck. Optimising memory helps nothing.

**Tools to identify bottlenecks:**

- **Profilers** — measure where CPU time is spent (function call counts, time per function)
- **System monitoring** — CPU, memory, disk I/O, network utilization
- **Database statistics** — query execution plans, slow query logs
- **Logs** — error rates, timeout frequencies
- **Traces** — latency breakdown across services (which service is slowest?)
- **Dashboards** — correlate metrics (when latency increased, what changed?)

**Example: request takes 1 second**

```
Trace breakdown:

- Application code: 100ms
- Database query: 700ms
- Cache lookup: 50ms
- Network overhead: 150ms
```

The database query is the bottleneck. Optimising application code saves 100ms (10% improvement). Optimising the query saves 700ms (70% improvement).

Always optimise the bottleneck first.

To learn about common performance bottlenecks and how to test for them under load, see [3_Common_Bottlenecks_and_Testing.md](file:///d:/Playground/Backend%20Notes/0_Foundations/3_Common_Bottlenecks_and_Testing.md).
