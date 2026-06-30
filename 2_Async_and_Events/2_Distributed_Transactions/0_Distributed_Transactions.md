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

To learn about the Saga pattern—the modern eventually-consistent alternative to distributed transactions—see [2_Saga_Pattern_Deep_Dive.md](file:///d:/Playground/Backend%20Notes/2_Async_and_Events/2_Distributed_Transactions/2_Saga_Pattern_Deep_Dive.md).
