---
title: "Message Semantics and Common Mistakes"
part: 3
part_title: "Async and Events"
chapter: 2
summary: "Covers messaging semantics (delivery guarantees, message ordering), the fanout pattern and common..."
---
# Message Semantics and Common Mistakes

Covers messaging semantics (delivery guarantees, message ordering), the fanout pattern and common messaging mistakes in production.

## Message semantics

### Delivery guarantees

**At most once**

- Message may not be delivered
- If delivered, only once
- Fastest but messages can be lost

```
Producer sends message
Queue sends to consumer
Network fails, ACK lost
Consumer processed, producer thinks not delivered
No retry, message lost
```

**At least once**

- Message guaranteed delivered
- May be delivered multiple times
- Slower but no loss (except idempotency issues)

```
Producer sends message
Queue sends to consumer
Consumer processes
If no ACK received, retry
May deliver twice
Requires idempotent processing
```

**Exactly once**

- Message guaranteed delivered exactly once
- Hardest to implement
- Usually at least once with idempotency
```
Producer sends message with unique ID
Queue sends to consumer
Consumer checks if already processed (by ID)
If already processed, skip
If not, process and store ID
Future redelivery: skip (already has ID)
```

**Trade-off:**

- At most once: fast, may lose
- At least once: slower, requires idempotency
- Exactly once: complexity, usually at least once + idempotency

Most systems use at least once with idempotent processing.

## Message ordering

### Ordered messages (within partition)

```
Producer sends:
  Message 1: update user name
  Message 2: send confirmation email

Consumer receives in order:
  Message 1: update name (succeeds)
  Message 2: send email (email includes new name)
```

Without ordering:
```
Consumer receives:
  Message 2: send email (email includes old name, name not updated yet)
  Message 1: update name (now happens)

Email has wrong name.
```

**How to guarantee:**

- Single consumer per message type (not parallel)
- Messages keyed by entity (all entity's messages to same partition)

**Kafka example:**
```
Topic: UserEvents

Partition 1: user 1-10000 messages
Partition 2: user 10001-20000 messages
Partition 3: user 20001-30000 messages

All user 5's messages go to Partition 1 (same key).
Partition 1 processes sequentially (maintains order).
```

**Trade-off:**

- Ordered: sequential processing, cannot parallelize
- Unordered: parallel processing, no order guarantee

Choose ordered only if order is required.

## Fanout pattern

One event triggers multiple actions.

```
OrderCreated event
  |
  +---> Inventory: decrease stock
  +---> Billing: charge customer
  +---> Notifications: send confirmation
  +---> Analytics: increment order count
```

**Without fanout (synchronous):**

```
Service A:

  1. Create order
  2. Call Inventory, wait for response
  3. Call Billing, wait for response
  4. Call Notifications, wait for response
  5. Call Analytics, wait for response
  6. Return to user

If any service slow, user waits.
If any service fails, order fails.
Cascading failures.
```

**With fanout (event-driven):**

```
Service A:

  1. Create order
  2. Publish OrderCreated event
  3. Return to user (immediately)

Services listen:
  Inventory: receives event, decreases stock
  Billing: receives event, charges customer
  Notifications: receives event, sends confirmation
  Analytics: receives event, increments count

Parallel processing, user doesn't wait.
```

**Advantages:**

- Loose coupling (services don't call each other)
- Parallel execution
- Scalable (add more subscribers easily)

**Challenges:**

- Eventual consistency (services see change at different times)
- No strong guarantee all actions complete
- More complex debugging (spread across multiple services)

## Common messaging mistakes

### 1. Message loss without acknowledgment

**Mistake:** delete message before processing

```
Consumer receives message
Consumer deletes message from queue
Consumer tries to process
Consumer crashes
Message lost (already deleted)
```

**Better:** delete only after successful processing.

### 2. Not handling duplicates

**Mistake:** process same message twice

```
Message sent to consumer
Consumer processes: update counter
Consumer crashes before ACKing
Message redelivered
Consumer processes again: update counter AGAIN

Counter incremented twice.
```

**Better:** make processing idempotent or track which messages processed.

### 3. No timeout on message processing

**Mistake:** message stuck forever

```
Message received by consumer
Consumer processing starts
Consumer deadlocks or hangs
Message never ACK'd
Queue doesn't know
No retry
Dead message

Meanwhile, new messages pile up.
Queue fills.
Producer can't send.
System stuck.
```

**Better:** set timeout, dead-letter queue for stuck messages.

### 4. No backpressure handling

**Mistake:** too many messages too fast

```
Producer sends 1,000 messages/sec
Consumer processes 100 messages/sec
Queue backlog grows
Memory exhausted
System crashes
```

**Better:** bound queue size, backpressure on producer, or add consumers.

### 5. Fanout without idempotency

**Mistake:** multiple consumers process same event, not idempotent

```
OrderCreated event published

Consumer 1 (Inventory): decrease stock (first time: OK, 100->99)
Consumer 2 (Billing): charge customer
Consumer 1 (Inventory): retry after crash (second time: 99->98)

But event should only decrease once.
Inventory off by one.
```

**Better:** make all consumers idempotent or use exactly-once semantics.

## Investigation: diagnosing messaging issues

**Symptom: Messages not being processed**

Check:

1. Is queue receiving messages? (produce test message)
2. Is consumer running? (check process)
3. Is consumer stuck? (check logs for errors)
4. Is consumer crashing on startup? (check logs)

**Symptom: Duplicate processing**

Check:

1. Are messages being delivered twice? (check event logs)
2. Is processing idempotent? (can retry safely?)
3. Are consumers acknowledging properly? (check ACK logs)

**Symptom: Queue is full, producer blocked**

Check:

1. Are consumers processing? (check throughput)
2. Is consumer slow? (check latency)
3. Are messages stuck? (check dead-letter queue)
4. Do you need more consumers? (increase parallelism)

**Symptom: Messages arriving out of order**

Check:

1. Are you requiring order? (need to?)
2. Are messages partitioned correctly? (same entity key?)
3. Are multiple consumers reading same partition? (violation of order)

## Trade-offs summary

| Pattern | Coupling | Latency | Complexity | Ordering |
|---------|----------|---------|------------|----------|
| Request-reply | Tight | Low | Low | N/A |
| Pub/Sub | Loose | Moderate | Medium | No |
| Event streaming | Loose | Moderate | High | Yes |

## Questions to think about

- Why is ordering hard in messaging?
- If a message is processed twice, when is that a problem?
- What's the difference between at-most-once and at-least-once?
- Why would you use request-reply instead of just calling a service synchronously?
- How do you know if a consumer is stuck processing a message?
- What happens if you have more consumers than partitions?
- Why is fanout powerful for loosely coupled systems?
- If a consumer crashes during processing, what should happen to the message?
- How would you debug a message that never gets processed?
- At what scale does asynchronous messaging become necessary?

## Summary

Messaging is fundamental to scaling systems. It decouples producers and consumers, enabling parallel processing and independent scaling.

Three patterns serve different needs:

- Request-reply: when you need a response
- Pub/Sub: when you want fanout to multiple consumers
- Event streaming: when you need durability and replay

The cost is eventual consistency and complexity (handling duplicates, out-of-order, stuck messages).
The benefit is scalability and loose coupling.
The best engineers understand these patterns deeply and choose based on requirements, not trends.
