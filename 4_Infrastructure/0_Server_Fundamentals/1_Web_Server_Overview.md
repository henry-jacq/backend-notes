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

## Web Server Software

Choosing the right web server software depends on the application stack, concurrency requirements and deployment scale. The three most common engines are Nginx, Apache and Tomcat.

### Nginx
Nginx is a lightweight, high-performance web server and reverse proxy.

-   **Event-Driven Concurrency:** Unlike traditional servers that allocate a thread or process per connection, Nginx utilizes an asynchronous, non-blocking event loop (using kernel interfaces like `epoll` on Linux). This allows a single master worker process to handle tens of thousands of concurrent connections with minimal memory usage.
-   **Common Use Cases:** Ideal for serving static assets, terminating SSL/TLS certificates, load balancing and serving as a reverse proxy for upstream application runtimes (such as Node.js or Go).

### Apache HTTP Server
The Apache HTTP Server is a modular, process-based web server.

-   **Multi-Processing Modules (MPMs):** Apache routes traffic using MPMs, either spawning a separate process per connection (pre-fork MPM) or running multiple threads per process (worker/event MPM). Because each process/thread holds its own memory context, Apache has a higher memory footprint under high concurrency than Nginx.
-   **Extensibility:** Apache supports dynamic configuration files (`.htaccess`) on a per-directory basis, making it highly flexible for shared hosting environments and traditional server-side rendering runtimes (like PHP).

### Apache Tomcat
Apache Tomcat is a Java Servlet container and application server.

-   **Java Application Server:** Unlike Nginx or Apache, which serve general HTTP assets, Tomcat is designed to compile and execute Java Servlets, JavaServer Pages (JSP) and Java Enterprise applications. It implements a Java Virtual Machine (JVM) thread pool to run application logic.
-   **Production Deployment:** While Tomcat can act as a standalone HTTP server, it is commonly placed behind a reverse proxy (such as Nginx) which handles static file delivery, SSL handshakes and DDoS filtering, passing only dynamic requests to Tomcat.



## Proxy Architectures

A proxy is an intermediary server that routes traffic between client devices and target web servers. Proxies are classified into two categories based on which side of the network connection they represent:

### Forward Proxy (Client-Side)
A forward proxy acts on behalf of client machines to access external internet resources.

-   **Traffic Flow:** Client -> Forward Proxy -> Internet.
-   **Mechanics:** Clients configure their browser to route requests through the proxy. The destination server sees the request originating from the proxy's IP address, hiding the client's internal identity.
-   **Common Use Cases:** Enforcing corporate content filters, caching external search queries locally and routing traffic around geographic network blocks.

### Reverse Proxy (Server-Side)
A reverse proxy acts on behalf of back-end application servers to manage incoming client requests.

-   **Traffic Flow:** Client -> Reverse Proxy -> Internal App Servers.
-   **Mechanics:** Clients query the reverse proxy directly (it exposes the public domain DNS). The proxy inspects the request, terminates SSL, routes it to private back-end servers (e.g. Node.js or Tomcat running on localhost) and passes responses back to the client.
-   **Common Use Cases:** SSL/TLS decryption offloading, load balancing traffic across multiple app instances, protecting private networks from direct internet exposure and caching dynamic responses at the edge.

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
