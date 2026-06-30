# Backend Notes: Systems Engineering

This is a structured knowledge base for building backend systems. It teaches engineering judgment, not just technologies.

## Philosophy

This repository exists to transform developers who can build REST APIs into engineers who can design and operate production systems.

The best backend engineers understand:
- **Why** systems are designed the way they are
- **When** each technology becomes necessary
- **What trade-offs** exist for every decision
- **How** to debug production issues systematically

This knowledge base answers those questions.

**Key principle:** Every section explains what problem a technology solves, when that problem becomes real, and what trade-offs exist. Technologies exist for reasons. Understanding those reasons is what separates good engineers from great engineers.


## How to Use This Repository

### Start here if you're beginning

1. **Read Foundations** (0_System_Evolution → 1_Asynchronous_Processing → 2_Performance_Engineering_Basics → 3_Common_Bottlenecks_and_Testing)
   - Understand why systems evolve, how async queues fit in, and how to measure/test performance baselines
   - This is prerequisite for everything else

2. **Read Data Storage** (0_Database_Bottlenecks_and_Replication → 1_Database_Sharding_and_Strategies → 2_CRUD_Operations_and_Performance → 3_CRUD_Patterns_at_Scale → Redis)
   - Databases are the original bottleneck
   - Learn database design for scale, sharding strategies, CRUD performance, and caching with Redis

3. **Read Async and Events** (0_Messaging_Patterns → 1_Message_Semantics_and_Mistakes → Kafka → Distributed_Transactions → Saga_Pattern)
   - How to handle asynchronous work, event streaming with Kafka
   - How to coordinate eventual consistency across services using Saga Patterns

4. **Read Reliability** (0_Reliability_Patterns → 1_Resource_Isolation_and_Fault_Tolerance → 2_Availability_and_Replication → 3_Failover_and_Multi_Region)
   - How to make systems continue working despite failures
   - Exponential backoffs, circuit breakers, resource isolating bulkheads, failovers, and multi-region deployment

5. **Read Infrastructure** (0_Under_the_Hood → 1_Web_Server_Overview)
   - Understand the physical layer (HTTP, TCP, web servers, and database connectivity)

6. **Read Operations** (0_Observability_Fundamentals → 1_Systematic_Debugging_and_Failure_Patterns)
   - How to debug production issues using metrics, logs, and traces systematically


## Key Insights

### Why this structure exists

1. **Foundations first** — You must understand why systems evolve before studying any technology
2. **Data storage early** — Databases are the bottleneck for most systems
3. **Async and events together** — Messaging makes sense only after understanding database limits
4. **Reliability after scale** — Design for failure only after you understand scale
5. **Infrastructure and operations last** — Understand problems before studying solutions


Every technology covered here is explained in context:
- **Kafka** — Why it exists (event replay, multiple independent consumers)
- **Redis** — Why it exists (repeated query problem)
- **Sharding** — Why it's necessary (write scaling)
- **Sagas** — Why they're needed (transactions don't work across services)

