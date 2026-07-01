---
title: "Resource Isolation and Fault Tolerance"
part: 4
part_title: "Reliability and Availability"
chapter: 2
summary: "This document covers bulkheads (resource isolation), how to combine reliability patterns, and common reliability..."
---
# Resource Isolation and Fault Tolerance

This document covers bulkheads (resource isolation), how to combine reliability patterns, and common reliability pitfalls.

## Bulkheads: containing failures

A bulkhead isolates resources so one failure doesn't exhaust all resources.

**Without bulkheads:**
```
Request 1: to database (acquires connection)
Request 2: to database (acquires connection)
...
Request 1000: to database (no connections left)

Heavy database queries starving light queries.
Light queries fail with "connection pool exhausted."
```

**With bulkheads:**
```
Heavy queries:
  Thread pool 1 (4 threads)
  Connection pool 1 (4 connections)

Light queries:
  Thread pool 2 (8 threads)
  Connection pool 2 (8 connections)

Heavy query starves pool 1, doesn't affect pool 2.
Light queries continue working.
```

**Where to use bulkheads:**

1. **Thread pools by request type**
   - Fast requests (light queries)
   - Slow requests (heavy queries)
   - Separate pools prevent starvation

2. **Connection pools by database**
   - Primary database (operational queries)
   - Secondary database (reporting queries)
   - Reporting doesn't starve operational

3. **Resources by customer**
   - Customer A's requests
   - Customer B's requests
   - One customer's bad behaviour doesn't affect other

**Trade-off:**

- Resource overhead (multiple pools instead of one)
- Complexity in configuration

## Combining patterns

Reliability patterns work together.

**Example: calling a database**

```
Request to database:

1. Retry (transient network failure)
   - Attempt 1 timeout
   - Attempt 2 timeout
   - Attempt 3 success

2. Circuit breaker (database down)
   - Error rate high
   - Circuit opens
   - Return cached response

3. Bulkhead (connection pool exhaustion)
   - Use dedicated connection pool
   - Prevent other requests starving
```

**Implementation sequence:**

1. Start with retries (cheap, handles most transients)
2. Add circuit breaker (when cascading failures possible)
3. Add bulkheads (when resource contention likely)

## Common reliability mistakes

### 1. Retrying without backoff

**Mistake:** retry immediately on failure

```python
for i in range(3):
    try:
        response = call_service()
        return response
    except:
        pass  # immediate retry
```

**Result:**

- Overwhelming already-struggling service
- Makes problem worse
- Service stays down longer

**Better:** use exponential backoff with jitter.

### 2. Retrying non-idempotent operations

**Mistake:** retry a POST without idempotency key

```
POST /transfer with { from: A, to: B, amount: $100 }

Attempt 1: timeout
Attempt 2: succeeds (creates transfer)
Attempt 3: succeeds (creates ANOTHER transfer)

Result: $200 transferred instead of $100
```

**Better:** use idempotency key

```
POST /transfer with { from: A, to: B, amount: $100, idempotencyKey: "txn-123" }

Attempt 1: timeout
Attempt 2: succeeds (creates transfer, stores idempotencyKey)
Attempt 3: succeeds (returns same transfer, no new transfer created)
```

### 3. Circuit breaker threshold too low

**Mistake:** open circuit after just 5 errors

**Result:**

- Circuit opens on temporary spike
- Service recovers but requests rejected
- Artificial unavailability

**Better:** use percentage-based threshold (open when > 50% of requests fail).

### 4. No fallback when circuit opens

**Mistake:** circuit opens, return error immediately

**Result:**

- User sees error
- Could have returned cached response

**Better:** when circuit opens, return fallback (cached response, degraded mode, default value).

### 5. Not monitoring circuit breaker state

**Mistake:** circuit opens, nobody notices

**Result:**

- Service recovers but circuit stays open
- Manual intervention required
- Unnecessary unavailability

**Better:** alert when circuit opens, monitor state, verify recovery.

## Investigation: diagnosing reliability issues

**Symptom: error rate spikes**

Check:

1. Is this temporary (transient failure)?
   - If yes, retries should handle it

2. Is this cascading (one service affecting others)?
   - If yes, circuit breaker should stop spread

3. Are resources exhausted (thread pool, connection pool)?
   - If yes, bulkheads prevent this

**Symptom: latency high but no errors**

Check:

1. Are retries happening?
   - Each retry adds latency
   - May be timeout-and-retry loop

2. Is circuit breaker half-open (testing)?
   - Increased latency during half-open

3. Are queues building?
   - Backlog of work waiting

## Trade-offs summary

| Pattern | Problem Solved | Cost | When |
|---------|----------------|------|------|
| Retries | Transient failures | Increased latency if fails | Common |
| Circuit Breaker | Cascading failures | Explicit errors | Frequent failures expected |
| Bulkheads | Resource starvation | Operational complexity | Mixed workloads |

## Questions to think about

- If a service recovers after 30 seconds, why does exponential backoff matter?
- What happens if circuit breaker threshold is too high (opens rarely)?
- Why is idempotency required for retries but not for first attempt?
- If you retry a GET request 3 times, why is that safe?
- What would happen if every service had a circuit breaker to every other service?
- How would you know if bulkheads are helping or just wasting resources?
- If a service is down, should you retry forever or give up?
- Why is jitter better than synchronised retries?
- At what error rate should a circuit breaker open?
- What should happen when circuit breaker opens?

## Summary

Reliability patterns are about automatic responses to failures:

- Circuit breakers prevent cascading failures.
- Bulkheads contain resource exhaustion.

Together, they make systems that continue working despite individual component failures.
