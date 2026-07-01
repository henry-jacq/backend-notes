---
title: "Observability Fundamentals"
part: 7
part_title: "Operations"
chapter: 1
summary: "Explains the fundamentals of observability in production systems: metrics, logs, traces and alerting..."
---
# Observability Fundamentals

Explains the fundamentals of observability in production systems: metrics, logs, traces and alerting strategies.

## Why observability matters

Production systems fail in ways you cannot predict.

- A database connection pool fills up (why? investigate)
- Response latency spikes at 3 AM (why? investigate)
- Error rate jumps from 0.1% to 5% (why? investigate)
- Memory grows constantly (why? investigate)
- A service becomes slow but CPU is not high (why? investigate)

Without observability (metrics, logs, traces), you are blind. You debug by guessing.
With observability, you see the state of the system and identify root cause.

## Levels of observability

### 1. Metrics

Quantitative measurements: numbers over time.

Examples:

- Requests per second
- Response latency (p50, p95, p99)
- CPU usage (%)
- Memory usage (%)
- Disk I/O (operations/sec)
- Network bandwidth (MB/sec)
- Error rate (%)
- Cache hit rate (%)
- Database query latency (ms)

**What metrics show:**

- Where is the problem (CPU high? Memory high? Disk slow?)
- How big is the problem (error rate 0.1% or 5%?)
- When did it start (3 AM spike or gradual?)
- How it correlates (error rate spike with latency spike?)

**Metrics limitations:**

- Show what is happening, not why
- Aggregated (p95 latency hides individual slow requests)
- Historical (show past, not current state)

### 2. Logs

Discrete events: what happened?

Examples:

- Application started
- User logged in
- Order created
- Payment failed
- Connection timeout
- Database error

**What logs show:**

- Timeline of events
- Error messages (why something failed)
- Context (which user, which transaction)

**Log limitations:**

- Verbose (millions of log lines)
- Requires searching to find relevant events
- Difficult to correlate across services
- Historical (cannot see current processing)

### 3. Traces

Request path: where did the time go?

Examples:
```
Request GET /product/123
  |
  ├── Authentication (5ms)
  ├── Database query (200ms)
  ├── Cache lookup (2ms)
  ├── Serialize response (3ms)
  |
  Total: 210ms
```

**What traces show:**

- Which component is slow
- How much time each step takes
- Dependencies between steps

**Trace limitations:**

- Overhead to collect
- Large volume (millions of traces)
- Requires setup

## Key metrics for different components

### Application metrics

- Request rate (requests/sec)
- Request latency (p50, p95, p99)
- Error rate (%)
- Throughput (operations/sec)
- Resource usage (CPU, memory, disk)

### Database metrics

- Query rate (queries/sec)
- Query latency (ms)
- Slow query count
- Connection count (active/max)
- Lock wait time
- Replication lag (if replicated)

### Cache metrics

- Hit rate (%)
- Eviction rate
- Memory usage
- Command latency

### Queue metrics

- Queue depth (jobs waiting)
- Processing rate (jobs/sec)
- Job failure rate
- Job duration

### Network metrics

- Bandwidth usage (MB/sec)
- Packet loss (%)
- Latency (ms)

## Alerting strategy

Metrics are only useful if you alert on them.

**Alert on:**

- Latency threshold exceeded (p95 > 200ms)
- Error rate threshold exceeded (> 1%)
- Resource exhaustion (CPU > 90%, memory > 85%)
- Specific error conditions (database connection failed)

**Do not alert on:**

- Metrics that are normal (CPU 50% is fine)
- Metrics you cannot act on
- Metrics that always fire (alert fatigue)

**Good alerts:**

- Have clear threshold
- Relate to SLA (latency threshold based on SLA)
- Actionable (alert implies action)
- Have low false positive rate

**Bad alerts:**

- Too many (alert fatigue, ignored)
- Unclear threshold
- Not correlated to actual problem

To learn about common failure patterns, systematic debugging workflows and debugging checklists, see [Systematic Debugging and Failure Patterns](file:///d:/Playground/Backend%20Notes/5_Operations/1_Systematic_Debugging_and_Failure_Patterns.md).
