---
title: "First Mental Model: There Is No Permanent Central Brain"
part: 3
part_title: "Async and Events"
chapter: 6
summary: "Many beginners imagine:"
---
Excellent question. This is where most people stop thinking of Kafka as a "message queue" and start understanding it as a **distributed system**.

You're basically asking:

> "If partitions are spread across multiple brokers (servers), who is coordinating everything? Where is Kafka's brain? How do all these brokers know about each other?"

Let's build the mental picture.

---

# First Mental Model: There Is No Permanent Central Brain

Many beginners imagine:

```text
          Master Server
                |
      -------------------
      |        |        |
   Broker1  Broker2  Broker3
```

Like a database master node controlling everything.

Kafka intentionally avoids this because:

```text
What if the brain dies?
```

Then the whole cluster dies.

Instead Kafka is designed as:

```text
+-----------+
| Broker 1  |
+-----------+
      ^
      |
      v
+-----------+
| Broker 2  |
+-----------+
      ^
      |
      v
+-----------+
| Broker 3  |
+-----------+
```

Every broker is a full Kafka server.

They communicate over TCP networking just like microservices communicate over HTTP/gRPC.

---

# What Actually Runs on a Broker?

Imagine 3 Linux servers.

```text
Server A
 └─ Kafka Broker 1

Server B
 └─ Kafka Broker 2

Server C
 └─ Kafka Broker 3
```

Each broker process:

* listens on a port (usually 9092)
* accepts producer connections
* accepts consumer connections
* talks to other brokers

Like:

```text
Broker1 <------TCP------> Broker2
Broker2 <------TCP------> Broker3
Broker1 <------TCP------> Broker3
```

They're constantly exchanging metadata.

---

# Then Who Keeps Cluster Information?

Historically:

```text
Kafka Brokers
      |
      |
   ZooKeeper
```

ZooKeeper was the metadata manager.

It knew:

* which brokers are alive
* topic metadata
* partition leaders
* cluster state

---

Today (Modern Kafka)

Kafka removed ZooKeeper.

Now it uses:

### KRaft Mode

(Kafka Raft)

Some brokers become:

```text
Controller Nodes
```

Example:

```text
Broker1
Broker2
Broker3  <-- Controller
```

or

```text
Controller1
Controller2
Controller3
```

These controllers store cluster metadata.

---

# Think of It Like Kubernetes

You know Kubernetes?

```text
Control Plane
     |
 Worker Nodes
```

Kafka KRaft is similar.

```text
Controller Nodes
      |
 Kafka Brokers
```

Controller manages metadata.

Brokers manage actual data.

---

# What Metadata Is Being Managed?

Imagine you create:

```text
Topic = Orders
Partitions = 3
Replication = 2
```

Someone must remember:

```text
Partition 0 -> Broker 1
Partition 1 -> Broker 2
Partition 2 -> Broker 3
```

And:

```text
Leader P0 -> Broker1
Leader P1 -> Broker2
Leader P2 -> Broker3
```

That information lives in the cluster metadata.

---

# Example Cluster

Suppose:

```text
Broker 1
Broker 2
Broker 3
```

Topic:

```text
Orders
```

Partitions:

```text
P0
P1
P2
```

Distributed as:

```text
Broker1
  P0 (Leader)
  P1 (Replica)

Broker2
  P1 (Leader)
  P2 (Replica)

Broker3
  P2 (Leader)
  P0 (Replica)
```

Notice:

A broker stores many partitions.

A partition may exist on multiple brokers.

---

# How Does a Producer Know Where To Send Data?

This is the cool part.

Producer does NOT blindly send to random brokers.

Step 1:

Producer connects to ANY broker.

```text
Producer
    |
    v
 Broker1
```

Broker1 returns metadata:

```text
Orders Topic

P0 -> Leader Broker1
P1 -> Leader Broker2
P2 -> Leader Broker3
```

Producer caches this.

Now producer directly talks to correct broker.

```text
Producer
   |
   +-----> Broker1 (P0)
   |
   +-----> Broker2 (P1)
   |
   +-----> Broker3 (P2)
```

No middleman.

---

# How Do Brokers Detect Failures?

Brokers continuously heartbeat.

Think:

```text
Broker1:
"Hey Controller, I'm alive."

Broker2:
"Still alive."

Broker3:
"Still alive."
```

Every few seconds.

---

# What Happens If Broker1 Dies?

Before:

```text
P0 Leader -> Broker1
P0 Replica -> Broker3
```

Broker1 crashes.

Controller notices:

```text
Heartbeat missing
```

Controller elects new leader:

```text
P0 Leader -> Broker3
```

Cluster updates metadata.

Producers get refreshed metadata.

Traffic resumes.

---

# This Is Why Replication Exists

Without replication:

```text
Broker1 dies

P0 gone forever
```

With replication:

```text
Broker1 dies

Replica promoted
```

No data loss (assuming proper configuration).

---

# Compare To Microservices

Microservices:

```text
Order Service
   |
   v
Payment Service
   |
   v
Inventory Service
```

Every service knows every other service.

Network becomes messy.

```text
Order --> Payment
Order --> Inventory
Order --> Notification
Order --> Analytics
```

Many connections.

---

Kafka:

```text
Order Service
      |
      v
    Kafka
   /  |  \
  /   |   \
Payment
Inventory
Analytics
```

Now services don't know each other.

But Kafka itself is still a distributed cluster:

```text
          Controller
               |
     --------------------
     |        |         |
 Broker1  Broker2  Broker3
```

---

# Physical Communication

Under the hood:

It's simply TCP sockets.

Like:

```text
Broker1
  IP: 10.0.0.1

Broker2
  IP: 10.0.0.2

Broker3
  IP: 10.0.0.3
```

Kafka config contains:

```properties
controller.quorum.voters=
1@10.0.0.1:9093,
2@10.0.0.2:9093,
3@10.0.0.3:9093
```

Each broker knows:

```text
Who are the other brokers?
Who are the controllers?
```

and opens TCP connections accordingly.

Exactly like distributed microservices communicating over the network.

---

### Beginner misconception

Many people think:

```text
Topic -> Broker
```

Wrong.

A topic is only a **logical concept**.

Reality is:

```text
Topic
  |
Partitions
  |
Files on Disk
  |
Stored on Brokers
```

A broker never stores a "topic file".

It stores partition directories.

```text
Broker1

/orders-0/
/payments-2/
/users-1/
```

The broker only sees partitions.

The topic exists mostly in metadata.

---

Checking question before we go deeper:

Suppose you have:

```text
3 Brokers
Orders Topic
6 Partitions
Replication Factor = 2
```

Can a single broker contain **multiple partitions of the same topic**, and can a single partition exist on **multiple brokers at the same time**? Why would Kafka want both of those to be true?
