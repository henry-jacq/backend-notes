---
title: "Reliability and Availability: Building Systems That Don't Fail"
part: 4
part_title: "Reliability and Availability"
type: "part_intro"
summary: "This section covers how to make systems resilient to failures and keep them running despite problems."
---
# Reliability and Availability: Building Systems That Don't Fail

This section covers how to make systems resilient to failures and keep them running despite problems.

## Learning path

### Reliability Patterns

**[Retries & Circuit Breakers](file:///d:/Playground/Backend%20Notes/3_Reliability_and_Availability/0_Reliability_Patterns.md)**

- The failure premise in distributed systems
- Retries (handling transient failures, exponential backoff, jitter, idempotency)
- Circuit breakers (preventing cascading failures, states and transitions)

**[Bulkheads & Fault Isolation](file:///d:/Playground/Backend%20Notes/3_Reliability_and_Availability/1_Resource_Isolation_and_Fault_Tolerance.md)**

- Bulkheads (resource pools and isolation by request type or customer)
- Combining patterns (retries + circuit breakers + bulkheads)
- Common reliability mistakes and investigation strategy

These patterns are "defensive programming" for distributed systems. Failures will happen. These patterns make systems respond gracefully.

### Availability and Fault Tolerance

**[Measuring Availability & Replication](file:///d:/Playground/Backend%20Notes/3_Reliability_and_Availability/2_Availability_and_Replication.md)**

- Measuring availability (target uptime percentage and downtime calculations)
- Data replication (synchronous vs asynchronous replication, trade-offs)

**[Failover & Multi-Region](file:///d:/Playground/Backend%20Notes/3_Reliability_and_Availability/3_Failover_and_Multi_Region.md)**

- Automatic failover handling and split-brain mitigation
- Multi-region deployment challenges (latency, consistency)
- Availability strategies (active-active vs active-passive)
- Health checks and graceful degradation
- Common availability mistakes and investigation strategy

These are "architectural" approaches to resilience. They prevent failures from becoming outages.

## How these connect

**Reliability Patterns** handle failures by responding automatically.

- Service is slow? Retry with backoff.
- Service is down? Circuit breaker stops sending requests.
- One service starving resources? Bulkhead isolates it.

**Availability and Fault Tolerance** prevent failures from happening.

- Database fails? Replica takes over.
- Entire region fails? Multi-region deployment survives.
- Service unhealthy? Health check removes it from rotation.

Together they create systems that both prevent failures and respond to them gracefully.

## Key concepts

- Transient vs permanent failures
- Exponential backoff
- Circuit breaker states (closed, open, half-open)
- Idempotency requirement
- Availability measurements (nines: 99%, 99.9%, 99.99%)
- Replication (sync vs async)
- Failover (manual vs automatic)
- Split-brain problem
- Multi-region latency

## When to use each pattern

**Retries:**

- Transient network failures
- Temporary overload
- Safe only if operation is idempotent

**Circuit Breaker:**

- Dependency failures
- Cascading failure risk
- Need fast failure (not wait for timeout)

**Bulkheads:**

- Mixed workloads
- Resource contention
- Fairness matters (prevent one type starving others)

**Replication:**

- High availability required
- Data loss unacceptable
- Ready for operational complexity

**Failover:**

- When replication exists
- Automatic for speed, manual for safety

**Multi-region:**

- Disaster recovery needed
- Geographic distribution important
- Can tolerate replication latency

## Common mistakes

- Retrying without backoff (overwhelming system)
- Circuit breaker threshold too low (opens unnecessarily)
- No fallback when circuit opens (user sees error)
- Replicating synchronously (slow writes)
- Sharding without considering failover (partial outage)
- Not testing failover (breaks when needed)
- Not monitoring circuit breaker state (manual intervention needed)

## Connection to other sections

**Reliability + Data Storage:**

- Replication of databases
- Failover across database replicas
- Consistency trade-offs

**Reliability + Async and Events:**

- Message retries
- Dead-letter queues
- Consumer group failover

**Reliability + Infrastructure:**

- Load balancers detecting failed servers
- Health checks
- Automated recovery

## Next sections

After reliability and availability:

- **Infrastructure** — how to operate these systems
- **Operations** — how to monitor and debug them
