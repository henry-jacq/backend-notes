---
title: "Messaging Patterns"
part: 3
part_title: "Async and Events"
chapter: 1
summary: "This document explains how asynchronous communication between services works. Messaging is not a technology..."
---
# Messaging Patterns

This document explains how asynchronous communication between services works. Messaging is not a technology choice—it is a fundamental architectural pattern for handling concurrent work.

## Why messaging exists

Synchronous communication (request-response) becomes a bottleneck at scale.

**Synchronous request-response:**

```
Client sends request
  |
  Service processes
  | (client waits)
  Service sends response
  |
  Client receives response
```

**Problem:** client must wait. If service is slow, client waits.

At scale:
- Many clients waiting
- Thread pool exhausted
- Resource exhaustion
- Cascading timeouts

**Asynchronous messaging:**

```
Client sends message
  |
  Queue stores message
  |
  Client continues immediately
  |
  Service processes at own pace
  |
  Service sends response message
  |
  Client receives response later (polling or callback)
```

**Benefit:** client doesn't wait. Work is decoupled.

## Message queue concept

A message queue is a buffer between producer and consumer.

```
Producer (client)
  |
  Message Queue (buffer)
  |
  Consumer (service)
```

**How it works:**

```
1. Producer sends message: "process order #123"
2. Queue stores message
3. Producer returns immediately
4. Consumer retrieves message when ready
5. Consumer processes order
6. Consumer acknowledges message (now removed from queue)
```

**Benefits:**
- Producer and consumer not synchronized
- Consumers can process at their own pace
- Multiple consumers can process same message type
- Messages persist (if queue crashes, messages not lost)

## Three messaging patterns

### 1. Request-reply

Consumer processes and sends response.

```
Producer sends message: "calculate total for order #123"
  |
  Consumer processes
  |
  Consumer sends reply message: "total is $99.99"
  |
  Producer receives reply
```

**Use cases:**
- Remote procedure calls
- RPC-like communication
- Producer needs result

**Challenges:**
- Still waiting for response (partially asynchronous)
- Requires correlation ID (to match request and reply)
- Reply queue must exist

### 2. Publish-subscribe

Producer broadcasts message. Multiple consumers receive.

```
Producer publishes: "OrderCreated"
  |
  +---> Consumer 1 (Inventory)
  +---> Consumer 2 (Billing)
  +---> Consumer 3 (Notifications)

All three receive same event.
```

**Use cases:**
- Event notifications
- Real-time updates
- Fanout (one event triggers multiple actions)

**Characteristics:**
- Multiple independent consumers
- Each consumer processes event independently
- Consumers process at own pace
- New consumers can subscribe later

**Challenge:** message retention

```
Producer publishes event
Consumer 3 doesn't exist yet (service down)
Event is published
30 minutes later, Consumer 3 comes back

Does it receive the event?

Pub/Sub (Redis): No (event lost)
Event streaming (Kafka): Yes (event retained)
```

### 3. Event streaming

Durable event log. Consumers replay history.

```
Producer publishes:
  Event 1: "OrderCreated"
  Event 2: "OrderCanceled"
  Event 3: "OrderShipped"

Consumer 1 starts: gets all three events
Consumer 2 starts now: can replay from beginning
Consumer 3 was processing but restarted: resumes from checkpoint
```

**Use cases:**
- Event sourcing (rebuilding state from events)
- Replay capability (reprocess events)
- Audit trail (immutable record)
- Multiple independent consumers

**Characteristics:**
- Events are immutable
- Events stored durably
- Consumers maintain offset (how far they've processed)
- Can replay from any point

To learn about delivery guarantees (at-least-once, exactly-once), message ordering, and common messaging mistakes, see [1_Message_Semantics_and_Mistakes.md](file:///d:/Playground/Backend%20Notes/2_Async_and_Events/0_Messaging/1_Message_Semantics_and_Mistakes.md).
