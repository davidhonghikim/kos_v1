---
title: "Prompt Template System"
description: "Architecture for prompt structure, validation, and lifecycle management across kAI and kOS systems"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["prompt-kind-specification.md", "prompt-management.md"]
implementation_status: "planned"
---

# Prompt Template System

This document defines the architecture, schema, storage, validation, and lifecycle management for prompts and prompt templates used throughout the `kAI` and `kOS` systems.

## Agent Context
**For AI Agents:** Use this system for all prompt operations. Follow the JSON schema exactly, implement proper validation, and ensure all prompts are versioned and auditable. Use the PromptLoader for template resolution and the Health Beacon Protocol for monitoring.

## Purpose

- Standardize prompt structure for all AI communication
- Support multi-agent chaining and reuse of prompt logic
- Enable localization, customization, and user overrides
- Provide tooling for testing, validation, and fallback logic

## Core Concepts

### A. Prompt Template
A structured, parameterized prompt format used by agents, services, or workflows.

### B. Prompt Instance
A resolved, runtime-filled prompt ready to be submitted to an LLM.

### C. Prompt Store
Central or distributed storage of all prompt templates, versioned and auditable.

### D. Prompt Bundle
A collection of related prompts (e.g., for onboarding, diagnostics, UI translation, etc.)

## Directory Layout

```bash
/services/prompts/
├── system/
│   ├── error_handling.json
│   ├── onboarding.json
│   └── fallback.json
├── agents/
│   ├── planner_agent.json
│   └── memory_agent.json
├── workflows/
│   ├── creative_writing.json
│   └── research_chain.json
├── bundles/
│   ├── ui_localization.en.json
│   └── diagnostics_bundle.json
└── validators/
    └── schema.prompts.json
```

## Prompt Template Schema (JSON)

```json
{
  "id": "planner_agent:weekly_summary",
  "description": "Prompt for summarizing weekly goals",
  "language": "en",
  "audience": "agent",
  "version": "1.0.0",
  "template": "Summarize the user's completed and pending goals for this week:",
  "parameters": [
    {"name": "completed", "type": "string"},
    {"name": "pending", "type": "string"}
  ],
  "style": "concise",
  "tone": "neutral",
  "safety": {
    "max_tokens": 256,
    "temperature": 0.3,
    "moderation": true
  },
  "tags": ["summary", "goals", "weekly"]
}
```

## TypeScript Implementation

```typescript
interface PromptTemplate {
  id: string;
  description: string;
  language: string;
  audience: 'agent' | 'user' | 'system';
  version: string;
  template: string;
  parameters: PromptParameter[];
  style: string;
  tone: string;
  safety: SafetyConfig;
  tags: string[];
}

interface PromptParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object';
  required?: boolean;
  default?: any;
}

interface SafetyConfig {
  max_tokens: number;
  temperature: number;
  moderation: boolean;
}

class PromptLoader {
  private templates: Map<string, PromptTemplate> = new Map();
  
  async loadTemplate(id: string): Promise<PromptTemplate | null> {
    return this.templates.get(id) || null;
  }
  
  async loadBundle(bundleName: string): Promise<PromptTemplate[]> {
    // Load all prompts in a bundle
    return Array.from(this.templates.values())
      .filter(template => template.tags.includes(bundleName));
  }
  
  async renderPrompt(id: string, parameters: Record<string, any>): Promise<string> {
    const template = await this.loadTemplate(id);
    if (!template) {
      throw new Error(`Template not found: ${id}`);
    }
    
    let rendered = template.template;
    for (const param of template.parameters) {
      const value = parameters[param.name] ?? param.default;
      if (param.required && value === undefined) {
        throw new Error(`Required parameter missing: ${param.name}`);
      }
      rendered = rendered.replace(new RegExp(`{{${param.name}}}`, 'g'), String(value));
    }
    
    return rendered;
  }
}
```

## Prompt Versioning

### Semver format: `1.2.0`
- MAJOR: Breaking structure or meaning change
- MINOR: Safe improvements or additional optional fields
- PATCH: Minor fixes or metadata tweaks

## Security and Moderation

- All prompts validated via schema before registration
- Max token + temperature limits enforced at render time
- Unsafe content filtering pre- and post-LLM response
- Restricted prompt sets for untrusted agents

## Cross-References

- [PromptKind Specification](prompt-kind-specification.md) - Unified prompt manager
- [Prompt Management](prompt-management.md) - Management architecture 