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

## Repository Structure

The repository is organized into 6 major sections, each with a clear progression:

```
0_Foundations/                     (start here)
├── 0_System_Evolution_and_Scalability.md
└── 1_Performance_Engineering.md

1_Data_Storage/                    (how to persist data)
├── 0_Basics/
├── 1_Relational_Databases/
│   ├── 0_Database_Design_for_Scale.md
│   └── 1_CRUD_Operations.md
└── 2_In_Memory_Caching/Redis/
    ├── 0_INTRO.md
    ├── 1_BASICS.md
    ├── 2_DATA_TYPES.md
    ├── 3_COMMANDS.md
    ├── 4_PUBSUB.md
    └── 5_SYSTEMS_PERSPECTIVE.md

2_Async_and_Events/               (handle work asynchronously)
├── 0_Messaging/
│   └── 0_Messaging_Patterns.md
├── 1_Event_Streaming/Kafka/
│   ├── 0_INTRO.md
│   ├── 1_BASICS.md
│   ├── 2_CONCEPTS.md
│   ├── 3_internals.md
│   └── 4_SYSTEMS_PERSPECTIVE.md
└── 2_Distributed_Transactions/
    ├── 0_Distributed_Transactions.md
    └── 1_Saga_Pattern.md

3_Reliability_and_Availability/   (make systems robust)
├── 0_Reliability_Patterns.md
└── 1_Availability_and_Fault_Tolerance.md

4_Infrastructure/                 (physical layer)
└── 0_Server_Fundamentals/
    ├── 0_Under_the_Hood.md
    └── 1_Web_Server_Overview.md

5_Operations/                     (running systems)
└── 0_Observability_and_Debugging.md
```

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

### Each section has a README

Every major folder has a README.md that explains:
- What the section teaches
- How documents flow
- How it connects to other sections
- When to use each concept

Read the section README before diving into documents.

## Key Insights

### Why this structure exists

1. **Foundations first** — You must understand why systems evolve before studying any technology
2. **Data storage early** — Databases are the bottleneck for most systems
3. **Async and events together** — Messaging makes sense only after understanding database limits
4. **Reliability after scale** — Design for failure only after you understand scale
5. **Infrastructure and operations last** — Understand problems before studying solutions

### No technologies for their own sake

Every technology covered here is explained in context:
- **Kafka** — Why it exists (event replay, multiple independent consumers)
- **Redis** — Why it exists (repeated query problem)
- **Sharding** — Why it's necessary (write scaling)
- **Sagas** — Why they're needed (transactions don't work across services)

If we're covering it, there's a real problem that made it necessary.

### Every document follows the same pattern

- **Why it exists** — What problem does it solve?
- **When necessary** — What symptoms indicate you need it?
- **How it works** — Mechanics of implementation
- **Breaking points** — Where does it fail?
- **Investigation** — How to debug issues
- **Trade-offs** — What are the costs?
- **Common mistakes** — What do people get wrong?
- **Thinking questions** — Reflection for engineering judgment

This structure ensures you understand not just what, but why.

## How Documents Are Written

- **Hand-crafted, not AI-generated** — Every word is intentional
- **No emojis, no filler** — Dense with information
- **Technical and professional** — Written for engineers
- **Mechanics, not outcomes** — Explains why something happens, not just that it happens
- **Practical mistakes included** — Real errors engineers make
- **Trade-off tables** — Showing costs of each approach

## Topics Covered

### Completed ✅

- System Evolution and Scalability
- Performance Engineering
- Database Design for Scale
- CRUD Operations
- Redis (complete with Systems Perspective)
- Messaging Patterns
- Kafka (complete with Systems Perspective)
- Distributed Transactions and Saga Pattern
- Reliability Patterns
- Availability and Fault Tolerance
- Server Fundamentals
- Observability and Debugging

### To Be Added

- Caching Strategies (cache-aside, write-through, invalidation patterns)
- Storage Design (relational, document, time-series databases)
- Capacity Planning and Forecasting
- API Architecture (REST, GraphQL, gRPC)
- Security (authentication, authorization, encryption)
- Production Operations (deployment, incident response)
- Cost Optimization at Scale

## Learning Outcomes

After working through this knowledge base, you will understand:

1. **System evolution** — Why systems scale from single server to distributed
2. **Bottleneck identification** — How to find what's actually slow
3. **Database scaling** — Replication, sharding, caching
4. **Asynchronous processing** — When and how to use
5. **Failure handling** — Retries, circuit breakers, replication
6. **Debugging methodology** — Systematic approach to production issues
7. **Trade-off thinking** — Every solution has costs
8. **Engineering judgment** — When to use each pattern

Most importantly, you'll develop the ability to reason about systems: to see a problem and think "we need a message queue" or "this needs caching" or "we should replicate", not because those are buzzwords, but because you understand the engineering reasons why.

## How to Contribute

This is a systems engineering knowledge base, not a tutorial. Contributions should:

- Explain why a pattern/technology exists (not just how to use it)
- Include trade-offs and costs
- Document common mistakes
- Follow the established structure and tone
- Be hand-crafted (no AI-generated content)
- Be specific and technical (no hand-waving)

---

**Start with 0_Foundations/0_System_Evolution_and_Scalability.md**