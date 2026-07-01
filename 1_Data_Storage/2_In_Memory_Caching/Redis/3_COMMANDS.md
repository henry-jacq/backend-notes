---
title: "Redis Common Commands"
part: 2
part_title: "Data Storage"
chapter: 8
summary: "Covers the common Redis commands for basic key management and the main data types."
---
# Redis Common Commands

Covers the common Redis commands for basic key management and the main data types.

## Key commands

- `SET key value`
  - Store a string value for a key.
- `GET key`
  - Retrieve the value stored at a key.
- `DEL key [key ...]`
  - Remove one or more keys.
- `EXPIRE key seconds`
  - Set a TTL for a key. The key is deleted after the TTL expires.
- `TTL key`
  - Return the remaining TTL in seconds, or `-1` if the key exists without expiration.
- `PERSIST key`
  - Remove the expiration from a key.
- `FLUSHDB`
  - Delete all keys in the current database.
- `FLUSHALL`
  - Delete all keys in all databases.
- `EXISTS key`
  - Check whether a key exists.
- `KEYS pattern`
  - Return keys matching a pattern. Use with caution in production because it may be slow on large databases.

## String commands

- `SETEX key seconds value`
  - Set a string value and expiration in one command.
- `SETNX key value`
  - Set the value only if the key does not already exist.
- `MSET key value [key value ...]`
  - Set multiple key-value pairs in one call.
- `MGET key [key ...]`
  - Retrieve multiple values in one call.
- `INCR key`
  - Increment an integer string value by one.
- `DECR key`
  - Decrement an integer string value by one.
- `INCRBY key increment`
  - Increment an integer string value by a specific amount.
- `DECRBY key decrement`
  - Decrement an integer string value by a specific amount.
- `APPEND key value`
  - Append a string to the current value.
- `STRLEN key`
  - Return the length of the string stored at the key.

## Hash commands

- `HSET key field value`
  - Set the string value of a field in a hash.
- `HGET key field`
  - Get the value of a field in a hash.
- `HGETALL key`
  - Return all fields and values in a hash.
- `HMGET key field [field ...]`
  - Get the values of multiple fields.
- `HDEL key field [field ...]`
  - Remove one or more fields from a hash.
- `HEXISTS key field`
  - Check whether a field exists in a hash.
- `HLEN key`
  - Return the number of fields in a hash.
- `HINCRBY key field increment`
  - Increment the integer value of a field by the given amount.

## List commands

- `LPUSH key value [value ...]`
  - Insert one or more values at the head of a list.
- `RPUSH key value [value ...]`
  - Insert one or more values at the tail of a list.
- `LPOP key`
  - Remove and return the first element of a list.
- `RPOP key`
  - Remove and return the last element of a list.
- `LRANGE key start stop`
  - Return a range of elements from a list.
- `LINDEX key index`
  - Get an element by its index in the list.
- `LLEN key`
  - Return the length of a list.
- `LSET key index value`
  - Set the list element at index to a new value.
- `LPUSHX key value`
  - Push a value onto the head only if the list already exists.
- `LINSERT key BEFORE|AFTER pivot value`
  - Insert a value before or after the pivot element.

## Set commands

- `SADD key member [member ...]`
  - Add one or more members to a set.
- `SMEMBERS key`
  - Return all members of a set.
- `SCARD key`
  - Return the number of members in a set.
- `SREM key member [member ...]`
  - Remove one or more members from a set.
- `SMISMEMBER key member [member ...]`
  - Check if one or more members exist in a set.
- `SPOP key [count]`
  - Remove and return one or more random members.
- `SDIFF key [key ...]`
  - Return the difference between sets.
- `SUNION key [key ...]`
  - Return the union of sets.
- `SINTER key [key ...]`
  - Return the intersection of sets.
- `SMOVE source destination member`
  - Move a member from one set to another.

## Sorted set commands

- `ZADD key score member [score member ...]`
  - Add one or more members with scores to a sorted set.
- `ZRANGE key start stop [WITHSCORES]`
  - Return a range of members by index.
- `ZREM key member [member ...]`
  - Remove one or more members from a sorted set.
- `ZRANK key member`
  - Return the rank of a member in the sorted set.
- `ZSCORE key member`
  - Return the score of a member.
- `ZCARD key`
  - Return the number of members in a sorted set.
