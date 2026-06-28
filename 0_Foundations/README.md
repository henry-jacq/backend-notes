# Foundations: Core Systems Engineering Thinking

This section establishes the mental models you need to understand why backend systems are designed the way they are.

## Learning path

**0_System_Evolution_and_Scalability.md** — Why systems evolve
- Single server limits
- Horizontal scaling concepts
- When systems need to evolve
- Breaking points and metrics

Start here. Understand why we even need databases, caches, message queues. They exist because single servers cannot handle real-world load.

**1_Performance_Engineering.md** — How to identify and fix bottlenecks
- Performance vs scalability distinction
- How to measure correctly (baselines matter)
- Finding the actual bottleneck (profilers, monitoring, traces)
- Common bottlenecks (CPU, memory, I/O, locks)
- Amdahl's Law (why some optimizations don't help)

Read this to learn how NOT to waste time optimizing the wrong thing. Most engineers optimize randomly. This teaches systematic debugging.

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

Read both documents in order. Foundation is a prerequisite for everything else. You cannot understand why Kafka exists or why sharding is necessary without understanding system evolution and performance engineering.
