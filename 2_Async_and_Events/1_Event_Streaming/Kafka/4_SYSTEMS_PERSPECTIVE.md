---
title: "Kafka: Why It Exists"
part: 3
part_title: "Async and Events"
chapter: 7
summary: "This document explains Kafka not as a technology to learn, but as a solution to specific breaking points that other..."
---
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
RabbitMQ is optimised for message delivery, not message storage. It deletes messages after delivery. At high volumes, this creates bottlenecks.

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
Databases are not optimised for streaming append-only workloads. Indexing, locking, and query optimisation create overhead.

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
- Append-only write pattern is optimised (sequential disk I/O, not random)
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

To learn about Kafka design details (partitions, consumer groups, replication, retention) and common setup mistakes, see [5_KAFKA_DESIGN_AND_MISTAKES.md](file:///d:/Playground/Backend%20Notes/2_Async_and_Events/1_Event_Streaming/Kafka/5_KAFKA_DESIGN_AND_MISTAKES.md).
