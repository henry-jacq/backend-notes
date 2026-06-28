# Kafka Basics

## Topic
A topic is a named stream of records. It is the logical category where producers write and consumers read data.

## Partition
A partition is an ordered, immutable sequence of records within a topic. Each record in a partition has an increasing offset.

## Broker
A broker is a Kafka server that stores partitions and serves client requests. Multiple brokers form a Kafka cluster.

## Cluster
A cluster is a group of Kafka brokers that work together. The cluster stores data and provides fault tolerance.

## Producer
A producer publishes records to a topic. The producer chooses the partition for each record, either automatically or explicitly.

## Consumer
A consumer reads records from one or more partitions. Consumers track their position using offsets.

## Consumer Group
A consumer group is a set of consumers that coordinate to read a topic in parallel. Each partition is read by only one consumer in the group.

## Replication
Replication copies partition data across multiple brokers. It provides availability and fault tolerance.

## Offset
An offset is a unique identifier for a record within a partition. Consumers use offsets to resume reading from a specific position.

## Ordering
Kafka guarantees order only within a partition. Records in different partitions may be processed in any order.
