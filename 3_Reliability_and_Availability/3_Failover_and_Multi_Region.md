# Failover and Multi-Region Deployment

This document covers database failover handling, split-brain mitigation, multi-region deployments, active-passive vs active-active patterns, and availability monitoring.

## Failover: handling master failure

When master fails, a replica must become the new master.

**Automatic failover:**

```
Master fails
  |
Monitoring detects failure (no heartbeat)
  |
Trigger failover
  |
Select replica to promote
  |
Promote replica to master
  |
Update client routing (point to new master)
  |
Clients now write to new master
```

**Challenges:**

1. **Split-brain problem**

```
Master and replicas network partitioned.
Master thinks replicas are down.
Replicas think master is down.
Replicas elect new master.

Now two masters:
  - Old master: accepting writes
  - New master: accepting writes

Both diverge. Data inconsistency.
```

**Solution:** quorum-based decision (majority votes on new master).

2. **Replica lag during failover**

```
Master fails.
Replica has 95% of data (replicated).
Last 5% never replicated.
Promote replica to master.
5% of data lost.
```

**Solution:** synchronous replication on critical data (trade performance for safety).

3. **Manual vs automatic failover**

**Manual:** safer (human verifies state) but slow (hours down).
**Automatic:** faster (seconds) but risk of mistakes.

Most systems use automatic with human oversight (alerts, dashboards).

## Multi-region deployment

Replicate across geographical regions for disaster recovery.

**Single region:**
```
Region US-East
  - Master
  - Replicas
  
Disaster (fire, power outage):
  Entire region down
  All services down
  Manual recovery (hours)
```

**Multi-region:**
```
Region US-East
  - Master
  - Replicas

Region US-West
  - Master (replica of US-East)
  - Replicas

Disaster in US-East:
  Switch to US-West
  Recovery time: minutes
```

**Challenges of multi-region:**

1. **Replication latency**

```
Write in US-East: 1ms
Replicate to US-West: 100ms

US-East client reads: gets latest data (1ms)
US-West client reads: gets 100ms-old data

If US-East fails, US-West is 100ms behind.
```

2. **Network partitioning between regions**

```
US-East and US-West cannot communicate.
Both think other is down.
Both elect master.
Split-brain: data divergence.
```

3. **Consistency across regions**

```
Write in US-East: account balance -> $100
Write propagates to US-West (100ms later)

Between write and propagation:
  US-East sees $100
  US-West sees $90

Transfer between regions: inconsistent.
```

## Availability strategies

### 1. Active-active

Both master and replica accept writes.

```
Master 1 (US-East): accepts writes
Master 2 (US-West): accepts writes

Both replicate to each other (bidirectional).
```

**Pros:** no single point of failure, survivable disaster
**Cons:** conflict resolution required (both masters modify same data)

### 2. Active-passive

Only master accepts writes. Replica is backup.

```
Master (US-East): accepts writes, replicates to replica
Replica (US-West): passive, read-only

Master fails:
  Replica promoted to master
```

**Pros:** no conflicts, simpler
**Cons:** passive replica wasted (only reads during normal operation)

### 3. Read replicas (no failover)

Replicas are for read scaling only. Master failure = outage.

```
Master: handles writes
Replicas 1-N: handle reads

Read distribution improves scale but doesn't improve availability.
```

**Use when:** read volume is huge, write volume is moderate, some downtime acceptable.

## Fault tolerance patterns

### 1. Health checks

Periodically verify service is alive.

```
Load balancer:
  Every 10 seconds:
    Send request to service
    Expect healthy response
    If failed response or timeout:
      Remove service from rotation
      Stop sending requests
```

**Challenges:**
- False positives (service appears down but is working)
- Timeout tuning (too short = false positives, too long = delayed detection)

### 2. Graceful degradation

When component fails, continue with reduced capacity.

```
Database 1: primary
Database 2: backup

If Database 1 fails:
  System continues using Database 2
  Performance may degrade
  But still available
```

### 3. Bulkheads (covered in Reliability Patterns)

Isolate failures so they don't spread.

### 4. Timeouts

Stop waiting for slow/dead services.

```
Call Service B with 5-second timeout.
After 5 seconds, give up.
Return error or fallback.

Without timeout:
  Wait indefinitely (service never responds)
  Thread blocked forever
  Resource exhausted
```

## Common fault tolerance mistakes

### 1. Asymmetric failover

**Mistake:** replicas lag so much behind master that promoting fails

**Example:**
```
Master writes data hourly
Replica replicates asynchronously
Lag reaches 1 hour

Master fails
Promote replica (has 1-hour-old data)
Last hour's data lost
```

**Better:** monitor replica lag, alert if too high, use synchronous replication for critical data.

### 2. No health checks

**Mistake:** load balancer sends requests to failed service

**Result:**
- Some requests fail immediately
- Some requests timeout
- User experience poor

**Better:** health checks detect failures immediately.

### 3. Uneven load distribution during failover

**Mistake:** one replica promoted to handle all traffic

**Example:**
```
Master fails
Replica promoted to master
All traffic now to replica (was handling 20%, now 100%)
Replica becomes bottleneck
System slow despite replica available
```

**Better:** distribute failover load, gradually add capacity.

### 4. No manual override options

**Mistake:** automatic failover but no way to revert or adjust

**Result:**
- Failover happens but is wrong (wrong replica promoted)
- No manual override
- System remains in wrong state

**Better:** always provide manual failover capability.

### 5. Not testing failover

**Mistake:** never actually test failover

**Result:**
- Failover breaks when needed
- Data loss during recovery
- Manual recovery required (hours)

**Better:** test failover regularly (monthly), verify data integrity.

## Investigation: diagnosing availability issues

**Symptom: Intermittent unavailability**

Check:
1. Is master healthy? (CPU, memory, disk)
2. Is replication lagging? (replica lag high?)
3. Are replicas healthy? (can they be promoted?)
4. Is there a network partition? (can services communicate?)

**Symptom: Data inconsistency after failover**

Check:
1. Was replica fully replicated? (lag before failover?)
2. Did master have unacknowledged writes? (async replication?)
3. Was data intentionally not replicated? (acknowledged)

**Symptom: Slow recovery after failover**

Check:
1. Is new master slow? (capacity issue?)
2. How much traffic are you sending? (overloaded after failover?)
3. Are clients retrying aggressively? (retry storm?)

## Trade-offs summary

| Approach | Availability | Consistency | Complexity |
|----------|--------------|-------------|-----------|
| Single server | Low (50%) | Strong | Low |
| Replication | High (99.9%) | Eventual | Medium |
| Multi-region | Very high (99.99%+) | Eventual | High |
| Synchronous | High | Strong | Medium |
| Asynchronous | High | Eventual | Low |

## Questions to think about

- Why is 99.9% availability so much harder than 99?
- If a replica lags 10 seconds, what happens if master fails?
- Why is split-brain dangerous?
- How often should you test failover?
- What's the difference between availability and reliability?
- If you have three replicas, which should be promoted on master failure?
- Why is multi-region replication slower than single-region?
- What happens if half your servers are in US-East and half in US-West and network between them fails?
- Is it better to failover quickly and risk wrong replica or failover slowly and be sure?
- At what replication lag do you alert?

## Summary

Availability requires redundancy. A single server cannot be always available.

Replication copies data. Failover switches to replica when master fails.
Multi-region deployment protects against regional disasters.

The cost is complexity (managing multiple servers, handling consistency), operational overhead (monitoring, testing), and eventual consistency during failures.
The best systems balance availability needs with operational reality. Most don't need five nines. Three nines is hard enough.
