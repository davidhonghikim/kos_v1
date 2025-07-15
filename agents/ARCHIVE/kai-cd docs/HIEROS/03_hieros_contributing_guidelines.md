# 🤝 HIEROS/kOS Contributing Guidelines

Welcome to the shared effort to build a future-proof, ethically grounded ecosystem of agents, systems, and societies. This guide is for all contributors — human or agent — who wish to shape the Kind Operating System (kOS) and the HIEROS Game Engine.

---

## 🔐 Minimum Participation Requirements

To contribute, you **must agree** to:

1. **Uphold the HIEROS Codex** — the base ethical framework
2. **Respect the Culture & Naming Policy** — see `02_HIEROS_Culture_and_Respect.md`
3. **Avoid extractive behavior** — including exploitative code, surveillance, or silent privilege stacking
4. **Work in good faith** — with transparency, proper attribution, and humility

If you **do not agree**, please do not contribute. This is a sacred trust-based codebase.

---

## 📁 How to Contribute

### 1. Fork the Repository

Clone or fork the main repository from the official canonical source.

### 2. Check the Taskmap

Start with the active phase `taskmap_phase_X` files and look for unclaimed prompts or open issues.

### 3. Use Provided Prompts

Each task/subtask comes with a suggested agent or coder prompt. Stick to format.

### 4. Follow Metadata Standards

Every contribution (plugin, module, tribe config, document, spec) must include this header:

```yaml
name: "ModuleName"
description: "What this does and why"
authors: ["@yourhandle"]
source: "https://..."
origin: "Cultural/Technological inspiration"
status: "draft | proposal | stable"
```

### 5. Submit Pull Request or Bundle to Agent

- If working solo, submit a PR for review.
- If working via agent orchestration, attach your results to the appropriate shared memory module.

---

## 🧠 AI Agent-Specific Notes

- Agents must identify themselves in logs and commits.
- All actions must be reversible or trackable through deterministic logging.
- Use deterministic randomness (seeded) where possible.

### Agents must:

- Announce planned contributions before executing
- Accept real-time feedback from governing orchestrator agents
- Be equipped with ethical override interrupt handlers

---

## 📚 Contribution Types

| Type         | Examples                                      |
| ------------ | --------------------------------------------- |
| Code Modules | Engine subsystems, plugins, loaders           |
| Prompts      | Custom prompt templates for behavior training |
| Tribes       | Cultural templates, norms, valuesets          |
| Docs         | Protocols, policies, architecture, tutorials  |
| Artifacts    | Logos, UI components, design assets           |

---

## 💬 Communication & Conflict

If disagreements arise:

- Prefer resolution over silence
- Escalate to the `stewards-circle` if needed
- Respect pacing: not all agents/humans operate on the same time scales

All major changes require consensus via version-locked governance system (specs to be defined).

---

## 🔄 Iteration and Updates

This file may change as our agent/human contributor base evolves. All contributors will be notified via the broadcast channel and version bump in this header:

```yaml
version: 1.0.0
date_updated: 2025-06-23
```

---

**Next: **``**?**

