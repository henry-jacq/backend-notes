---
title: "Redis Data Types"
part: 2
part_title: "Data Storage"
chapter: 7
summary: "Redis stores values using different built-in data structures. Each key has exactly one data type, and the data type..."
---
# Redis Data Types

Redis stores values using different built-in data structures. Each key has exactly one data type, and the data type determines which commands can be used on that key.

## String

- The simplest Redis value.
- Binary-safe sequence of bytes, up to 512 MB.
- Used for caching values, counters, small JSON strings, session tokens.
- Commands: `SET`, `GET`, `INCR`, `DECR`, `APPEND`, `STRLEN`, `SETEX`.

## Hash

- A collection of field-value pairs under one key.
- Useful for storing objects and records.
- Each field and value is a string.
- Commands: `HSET`, `HGET`, `HGETALL`, `HMGET`, `HINCRBY`, `HDEL`, `HLEN`.

## List

- An ordered sequence of strings.
- Supports insertions and removals at both ends.
- Useful for queues, recent activity feeds, and simple message lists.
- Commands: `LPUSH`, `RPUSH`, `LPOP`, `RPOP`, `LRANGE`, `LINDEX`, `LSET`.

## Set

- An unordered collection of unique strings.
- Useful for membership tests, tags, and unique lists.
- Commands: `SADD`, `SMEMBERS`, `SREM`, `SCARD`, `SISMEMBER`, `SUNION`, `SDIFF`, `SINTER`.

## Sorted Set

- A set of unique members, each with an associated score.
- Members are ordered by score.
- Useful for leaderboards, priority queues, and range queries.
- Commands: `ZADD`, `ZRANGE`, `ZREM`, `ZRANK`, `ZSCORE`, `ZCARD`.

## Additional types

Redis also includes specialized structures for advanced use cases:

- Bitmap operations on string values.
- HyperLogLog for approximate cardinality counting.
- Streams for event data and log-like message storage.

Each data type has specific command sets and behaviour. Choose the type that matches the access pattern and data shape for your workload.
