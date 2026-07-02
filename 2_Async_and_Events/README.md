---
title: "Async and Events: Asynchronous Processing and Messaging"
part: 3
part_title: "Async and Events"
type: "part_intro"
summary: "This section covers how to handle work asynchronously, decouple services and process events at scale."
---
# Async and Events: Asynchronous Processing and Messaging

This section covers how to handle work asynchronously, decouple services and process events at scale.

## Chapters

**Core Messaging Patterns**

- Why messaging exists (decoupling producers and consumers)
- Message queue concepts and buffers
- Three patterns: request-reply, publish-subscribe, event streaming

**Message Semantics and Failure Modes**

- Delivery guarantees (at-most-once, at-least-once, exactly-once)
- Ordering constraints and idempotency
- Fanout pattern details
- Common messaging mistakes (losing messages, duplicate handling, backpressure)

**Event Streaming (Kafka)**

- What Kafka is (distributed event log)
- Core concepts (topics, partitions, consumer groups)
- Why Kafka exists (multiple independent consumers, replay capability)
- Internal mechanisms and partition replication
- Kafka design choices (partitions, consumer groups, replication, retention)
- When Kafka is necessary and common mistakes to avoid

**Distributed Coordination**

- Why transactions across independent systems fail at scale
- Two-Phase Commit (2PC) design and why it fails in distributed networks
- Why 2PC works for databases but not services

**Saga Pattern Overview**

- Shorter introduction to Saga patterns, orchestration, choreography and compensating actions

**Saga Pattern Details and Mistakes**

- Choreography vs Orchestration details
- Saga trade-offs vs 2PC
- Eventual consistency boundaries
- Compensation logic challenges (partial updates, non-reversible operations)
- Common saga mistakes and investigation strategy

## How these connect

1. **Messaging patterns** & **Message semantics and mistakes** explain conceptual problems messaging solves and delivery semantics.
2. **Kafka** shows how Kafka implements event streaming at scale.
3. **Distributed transactions** & **Saga pattern deep dive** explain how to coordinate work across independent systems safely.

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

