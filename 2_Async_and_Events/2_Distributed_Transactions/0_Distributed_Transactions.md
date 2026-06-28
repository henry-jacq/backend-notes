# Distributed Transactions

This document explains why coordinating transactions across independent systems is fundamentally difficult and what trade-offs engineers must make.

## The coordination problem

A distributed transaction is a logical operation that spans multiple independent systems.

**Example: bank transfer**

```
Source account (Service A): decrease balance by $100
Destination account (Service B): increase balance by $100

Both must succeed, or neither.
```

If Service A succeeds but Service B fails:
- Money leaves source account
- Money never arrives at destination
- Money is lost

**Example: e-commerce order**

```
Order Service (Service A): create order
Inventory Service (Service B): decrease stock
Billing Service (Service C): charge payment
Shipping Service (Service D): create shipment
```

If order created but billing fails:
- Order exists without payment
- Inventory decremented without charge
- Customer shipped without paying

The coordination problem: how do you guarantee either all services succeed or all roll back?

## Why local transactions don't work across services

In a single database:

```sql
BEGIN TRANSACTION
  UPDATE accounts SET balance = balance - 100 WHERE id = 1
  UPDATE accounts SET balance = balance + 100 WHERE id = 2
COMMIT
```

If either update fails, the entire transaction rolls back. Both changes succeed or neither.

Across services, this is impossible:

```
Service A: START TRANSACTION
Service A: update balance
Service A: request Service B to update

Service B: Did not start transaction yet
Service B: Update balance
Service B: Commit

Service A: But Service C failed!
Service A: Rollback
Service A: Now inconsistent (A rolled back, B committed)
```

Each service has its own database, its own transaction boundaries. You cannot wrap them in a single database transaction.

## Two-phase commit: the traditional approach

Two-phase commit (2PC) attempts to solve this with a coordinator.

```
Coordinator
  |
  +---> Service A
  +---> Service B
  +---> Service C
```

**Phase 1: Prepare**

Coordinator asks each service: "Can you commit this change?"

```
Coordinator -> Service A: "Can you decrease balance by $100?"
Service A: "Yes, I have locked the balance, it's reserved."

Coordinator -> Service B: "Can you increase balance by $100?"
Service B: "Yes, I have locked the balance, it's reserved."

Coordinator -> Service C: "Can you charge $100?"
Service C: "Yes, payment is authorized."
```

**Phase 2: Commit**

Coordinator tells each service: "Commit now"

```
Coordinator -> Service A: "Commit"
Service A: Commit (balance decreased)

Coordinator -> Service B: "Commit"
Service B: Commit (balance increased)

Coordinator -> Service C: "Commit"
Service C: Commit (payment charged)
```

All committed. Transaction complete.

## Why two-phase commit fails at scale

### 1. Network failures

```
Coordinator -> Service A: "Prepare" (Service A locks resources)
Service A -> Coordinator: "Ready" (message lost)

Coordinator: Did not receive response, assumes failure
Coordinator -> Service A: "Abort"
Service A: Abort (releases locks, rolls back)

Meanwhile, at the same moment:
Service A actually committed before the abort message arrived.
Inconsistency: coordinator thinks rolled back, Service A committed.
```

Network failures can leave coordinator and service in different states.

### 2. Timeout ambiguity

```
Coordinator -> Service B: "Commit"
Network delay or Service B slow processing.
Coordinator waits 30 seconds.
Coordinator times out, assumes Service B failed.
Coordinator -> Service A: "Abort"
Service A: Abort

But Service B is still processing.
Service B eventually commits anyway.
Result: Service A rolled back, Service B committed.
Inconsistency.
```

What happens on timeout is ambiguous. Abort or retry?

### 3. Blocking and resource exhaustion

During prepare phase, services lock resources:

```
Service A locks account balance for 5 seconds (prepare)
Other transactions waiting to access balance blocked
If many transactions in prepare phase:
  - Resources held
  - Other transactions blocked
  - Cascading delays
```

At scale, this becomes unacceptable latency.

### 4. Coordinator single point of failure

```
Coordinator fails during commit.
Services in prepare phase, waiting for commit instruction.
Services have resources locked.
Other transactions blocked.
```

If coordinator is down, what do services do? Wait indefinitely? Abort? Nobody knows.

### 5. Limited to same organization

Two-phase commit requires strong coupling:
- Coordinator must know about all services
- Services must implement two-phase protocol
- All services must be operational
- All systems must trust coordinator

Across organizations (company A and company B), not possible.

## Why 2PC works for databases but not services

A single database with multiple sessions uses 2PC internally:

```
Session 1: START TRANSACTION
Session 1: update row
Session 2: try to access same row
Session 2: blocked (row locked)
Session 1: COMMIT or ROLLBACK
Session 2: proceeds
```

Works because:
- Single coordinator (the database)
- Same hardware (no network delay)
- Strong consistency guarantee from database

Across independent services:
- Multiple coordinators (each service)
- Network delay (messages may be lost)
- No single source of truth
- Network may partition

2PC is not suitable.

## Saga pattern: the distributed transaction alternative

Instead of trying to guarantee all-or-nothing, Saga accepts eventual consistency.

Saga breaks the transaction into steps with compensation:

```
Step 1: Order Service creates order
  If success -> Step 2
  If fail -> Compensate (delete order)

Step 2: Inventory Service decreases stock
  If success -> Step 3
  If fail -> Compensate (increase stock)

Step 3: Billing Service charges payment
  If success -> Done
  If fail -> Compensate (refund, restore inventory, delete order)
```

**Key difference:** each step is a local transaction (within one service).

### Choreography-based saga

Services react to events:

```
Order Service creates order -> emits OrderCreated

Inventory Service receives OrderCreated -> decreases stock -> emits InventoryDecreased

Billing Service receives InventoryDecreased -> charges payment -> emits PaymentCharged

If Billing fails -> emits PaymentFailed

Inventory Service receives PaymentFailed -> refunds stock
Order Service receives PaymentFailed -> cancels order
```

**Pros:**
- Simple, no coordinator
- Services are loosely coupled

**Cons:**
- Logic scattered across services
- Hard to understand flow
- Circular dependencies possible

### Orchestration-based saga

Dedicated orchestrator coordinates:

```
Orchestrator:
  1. Tell Order Service to create order
  2. Wait for response
  3. Tell Inventory Service to decrease stock
  4. Wait for response
  5. Tell Billing to charge
  6. If fail, tell Inventory to refund, tell Order to cancel
```

**Pros:**
- Workflow centralized
- Easy to understand
- Easier to debug

**Cons:**
- Orchestrator is coordinator (but simpler than 2PC)
- More operational complexity

## Trade-offs of sagas versus 2PC

| Aspect | 2PC | Saga |
|--------|-----|------|
| Consistency | Strong (atomic) | Eventual (may be inconsistent temporarily) |
| Latency | Low | Higher (multiple round trips) |
| Failure recovery | Automatic | Manual (compensation logic needed) |
| Complexity | Simple | Complex (compensation is hard) |
| Availability | Lower (blocking) | Higher (no blocking) |
| Scalability | Poor | Good |
| Network failure handling | Poor | Better |

## When eventual consistency is acceptable

**Good for Saga:**

- E-commerce order processing (customer waits, eventual is okay)
- Account transfers (small delay acceptable)
- Inventory updates (eventual consistency okay, overselling prevented later)

**Bad for Saga (use 2PC or redesign):**

- Financial transaction (cannot have "maybe" state)
- Atomic stock allocation (must be guaranteed)
- Account balance verification (must be accurate immediately)

In practice, most business processes tolerate eventual consistency. The key is detecting and fixing eventual inconsistencies.

## Compensation logic challenges

Writing compensation is hard because:

### 1. Partial compensation

```
Step 1: Create order record
Step 2: Decrease inventory from 100 to 50
Step 3: Charge payment (fails)

Compensation:
  - Delete order (undo step 1)
  - Increase inventory back to 100 (undo step 2)
```

Simple.

But what if during compensation:

```
Step 3 failed so compensation starts:
Step 2 compensation: Increase inventory

But another order just came in, expecting 50 in stock.
Now inventory becomes 100 before the other order updated.
Race condition.
```

Compensation is not guaranteed to be atomic.

### 2. Non-reversible operations

```
Step: Send email to customer

Compensation: "Unsend" email?
Cannot delete already delivered email.
```

Some operations are irreversible.

Solution: accept side effects.
```
Send apology email as compensation.
```

### 3. Idempotency requirement

```
Step: Charge $100 payment

If payment service times out:
Compensation logic retries.
Charges $100 again.

Customer charged twice.
```

Every step and compensation must be idempotent (safe to retry).

## Common saga mistakes

### 1. Not handling timeouts

**Mistake:** assume step always completes or fails quickly

**Result:**
- Long timeout means long saga duration
- Short timeout means premature failure
- Retry logic needed

### 2. Missing idempotency

**Mistake:** steps not idempotent

**Result:**
- Retries cause duplicates (charged twice, order created twice)
- Compensation applied multiple times
- Data corruption

### 3. No monitoring of saga state

**Mistake:** no visibility into which sagas are in progress

**Result:**
- Compensation stuck (service that should undo is down)
- Manual recovery required
- Data inconsistency not detected

### 4. Circular compensation dependencies

**Mistake:** A depends on B, B depends on A

**Result:**
- Deadlock (A waits for B, B waits for A)
- Cannot recover

### 5. Inconsistency not addressed

**Mistake:** saga completes but data is inconsistent

**Result:**
- Users see wrong state
- Compensations don't happen
- Data integrity issues persist

## Investigation: identifying saga problems

**Symptoms:**

1. **Saga hangs**
   - Waiting for step that never responds
   - Service down
   - Network timeout

2. **Partial completion**
   - Some steps committed, later steps failed
   - Compensation didn't run
   - Data inconsistent

3. **Duplicate operations**
   - Same operation ran twice
   - Idempotency not enforced

4. **Compensation failure**
   - Compensation started but failed
   - Cannot undo failure
   - Data stuck in bad state

## Questions to think about

- Why is two-phase commit worse at scale than saga?
- What happens if compensation fails?
- How do you know if a saga is stuck?
- Why must saga steps be idempotent?
- What operations are hard to compensate?
- Would you use 2PC for payment processing?
- What happens if network partitions during saga?
- How do you handle cascade failures in saga?
- Why is saga complexity worth eventual consistency?
- At what scale does eventual consistency become necessary?

## Summary

Distributed transactions are fundamentally hard because:
- Network can fail (messages lost, delayed)
- Services can fail independently
- Coordinator can fail
- No global clock (timing ambiguous)

Two-phase commit attempts strong consistency but fails at scale due to blocking, coordinator dependency, and network fragility.

Saga pattern accepts eventual consistency but requires:
- Compensation logic for each step
- Idempotent operations (safe to retry)
- Monitoring to detect inconsistencies
- Manual repair when things go wrong

The trade-off: lower availability and throughput for strong consistency (2PC) versus higher availability and throughput but eventual consistency (Saga).

Most production systems use Saga (or no coordination, accepting eventual inconsistency). 2PC is rarely used outside of traditional databases.
