---
title: "Kafka: Design Choices and Common Mistakes"
part: 3
part_title: "Async and Events"
chapter: 8
summary: "Covers Kafka's breaking points, partitions, consumer groups, replica dynamics and common mistakes in..."
---
# Kafka: Design Choices and Common Mistakes

Covers Kafka's breaking points, partitions, consumer groups, replica dynamics and common mistakes in event-driven systems.

## Breaking points: why Kafka design choices exist

### Partitions: why data is split

**Problem:** single server has throughput limit (disk I/O speed, CPU)

**Solution:** split topic into multiple partitions, each on different server

```
Topic: Orders (1 million events/sec)

Partition 0 (Server 1): events with key hash 0-33%
Partition 1 (Server 2): events with key hash 33-66%
Partition 2 (Server 3): events with key hash 66-100%

Each server handles 333k events/sec
```

**Breaking without partitions:**

- Single broker disk I/O saturated
- Response time increases
- Bottleneck is not solvable by adding brokers (one broker handles all)

**How partitions help:**

- Multiple brokers distribute load
- Each partition is independent (can be consumed independently)
- Ordering guaranteed within partition (all orders from user 1 in same partition, processed in order)

### Consumer groups: why parallel consumption

**Problem:** single consumer cannot keep up with event rate

**Solution:** consumer group, multiple consumers, each reads different partitions

```
Topic has 3 partitions
Consumer Group A:
  Consumer 1 reads partition 0
  Consumer 2 reads partition 1
  Consumer 3 reads partition 2

Each consumer processes independently.
Coordinated by consumer group coordinator.
```

**Breaking without consumer groups:**

- One consumer tries to read 1 million events/sec
- Consumer CPU maxed, cannot process fast enough
- Events accumulate on broker (broker memory fills)
- Broker crashes or becomes unavailable

**How consumer groups help:**

- Multiple consumers split the work
- Each consumer has less data to process
- Linear scaling (add consumer = proportional throughput increase)
- Offset tracking per consumer (different consumers at different positions)

### Replication: why redundancy

**Problem:** single broker holding partition fails, events are lost

**Solution:** replicate partition across multiple brokers

```
Partition 0:
  Leader: Broker 1 (receives writes)
  Follower: Broker 2 (copies data from leader)
  Follower: Broker 3 (copies data from leader)

If Broker 1 crashes, Broker 2 or 3 becomes leader.
Data not lost.
```

**Breaking without replication:**

- Hardware failure = event loss
- Broker planned maintenance = downtime
- Network partition = loss of broker

**How replication helps:**

- Data survives broker failure
- Replication lag is small (followers keep up)
- If leader fails, election happens, follower becomes leader
- Zero event loss (if configured with right acknowledgement policy)

### Retention: why events aren't deleted

**Problem:** traditional systems delete after delivery. Replay is impossible.

**Solution:** keep events on disk indefinitely (or by retention policy)

**Breaking without retention:**

- Consumer crashes, restarts, asks for same events
- Those events already deleted
- Consumer missed them
- No way to recover

**With retention:**

- Events kept for X days or X bytes
- Consumer can seek back and replay
- New consumers can read from beginning
- Auditing is possible

## Investigation: how engineers identify messaging problems

**When traditional messaging breaks, what do you see?**

1. **Message loss during broker failure**
   - Producer sends message
   - Broker crashes before replicating
   - Message gone
   - Check: broker logs, replication factor, durability settings

2. **Consumer cannot keep up**
   - Messages accumulate on broker
   - Broker memory grows
   - Response latency increases
   - Check: consumer lag, queue depth, consumer CPU

3. **High latency for fan-out patterns**
   - One event, many consumers
   - Broker becomes bottleneck
   - Each consumer waits
   - Check: broker CPU, memory, message latency per consumer

4. **No way to replay events**
   - Consumer crashes
   - Events deleted while consumer was down
   - Recovery impossible
   - Check: message retention policy, oldest message timestamp

5. **Broker rebalancing causes message loss**
   - Adding/removing brokers
   - Rebalancing happens
   - Messages lost in flight
   - Check: rebalancing logs, acknowledgement settings

## Trade-offs: Kafka vs alternatives

### Kafka vs RabbitMQ

| Aspect | Kafka | RabbitMQ |
|--------|-------|----------|
| Storage | Disk (permanent) | RAM (temporary) |
| Use case | Event streaming, audit trail | Task queues, notifications |
| Throughput | Very high (millions/sec) | Moderate (thousands/sec) |
| Consumer replay | Built-in | Not built-in |
| Ordering | Per partition | No guarantee |
| Complexity | Higher | Lower |

**Choose RabbitMQ when:**

- Events don't need to be replayed
- Low to moderate volume
- Simple pub/sub is enough

**Choose Kafka when:**

- Need to replay events
- High volume
- Multiple independent consumers

### Kafka vs databases

| Aspect | Kafka | Database |
|--------|-------|----------|
| Write pattern | Append-only | Random write/update |
| Query capability | Offset-based | Complex queries |
| Scale model | Partition by key | Shard by key |
| Consumer state | Consumer tracks offset | App tracks state |

**Choose database when:**

- Complex queries needed
- Random access patterns
- State updates (not just appends)

**Choose Kafka when:**

- Sequential ordering important
- Same event stream, multiple consumers
- Audit trail

### Kafka vs pub/sub (Cloud Pub/Sub, SNS)

| Aspect | Kafka | Pub/Sub |
|--------|-------|---------|
| Persistence | Disk (configurable) | Cloud storage |
| Ordering | Per partition | No guarantee |
| Operational complexity | High (self-hosted) | Low (managed) |
| Cost | Infrastructure | Usage-based |

**Choose managed pub/sub when:**

- Operational overhead unacceptable
- Moderate volume
- Cloud-native architecture

**Choose Kafka when:**

- Precise control needed
- On-premises required
- Very high volume
- Specific ordering requirements

## Common Kafka mistakes

### 1. Too many partitions

**Mistake:** create 100 partitions for a small workload

**Result:**

- Rebalancing slow (coordinator must move 100 partitions)
- Each partition replication overhead
- Consumer group rebalancing causes lag spikes
- Operational complexity high

**Better:** start with 3-5 partitions, increase if actual bottleneck.

### 2. No consumer group

**Mistake:** single consumer reads entire topic

**Result:**

- Consumer becomes bottleneck
- Cannot scale
- If consumer crashes, events pile up

**Better:** consumer group with multiple consumers (one per partition if needed).

### 3. Ignoring offset management

**Mistake:** consumer doesn't track offset, always reads from beginning

**Result:**

- Duplicates processed
- Idempotency not enforced
- Events processed multiple times

**Better:** track offset correctly (in Kafka or external database), ensure idempotency.

### 4. Synchronous processing in consumer

**Mistake:** consumer processes events one at a time, serialised

**Result:**

- Throughput limited by consumer processing speed
- Cannot batch operations

**Better:** batch events, process in parallel, commit offset after batch.

### 5. No monitoring

**Mistake:** no alerts on consumer lag

**Result:**

- Consumer falls behind
- Days pass before anyone notices
- When noticed, huge backlog exists

**Better:** monitor consumer lag, alert if lag > threshold.

## Questions to think about

- If an event stream is only read by one consumer, does Kafka help versus a simple queue?
- Why does Kafka require ordering within a partition but not across partitions?
- What happens to consumer lag if a consumer crashes for 1 hour?
- Why is offset commit important?
- If you have 100 million events per second and 10 consumers, how should you partition?
- What would break if Kafka didn't replicate partitions?
- Why is consumer group coordination necessary?
- What happens if a consumer is very slow (takes 10 seconds per event)?
- If message retention is 7 days but a consumer is offline for 10 days, what happens?
- Would Kafka be useful for a system with 10 events per hour?

## Summary

Kafka exists because traditional messaging systems could not handle:

- High volume (millions of events/second)
- Multiple independent consumers
- Event replay capability
- Permanent audit trail

Kafka's design (partitions, replication, retention, consumer offsets) solves these problems by treating events as an immutable log, not a queue to be deleted after delivery.

Understanding why Kafka chose this design teaches the broader lesson: every architecture decision is a response to a specific breaking point. No technology is universally better. Kafka solves specific problems that other systems cannot.
