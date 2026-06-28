# Kafka: Why It Exists

This document explains Kafka not as a technology to learn, but as a solution to specific breaking points that other messaging systems cannot handle.

## The messaging problem that kafka solves

Before Kafka, messaging systems existed (RabbitMQ, ActiveMQ, JMS). They worked fine for moderate volumes.

But at scale (thousands to millions of messages per second), they failed for one reason: they were not designed to store data permanently on disk.

Traditional messaging systems:
- Delivered messages from producer to consumer
- Deleted messages after delivery
- Stored messages in RAM
- Lost messages if the broker crashed

This works for notification systems and lightweight event distribution. It breaks when:
- You need to replay events (a consumer crashed, came back online, wants old messages)
- You want to audit what happened (keep all messages forever)
- Multiple consumers need to process the same stream independently
- A consumer is temporarily down (messages accumulate while waiting for consumer to come back)
- You need to scale to millions of events per second

## Why existing systems broke at scale

### RabbitMQ and similar brokers

**Design:** messages queued in RAM, persisted to disk, then deleted after delivery

**What worked:**
- Simple pub/sub model
- Fair distribution across consumers
- Low latency
- Small to moderate message volumes

**Symptoms of breaking:**
- Broker crash = message loss (despite persistence, some messages in flight)
- Broker becomes a bottleneck (all messages flow through one server)
- Scaling horizontally is hard (each broker is independent, message routing complex)
- Consumer replay is not built in (consumer doesn't remember position, has to ask broker for old messages which may be deleted)
- High memory usage (broker holds messages in queue)

**Why it breaks:**
RabbitMQ is optimized for message delivery, not message storage. It deletes messages after delivery. At high volumes, this creates bottlenecks.

### Traditional databases as message storage

**Design:** store events as rows in a table, consumer queries periodically

**What worked:**
- Permanent storage
- ACID guarantees
- Complex queries on events
- Multiple consumers reading same data

**Symptoms of breaking:**
- Query performance degrades (millions of rows, scanning slow)
- Writes become contention point (all writers hit same table)
- Consumer state management is complex (consumer must track last read offset in separate table)
- Tail latency high (queries on large tables are slow)
- Network overhead high (every event transmitted from database to consumer)

**Why it breaks:**
Databases are not optimized for streaming append-only workloads. Indexing, locking, and query optimization create overhead.

## Kafka's design decision: immutable log

Kafka chose a different model:

**Design:** events are immutable, stored in an append-only log on disk, never deleted (until retention expires), multiple consumers each track their position

```
Partition = append-only log on disk

Producer appends events:
Event 1 [offset 0]
Event 2 [offset 1]
Event 3 [offset 2]
...
Event N [offset N-1]

Consumer 1 reads: offsets 0-5
Consumer 2 reads: offsets 0-10
Consumer 3 reads: starting from offset 7

All read the same log independently.
```

**Why this matters:**

- Events are never deleted (until retention policy expires)
- Multiple consumers can read the same events independently
- Consumers track their position (offset)
- Append-only write pattern is optimized (sequential disk I/O, not random)
- No in-memory queuing, no message loss
- Horizontal scaling by splitting into partitions (each partition on different broker)

## When Kafka becomes necessary

Kafka was built at LinkedIn to handle their event pipeline: thousands of events per second from production systems, multiple downstream consumers (analytics, real-time updates, auditing), events needed to be replayed if consumers crashed.

**Symptoms that Kafka is needed:**

1. **Multiple consumers, same event stream**
   - Analytics team wants events for reporting
   - Real-time team wants events for dashboards
   - Auditing team wants events for compliance
   - Each consumer processes at different rates
   - RabbitMQ struggles with fan-out at scale

2. **Consumer replay capability**
   - A consumer crashes for 2 hours
   - Comes back online, needs to process missed events
   - Without Kafka, those events may already be deleted
   - With Kafka, consumer seeks to last offset, replays

3. **High volume streaming**
   - Millions of events per second
   - RabbitMQ brokers become saturated
   - Kafka partitions scale horizontally (partition 1 on broker 1, partition 2 on broker 2)

4. **Append-only audit trail**
   - Events must be kept forever (compliance)
   - Traditional queues delete after delivery
   - Kafka retention policies keep for days/weeks/months/forever

5. **Decoupling producers from consumers**
   - Producer writes events, doesn't care about consumers
   - Consumers can be added later without changing producer
   - RabbitMQ requires routing rules

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

**Mistake:** consumer processes events one at a time, serialized

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
