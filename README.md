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

1. **Read Foundations** (0_System_Evolution_and_Scalability → 1_Performance_Engineering)
   - Understand why systems evolve and how to measure performance
   - This is prerequisite for everything else

2. **Read Data Storage** (Database_Design_for_Scale → CRUD_Operations → Redis)
   - Databases are the original bottleneck
   - Learn why, how to scale them, and when caching helps

3. **Read Async and Events** (Messaging_Patterns → Kafka → Distributed_Transactions)
   - How to handle asynchronous work
   - Why Kafka is different from simple queues
   - How to coordinate work across services

4. **Read Reliability** (Reliability_Patterns → Availability_and_Fault_Tolerance)
   - How to make systems continue working despite failures
   - Replication, failover, multi-region deployment

5. **Read Infrastructure** (Under_the_Hood → Web_Server_Overview)
   - Understand the physical layer
   - HTTP, TCP, web servers

6. **Read Operations** (Observability_and_Debugging)
   - How to debug production issues
   - Monitoring, metrics, traces


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

