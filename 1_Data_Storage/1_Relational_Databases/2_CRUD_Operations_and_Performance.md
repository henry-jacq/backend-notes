---
title: "CRUD Operations and Performance"
part: 2
part_title: "Data Storage"
chapter: 3
summary: "This document explains Create, Read, Update, Delete (CRUD) operations—the fundamental interactions with relational..."
---
# CRUD Operations and Performance

This document explains Create, Read, Update, Delete (CRUD) operations—the fundamental interactions with relational databases—and analyzes their performance characteristics and locking mechanisms.

## CRUD overview

Every database interaction is one of four operations:

- **Create** (INSERT): Add new data
- **Read** (SELECT): Retrieve existing data
- **Update** (UPDATE): Modify existing data
- **Delete** (DELETE): Remove existing data

## Create (INSERT)

Creating a new record adds data to the database.

### Single record insert

```sql
INSERT INTO users (id, name, email, created_at)
VALUES (1, 'Alice', 'alice@example.com', NOW())
```

**What happens:**

1. Validate data (email format correct?)
2. Check constraints (unique email? foreign keys valid?)
3. Find space on disk
4. Write data to disk
5. Update indexes
6. Write to log (durability)
7. Return success

**Cost:**

- Single insert: microseconds to milliseconds
- High-volume inserts: indexes slow this down
- Constraints add overhead

### Bulk inserts

```sql
INSERT INTO users (id, name, email) VALUES
(1, 'Alice', 'alice@example.com'),
(2, 'Bob', 'bob@example.com'),
(3, 'Charlie', 'charlie@example.com')
```

**Better than 3 separate INSERT statements:**

- Network round trips: 3 vs 1
- Index updates: batch optimised

### Batch insert performance

```
1,000 rows inserted one-by-one: 1,000 network round trips
1,000 rows inserted in batches of 100: 10 network round trips
Same data, 100x fewer round trips
```

**Trade-off:**

- Batching increases throughput
- Reduces latency per row
- Increases memory usage per batch

## Read (SELECT)

Reading retrieves existing data.

### Full table scan

```sql
SELECT * FROM users WHERE age > 30
```

**Execution:**

1. Start at first row
2. Check condition (age > 30?)
3. If true, include in result
4. Move to next row
5. Repeat until end

**Problem at scale:**

- 1 billion rows
- Half match condition
- All 1 billion rows scanned
- Each row read from disk
- 10ms per disk read = billions of milliseconds

**Symptom:** query returns results but takes hours.

### Index scan

```sql
SELECT * FROM users WHERE age > 30
-- With index on age
```

**Execution with index:**

1. Look up age > 30 in index
2. Index has pre-sorted list of ages
3. Find first age > 30 (binary search)
4. Follow pointers to matching rows
5. Only relevant rows read

**Performance improvement:**

- Full scan: 10 seconds (scan all rows)
- Index scan: 100 milliseconds (direct lookup)
- 100x faster

**Trade-off:**

- Index takes disk space
- Index slows down writes (index must be updated)

### Join operations

```sql
SELECT users.name, orders.total
FROM users
JOIN orders ON users.id = orders.user_id
WHERE users.region = 'us-west'
```

**Execution:**

1. Find users in region us-west (possibly with index)
2. For each user, find matching orders
3. Combine results

**At scale:**

- Users table: 1 million rows
- Orders table: 100 million rows
- If join unoptimized: nested loop 1M * 100M = 100 trillion checks
- Each check: disk I/O

**Solution:** indexes on join columns, query planner optimisation.

## Update (UPDATE)

Updating modifies existing records.

### Simple update

```sql
UPDATE users SET email = 'alice2@example.com' WHERE id = 1
```

**What happens:**

1. Find row with id=1 (index lookup)
2. Check constraints (new email unique?)
3. Update the row
4. Update all indexes (if columns in indexes changed)
5. Write to log
6. Acknowledge to client

**Cost:**

- Lookup: fast (index)
- Constraint check: depends on what constraints
- Index updates: can be expensive if many indexes

### Bulk update

```sql
UPDATE users SET status = 'verified' WHERE signup_date < '2020-01-01'
```

**Without index on signup_date:**

- Full table scan of all users
- Check condition for each row
- Update matching rows
- Update all indexes for each row

**With index on signup_date:**

- Index lookup: find users before 2020
- Update only those rows
- Update indexes only for those rows

**Performance difference:**

- Full scan: 1 hour (scan all users)
- Index scan: 1 second (direct access to old users)

### Locking and contention

```sql
UPDATE accounts SET balance = balance - 100 WHERE id = 1
-- And at same time:
UPDATE accounts SET balance = balance + 100 WHERE id = 1
```

**Issue:** both transactions read same balance, update independently, one update overwrites the other.

**Solution:** database locks row during update.

```
Transaction 1: lock row 1, read balance ($1000)
Transaction 2: wait for lock to release
Transaction 1: update balance ($900), release lock
Transaction 2: lock row 1, read balance ($900)
Transaction 2: update balance ($800), release lock

Correct.
```

**Cost of locks:**

- High contention (many updates to same row): transactions wait
- Waits cause latency spikes
- High-frequency updates to hot rows become bottleneck

## Delete (DELETE)

Deleting removes records.

### Simple delete

```sql
DELETE FROM users WHERE id = 1
```

**What happens:**

1. Find row with id=1
2. Mark row as deleted (or physically remove)
3. Update indexes
4. Write to log
5. Acknowledge

**Cost:**

- Lookup: fast with index
- Index removal: expensive if many indexes

### Cascade deletes

```sql
DELETE FROM users WHERE id = 1
-- Cascades to:
DELETE FROM orders WHERE user_id = 1
DELETE FROM payments WHERE user_id = 1
DELETE FROM notifications WHERE user_id = 1
```

**Problem at scale:**

- Delete one user
- User has 1 million orders
- 1 million cascade deletes
- Each with index updates
- Single delete takes hours

**Solution:**

- Soft deletes (mark as deleted, don't physically delete)
- Batch deletes over time
- Denormalize (don't need cascade if data denormalized)

To see how these operations behave in scale-heavy patterns and identify common mistakes, see [3_CRUD_Patterns_at_Scale.md](file:///d:/Playground/Backend%20Notes/1_Data_Storage/1_Relational_Databases/3_CRUD_Patterns_at_Scale.md).
