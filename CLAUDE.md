# CLAUDE.md: Developer and Agent Guidelines

This document provides developer guidelines, build instructions and strict styling rules for contributing to the **Backend Notes: Systems Engineering** repository.

---

## 1. Project Purpose and Structure

The goal of this project is to compile high-quality, logic-driven systems engineering and backend notes into a single cohesive, print-ready PDF book.

### Logical Narrative Flow
For every topic or system design concept introduced, prose must follow a natural flow:
1.  **Why:** Why does this technology or design pattern exist? (What problem is it solving?)
2.  **What:** What is the abstraction or architecture?
3.  **How:** How does it operate under the hood? (Deep dive into kernel features, storage layers or protocols.)
4.  **What If:** What happens when failure states occur? (Noisy neighbours, resource exhaustion, database locks or network partition states.)

---

## 2. Core Build and Validation Commands

The project uses modular Python scripts located in the `tools/` directory.

### Compile PDF
Generates `backend_notes.pdf` from the markdown source files via WeasyPrint:
```bash
python build_book.py
```

### Validate Compliance
Runs a unittest-based validation suite checking formatting, spelling and syntax rules:
```bash
python build_book.py --check
```

### Auto-Fix Formatting
Runs sanitizers to automatically resolve spelling discrepancies, markdown spacing and minor syntax errors:
```bash
python build_book.py --fix
```

---

## 3. Strict Style Constraints (Checked by CI/Validators)

Any files registered in `tools/config.py` under `FILES_CONFIG` must strictly conform to these rules. Validation failures will halt the build:

### Spelling (American English)
Prose must conform to **American English (US)** spelling conventions. Do not use British or Indian English variants in prose (code blocks, imports and CLI commands are excluded):
-   *Yes:* `standardized`, `centralized`, `organization`, `optimization`, `behavior`, `utilization`, `color`.
-   *No:* `standardised`, `centralised`, `organisation`, `optimisation`, `behaviour`, `utilisation`, `colour`.

### Oxford Comma Avoidance
Do not use the Oxford comma (`", and"`) in lists within prose text.
-   *Incorrect:* "...networking, protocols, and gateways."
-   *Correct:* "...networking, protocols and gateways."

### Markdown List Spacing
To ensure compatibility with the Python-Markdown parser used during PDF generation, **every bulleted or numbered list block must be preceded by a blank line**.
-   *Incorrect:*
    ```markdown
    Some introduction text.
    - First list item
    ```
-   *Correct:*
    ```markdown
    Some introduction text.

    - First list item
    ```

### Self-Referential Language
Prose must never refer to the document or chapter itself using terms like *"This document explains..."* or *"This chapter covers..."*. Let the headers and flow guide the reader directly.

### Unicode Arrow and Character Safety
Do not use raw Unicode arrow characters (such as `→`, `←`, `⇒` or `⇐`) or specific unicode emoji symbols. These fail during WeasyPrint PDF layout generation.
-   Use text or standard ASCII characters (e.g. `->`, `<=`, `<=>`) instead.

### Frontmatter Schema
Each source markdown file must begin with valid YAML frontmatter containing:
-   `title`: The chapter or document title.
-   `part`: The numeric part of the book.
-   `part_title`: The title of the corresponding part.
-   `chapter`: (Required for chapter types) The chapter number, which must match the configuration index in `tools/config.py`.
-   `summary`: A short, descriptive summary.

---

## 4. Chapter Registration

When adding a new markdown note, you must register it inside **[tools/config.py](file:///d:/Playground/Backend%20Notes/tools/config.py)** under `FILES_CONFIG`. The order of files in this list dictates their compilation order in the final PDF.
