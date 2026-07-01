---
title: "Infrastructure: Servers and Networks That Run Systems"
part: 5
part_title: "Infrastructure"
type: "part_intro"
summary: "This section covers the physical and virtual infrastructure that runs backend systems."
---
# Infrastructure: Servers and Networks That Run Systems

This section covers the physical and virtual infrastructure that runs backend systems.

## Learning path

### Server Fundamentals

**0_Under_the_Hood.md** — HTTP protocol, TCP, web servers, databases

How communication actually works:

- HTTP protocol (requests, responses)
- TCP foundation (reliable delivery)
- Request/response cycle
- Web server operation
- Database connectivity
- Connection pooling

Understand the mechanics before studying higher-level patterns. Everything is built on top of these fundamentals.

**1_Web_Server_Overview.md** — Nginx, Apache, application servers

How servers handle requests:

- Server types and characteristics
- Operating system considerations
- Configuration and performance tuning
- Security and hardening
- Backup and disaster recovery
- Automation and CI/CD
- Monitoring and alerting

This is the "operations" side of infrastructure: how to run systems in production.

## Key concepts

- HTTP protocol structure
- TCP reliability (3-way handshake, retransmission)
- Connection pooling (reusing connections)
- Thread models (blocking, non-blocking)
- Load balancing
- Reverse proxies
- SSL/TLS encryption
- DNS resolution
- Network latency

## Connection to other sections

**Infrastructure + Reliability:**

- Load balancers distributing traffic
- Health checks removing failed servers
- Failover automation

**Infrastructure + Data Storage:**

- Database connectivity
- Connection pooling to databases
- Replica selection

**Infrastructure + Async and Events:**

- Message broker infrastructure
- Kafka cluster setup
- Network between services

**Infrastructure + Operations:**

- Monitoring servers
- Log aggregation from servers
- Performance metrics collection

**Infrastructure + API Design:**

- HTTP protocol fundamentals underpin REST and GraphQL
- Load balancers distribute API traffic
- API gateways handle auth, rate limiting and routing
- SSL/TLS termination at gateway or load balancer

## Typical deployment layers

```
User Internet
    |
Load Balancer
    |
Web Servers (Nginx, Apache)
    |
Application Servers (Node, Python, Java)
    |
Cache Layer (Redis)
    |
Databases (Replicated, Sharded)
    |
Message Brokers (Kafka, RabbitMQ)
```

Each layer has its role:

- Load balancer: distribute traffic
- Web server: parse HTTP, route to app
- Application: business logic
- Cache: reduce database load
- Database: persist data
- Message broker: async processing

## Next sections

After understanding infrastructure:

- **Operations** — monitoring, debugging, incident response for all of the above
