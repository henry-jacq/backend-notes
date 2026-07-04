---
title: "Under the Hood: Servers and HTTP"
part: 5
part_title: "Infrastructure"
chapter: 1
summary: "No summary available"
---


# Under the Hood: Servers and HTTP

## What is a Server?

A server is a machine or process that listens for requests, processes them and returns responses. It may serve static files, run application logic, query a database, validate authentication, or proxy requests to other services.

Servers can be physical machines, virtual instances, or cloud-provisioned resources. They run an operating system and application software.

## Client-Server Model

In client-server architecture, a client sends a request for a service or data and the server provides it. The client may be a browser, mobile app, IoT device, or another backend service.

Communication between clients and servers relies on protocols. A protocol is a set of rules that defines how messages are structured and exchanged.

### Typical deployment layers

In production, client requests rarely hit an application server directly. Instead, they traverse multiple specialized infrastructure layers:

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

Each layer serves a specific architectural role:

- **Load balancer:** Distributes incoming traffic across multiple servers.
- **Web server:** Handles incoming HTTP parsing, static file routing and SSL/TLS termination.
- **Application server:** Executes core business logic and API routing.
- **Cache layer:** Stores frequently accessed items in memory to reduce database query load.
- **Database:** Persists relational or non-relational business records.
- **Message broker:** Manages asynchronous message streams and background tasks.

## Communication Protocols

Protocols define the format and behavior of requests and responses. Different protocols serve different purposes:

- HTTP/HTTPS: web traffic and APIs
- FTP/SFTP: file transfer
- SMTP: email
- WebSockets: real-time bidirectional communication
- gRPC: efficient service-to-service communication

## HTTP: A Protocol Built on TCP

HTTP is a protocol built on top of TCP.

HTTP is basically a TCP connection with a defined structure for communication between systems over the internet.

An HTTP request or response has a header and a body.

- The header carries information such as who is sending it, what kind of data is being sent and where it is going.
- The body contains the actual data, also called the payload.

Example HTTP request:

```
GET /products/123 HTTP/1.1
Host: api.example.com
Accept: application/json
```

Example HTTP response:

```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 123,
  "name": "Wireless Keyboard",
  "price": 49.99
}
```

## How Web Servers Work

We can build our own HTTP server by opening a socket on a port and handling structured HTTP requests and responses. Once the server speaks the correct HTTP format, a browser or API client can understand it.

This is the basic working model behind server technologies such as Apache, Tomcat and Nginx.

A web server's job is to:

1. Listen on a port (usually 80 for HTTP, 443 for HTTPS)
2. Accept incoming client connections
3. Parse the HTTP request
4. Process the request (serve a file, run application code, query a database, etc.)
5. Format an HTTP response
6. Send the response back to the client
7. Close or keep the connection open for more requests

This simple pattern, repeated thousands of times per second, is how web servers handle traffic.

In step 4, when a web server processes a request, it often needs to retrieve or store data. This is where databases come in. A web server rarely acts alone—it typically communicates with a database to handle the client's request.

## Connecting to Databases

Application runtimes (Node.js, Python, Java, etc.) often need to read or write data. Databases store that data. The runtime connects to a database over the network using a database-specific protocol.

This is similar to how a client connects to a web server: the application opens a socket connection to the database's address and port, then communicates using a structured protocol.

### Database Location

A database can be located:

- On the same machine as the application
- On a different machine in the same network
- On a separate server in a data center
- In a cloud service (AWS RDS, Azure Database, etc.)

The database is accessed by its address, which is usually a hostname or IP address and a port number.

Example addresses:

```
localhost:5432          (PostgreSQL on same machine)
db.example.com:3306     (MySQL on another machine)
10.0.0.5:27017         (MongoDB on a specific IP)
my-db.region.rds.amazonaws.com:5432  (AWS database)
```

### Database Communication Protocols

Databases listen on specific ports and use their own protocols for communication. Different databases use different protocols:

- PostgreSQL: port 5432, uses PostgreSQL protocol
- MySQL: port 3306, uses MySQL protocol
- MongoDB: port 27017, uses MongoDB protocol
- SQL Server: port 1433, uses TDS (Tabular Data Stream) protocol
- Redis: port 6379, uses RESP (Redis Serialization Protocol)

Each protocol defines how queries are sent, results are returned and connections are managed.

### How Applications Connect to Databases

When an application needs data, it:

1. Creates a connection to the database address and port
2. Authenticates with a username and password
3. Sends a query or command using the database protocol
4. Receives the result
5. Closes the connection or keeps it open for reuse

The application's database client library handles the protocol details. It opens a TCP socket to the database address, authenticates, sends the query in the database protocol format and returns the result.

### Connection Pooling

Opening a new database connection is expensive. Connection pooling reuses connections instead of creating new ones for each request. A pool keeps a set of open connections ready to use and applications check out and return connections as needed.

This is more efficient for high-traffic applications.

