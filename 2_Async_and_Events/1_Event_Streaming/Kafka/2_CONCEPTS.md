---
title: "Kafka Concepts"
part: 3
part_title: "Async and Events"
chapter: 5
summary: "Explains the key Kafka concepts from `prompt.md`."
---
# Kafka Concepts

Explains the key Kafka concepts from `prompt.md`.

## Message
A message is a single record or event sent to Kafka. It contains a key, a value and optional metadata such as a timestamp and headers.

- Definition: a unit of data produced to Kafka.
- Analogy: a shipping label attached to a package.
- Architecture: a producer sends messages to a topic and a consumer reads them from a partition.
- Without it: Kafka would have nothing to store or transport.

## Producer
A producer is a client application that writes messages to a Kafka topic.

- Definition: the source of data in Kafka.
- Analogy: a factory that packages and sends goods into a delivery network.
- Architecture: it connects to a broker, obtains topic metadata and sends messages to the correct partition.
- Without it: there would be no new data entering Kafka.

## Consumer
A consumer reads messages from one or more Kafka partitions.

- Definition: an application that reads and processes Kafka messages.
- Analogy: a warehouse worker opening packages from a conveyor belt.
- Architecture: it connects to brokers, fetches messages from assigned partitions and tracks offsets.
- Without it: data would accumulate in Kafka without being processed.

## Topic
A topic is a named category for storing messages.

- Definition: the logical stream or feed of related messages.
- Analogy: a mailbox for a specific type of message, such as orders or logs.
- Architecture: producers write to a topic and consumers subscribe to it.
- Without it: Kafka would have no way to organize different types of data.

## Partition
A partition is a unit of parallelism and ordering within a topic.

- Definition: an ordered, append-only sequence of messages inside a topic.
- Analogy: a lane on a highway where cars follow one another.
- Architecture: each topic is split into partitions and each partition is stored on one or more brokers.
- Without it: Kafka would be a single queue and could not scale efficiently.

## Broker
A broker is a Kafka server that stores partitions and handles client requests.

- Definition: a Kafka node that accepts reads and writes.
- Analogy: a post office that keeps packages and delivers them to customers.
- Architecture: brokers hold partition logs, serve producers and consumers and exchange metadata with other brokers.
- Without it: Kafka would have no storage or runtime process.

## Cluster
A cluster is a group of Kafka brokers working together.

- Definition: the distributed Kafka deployment.
- Analogy: a fleet of delivery trucks and warehouses coordinating to move packages.
- Architecture: brokers share metadata, maintain replication and provide fault tolerance as a cluster.
- Without it: Kafka would be a single, non-resilient server.

## Consumer Group
A consumer group is a group of consumers that coordinate to read a topic together.

- Definition: a set of consumers sharing a group ID and dividing partition consumption.
- Analogy: a team of workers that split an assembly line among themselves.
- Architecture: each partition is consumed by only one consumer within the group, enabling parallel processing.
- Without it: scaling consumers would be harder and duplicate processing would be common.

## Replication
Replication makes copies of partition data across multiple brokers.

- Definition: the process of storing the same partition log on more than one broker.
- Analogy: making backup copies of a document in several safes.
- Architecture: one replica is the leader and others are followers. Followers copy data from the leader.
- Without it: Kafka would lose data if a broker failed.

## Offset
An offset is the position of a message in a partition.

- Definition: a sequential number assigned to each message within a partition.
- Analogy: a page number in a book.
- Architecture: consumers use offsets to remember where they stopped reading.
- Without it: consumers could not resume reliably or know which messages they already processed.

## Logical vs Physical

- Topic: logical boundary for a stream of messages.
- Partition: physical slice of a topic that stores ordered logs.
- Broker: physical server that holds partitions on disk.

Each topic may span multiple partitions. Each partition is stored on one or more brokers. This separation allows Kafka to scale and remain fault tolerant.

## Example

1. A producer sends an order message to the `orders` topic.
2. Kafka assigns the message to a partition based on a key or partitioner.
3. The message is appended to the partition log on one broker.
4. A consumer in a consumer group reads the message from that partition.
5. The consumer commits the offset after processing.

## Ordering

- Kafka guarantees the order of messages within a single partition.
- Kafka does not guarantee a global order across partitions.
- Keys affect partition assignment and records with the same key usually go to the same partition.

## Why Kafka uses partitions and brokers

- Partitions provide parallelism and allow many consumers to process data concurrently.
- Brokers provide storage and availability for partitions.
- Kafka uses partitioned logs instead of one giant queue to support large volumes and high throughput.
