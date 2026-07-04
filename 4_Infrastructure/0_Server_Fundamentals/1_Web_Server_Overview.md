---
title: "Web Server Overview"
part: 5
part_title: "Infrastructure"
chapter: 2
summary: "A web server receives client requests, processes them and returns responses. It may serve static files, run..."
---
# Web Server Overview

A web server receives client requests, processes them and returns responses. It may serve static files, run application logic, query databases, validate authentication, or proxy requests to other services.

Backend engineers set up and maintain servers that host applications, APIs, background jobs and databases. Good server design affects response time, security, scalability and recovery speed.

## Client-Server Architecture

In client-server architecture, a client requests a service and the server provides it. The client may be a browser, mobile app, IoT device, or another backend service. The server listens for requests, processes them and returns responses.

This separates responsibilities: clients handle user interaction, servers manage business logic, storage and authentication.

Example request-response:

```
Client sends:   GET /products/123 HTTP/1.1
Server returns: { "id": 123, "name": "Wireless Keyboard", "price": 49.99 }
```

## Architecture Patterns

### Two-Tier Architecture

Client communicates directly with a server or database. Simple but tight coupling.

```
Client <--> Server (with DB)
```

### Three-Tier Architecture

Separates presentation, application and data layers.

```
Client <--> App Server <--> Database
```

The client handles presentation. The app server handles business logic. The database stores data. This improves organization and security.

### N-Tier Architecture

Adds more layers: API gateways, caching, message queues, microservices, search services.

```
Client
  |
  v
API Gateway
  |
  +---> Web Tier <--> Business Logic <--> Database
  |
  +---> Cache <--> Queue
```

More flexible and scalable, but more operational complexity.

## Server Types

### Dedicated Servers

Physical machine assigned to one application. Strong performance, full control, but expensive and requires maintenance.

### Virtual Private Servers (VPS)

Virtualized portion of a physical server. Shared hardware but isolated OS and resources. Good balance of cost and control.

### Cloud Servers

Provided by AWS, Azure, Google Cloud, etc. Flexible, scalable, pay-as-you-go pricing. Costs can grow quickly if not monitored.

## Operating Systems

### Linux

Ubuntu, Debian, Rocky Linux, AlmaLinux, CentOS Stream. Popular for servers because it is stable, secure, scriptable and open-source.

### Windows Server

Used for .NET applications, Active Directory, SQL Server and enterprise tools. Graphical administration and PowerShell automation.

## Server Configuration

A server needs software, firewall rules, environment variables, database connections, reverse proxies and logging.

Common components:

- Web Server Software: Nginx, Apache, Caddy, IIS
- Databases: PostgreSQL, MySQL, MongoDB, SQL Server
- Caching: Redis, Memcached
- Runtimes: Node.js, Python, Ruby, Java, Go, .NET

Example setup: Ubuntu + Nginx (reverse proxy) + Node.js (app) + MongoDB (database)

Nginx forwards requests from port 80 to Node.js on port 3000.

## Security

Security should be layered. No single control is enough.

Practices:

- Firewalls: restrict traffic to only required ports (SSH, HTTP, HTTPS)
- SSL/TLS: use HTTPS for client-server communication
- User Access: prefer SSH keys, disable password login where possible
- Updates: keep OS and dependencies patched
- Intrusion Detection: monitor logs and use fail2ban or audit tools

## Performance Tuning

Optimization should be guided by metrics, not guesses.

Monitor:

- CPU, memory, disk, network usage
- Request latency
- Error rates
- Database query time
- Cache hit rate

Strategies:

- Load Balancing: distribute requests across servers
- Caching: store frequently requested data
- Database Indexing: optimize queries
- Resource Monitoring: use tools like Prometheus, Grafana, or htop

## Backup and Disaster Recovery

Protect against data loss and downtime with:

- Regular automated backups
- Redundancy: replicas, failover systems
- Test restores regularly to verify they work

## Automation and CI/CD

Use scripts, configuration management, containers and CI/CD pipelines to keep environments consistent.

Common tools:

- Scripting: Bash, Python, PowerShell
- Configuration Management: Ansible, Puppet, Chef
- CI/CD: GitHub Actions, GitLab CI, Jenkins, CircleCI

## Monitoring and Alerts

Detect issues quickly with monitoring and alerting.

Monitor:

- Infrastructure: CPU, memory, disk, network
- Application: latency, error rates, throughput, database latency

Tools:

- Monitoring: Prometheus, Grafana, Datadog, CloudWatch
- Logging: ELK Stack, Loki, Splunk
- Alerts: Email, SMS, PagerDuty, Slack

Example alert:

```
Trigger if:

- p95 latency > 500ms for 5 minutes
- 5xx errors > 2% for 3 minutes
- CPU > 90% for 10 minutes
```

Metrics show that something is wrong. Logs explain why. Together, they help teams respond faster and maintain reliable servers.
