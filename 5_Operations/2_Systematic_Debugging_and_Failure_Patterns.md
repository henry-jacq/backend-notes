---
title: "Systematic Debugging and Failure Patterns"
part: 7
part_title: "Operations"
chapter: 3
summary: "Covers common failure patterns in production environments, step-by-step troubleshooting workflows and..."
---
# Systematic Debugging and Failure Patterns

Covers common failure patterns in production environments, step-by-step troubleshooting workflows and debugging checklists.

## Building intuition: common failure patterns

### Pattern 1: Database is slow

**Metrics indicate:**

- Response latency increasing
- Database CPU at 100%
- Database connection pool filling
- Disk I/O high

**Logs show:**

- Slow query warnings
- Lock wait messages
- Connection timeout errors

**Investigation:**

1. Check slow query log (which queries are slow?)
2. Check query execution plan (full scan or index?)
3. Check for lock contention (other transactions blocking?)
4. Check data volume (table too large?)

**Example root causes:**

- Missing index (full table scan)
- N+1 queries (application fetching one-by-one)
- Hot row (many transactions on same row)
- Query change (new slow query deployed)

### Pattern 2: Memory leak or growth

**Metrics indicate:**

- Memory usage growing over time
- Garbage collection pauses increasing
- Eventually out-of-memory

**Logs show:**

- OutOfMemory error
- Garbage collection logs

**Investigation:**

1. Heap dump (where is memory used?)
2. Object allocation profiler (what is creating objects?)
3. Reference count (what is holding references?)

**Example root causes:**

- Objects never released (circular references)
- Cache growing unbounded (no eviction)
- Accidental string concatenation (creating copies)
- Static references keeping objects alive

### Pattern 3: Request timeout

**Metrics indicate:**

- Latency p99 increased
- Timeout error rate increased
- Thread count high (threads waiting)

**Logs show:**

- Timeout messages
- Incomplete traces (request started but never finished)

**Investigation:**

1. Thread dump (what are threads doing?)
2. Lock traces (are threads waiting for locks?)
3. Trace analysis (where did request get stuck?)

**Example root causes:**

- Downstream service slow (waiting for response)
- Database connection pool exhausted
- Lock contention
- Garbage collection pause

### Pattern 4: Error rate spike

**Metrics indicate:**

- Error rate from 0.1% to 5%
- Specific error type (timeout, database error, etc.)

**Logs show:**

- Error messages
- Stack traces
- Correlation with other events

**Investigation:**

1. Check what error type increased
2. Check when it started (correlation with deployment? traffic change?)
3. Check if it affects all users or specific ones

**Example root causes:**

- Dependency went down (database, cache, external API)
- Traffic spike (system overloaded)
- New code deployed with bug
- Cascading failure (one service failure triggers others)

### Pattern 5: Cascading failure

**Symptom:**
```
Service A slow or down
  |
  -> Service B (depends on A) times out
    |
    -> Service C (depends on B) times out
      |
      -> Service D (depends on C) times out
```

Each service failure cascades.

**Metrics indicate:**

- Multiple services showing errors
- Errors growing over time (not stabilizing)
- Latency increasing across services

**Investigation:**

1. Find the root service (which service failed first?)
2. Determine cause of root failure
3. Fix root, others recover

**Example root causes:**

- One service down, others depend on it
- Resource exhaustion (thread pool full, connection pool full)
- Retry storms (service retries too aggressively, overwhelming system)

## Debugging strategy: systematic approach

**When a problem occurs:**

### 1. Define the problem precisely

Not "it's slow."
Instead: "latency p99 increased from 200ms to 500ms at 3:05 AM."

**Questions:**

- What metric changed?
- How much did it change?
- When did it start?
- Is it still happening?
- Does it affect all users or some?

### 2. Check metrics

Look at all relevant metrics:

```
Latency: increased (p99 500ms)
Error rate: unchanged (0.1%)
CPU: 80%
Memory: 50%
Disk I/O: high
Database CPU: 100%
```

**Hypothesis:** database is slow.

### 3. Check logs

Search logs for errors or warnings around the time problem occurred.

```
3:05 AM: query timeout
3:05 AM: slow query detected
3:05 AM: lock wait timeout
```

**Hypothesis:** database query is waiting for lock.

### 4. Check traces

If using distributed tracing, look at slow requests.

```
Request GET /product/123
  |
  ├── Auth (5ms)
  ├── DB query (450ms)  <- THIS IS SLOW
  └── Serialize (3ms)
```

**Hypothesis:** specific database query is slow.

### 5. Investigate database

Check slow query log:

```
Query: SELECT * FROM products WHERE id = 123
Execution time: 450ms
Rows examined: 1,000,000
Rows returned: 1
Query plan: Full table scan (no index)
```

**Root cause:** missing index on `id` column.

### 6. Verify fix

Add index, monitor metrics, latency returns to normal.

```
Before: p99 latency 500ms
After: p99 latency 150ms
Query time: 5ms
```

## Common debugging mistakes

### 1. Guessing at root cause

**Mistake:** "it's probably the cache," make changes without data

**Result:**

- Wrong component fixed
- Problem persists
- Time wasted

**Better:** use metrics and logs to identify actual bottleneck.

### 2. Changing multiple things at once

**Mistake:** add caching, increase connection pool, upgrade database all at once

**Result:**

- Problem goes away but don't know which fix helped
- If something breaks, don't know which change caused it

**Better:** change one thing, measure impact, then change next.

### 3. Not correlating metrics

**Mistake:** see latency spike, check only latency metric

**Result:**

- Miss context (was CPU also high? Error rate?)
- Wrong hypothesis

**Better:** check all relevant metrics together.

### 4. Ignoring historical context

**Mistake:** problem occurred at 3 AM, don't check what deployed yesterday

**Result:**

- Obvious cause missed (new code deployed)

**Better:** always check what changed recently (code, config, traffic).

### 5. Not reproducing the problem

**Mistake:** problem reported as "sometimes slow," don't try to reproduce

**Result:**

- Cannot verify root cause
- Cannot verify fix works

**Better:** always try to reproduce (even if hard).

## Observability checklist

**For every production system:**

- [ ] Metrics for request latency (p50, p95, p99)
- [ ] Metrics for error rate
- [ ] Metrics for throughput (requests/sec)
- [ ] Metrics for resource usage (CPU, memory, disk)
- [ ] Dependency-specific metrics (database latency, cache hit rate)
- [ ] Logs with context (which request, which user)
- [ ] Traces showing request path
- [ ] Alerts on latency threshold
- [ ] Alerts on error rate threshold
- [ ] Alerts on resource exhaustion
- [ ] Runbook for common failures
- [ ] On-call rotation with access to logs, metrics, traces

## Questions to think about

- If latency spike happens but error rate is unchanged, where is the problem?
- If database CPU is 90% and application CPU is 10%, what is the bottleneck?
- If an alert fires but the metric is actually fine (false positive), what does that mean?
- How would you debug a problem that happens randomly, not reproducibly?
- If you add more caching and latency still increases, what else could be slow?
- Why is memory growing constantly a problem even if system is working fine?
- What would you check first if error rate spikes to 50%?
- If removing one service from load balancer makes everything fast, what does that tell you?

## Summary

Observability is the ability to understand your system from its external outputs. Common failures have patterns. Learning to recognize them (database slow, cascade failure, memory leak) helps you debug faster.

Systematic debugging (define problem -> check metrics -> check logs -> check traces -> investigate) beats random guessing every time.
