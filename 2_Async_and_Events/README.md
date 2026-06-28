# Async and Events: Asynchronous Processing and Messaging

This section covers how to handle work asynchronously, decouple services, and process events at scale.

## Learning path

### 0_Messaging/

**0_Messaging_Patterns.md** — Request-reply, Pub/Sub, Event Streaming
- Why messaging exists (decoupling producers and consumers)
- Message queue concept (buffer between producer and consumer)
- Three patterns: request-reply, publish-subscribe, event streaming
- Delivery semantics (at-most-once, at-least-once, exactly-once)
- Ordering and idempotency
- Common mistakes (losing messages, duplicates, backpressure)

Start here to understand what messaging solves conceptually.

### 1_Event_Streaming/Kafka/

**0_INTRO.md** through **4_SYSTEMS_PERSPECTIVE.md**

Kafka is the implementation of event streaming at scale:
- What Kafka is (distributed event log)
- Core concepts (topics, partitions, consumer groups)
- Why Kafka exists (multiple independent consumers, replay capability)
- When Kafka is necessary
- How to investigate Kafka issues

This progression shows:
- What problem messaging solves (abstract)
- How Kafka solves it specifically (concrete)
- Why Kafka is different from simple message queues

### 2_Distributed_Transactions/

**0_Distributed_Transactions.md** — Why coordinating across services is hard

Why transactions across independent systems are fundamentally different from database transactions:
- Why 2PC (two-phase commit) fails at scale
- Saga pattern (distributed transactions with eventual consistency)
- Choreography vs Orchestration
- Compensation logic (reverting failed operations)

**1_Saga_Pattern.md** — The practical pattern for distributed work

Detailed exploration of Saga pattern:
- How Saga works
- When to use Saga vs 2PC
- Common mistakes (not idempotent, stuck compensations)

## How these connect

1. **Messaging_Patterns** explains conceptual problems messaging solves
2. **Kafka** shows how Kafka solves those problems at scale
3. **Distributed_Transactions** explains why coordinating work across systems is hard

Understanding all three teaches you:
- When to use async/events (reduce database writes)
- How to implement (message queues, Kafka)
- How to coordinate (Saga pattern)

## Key concepts

- Producer/consumer decoupling
- Message ordering (when does it matter?)
- Idempotency (safe to retry)
- Fanout (one event triggers multiple actions)
- At-least-once semantics
- Consumer groups (multiple consumers, same topic)
- Partitioning (throughput scaling)
- Event replay (recover state from history)
- Eventual consistency (accept temporary inconsistency)

## When to use messaging

**Request-reply:**
- When you need immediate response
- Synchronous workflows

**Pub/Sub:**
- Multiple consumers of same event
- Loose coupling needed
- Fanout (one event, many actions)

**Event Streaming (Kafka):**
- Audit trail needed (immutable history)
- Consumer independence (start consuming at any time)
- Very high volume (millions of events)
- Replay needed (reprocess historical events)

## Common mistakes to avoid

- Message loss (not acknowledging properly)
- Duplicates (not handling idempotency)
- Out-of-order processing (when order matters)
- Backpressure not handled (queue fills, system crashes)
- Cross-service transactions that aren't idempotent

## Connection to Data Storage

Messaging typically works alongside databases:
- Producer writes to database, then publishes event
- Consumer receives event, writes to own database
- Multiple independent systems, each with own data

This creates the challenge: ensure write to database and publish to queue are coordinated (both succeed or both fail).

## Next sections

After async and events:
- **Reliability** — handle failures in message processing
- **Infrastructure** — servers that run these systems
- **Operations** — monitor and debug async systems
