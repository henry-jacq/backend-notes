
Redis is a key-value store that is often used as a database, cache, and message broker. It supports various data structures such as strings, hashes, lists, sets, and sorted sets. Redis is known for its high performance, scalability, and support for complex data types. It can be used in a variety of applications, including real-time analytics, session management, and pub/sub messaging systems.


Logical Data Model:

key: Printable ASCII string that uniquely identifies a value in the Redis database.

value: The data associated with a key, which can be of various types such as;
- Primitive types: integers, floats, and booleans.
- Container types: strings, lists, sets, sorted sets, and hashes.

Common Commands:

- SET key value: Sets the value of a key.
- GET key: Retrieves the value of a key.
- DEL key: Deletes a key and its associated value.
- EXPIRE key seconds: Sets a time-to-live (TTL) for a key, after which it will be automatically deleted.
- FLUSHALL: Removes all keys from the current database.