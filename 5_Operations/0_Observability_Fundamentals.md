---
title: "Observability Fundamentals"
part: 7
part_title: "Operations"
chapter: 1
summary: "Explores the core pillars of system observability, contrasting metrics, logs, traces and alerting strategies while introducing Prometheus, Grafana, Jaeger and log rotation policies."
---
# Observability Fundamentals

Production systems fail in unpredictable ways. A database connection pool may saturate, response latency may spike at midnight, or a memory leak may slowly degrade resources over several days. Without visibility into these internal states, troubleshooting degenerates into blind guesswork. Observability provides the telemetry required to understand system behavior, identify root causes and optimize performance under live production loads.



## 1. Why Observability Matters

Traditional debugging is a manual, interactive process performed during development. Using breakpoints, local testing setups and stack traces, developers inspect execution flows in real time. However, this model does not scale to production, where requests execute concurrently, state is distributed and stopping execution is impossible.

Observability is a continuous, automated telemetry pipeline. Instead of stepping through code, operations teams monitor active workloads using structured telemetry. 

While logging can expose anomalies that prompt deeper debugging, insights from debugging inform what details you choose to observe. Together, they establish a closed-loop diagnostic lifecycle.



## 2. The Three Pillars of Observability

Observability relies on three primary data types: **Metrics**, **Logs** and **Traces**. Each serves a distinct diagnostic role and they are typically visualised using specialized monitoring stacks like Prometheus, Grafana, Zipkin and Jaeger.

```
+--------------------------------------------------------------------------+
|                       THE OBSERVABILITY TRIAD                            |
+-------------------------------------+------------------------------------+
|               METRICS               |                LOGS                |
|  "What is the system load?"         |  "What exact event occurred?"      |
|  - Quantitative (Numbers over time) |  - Discrete, timestamped prose     |
|  - Managed via Prometheus/Grafana   |  - Centralized in ELK/CloudWatch   |
+-------------------------------------+------------------------------------+
                                      |
                                      v
                             +------------------+
                             |     TRACES       |
                             |  "Where is the   |
                             |   bottleneck?"   |
                             |  - Span timelines|
                             |  - Jaeger/Zipkin |
                             +------------------+
```

### Metrics (Quantitative State)
Metrics are numeric measurements aggregated over time, characterized by low storage overhead and high query speeds.

-   **Scrape Pipeline:** Prometheus pulls metrics at regular intervals from application endpoints via HTTP scrape loops, storing data in a local Time-Series Database (TSDB).
-   **Dashboard Visualization:** Grafana queries these metrics using PromQL, plotting trends such as request rates, resource utilization (CPU, memory, disk I/O) and cache hit ratios.
-   **Limitations:** Metrics show *that* a latency spike occurred, but they cannot show *why* individual transactions failed.

### Logs (Discrete Events)
Logs represent chronological records of events occurring within a software application or host operating system.

-   **Categories:** Modern applications generate Access logs (tracking request routes), Error logs (failed database connections), Event logs (completed cron exports) and Audit logs (security privilege changes).
-   **Metadata:** A structured log include a precise timestamp, context information (request ID, environment, user ID) and a descriptive message.
-   **Log Levels:** Logs are classified by severity (DEBUG, INFO, WARN, ERROR, FATAL) to help teams prioritize and filter alerts.
-   **Aggregation:** Platforms like AWS CloudWatch Logs or Elasticsearch ingest log events to support centralized full-text search.

### Traces (Distributed Request Paths)
Traces record the end-to-end execution path of a single request as it propagates through a distributed microservices network.

-   **Architecture:** Trace tools like Zipkin or Jaeger instrument applications to inject unique Trace IDs and Span IDs into outgoing HTTP headers.
-   **Span timelines:** The trace maps how much time was spent inside each dependency (e.g. database query, authorization filter, API gateway transition).



## 3. How Observability Works Under the Hood

### Prometheus Metrics Scrape Loop
Rather than applications pushing metrics to a central storage engine, Prometheus operates on a pull-based model:

-   **Scrape Target Discovery:** Prometheus discovers active targets using static files or dynamic service registries (e.g. Kubernetes API).
-   **HTTP Poll:** At a configured interval (such as every 15 seconds), Prometheus sends an HTTP GET request to each target's `/metrics` endpoint, pulling text-formatted metric counts.
-   **TSDB Writing:** The retrieved values are appended directly to the local Time-Series Database, index-mapped by label sets.

### Distributed Trace Propagation
To trace a request traversing multiple network boundaries, microservices must coordinate to pass context parameters:

-   **Context Injection:** The originating service creates a globally unique `Trace ID` and a parent `Span ID`. When calling a downstream service, it injects these identifiers into the HTTP headers (standardized by the W3C Trace Context specification as `traceparent`).
-   **Context Extraction:** The downstream service extracts the headers, starts a new child span and passes the updated headers to any subsequent calls.
-   **Asynchronous Collection:** Each microservice asynchronously sends completed span records to a centralized trace collector (such as Zipkin or Jaeger) via UDP or gRPC, preventing trace collection from blocking request execution.



## 4. What If Things Break? (Observability Failure Modes)

### Distributed Trace Performance Overhead
Tracing every single network request incurs noticeable serialization, memory and network bandwidth costs:

-   **What happens:** Under high-traffic loads, the overhead of exporting traces synchronously can overwhelm microservice container resources, causing CPU spikes and network congestion.
-   **Mitigation:** Configure probabilistic sampling (e.g. collecting traces for only 1% or 0.1% of requests) rather than tracing 100% of network traffic.

### Alert Fatigue and Monopolization
Setting noisy alert thresholds leads to operator desensitization, where critical alerts are missed because of constant false alarms:

-   **What happens:** If CPU alerts trigger at 70% during normal batch processing cycles, team members begin ignoring notifications, missing the genuine outage that occurs later.
-   **Mitigation:** Alert strictly on actionable conditions (e.g. user-facing error rate exceeding 1%) rather than transient resource usage anomalies.
