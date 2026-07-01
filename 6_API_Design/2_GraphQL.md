---
title: "GraphQL"
part: 6
part_title: "API Design"
chapter: 3
summary: "GraphQL is a query language for APIs, developed by Facebook in 2012 and open-sourced in 2015. It was created to..."
---
# GraphQL

GraphQL is a query language for APIs, developed by Facebook in 2012 and open-sourced in 2015. It was created to solve a specific problem: mobile clients at Facebook needed different data than web clients, and REST APIs were either returning too much data (over-fetching) or requiring too many requests (under-fetching).

GraphQL is not a replacement for REST. It solves different problems and creates different ones.

## The problem GraphQL solves

### Over-fetching with REST

```
REST: GET /users/123

Response:
{
  "id": 123,
  "name": "Alice",
  "email": "alice@example.com",
  "phone": "+1-555-0100",
  "address": { ... },
  "preferences": { ... },
  "created_at": "2024-01-01",
  "updated_at": "2024-06-15",
  "avatar_url": "...",
  "bio": "..."
}

Mobile app only needs: name and avatar_url
-> 80% of the response data is wasted bandwidth
```

### Under-fetching with REST

```
To render a user profile page:
  GET /users/123           -> user data
  GET /users/123/posts     -> user's posts
  GET /users/123/followers -> follower count
  GET /users/123/following -> following count

4 HTTP requests to render one page
On mobile: 4 round trips × 200ms each = 800ms minimum
```

### GraphQL solution

```
One request:

POST /graphql
{
  user(id: 123) {
    name
    avatarUrl
    posts(first: 5) {
      title
      createdAt
    }
    followersCount
    followingCount
  }
}

One response with exactly the data needed.
```

## Core concepts

### Schema definition

GraphQL is schema-first. The schema defines what clients can query.

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
  followers: [User!]!
  followersCount: Int!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
  createdAt: DateTime!
}

type Comment {
  id: ID!
  text: String!
  author: User!
}
```

The `!` means non-nullable. `[Post!]!` means a non-nullable list of non-nullable Posts.

### Queries (reading data)

```graphql
query GetUser {
  user(id: 123) {
    name
    email
    posts(first: 10) {
      title
      createdAt
    }
  }
}
```

The client specifies exactly which fields it needs. The server returns only those fields.

### Mutations (writing data)

```graphql
mutation CreatePost {
  createPost(input: {
    title: "GraphQL in Production"
    content: "..."
  }) {
    id
    title
    createdAt
  }
}
```

Mutations modify data. The response contains the created/updated resource — the client specifies which fields to return.

### Subscriptions (real-time updates)

```graphql
subscription OnNewComment {
  commentAdded(postId: 456) {
    id
    text
    author {
      name
    }
  }
}
```

Subscriptions push data to the client when events occur. Implemented over WebSockets typically.

## The type system

GraphQL's type system is its strength. The schema is a contract between client and server.

```graphql
# Scalar types
String, Int, Float, Boolean, ID

# Custom scalars
scalar DateTime
scalar Email
scalar URL

# Enums
enum OrderStatus {
  PENDING
  SHIPPED
  DELIVERED
  CANCELLED
}

# Input types (for mutations)
input CreateUserInput {
  name: String!
  email: Email!
  role: UserRole = VIEWER    # default value
}

# Interfaces
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  name: String!
}

# Union types
union SearchResult = User | Post | Comment
```

The type system enables:
- Automatic validation (invalid queries rejected before execution)
- IDE autocompletion
- Generated client code (TypeScript types from schema)
- Self-documenting API

## Resolvers

Resolvers are functions that fetch data for each field in the schema.

```
Schema:                      Resolver:

type User {
  id: ID!                    -> return user.id from database
  name: String!              -> return user.name from database
  posts: [Post!]!            -> query posts table WHERE author_id = user.id
  followersCount: Int!       -> query COUNT(*) from followers WHERE user_id = user.id
}
```

Each field has a resolver. Parent fields resolve first, then child fields use the parent's result.

```
Query:
{
  user(id: 123) {         <- Root resolver: fetch user 123 from DB
    name                   <- Trivial resolver: return user.name
    posts {                <- Resolver: SELECT * FROM posts WHERE author_id = 123
      title                <- Trivial resolver: return post.title
      comments {           <- Resolver: SELECT * FROM comments WHERE post_id = ?
        text               <- Trivial resolver: return comment.text
      }
    }
  }
}
```

## The N+1 problem

The most critical performance issue in GraphQL.

```
Query:
{
  users(first: 10) {
    name
    posts {
      title
    }
  }
}

Execution:
1. Fetch 10 users           -> 1 query: SELECT * FROM users LIMIT 10
2. For each user, fetch posts:
   -> SELECT * FROM posts WHERE author_id = 1
   -> SELECT * FROM posts WHERE author_id = 2
   -> SELECT * FROM posts WHERE author_id = 3
   ... (10 queries)

Total: 1 + 10 = 11 queries for one GraphQL request
```

With nested relationships, this compounds:
```
10 users × 5 posts each × 3 comments each = 1 + 10 + 50 = 61 queries
```

### DataLoader: solving N+1

DataLoader batches and caches resolver calls within a single request.

```
Without DataLoader:
  SELECT * FROM posts WHERE author_id = 1
  SELECT * FROM posts WHERE author_id = 2
  SELECT * FROM posts WHERE author_id = 3
  ...

With DataLoader:
  SELECT * FROM posts WHERE author_id IN (1, 2, 3, ..., 10)
  -> 1 query instead of 10
```

**How DataLoader works:**
1. Collect all IDs requested in the current tick
2. Batch them into a single query
3. Distribute results back to individual resolvers
4. Cache results for the duration of the request

DataLoader is essential for production GraphQL. Without it, GraphQL APIs are slower than REST.

## Query complexity and depth limiting

Clients can write arbitrarily expensive queries:

```graphql
# Malicious or accidentally expensive query
{
  users(first: 1000) {
    posts(first: 100) {
      comments(first: 100) {
        author {
          posts(first: 100) {
            comments(first: 100) {
              text
            }
          }
        }
      }
    }
  }
}
```

This could trigger millions of database queries.

**Protections:**
- **Depth limiting** — reject queries deeper than N levels (typically 5-7)
- **Complexity scoring** — assign cost to each field, reject queries exceeding a budget
- **Pagination limits** — cap `first`/`last` arguments (max 100)
- **Timeout** — kill queries that take too long
- **Persisted queries** — only allow pre-approved query shapes in production

```
Complexity scoring example:

Field          | Cost
user           | 1
posts(first:N) | N × 2
comments       | 1

Query: user { posts(first: 10) { comments { text } } }
Cost: 1 + (10 × 2) + (10 × 1) = 31

Budget: 100
Result: allowed
```

## When GraphQL beats REST

- **Multiple client types** — mobile needs different data than web
- **Complex, nested data** — one query replaces multiple REST calls
- **Rapidly evolving frontend** — frontend teams add fields without backend changes
- **Aggregation layer** — single GraphQL API over multiple microservices

## When REST beats GraphQL

- **Simple CRUD** — GraphQL adds unnecessary complexity
- **File uploads** — GraphQL handles binary data poorly
- **Caching** — REST caches easily with HTTP caching (URL-based). GraphQL uses POST for everything, making HTTP caching impossible without extra tooling
- **Small teams** — GraphQL's tooling overhead may not pay off
- **Public APIs** — REST is more widely understood by external consumers

## GraphQL caching challenge

```
REST caching is simple:
  GET /users/123 -> cache by URL
  CDN, browser, proxy can all cache

GraphQL caching is hard:
  POST /graphql -> same URL, different query in body
  CDN cannot distinguish queries
  Need application-level caching
```

Solutions:
- **Persisted queries** — hash queries, use GET with query ID
- **Response caching** — cache full responses by query hash
- **Field-level caching** — cache individual resolver results
- **CDN integration** — tools like Apollo Server support CDN cache hints

## Common GraphQL mistakes

1. **Ignoring N+1** — deploying without DataLoader
2. **No query limits** — allowing arbitrarily expensive queries
3. **Exposing database schema** — GraphQL schema should model the domain, not the database
4. **Over-engineering** — using GraphQL for a simple CRUD API with one client
5. **No error handling** — GraphQL returns 200 even for errors. Errors are in the response body — handle them properly.

GraphQL solves the flexibility problem — clients get exactly the data they need. For service-to-service communication where performance and strong contracts matter more than flexibility, see [3_gRPC.md](file:///d:/Playground/Backend%20Notes/6_API_Design/3_gRPC.md).
