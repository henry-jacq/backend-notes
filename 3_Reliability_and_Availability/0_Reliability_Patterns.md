---
title: "Reliability Patterns"
part: 4
part_title: "Reliability and Availability"
chapter: 1
summary: "This document explains how to build systems that continue working when failures occur. Reliability is not about..."
---
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

To learn about bulkheads, combining these patterns, and diagnosing reliability issues, see [1_Resource_Isolation_and_Fault_Tolerance.md](file:///d:/Playground/Backend%20Notes/3_Reliability_and_Availability/1_Resource_Isolation_and_Fault_Tolerance.md).
