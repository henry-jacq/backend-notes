---
title: "Geospatial Indexing and Proximity Search"
part: 2
part_title: "Data Storage"
chapter: 5
summary: "Explains how databases index and query two-dimensional spatial data, comparing specialised spatial trees (R-trees, Quadtrees) against space-filling curves and encoded keys (Geohashes, S2, H3)."
---
# Geospatial Indexing and Proximity Search

Proximity search is a core requirement for ride-sharing dispatch, local delivery routing and location-based recommendations. These applications frequently query the closest points (e.g. drivers near a rider) or determine if a coordinate falls inside a service zone. 

Geographic queries pose unique indexing challenges that traditional database structures cannot solve efficiently.

## The Spatial Indexing Challenge

Standard database indexes like B-trees are one-dimensional (1D). They sort keys sequentially along a single line (e.g. numeric IDs, timestamps or alphabetical names). 

Geospatial coordinates, however, are two-dimensional (2D), consisting of latitude and longitude. Sorting data along a single dimension does not preserve geographic closeness in 2D space:

-   **The 1D Sorting Problem:** If you sort records by latitude alone, two coordinates with similar latitudes will be adjacent in the index, even if their longitudes are on opposite sides of the globe.
-   **Separate 1D Indexes:** Creating separate B-trees on latitude and longitude is highly inefficient. A query for a small bounding box requires intersecting the results of both index scans. This process forces the database to scan millions of candidate rows only to discard the vast majority of them.

To query proximity efficiently, databases must map 2D coordinates to a structure that preserves spatial closeness. Modern systems use two primary architectural approaches: **Custom Spatial Trees** and **Encoded Keys (Space-Filling Curves)**.



## 1. Custom Spatial Trees

Custom spatial trees are purpose-built structures designed to group and balance multi-dimensional geometric data on disk or in memory.

### Quadtrees and KD-Trees

-   **Quadtree (1974):** Recursively subdivides 2D space into four quadrants (North-East, North-West, South-East, South-West) until each quadrant contains fewer than a threshold number of points. It handles varying density well but can become deeply unbalanced in highly populated urban areas.

```
Quadtree Space Partitioning:
+-------------------+-------------------+
|                   |         •         |
|      NW (01)      |      NE (00)      |
|                   |                   |
+-------------------+---------+---------+
|                   |    •    |         |
|      SW (10)      |  (110)  |  (111)  |
|                   |---------+---------|
|                   |         |    •    |
+-------------------+---------+---------+
```

-   **KD-tree (1975):** A binary search tree that alternates axis splits (e.g. splitting on latitude at level 1, then longitude at level 2). While excellent for in-memory nearest-neighbour searches, both Quadtrees and KD-trees suffer from poor disk performance because following pointers across nodes forces random disk I/O.

### R-Trees and R*-Trees
-   **R-Tree (1984):** Groups spatial objects (points, lines or polygons) into nested **Minimum Bounding Rectangles (MBRs)**. It is a balanced tree structure specifically optimized for disk page layouts, allowing predictable disk read performance.
-   **R*-Tree (1990):** Implements smarter insertion algorithms to minimize MBR overlap. This structure powers spatial indexing extensions in mature databases, such as PostGIS (PostgreSQL), SpatiaLite (SQLite) and Oracle Spatial.

<div class="takeaway-box">
    <strong>Key Takeaway on Spatial Trees:</strong> Spatial trees are ideal for complex geometries. They natively index and query exact containment or intersection of lines (e.g. roads) and polygons (e.g. delivery zones). However, write performance is moderate to low due to complex rebalancing heuristics during updates, making them less suitable for highly dynamic point data.
</div>



## 2. Encoded Keys (Space-Filling Curves)

Encoded key approaches project 2D geographic coordinates into a single, sortable 1D integer or string key. This allows systems to leverage existing, highly optimized B-tree indexes without requiring custom database engines or spatial extensions.

### The Space-Filling Curve (Z-Order)
To flatten 2D coordinates into a 1D sequence while preserving spatial proximity, Geohashing interleaves the bits of latitude and longitude. The resulting binary path forms a Z-order space-filling curve (Morton curve):

```
Z-Order Morton Curve:
00 (NW) ---------> 01 (NE)
                    /
                   /
                  /
                 v
10 (SW) ---------> 11 (SE)
```

By following this recursive Z-shape, geographic space is divided into a grid where close prefix matches represent close physical neighbours.

### Why Encoded Keys are Recommended for Live Point Tracking
In modern high-throughput architectures (e.g. tracking moving vehicles, live deliveries or active users), coordinates update constantly.

-   **Custom Tree Overhead:** In custom spatial trees like R-trees, moving a coordinate requires deleting a point from a node, potentially triggering structural splits or merges and then inserting the point elsewhere. This rebalancing is CPU-intensive and prone to lock contention under concurrent writes.
-   **B-Tree Range Updates:** With space-filling encodings, a coordinate update is simplified into a fast, O(log N) key update in a standard B-tree index. This structure scales seamlessly to millions of writes using generic database clusters.

### Core Techniques

| Indexing Method | Geometric Primitive | Properties | Common Implementations |
| :--- | :--- | :--- | :--- |
| **Geohash (2008)** | Square grid | Divides the globe into hierarchical grids represented by base-32 strings. Prefix matching implies spatial proximity. | Redis GEO commands (stored as sorted set zset integers) |
| **S2 (2011)** | Spherical projection | Projects the globe onto the six faces of a cube, subdividing them using a Hilbert curve. Highly optimized for spherical geometry. | MongoDB `2dsphere` indexes |
| **H3 (2008)** | Hexagonal tiling | Uses hierarchical hexagons. Hexagons are ideal for proximity search because every neighbour cell is equidistant (six equidistant neighbours). | Uber dispatching and dynamic surge pricing |

### Key Architectural Implementations

-   **The 3x3 Grid Trick:** Because grid borders are artificial, two coordinates separated by a few meters might fall into different parent cells (boundary artifacts). To prevent missing close points, proximity queries must scan the target cell plus its eight surrounding neighbours (a 3x3 grid) and apply post-query distance filtering.
-   **Multi-Resolution Zoom:** Hierarchical encodings (like Geohash or H3) allow clients to alter the resolution by truncating the key. For example, a 5-character Geohash covers ~5 km, while a 9-character Geohash narrows down to ~5 m.



## Spatial Index Selection Matrix

| Dimension | Custom Spatial Trees (e.g. R-Tree) | Encoded Keys (e.g. Geohash, H3) |
| :--- | :--- | :--- |
| **Supported Data** | Points, lines, complex polygons | Points only (polygons require approximation) |
| **Disk Performance** | High (page-aligned balanced trees) | Very high (standard B-Tree range scans) |
| **Write Throughput** | Moderate (costly balancing overhead) | Extremely high (simple integer key updates) |
| **Implementation Cost** | High (requires spatial database extensions) | Low (compatible with any generic key-value store) |
| **Primary Use Cases** | Geographic Information Systems (GIS), delivery zones | Ride-sharing dispatch, live vehicle tracking, rate limiting |



## SQL Index Types

Modern databases handle indexing requirements differently depending on the query semantics:

### 1. Hash Indexes (O(1) Exact Matches)
A Hash index uses a hash function to map keys to bucket addresses. It is extremely fast for exact match lookups (`=`) but cannot perform range scans or handle inequality queries.

```sql
-- Create a hash index for exact string matching in PostgreSQL
CREATE INDEX idx_user_sessions ON sessions USING HASH (session_token);

-- Query using the hash index (O(1) lookup performance)
SELECT * FROM sessions WHERE session_token = 'xyz123';
```

### 2. B-Tree Indexes on Encoded Keys (Geohashing)
By storing a spatial coordinate as a Geohash string, standard B-tree range queries can retrieve nearby locations by matching common prefixes.

```sql
-- Query drivers in a specific region using Geohash prefix range scan on a standard B-tree
SELECT * FROM drivers 
WHERE geohash LIKE 'tdr1v%' 
  AND ST_Distance(geom, ST_MakePoint(77.59, 12.97)) < 5000;
```

### 3. R-Tree Indexes (GiST in PostGIS)
R-trees allow queries on complex shapes (like polygons and lines). PostGIS implements this using Generalized Search Trees (GiST).

```sql
-- Create a spatial index using GiST (which builds an underlying R-Tree)
CREATE INDEX idx_zones_geom ON delivery_zones USING GIST (geom);

-- Query containment of a coordinate inside delivery zone polygons
SELECT name FROM delivery_zones 
WHERE ST_Contains(geom, ST_SetSRID(ST_Point(77.59, 12.97), 4326));
```



## Database Index Selection Flow

When designing database queries at scale, use this logical pathway to determine the most efficient access path and index structure:

![Database Index Selection Flow](1_Data_Storage/1_Relational_Databases/index-selection-flow.png)
