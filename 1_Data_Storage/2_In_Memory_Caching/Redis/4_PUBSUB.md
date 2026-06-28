# Redis Pub/Sub

Publish/subscribe is a messaging pattern in Redis. It allows one client to publish messages to a channel and many clients to receive those messages by subscribing.

## Concepts

- Publisher: a client that sends messages to a channel.
- Subscriber: a client that listens for messages on one or more channels.
- Channel: a named destination for messages.
- Pattern subscription: a subscriber can subscribe to channels that match a pattern.

Redis Pub/Sub is not a durable queue. Messages are delivered only to clients that are currently subscribed. If no subscriber is listening, published messages are discarded.

## Commands

- `SUBSCRIBE channel [channel ...]`
  - Subscribe the client to one or more channels.
- `UNSUBSCRIBE [channel ...]`
  - Unsubscribe the client from one or more channels.
- `PSUBSCRIBE pattern [pattern ...]`
  - Subscribe the client to channels that match one or more patterns.
- `PUNSUBSCRIBE [pattern ...]`
  - Unsubscribe the client from one or more patterns.
- `PUBLISH channel message`
  - Publish a message to a channel.

## Behavior

- Subscribers receive messages only while they remain connected and subscribed.
- Channels do not store messages. Redis forwards messages directly to active subscribers.
- Pub/Sub is useful for real-time notifications, event fan-out, and lightweight inter-process communication.
