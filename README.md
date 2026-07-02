# Backend Notes: Systems Engineering

This repository contains structured systems engineering notes compiled into a single book-style PDF.

## Structure of the Book

The notes are organised into seven distinct parts:

- **Part I: Foundations** — Core systems engineering thinking, scaling, queues and performance engineering fundamentals.
- **Part II: Data Storage** — Relational database limits, sharding, CRUD operations at scale and in-memory caching with Redis.
- **Part III: Async and Events** — Messaging patterns, message semantics, Kafka event streaming and distributed transactions (Sagas).
- **Part IV: Reliability and Availability** — Defensive patterns (retries, circuit breakers, bulkheads), replication and multi-region failover.
- **Part V: Infrastructure** — HTTP/TCP networking, web server architectures (Nginx/Apache) and request execution flows.
- **Part VI: API Design** — Protocols, REST, GraphQL, gRPC, state management, versioning, security and API gateways.
- **Part VII: Operations** — Observability fundamentals (metrics, logs, traces), alerting and systematic production debugging.

## PDF Compilation Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install GTK & Pango Dependencies (Windows)
WeasyPrint requires GTK3 and Pango for document rendering. Install these using MSYS2:

1. Download and run the installer from the [MSYS2 website](https://www.msys2.org/).
2. Launch the **MSYS2 UCRT64** terminal from your Start Menu.
3. Update the package database:
   ```bash
   pacman -Syu
   ```
4. Install the required GTK3 and Pango packages:
   ```bash
   pacman -S mingw-w64-ucrt-x86_64-gtk3 mingw-w64-ucrt-x86_64-pango
   ```

The compile script automatically loads these DLLs from `C:\msys64\ucrt64\bin`.

### 3. Build & Validate the Book
Run the central tooling script at the repository root:

- **Generate the PDF Book**:
  ```bash
  python build_book.py
  ```
- **Check compliance** (spelling, formatting and layout validation):
  ```bash
  python build_book.py --check
  ```
- **Auto-fix layout and spelling** in source files:
  ```bash
  python build_book.py --fix
  ```

The compiled book is saved as `backend_notes.pdf`.