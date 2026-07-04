---
title: "Foundations: Core Systems Engineering"
part: 1
part_title: "Foundations"
type: "part_intro"
summary: "This section establishes the mental models you need to understand why backend systems are designed the way they are."
---
# Foundations: Core Systems Engineering

This section establishes the mental models you need to understand why backend systems are designed the way they are.

## Chapters

**Core System Evolution**

- Single server limits
- Vertical vs Horizontal scaling concepts
- Database and caching scaling bottlenecks
- Replication and sharding introductory concepts

**Event-driven and Queue Scaling**

- Asynchronous work queues
- Event streaming and distributed messaging
- Breaking points and metrics
- Common scaling mistakes

**Performance Engineering Fundamentals**

- Performance vs scalability distinction
- How to define performance requirements
- Establishing current baselines
- Profiling and finding the actual bottleneck

**Common Bottlenecks and Testing**

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
