---
title: "Documentation Naming & Formatting Conventions"
description: "Comprehensive conventions for all Markdown documents in the documentation system"
type: "conventions"
status: "current"
priority: "high"
last_updated: "2025-01-27"
agent_notes: "Essential formatting and naming standards - must be followed for all documentation"
---

# 04: Documentation Naming & Formatting Conventions

> **Scope:** These conventions apply to every Markdown document created under the `documentation/` tree (developers, users, agents, reports) as well as ad-hoc notes created by the AI agent.

   ---

   ## 1. File Naming
   1. **Numeric Prefix** – Begin every filename with a two-digit ordinal (`00_`, `01_`, `02_` …) to guarantee deterministic sorting in directory listings.
   2. **Descriptive Title** – Follow the prefix with a concise, PascalCase description.
      *Examples:*
      - `03_Execution_Plan.md`
      - `07_Build_And_Deployment.md`
   3. **Underscore Separator** – Use underscores (`_`) between words; avoid spaces or dashes.
   4. **Extension** – Use the `.md` extension for Markdown; `.png`/`.jpg` for assets.

   ## 2. Document Header
   Each file **must** start with a level-1 heading using the same ordinal and title as the filename:
   ```markdown
   # 03: Execution Plan – Comprehensive Audit & Verification of Kai-CD Codebase
   ```

   ## 3. Section Hierarchy
   • `##` for top-level sections.  
   • `###` for sub-sections.  
   • Avoid going deeper than `####`.

   ## 4. Task & Status Tables (Deprecated)
   *Old checkbox-based tables are kept here for legacy reference but **should not** be used in new documents. Use the color-coded status indicators defined below instead.*

   ```markdown
   | ✓ | Step | Description | Owner |
   | --- | --- | --- | --- |
   | [x] | Example completed step. | Agent |
   ```

   ## 5. Task Status Indicators (Color-Coded)
   Use emoji squares to convey status at a glance. Standard palette:

   | Emoji | Meaning |
   | --- | --- |
   | 🟩 | Completed / Done |
   | 🟦 | In Progress |
   | ⬜ | Not Started |
   | 🟨 | Needs Review |
   | 🟥 | Blocked / Error |

   ### Example Table
   ```markdown
   | 🟩 | Step | Description | Owner |
   | --- | --- | --- | --- |
   | 🟩 | P0-1 | Review core docs. | Agent |
   | ⬜ | P0-2 | Inventory high-risk modules. | Agent |
   ```

   *(Previously defined checkbox syntax is superseded by this color-coded box system.)*

   ## 6. Inline Code & Paths
   • Wrap filenames, directories, and code snippets in back-ticks: `src/utils/apiClient.ts`.

   ## 7. Code Block Citations
   When pasting source excerpts, use the required Cursor format:
   ```text
   ```12:34:src/utils/apiClient.ts
   // ... code ...
   ```
   ```
   `startLine:endLine:path` **must** match the snippet.

   ## 8. Language & Tone
   • Use imperative voice for instructions ("Run `npm install`", "Add the dependency").  
   • Keep sentences short; favour clarity over verbosity.

   ## 9. Asset Placement
   • Place images in an `assets/` sub-directory adjacent to the Markdown file whenever feasible.  
   • Reference with relative paths: `![Alt text](./assets/diagram.png)`.

   ## 10. Change Log Footers (Optional)
   Large docs may end with a mini changelog:
   ```markdown
   ---
   ### Changelog
   – 2025-06-20 • Initial draft (AI agent)
   ```

   ---

   *Adherence to this guide ensures that all contributors – human or AI – produce easy-to-navigate, consistently formatted documentation.* 