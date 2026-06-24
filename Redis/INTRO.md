# Redis

Redis is a key-value store that is often used as a database, cache, and message broker. It supports various data structures such as strings, hashes, lists, sets and sorted sets.

Redis is known for its high performance, scalability and support for complex data types. It can be used in a variety of applications, including real-time analytics, session management and pub/sub messaging systems.

---

### Logical Data Model

key: Printable ASCII string that uniquely identifies a value in the Redis database.

value: The data associated with a key, which can be of various types such as;

- Primitive types: integers, floats, and booleans.
- Container types: strings, lists, sets, sorted sets, and hashes.

---

### Common Commands

- **SET key value**: Sets the value of a key.
- **GET key**: Retrieves the value of a key.
- **DEL key**: Deletes a key and its associated value.
- **EXPIRE key seconds**: Sets a time-to-live (TTL) for a key, after which it will be automatically deleted.
- **FLUSHALL**: Removes all keys from the current database.
- **TTL key**: Returns the remaining time-to-live of a key in seconds.
- **SETEX key** seconds value: Sets the value of a key and its expiration time in one command.
- **PERSIST key**: Removes the expiration from a key, making it persistent.
- **KEYS pattern**: Returns all keys matching a given pattern.

  - \* : Matches any number of characters.
  - ? : Matches a single character.
  - \[ ] : Matches any one of the characters inside the brackets.
  - \ : Escapes special characters in the pattern.

- **STRLEN key**: Returns the length of the value
- **SETNX key value**: Set key value if key not exists
- **MSET [key value...]**: Set multiple key and value at same time
- **INCR key**: Increment the value
- **DECR key**: Decrement the value
- **INCRBY key increment_value**: Increment by specific value
- **DECRBY key decrement_value**: Decrement by specific value
- **APPEND key value**: The specified value is appended and updated string length is returned

---

### Redis Hashes

Redis hashset structure
```
Redis Key -> [
  Value: Redis Hash
  Field1 -> Value1
  Field2 -> Value2
  Field3 -> Value3
  Field4 -> Value4
]
```

- **HMSET [key value]**: Creates multiple hash key-values.
- **HGET key field_name**: Returns the value of the field in the hashset
- **HGETALL key**: Returns all the field name and value
- **HEXISTS key field_name**: Returns integer (0-false,1-true)
- **HDEL key field_name**: deletes a field name from the hashset
- **HSETNX key field_name value**: Setting the field & value if the field doesn't exist
- **HKEYS key**: returns all the field names
- **HLEN key**: returns the length of the key
- **HMGET key [field_name...]**: Returns values of multiple fields

---

### Redis Lists

It is lists of strings **sorted by their insertion order**. A list would have **head on the top** and **tail on the bottom**.


```
      Redis Key
          |
-----------------------
|value: redis list    |
|                     |
| HEAD <-> Value 1    |
|  ----------|        |
|  |                  |
| Value 2 <-> Value 3 |
|  --------------|    |
|  |                  |
| Value 4 <-> TAIL    |
|----------------------
```

- **LPUSH key [value...]**: Create a list of numbers
- **LPOP key**: Remove the last element from the top of list
- **LRANGE key from to**: used to retrieve list data using indices
- **RPUSH key value**: Will push into the end of the list (or tail)
- **RPOP key**: Remove the last element from the tail of the list
- **LINDEX index**: Returns the value in the index
- **LLEN key**: return the length of the value
- **LSET key index new_value**: set value by using index
- **LPUSHX key value**: used to set the key value if key not exists
- **LINSERT num BEFORE|AFTER pivot value**: Insert new value before or after the pivot element

---

don't fill with words generalized

### Redis Sets

```
Redis Key -> Redis Set (Multiple values)
```

The values in redis set are unique
And also it is unordered list

- **SADD key [values...]**: To create a set with key and values
- **SMEMBERS key**: To see the members of the set
- **SCARD key**: To see the count of members in the set
- **SDIFF set1 set2**: return the difference of two set values
- **SDIFFSTORE new_set set1 set2**: Stores the difference of two set values in new set
- **SUNION set1 set2**: Returns the combination of unique values from two sets
- **SUNIONSTORE new_set set1 set2**: Stores the combination of unique values from two sets
- **SREM set_name value**: removes the value from the set
- **SPOP key count**: removes random values based on given count
- **SINTER set1 set2**: returns unique combinations of intersecting values in both sets
- **SINTERSTORE set1 set2**: Stores unique combinations of intersecting values in both sets
- **SMOVE source_set dest_set value**: Move the value from one set to another

