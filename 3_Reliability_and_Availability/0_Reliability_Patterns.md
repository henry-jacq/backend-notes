# Reliability Patterns

This document explains how to build systems that continue working when failures occur. Reliability is not about preventing failures—failures happen. It is about containing them.

## The failure premise

Failures are inevitable.

- Network packets are lost
- Servers crash
- Services become slow
- Databases lock up
- Disks fill up

A naive system stops working when something fails.

A reliable system detects failures and responds automatically. It continues operating despite failures.

## Why reliability matters

**Without reliability:**
```
User request -> Service A -> Service B (fails)
Result: user sees error, session lost, data lost
```

**With reliability:**
```
User request -> Service A -> Service B (fails)
                            -> Fallback (cached response)
Result: user sees slightly stale data, continues working
```

The difference: user experience continues, data is preserved.

## Three fundamental patterns

### 1. Retries: handling transient failures

A transient failure is temporary and usually succeeds if retried.

**Example:**
```
Request to downstream service:
Attempt 1: timeout (network congestion)
Attempt 2: success

Network packet lost:
Attempt 1: no response
Attempt 2: packet arrives
```

Retrying works for transient failures.

**When retries help:**
- Network timeout (usually brief)
- Temporary overload (service recovers quickly)
- Momentary unavailability (service restarts, comes back)

**When retries don't help:**
- Permanent failure (service down permanently)
- Bug in downstream service (retrying same request returns same error)
- Permanent resource exhaustion

**Retry strategy:**

```
Attempt 1: wait 100ms, try again
Attempt 2: wait 200ms, try again
Attempt 3: wait 400ms, try again
Attempt 4: give up, return error
```

**Exponential backoff:** each retry waits longer than the previous one.

**Why backoff helps:**
- Don't overwhelm struggling service
- Give service time to recover
- Spread requests (not thundering herd)

**Example without backoff:**
```
Service is down.
All clients retry immediately.
Request rate spikes.
Service overwhelmed even more.
Service stays down longer.
```

**Example with backoff:**
```
Service is down.
Clients retry with increasing delays.
Request rate stays manageable.
Service recovers.
Retries succeed.
```

**Retry limits:**
- Max 3 retries (diminishing returns)
- Max total time (don't wait forever)
- Jitter (add randomness to prevent synchronized storms)

**Idempotency requirement:**
Retries only safe if operation is idempotent (retrying has no additional effect).

```
GET /user/123
Safe to retry (reading same data multiple times = same result)

POST /orders
Dangerous to retry without idempotency (may create duplicate orders)

POST /orders with idempotency key
Safe to retry (same key = same order)
```

### 2. Circuit breakers: preventing cascading failures

A circuit breaker detects when a downstream service is failing and stops sending requests to it.

**Without circuit breaker:**
```
Service A calls Service B
Service B is down
Service A waits for timeout (5 seconds)
Request returns error after 5 seconds
User sees error after 5 seconds

100 requests per second to Service B
100 * 5 = 500 second-equivalents of wasted waiting
```

**With circuit breaker:**
```
Service A calls Service B
Service B is down
Circuit breaker opens (stops sending requests)
Request fails immediately (100ms)
User sees error after 100ms
Reduces wasted waiting by 50x
```

**Circuit breaker states:**

1. **Closed (normal)**
   - Requests flow to downstream service
   - Monitoring success/failure rate

2. **Open (failure detected)**
   - Stop sending requests immediately
   - Return error to caller
   - Wait for recovery

3. **Half-open (testing recovery)**
   - Allow one test request through
   - If succeeds, go to Closed
   - If fails, go back to Open

**Example flow:**

```
Closed state:
  Request 1: success
  Request 2: success
  Request 3: success

Failure detection (error rate > 50%):
  Request 4: fail
  Request 5: fail
  Request 6: fail
  Circuit opens (stop sending requests)

Open state (60 seconds):
  Request 7: rejected immediately (circuit open)
  Request 8: rejected immediately (circuit open)

60 seconds passed, enter half-open:
  Request 9: allowed (test request)
  Request 9: succeeds

Back to closed:
  Request 10: success
```

**Benefits:**
- Fast failure (fail immediately, not after timeout)
- Prevents overwhelming struggling service
- Signals to user that service is down (not hanging)

**Trade-off:**
- User sees error instead of cached response or fallback
- Must have fallback strategy

### 3. Bulkheads: containing failures

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
   - One customer's bad behavior doesn't affect other

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

3. Bulkhead (connection exhaustion)
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
- Why is jitter better than synchronized retries?
- At what error rate should a circuit breaker open?
- What should happen when circuit breaker opens?

## Summary

Reliability patterns are about automatic responses to failures.

Retries handle transient failures (network blips, temporary overload).
Circuit breakers prevent cascading failures (one service failing doesn't break others).
Bulkheads contain resource exhaustion (one type of request doesn't starve others).

Together, they make systems that continue working despite individual failures.

The best engineers think about reliability from the start. Add these patterns incrementally as failures emerge, don't wait until systems are on fire.
