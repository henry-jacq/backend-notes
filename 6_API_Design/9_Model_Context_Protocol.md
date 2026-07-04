---
title: "Model Context Protocol (MCP)"
part: 6
part_title: "API Design"
chapter: 10
summary: "Introduces the Model Context Protocol (MCP), contrasting it with traditional APIs, detailing its client-server stdio/network architecture, tool/resource/prompt abstractions and configuration patterns for AI integrations."
---
# Model Context Protocol (MCP)

> [WARNING]
> **Protocol Stage Disclaimer:** The Model Context Protocol (MCP) is currently in its early development stages and has not yet been officially standardised across the broader web and networking bodies. It represents an emerging standard for AI-to-software semantic integration.

Historically, software communication was designed strictly for machine-to-machine interactions using structured, predefined contracts like REST, gRPC or GraphQL. However, the rise of Large Language Models (LLMs) and autonomous AI agents has introduced a new client type: software that must reason, discover and interact with its environment dynamically.

The **Model Context Protocol (MCP)** is an open-standard protocol designed to address this paradigm shift, serving as a semantic middleware translation layer between AI models and physical resources.



## Traditional APIs vs. Model Context Protocol

Traditional APIs are built on the assumption that the client program has hardcoded expectations about the server's endpoints, request shapes and response structures. MCP, by contrast, assumes the client (an AI model) has no prior knowledge of the target system and must discover capabilities dynamically.

```
Traditional API Model                       Model Context Protocol (MCP)
+------------------+                        +------------------+
|  Human Developer |                        |     AI Model     |
| (Hardcoded API)  |                        |  (Dynamic Query) |
+------------------+                        +------------------+
         |                                           |
         v (REST / gRPC)                             v (Handshake)
+------------------+                        +------------------+
|   Fixed Route    |                        |   MCP Server     |
| (/api/v1/users)  |                        |  (Self-Describes)|
+------------------+                        +------------------+
```

| Aspect | Traditional APIs | Model Context Protocol (MCP) |
| :--- | :--- | :--- |
| **Primary Client** | Other compiled programs or human developers | AI models and autonomous reasoning agents |
| **Contract Style** | Static, predefined routing endpoints | Dynamic, self-describing JSON schemas |
| **Integration Effort** | High (bespoke integration code for each API) | Low (generic plug-and-play client configurations) |
| **Adaptability** | Rigid (breaking changes require code rewrites) | High (model reasons and adapts to schema updates) |
| **Role in Stack** | Core data retrieval and transaction layer | Semantic translation layer wrapping underlying APIs |



## The Philosophy of Semantic Communication

In traditional systems, the integration contract defines raw inputs and outputs. Under the Model Context Protocol, however, the server provides more than structured output; it exposes a detailed **semantic description** of its capabilities.

Because LLMs reason exclusively using language, the textual descriptions in the JSON schemas are what guide the model's choices. To bridge the gap between AI agents and system resources, we provide an MCP server that the agent (or MCP client) uses to talk directly with our systems. This layout enables applications to be dynamically controlled by the LLM without requiring hardcoded logic or human intervention.



## Core Architectural Components

MCP establishes a clear bidirectional lifecycle using three primary abstraction primitives: **Tools**, **Resources** and **Prompts**.

When an AI client initiates a connection to an MCP server, they perform a handshake where the server registers its manifest (a JSON schema of its capabilities) directly into the model's system context.

### 1. Tools (Write Operations & Actions)
Tools represent write operations, allowing the model to change the state of the external world (e.g. clicking a button, running a script or sending an email).

-   The server exposes tools using standard JSON schemas.
-   The schema contains the tool name, a natural language description of what it does and detailed parameter data types.
-   The LLM reads this description and decides whether and how to invoke the tool.

### 2. Resources (Read Operations & Context)
Resources represent read operations, acting as a data feed that the model can inspect to gather context (e.g. system logs, file contents or database state).

-   Resources are identified using URI templates (such as `sys://logs/console` or `db://customer/stats`).
-   The model can retrieve these resources to inspect the environment before executing actions.

### 3. Prompts (Templates & Guidelines)
Prompts are server-defined templates designed to guide the model's reasoning process.

-   They provide domain-specific instructions on how the model should approach the tools and resources.
-   This keeps system-specific reasoning rules inside the server code, keeping the core AI agent framework plug-and-play.



## Connection and Execution Architecture

Most MCP implementations run over standard input/output (`stdio`) channels as background processes, though they can also operate over network sockets (such as WebSockets or HTTP SSE).

```
+---------------------+                    +----------------------+
|  MCP Client / Host  |    spawn stdio     |      MCP Server      |
|  (Claude Desktop)   | <================> |  (Background Process)|
+---------------------+     REST / gRPC    +----------------------+
                                                      |
                                                      v (API / OS calls)
                                           +----------------------+
                                           | Target Environment  |
                                           |  (Filesystem / OS)   |
                                           +----------------------+
```

### 1. Configuration (`mcp.json`)
The client spins up the server as a subprocess using a configuration file defining the executable path, command-line arguments and environment variables:

```json
{
  "mcpServers": {
    "filesystem-manager": {
      "command": "node",
      "args": ["/dist/filesystem-server/index.js", "--safe-mode"],
      "env": {
        "ROOT_DIR": "/var/data"
      }
    }
  }
}
```

### 2. Lifecycle Handshake Flow

1.  **Spawn:** The client spawns the server process according to the configured `command` and `args`.
2.  **Handshake:** The client sends an `initialize` request over the channel.
3.  **Registration:** The server responds with its manifest containing the JSON schemas of its Tools, Resources and Prompts.
4.  **Ready:** The client injects these capabilities into the LLM's system prompt. The model can now invoke the registered tools.



## Security and Guardrails in Autonomous Systems

Giving an AI agent direct access to systems introduces significant security risks. Because the agent executes tools dynamically based on system states, developers must consider what happens if something goes wrong. For example:

-   **Destructive Actions:** The agent could trigger a heavy database change, run a slow search query that locks tables or delete vital user assets.
-   **Resource Monopolisation:** The agent might hold open a network connection, access a file stream or run loops for unknown reasons, starving other system processes.

To mitigate these risks, developers must implement **guardrails** at the MCP server level:

-   **ReadOnly Scopes:** Enforce strict write privileges, permitting LLM tools to modify resources only when explicitly authorised.
-   **Transaction Auditing:** Require a human-in-the-loop validation layer for critical actions (such as dropping databases, modifying production states or running massive migrations).
-   **Resource Quotas:** Bind timeouts, memory limits and execution budgets to every tool call, preventing runaway agent actions from exhausting hardware resources.



<div class="takeaway-box">
    <strong>Key Takeaway:</strong> The Model Context Protocol represents a shift from machine-to-machine integrations to model-to-environment interactions. Rather than coding bespoke endpoint clients, developers design self-describing servers that explain *what* capabilities are available, allowing LLMs to reason and select tools dynamically.
</div>
