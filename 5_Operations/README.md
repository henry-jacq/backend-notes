# Operations: Running and Debugging Production Systems

This section covers how to operate backend systems in production: monitoring, debugging, incident response.

## Learning path

### Observability and Debugging

**0_Observability_and_Debugging.md** — Metrics, logs, traces

How to understand what's happening in production:
- Why observability matters (systems fail in unpredictable ways)
- Three pillars of observability (metrics, logs, traces)
- Building debugging intuition
- Common failure patterns
- Systematic debugging strategy
- Key metrics for different components

This document teaches you how to debug production issues systematically instead of guessing randomly.

## Key concepts

- Metrics (quantitative measurements over time)
- Logs (discrete events)
- Traces (request path through system)
- Alerting strategy
- SLO (service level objectives)
- Debugging methodology
- Root cause analysis

## Common failure patterns you'll learn

1. **Database is slow** — metrics show database CPU high, disk I/O high
2. **Memory leak or growth** — metrics show memory increasing over time
3. **Request timeout** — latency p99 increased, thread count high
4. **Error rate spike** — specific error types increased
5. **Cascading failure** — one service failure triggers others

## Connection to other sections

**Operations + Data Storage:**
- Database query monitoring
- Slow query logs
- Replication lag alerts

**Operations + Async and Events:**
- Consumer lag monitoring (how far behind consumer is)
- Message queue depth
- Dead-letter queue alerts

**Operations + Reliability:**
- Circuit breaker state monitoring
- Retry rate monitoring
- Failover verification

**Operations + Infrastructure:**
- Server metrics (CPU, memory, disk)
- Network metrics (latency, bandwidth)
- Connection pool exhaustion

## Practical skills

After this section, you'll know how to:
- Identify where a problem actually is (not guess)
- Correlate metrics to understand cause
- Debug systematically
- Set up alerts that matter
- Respond to production issues
- Verify fixes work

## Debugging methodology

1. **Define the problem precisely** (not "it's slow", but "p99 latency 500ms")
2. **Check metrics** (what changed? CPU? Memory? Disk?)
3. **Check logs** (error messages? Stack traces?)
4. **Check traces** (which component took time?)
5. **Investigate root cause** (why did component slow down?)
6. **Verify fix** (does problem go away?)

This is the systematic approach that separates senior engineers from junior ones.

## Next: Advanced topics

After mastering operations monitoring:
- **Capacity planning** — forecasting growth, resource planning
- **Incident response** — handling production emergencies
- **Security** — protecting systems from attacks
- **Cost optimization** — efficiency at scale

These are advanced topics built on top of everything you've learned so far.
