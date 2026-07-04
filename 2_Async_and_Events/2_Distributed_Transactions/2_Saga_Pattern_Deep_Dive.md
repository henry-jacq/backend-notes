---
title: "Saga Pattern Deep Dive"
part: 3
part_title: "Async and Events"
chapter: 11
summary: "Covers the details of the Saga Pattern, choreography vs orchestration, eventual consistency..."
---
# Saga Pattern Deep Dive

Covers the details of the Saga Pattern, choreography vs orchestration, eventual consistency trade-offs and how to deal with compensation failures.

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

<div class="warning-box">
    <strong>Idempotency Warning:</strong> In distributed transactions, network failures will cause duplicate requests. If steps or compensating actions are not idempotent, retries will result in duplicate payments, double-ordered inventory and data corruption.
</div>

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

Saga pattern accepts eventual consistency but requires:

- Compensation logic for each step
- Idempotent operations (safe to retry)
- Monitoring to detect inconsistencies
- Manual repair when things go wrong

The trade-off: lower availability and throughput for strong consistency (2PC) versus higher availability and throughput but eventual consistency (Saga).
