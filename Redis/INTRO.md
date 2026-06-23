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
