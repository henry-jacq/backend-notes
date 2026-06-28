# Reliability and Availability: Building Systems That Don't Fail

This section covers how to make systems resilient to failures and keep them running despite problems.

## Learning path

### Reliability Patterns

**0_Reliability_Patterns.md** — Retries, circuit breakers, bulkheads

How to handle component failures automatically:
- Retries (handling transient failures)
- Circuit breakers (preventing cascading failures)
- Bulkheads (resource isolation)
- Combining patterns effectively

These patterns are "defensive programming" for distributed systems. Failures will happen. These patterns make systems respond gracefully.

### Availability and Fault Tolerance

**1_Availability_and_Fault_Tolerance.md** — Replication, failover, multi-region

How to keep systems running when components fail:
- Measuring availability (99.9% vs 99.99%)
- Replication (copies of data)
- Failover (switching to replica on failure)
- Multi-region deployment
- Active-active vs active-passive
- Health checks

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
