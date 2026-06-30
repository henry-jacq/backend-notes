# Foundations: Core Systems Engineering Thinking

This section establishes the mental models you need to understand why backend systems are designed the way they are.

## Learning path

**[0_System_Evolution.md](file:///d:/Playground/Backend%20Notes/0_Foundations/0_System_Evolution.md)** — Core System Evolution
- Single server limits
- Vertical vs Horizontal scaling concepts
- Database and caching scaling bottlenecks
- Replication and sharding introductory concepts

**[1_Asynchronous_Processing.md](file:///d:/Playground/Backend%20Notes/0_Foundations/1_Asynchronous_Processing.md)** — Event-driven and Queue Scaling
- Asynchronous work queues
- Event streaming and distributed messaging
- Breaking points and metrics
- Common scaling mistakes

**[2_Performance_Engineering_Basics.md](file:///d:/Playground/Backend%20Notes/0_Foundations/2_Performance_Engineering_Basics.md)** — Performance Engineering Fundamentals
- Performance vs scalability distinction
- How to define performance requirements
- Establishing current baselines
- Profiling and finding the actual bottleneck

**[3_Common_Bottlenecks_and_Testing.md](file:///d:/Playground/Backend%20Notes/0_Foundations/3_Common_Bottlenecks_and_Testing.md)** — Common Bottlenecks and Testing
- Common bottlenecks (CPU, Memory, locks, Network, Disk)
- Amdahl's Law (diminishing returns)
- Caching decisions and premature optimization traps
- Types of performance testing (Load, Stress, Soak, Spike) and monitoring

Read these in order. They build a systematic thinking framework for building and operating production systems.

## Key concepts you'll learn

- Why single server isn't enough
- How to measure whether something is actually a problem
- What breaks first as systems scale (usually databases)
- How to identify what's actually slow (not guessing)
- Why caching helps (and when it doesn't)

## Next sections

After foundations, you'll study specific technologies and patterns:
- **Data Storage** — how to persist and query data efficiently
- **Async and Events** — how to handle work asynchronously
- **Reliability** — how to make systems continue working despite failures
- **Infrastructure** — how servers work and how systems run
- **Operations** — how to debug production issues

## Reading strategy

Read all four documents in order. Foundation is a prerequisite for everything else. You cannot understand why Kafka exists or why sharding is necessary without understanding system evolution and performance engineering.

