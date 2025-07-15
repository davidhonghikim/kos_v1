---
title: "PromptKind - Unified Prompt Manager Specification"
description: "Complete architecture and protocol interfaces for the PromptKind module handling prompt creation, validation, sharing, and lifecycle management"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["prompt-management.md", "agent-protocols-and-hierarchy.md", "artifact-management.md"]
implementation_status: "planned"
---

# PromptKind – Unified Prompt Manager Specification

This document defines the architecture, functionality, and protocol interfaces for the `PromptKind` module—the unified prompt manager system for both `kAI` and `kOS`. It handles creation, validation, sharing, injection, and lifecycle management of prompts across user agents, workflows, and services.

## Agent Context
**For AI Agents:** PromptKind is the standardized interface for all prompt operations. Use the PromptExecutionEngine.run() method for prompt injection, follow the template format exactly, and implement proper security validation. All prompt sharing must use signed exports via PromptShare for trust verification.

## Purpose

PromptKind provides the standardized interface and infrastructure for:

- Persistent, structured prompt libraries
- Safe, consistent prompt injection across agents
- Prompt templating and dynamic slot injection
- Prompt evaluation and ranking tools
- Prompt lifecycle audit logs
- Secure sharing and reuse across agents and users

## Directory Structure

```text
src/
└── promptkind/
    ├── core/
    │   ├── PromptTemplate.ts           # Template format and slot logic
    │   ├── PromptLibrary.ts            # Local and synced prompt store
    │   ├── PromptExecutionEngine.ts   # Runtime injection engine
    │   └── PromptAudit.ts               # Prompt invocation logs
    ├── ui/
    │   ├── PromptEditor.tsx            # Rich editor component (frontend)
    │   └── PromptBrowser.tsx           # Searchable library interface
    ├── services/
    │   ├── PromptSyncService.ts       # Remote sync with `PromptSync`
    │   ├── PromptShare.ts              # Secure prompt sharing wrapper
    │   └── PromptRanking.ts            # Runtime prompt feedback and scoring
    └── types/
        └── PromptTypes.ts               # Schema and validation types
```

## Prompt Template Format

Templates use double-brace `{{slot}}` syntax and support metadata annotations:

```json
{
  "id": "goal-setting-v1",
  "title": "Goal Setting Prompt",
  "description": "Prompt for helping user define a SMART goal",
  "template": "Please help the user create a SMART goal for {{goal_topic}}.",
  "slots": ["goal_topic"],
  "tags": ["coaching", "planning"],
  "owner": "agent:planner",
  "auditable": true
}
```

## TypeScript Implementation

```typescript
interface PromptTemplate {
  id: string;
  title: string;
  description: string;
  template: string;
  slots: string[];
  tags: string[];
  owner: string;
  auditable: boolean;
  version?: string;
  created_at?: string;
  updated_at?: string;
  metadata?: Record<string, any>;
}

interface PromptExecutionContext {
  promptId: string;
  variables: Record<string, any>;
  sessionId?: string;
  agentId: string;
  timestamp: string;
}

interface PromptExecutionResult {
  promptId: string;
  resolvedPrompt: string;
  executionId: string;
  timestamp: string;
  success: boolean;
  error?: string;
}

class PromptExecutionEngine {
  private library: PromptLibrary;
  private audit: PromptAudit;
  
  constructor(library: PromptLibrary, audit: PromptAudit) {
    this.library = library;
    this.audit = audit;
  }
  
  async run(promptId: string, context: Record<string, any>): Promise<PromptExecutionResult> {
    const template = await this.library.getPrompt(promptId);
    if (!template) {
      throw new Error(`Prompt not found: ${promptId}`);
    }
    
    const resolvedPrompt = this.resolveTemplate(template, context);
    const executionId = this.generateExecutionId();
    
    const result: PromptExecutionResult = {
      promptId,
      resolvedPrompt,
      executionId,
      timestamp: new Date().toISOString(),
      success: true
    };
    
    await this.audit.logExecution(result);
    return result;
  }
  
  private resolveTemplate(template: PromptTemplate, context: Record<string, any>): string {
    let resolved = template.template;
    
    for (const slot of template.slots) {
      const value = context[slot];
      if (value === undefined) {
        throw new Error(`Missing required slot: ${slot}`);
      }
      resolved = resolved.replace(new RegExp(`{{${slot}}}`, 'g'), String(value));
    }
    
    return resolved;
  }
  
  private generateExecutionId(): string {
    return `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

class PromptLibrary {
  private prompts: Map<string, PromptTemplate> = new Map();
  
  async savePrompt(template: PromptTemplate): Promise<void> {
    this.validateTemplate(template);
    this.prompts.set(template.id, template);
  }
  
  async getPrompt(id: string): Promise<PromptTemplate | null> {
    return this.prompts.get(id) || null;
  }
  
  async searchPrompts(query: string, tags?: string[]): Promise<PromptTemplate[]> {
    const results = Array.from(this.prompts.values());
    
    return results.filter(prompt => {
      const matchesQuery = prompt.title.includes(query) || 
                          prompt.description.includes(query) ||
                          prompt.template.includes(query);
      
      const matchesTags = !tags || tags.every(tag => prompt.tags.includes(tag));
      
      return matchesQuery && matchesTags;
    });
  }
  
  private validateTemplate(template: PromptTemplate): void {
    if (!template.id || !template.title || !template.template) {
      throw new Error('Invalid prompt template: missing required fields');
    }
    
    // Validate slot references
    const templateSlots = this.extractSlots(template.template);
    const declaredSlots = new Set(template.slots);
    
    for (const slot of templateSlots) {
      if (!declaredSlots.has(slot)) {
        throw new Error(`Undeclared slot in template: ${slot}`);
      }
    }
  }
  
  private extractSlots(template: string): string[] {
    const slotRegex = /{{(\w+)}}/g;
    const slots: string[] = [];
    let match;
    
    while ((match = slotRegex.exec(template)) !== null) {
      slots.push(match[1]);
    }
    
    return slots;
  }
}
```

## Capabilities

| Feature                 | Description                                                |
| ----------------------- | ---------------------------------------------------------- |
| Prompt Templating       | Templates with required slots, defaults, conditions        |
| Prompt Injection        | Injected into agent context or model call chain            |
| Prompt Library          | Tagged, filterable, versioned                              |
| Sharing & Import/Export | Signed bundles for agent-to-agent or user-to-user transfer |
| Lifecycle Logging       | Logs which agent invoked which prompt, when, and how       |
| Ranking & Feedback      | Prompts can be scored post-hoc or in-session               |
| Chainable Prompts       | Supports sequences and branching (multi-step workflows)    |

## Integration Points

- Agents call `PromptExecutionEngine.run(promptId, context)`
- Prompts injected into Langchain/LLM chain as prefix or suffix
- Sharing uses signed export via `PromptShare`
- Ranking integrated with feedback UI and agent logs

## PromptKindSync Protocol

PromptKindSync is a mini-protocol that allows prompt syncing between agents and between a user and their cloud vault:

```typescript
interface PromptSyncPacket {
  promptId: string;
  version: string;
  promptJSON: object;
  signature: string;
  timestamp: string;
  source: string; // DID
  target: string;  // DID
}

class PromptSyncService {
  async syncPrompt(packet: PromptSyncPacket): Promise<boolean> {
    // Verify signature
    if (!this.verifySignature(packet)) {
      throw new Error('Invalid prompt signature');
    }
    
    // Check timestamp
    if (!this.isValidTimestamp(packet.timestamp)) {
      throw new Error('Invalid or expired timestamp');
    }
    
    // Process sync
    const template = packet.promptJSON as PromptTemplate;
    await this.library.savePrompt(template);
    
    return true;
  }
  
  private verifySignature(packet: PromptSyncPacket): boolean {
    // Implement signature verification logic
    return true; // Placeholder
  }
  
  private isValidTimestamp(timestamp: string): boolean {
    const now = Date.now();
    const packetTime = new Date(timestamp).getTime();
    const maxAge = 5 * 60 * 1000; // 5 minutes
    
    return (now - packetTime) <= maxAge;
  }
}
```

## Security Features

- **Prompt Hashing** for tamper verification
- **Slot Constraints** to prevent prompt injection attacks
- **Audit Trail** with redacted sensitive values
- **Owner Signing** for trusted source verification
- **Prompt Locking** (read-only flags)

## UI Components

- PromptKindEditor: Full template editing with live preview
- PromptKindLibrary: Searchable and filterable UI
- PromptStatsPanel: Success rates, usage logs, rankings

## Example Prompt Lifecycle

1. User creates prompt `p1` using PromptEditor
2. `p1` saved to `PromptLibrary`
3. Agent `GoalPlanner` calls `run('p1', { goal_topic: 'exercise' })`
4. Prompt injected into chain as prefix
5. On complete, feedback form triggers `PromptRanking`
6. Stats updated in `PromptAudit`
7. User shares prompt with their friend via `PromptShare`

## Roadmap

| Feature                          | Status   |
| -------------------------------- | -------- |
| Visual Prompt Chaining UI        | Planned  |
| Prompt Auto-Ranking via Model    | Planned  |
| Git-based Prompt Version Control | Planned  |
| Prompt Marketplace               | Future   |
| Prompt Linting Rules Engine      | Drafting |

## Implementation Guidelines

1. **Template Validation**: All templates must pass validation before storage
2. **Slot Security**: Implement strict slot validation to prevent injection attacks
3. **Audit Compliance**: All prompt executions must be logged with full context
4. **Signature Verification**: All shared prompts must have valid signatures
5. **Version Control**: Maintain version history for all prompt modifications

## Cross-References

- [Prompt Management](prompt-management.md) - General prompt management architecture
- [Agent Protocols](../protocols/agent-protocols-and-hierarchy.md) - Agent communication
- [Artifact Management](artifact-management.md) - Artifact storage and versioning
- [Security Framework](../security/agent-trust-protocols.md) - Trust and security protocols 