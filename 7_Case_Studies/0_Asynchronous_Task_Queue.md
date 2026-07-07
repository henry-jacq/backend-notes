---
title: "Designing an Asynchronous Task Queue"
part: 8
part_title: "System Design Case Studies"
chapter: 1
summary: "Case study on building an extensible asynchronous task queue supporting database and Redis drivers, dynamic worker scaling and Directed Acyclic Graph (DAG) task chaining."
---
# Designing an Asynchronous Task Queue

## Why Asynchronous Task Queues Exist
In user-facing applications, performing high-latency operations synchronously degrades user experience and exhausts web server request threads. For example, in a hostel outpass generation system, when a student requests an exit pass, the system must perform three distinct heavy tasks:

1.  **PDF Document Generation:** Constructing layout and compiling student metadata into a printable PDF.
2.  **QR Code Generation:** Generating cryptographic QR codes encoding authorization tokens.
3.  **Email Notification:** Establishing connections with external SMTP servers and transmitting emails containing PDF attachments.

Executing these operations inside the synchronous request-response flow blocks the student client browser for seconds, which causes thread pool starvation and crashes under registration spikes.

To prevent this, the application delegates these time-consuming operations to an asynchronous background worker pool using an **Asynchronous Task Queue** where jobs are managed by an abstracted storage driver.



## High-Level System Abstractions
An asynchronous task queue splits task storage from task execution:

-   **Queue Driver:** The underlying storage mechanism (such as a database table or a Redis cache) used to hold and coordinate task states.
-   **Job Payload:** A serialized JSON object defining the task type (e.g. `generate_outpass`), execution attempts and references to entity data.
-   **Background Worker:** A standalone execution process that constantly queries the queue driver, acquires pending jobs, runs the code and records results.
-   **Supervisor:** A manager daemon process that monitors queue depth across drivers and dynamically scales background workers.



## Under the Hood Operations

### Queue Driver Architectures
By abstracting the queue interface, developers can switch queue drivers based on scale and infrastructure budgets:

#### 1. Relational Database Driver (SQL Table)
A database-backed driver is simple to monitor and requires no additional infrastructure.

*   **Database Schema:** A `jobs` table tracks the lifecycle of each job:
```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    attempts INTEGER DEFAULT 0,
    reserved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
*   **Atomic Acquisition:** To prevent multiple concurrent workers from picking up the same job, workers execute queries inside transactions using row-level locking:
```sql
SELECT * FROM jobs 
WHERE status = 'pending' AND (reserved_at IS NULL OR reserved_at < NOW() - INTERVAL '15 minutes')
LIMIT 1 
FOR UPDATE SKIP LOCKED;
```

The `FOR UPDATE` clause locks the acquired row, while `SKIP LOCKED` instructs other workers to ignore locked rows, allowing concurrent processing without thread blockages.


#### 2. In-Memory Cache Driver (Redis)
For high-volume, low-latency queues, a Redis-backed driver avoids database query overhead.

*   **Active Queue:** Uses Redis Lists. The application publishes tasks using `LPUSH` and workers retrieve them using `BRPOP` (blocking list pop), which sleeps the worker until a message arrives, eliminating database CPU polling overhead.
*   **Delayed/Failed Queues:** Uses Redis Sorted Sets (`ZSET`). Delayed tasks are queued with execution timestamps as scores. A worker polls the set using `ZRANGEBYSCORE` to push due jobs into the active List.

### Job Dependencies and DAG Chaining
Often, background tasks must run in a specific sequence because one task requires the output of another. In our outpass system:
`Generate PDF` -> `Generate QR` (embeds PDF link) -> `Send Email` (requires PDF attachment).

To implement this, the queue framework supports **Job Chaining** modeled as a Directed Acyclic Graph (DAG):

-   **Dependency Schema:** Each job record registers a list of prerequisite parent job IDs and a counter of pending dependencies:
    ```json
    {
      "job_id": "job_email_123",
      "parent_ids": ["job_pdf_456"],
      "pending_dependencies": 1
    }
    ```
-   **Blocked Status:** A job with `pending_dependencies > 0` is created with a `blocked` status. Workers ignore blocked jobs.
-   **State Propagation:** When a parent job completes, it writes its output (e.g. the compiled PDF file path) to a shared context datastore. The queue engine then finds all child jobs waiting on this parent, decrements their `pending_dependencies` counter and updates their status to `pending` once the counter reaches zero.

### Cron and Scheduled Tasks (Delayed Execution)
In addition to executing jobs immediately, an asynchronous task queue can schedule tasks for delayed or recurring execution (similar to system cron daemons).

-   **Delayed Scheduling:** The queue table (or Redis sorted set) includes a `run_at` timestamp. Workers ignore these jobs until the current system clock surpasses the `run_at` value.
-   **Self-Perpetuating Recurring Jobs:** To run a task periodically (e.g. generating hostel attendance reports every Sunday at midnight), the worker processes the job and, upon successful completion, calculates the *next* execution timestamp using a cron expression parser (e.g. `0 0 * * 0`). It then writes a new job entry back into the queue with that future `run_at` value, creating a self-sustaining distributed scheduler.

### Retries and Dead-Letter Auditing
-   **Automatic Retries:** If a job fails, the worker catches the exception, increments the `attempts` counter and resets the status to `pending` (or adds it to a delayed queue driver) to retry later.
-   **Audit Log (Dead-Letter Queue):** If a job fails more than 3 times, retries are aborted. The worker moves the payload and stack trace to a `failed_jobs` storage table, allowing engineers to audit failures without cluttering active queues.
