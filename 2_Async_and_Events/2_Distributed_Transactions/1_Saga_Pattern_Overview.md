---
title: "Saga Design Pattern"
part: 3
part_title: "Async and Events"
chapter: 10
summary: "The Saga pattern is a way to manage a distributed transaction when multiple services must complete work together,..."
---
# Saga Design Pattern

The Saga pattern is a way to manage a distributed transaction when multiple services must complete work together, but you do not want to rely on a single global transaction.

A distributed transaction is a logical operation that needs to span multiple independent databases or services, where all the steps must either succeed together or be cleaned up when something goes wrong.

## Why it exists

In a monolithic application, one database transaction can roll back everything if something fails. In a distributed system, each service often has its own database. A failure in one service can leave other services already updated.

A saga solves this by breaking the work into small steps and adding compensating actions.

## Simple definition

A saga is a sequence of local transactions.

Each step:

- performs its own work
- publishes an event or sends a message
- triggers the next step

If a later step fails, the saga executes compensating actions to undo the earlier steps.

## Example

Imagine an e-commerce order flow:

1. Create order
2. Charge payment
3. Reserve inventory
4. Ship order

If payment succeeds but inventory reservation fails, the saga must undo the payment and cancel the order.

## Core idea

Instead of "all or nothing", a saga follows "do as much as possible, then compensate what was already done".

This makes the system more resilient in distributed environments.

## Distributed transactions and 2-phase commit

Before Saga, many systems tried to use two-phase commit for distributed transactions.

In two-phase commit, there is a new component called a coordinator. The coordinator makes sure that all the participants in a transaction agree on the outcome before any of them make their changes permanent.

The problem is that two-phase commit is difficult to scale and can become a bottleneck. It also assumes strong coordination and availability, which is hard in large distributed systems.

This is one reason why Saga became popular: it avoids the rigidity of a global transaction manager and uses local transactions plus compensation instead.

## Types of saga

### 1. Choreography-based saga

Each service reacts to events and decides what to do next.

Flow:

- Service A completes work
- Service A publishes an event
- Service B listens and performs its step
- If something fails, the services publish failure events and trigger compensations

Pros:

- simple when the flow is straightforward
- low central coordination

Cons:

- harder to trace and debug as the flow grows
- logic becomes spread across services

### 2. Orchestration-based saga

A dedicated orchestrator controls the workflow.

Flow:

- Orchestrator tells Service A to start
- Orchestrator waits for result
- Orchestrator tells Service B to continue
- If a step fails, the orchestrator runs compensating actions

This is how saga orchestration works: the orchestrator acts like a workflow manager that knows the current state of the business process and decides what should happen next.

Pros:

- easier to monitor and control
- central place for business workflow logic

Cons:

- introduces an extra component
- orchestrator becomes a critical part of the system

## Compensating actions

A compensating action is the reverse of a completed step.

Examples:

- refund payment
- release reserved inventory
- cancel an order
- delete a created record

Compensation must be designed carefully. Some actions may not be fully reversible.

## When to use saga

Use saga when:

- multiple services must coordinate
- each service has its own database
- strong distributed transactions are too expensive or not available
- you want better fault tolerance and service independence

## When not to use saga

Avoid saga when:

- the workflow is simple and can stay in one service
- atomicity is required and the business can accept a single transaction boundary
- compensation logic is too complex or impossible to model safely

## Benefits

- avoids a single global transaction
- improves service independence
- improves resilience for partial failures
- supports long-running business workflows

## Drawbacks

- more complex than a local transaction
- compensation logic can be difficult
- debugging and monitoring are harder
- eventual consistency is common

## Important design concerns

### 1. Idempotency

A step may be retried after a timeout or network issue. The service should be able to safely process the same request more than once.

### 2. Retry policies

Retries help with transient failures, but they should be controlled to avoid duplicate effects.

### 3. Timeouts and deadlines

Long-running workflows need clear timeout rules and recovery behavior.

### 4. Monitoring

You need visibility into which step failed and which compensation already ran.

### 5. Transactional outbox

A transactional outbox is a pattern used to make sure that a business action and the event that announces it are stored safely together. This helps avoid losing events when a database transaction commits but the message send fails.

### 6. Idempotent operations

Idempotent operations are operations that can be retried many times without causing duplicate effects. This is very important in saga systems because retries are common. A good example is refunding a payment: even if the operation is retried multiple times, the user should receive only one refund.

### 7. Consistency model

Saga-based systems usually use eventual consistency. That means the system may be temporarily inconsistent while compensation or retries occur.

## Summary

The Saga pattern is a practical approach for handling distributed business workflows without a single global transaction. It trades strong consistency for resilience, flexibility and service independence.

In short:

- break the workflow into local transactions
- publish events or trigger the next step
- use compensating actions on failure
- accept eventual consistency when needed
