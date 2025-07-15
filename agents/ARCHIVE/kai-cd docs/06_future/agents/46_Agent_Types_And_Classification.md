---
title: "Agent Types & Classification System"
description: "Complete taxonomy of agents in the Kind ecosystem with behavioral classes, modular capabilities, and interoperability requirements"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["agent-hierarchy.md", "agent-lifecycle-and-execution.md", "agent-protocols-and-hierarchy.md"]
implementation_status: "planned"
---

# Agent Types & Classification System

This document defines the full taxonomy of agents in the Kind ecosystem, detailing core types, behavioral classes, modular capabilities, and interoperability requirements for constructing, identifying, and evolving agents in both `kAI` and `kOS` environments.

## Agent Context
**For AI Agents:** This classification system is fundamental for agent self-identification, capability declaration, and inter-agent routing. Use this taxonomy to determine appropriate agent interactions, trust levels, and permission boundaries. Implement the declaration format exactly as specified for system compatibility.

## Purpose

To standardize how agents are categorized, declared, deployed, and evolved across the ecosystem:

- Provide semantic clarity between types of agents
- Enable programmatic filtering, access control, and routing
- Encourage modular reuse and composability
- Support autonomy, safety, and chain-of-trust guarantees

## Primary Classification Tiers

Each agent must declare:

- **Agent Class** — Role in the system
- **Specialization** — Field or domain of expertise
- **Authority Type** — Trust level and permissions
- **Modular Capabilities** — Loadable behaviors

## Core Agent Classes

### 1. `system.core`

- Responsible for platform integrity
- Examples: SchedulerAgent, ConfigManager, KernelSupervisor

### 2. `user.personal`

- Dedicated to a specific user
- Private, memory-retentive, long-running
- Examples: DailyAssistant, GoalPlanner, SchedulerAgent

### 3. `network.linker`

- Broker between multiple agents
- Handles routing, delegation, interoperability
- Examples: TrustBridge, MeshRouter, ProxyExecutor

### 4. `domain.specialist`

- Expert in a narrow field
- Activated per-query or by scheduler
- Examples: FinancialAdvisor, LegalParser, WellnessCoach

### 5. `orchestrator`

- Coordinates other agents
- Maintains workflow state and dependencies
- Examples: CreativeStudioCoordinator, CareNetworkManager

### 6. `utility.service`

- Stateless or fast-spawning tasks
- Examples: Transcoder, Notifier, Cleaner, Indexer

## Authority Types

| Authority Level | Description                               |
| --------------- | ----------------------------------------- |
| `root.kernel`   | Full system access                        |
| `trusted.user`  | Verified personal assistant               |
| `linked.trust`  | Federated agent with chain-of-trust proof |
| `restricted`    | Untrusted or sandboxed task agent         |
| `external`      | Third-party or open network agent         |

## Specializations (Domain Tags)

Each agent may declare 1 or more domain tags:

```typescript
['finance', 'legal', 'medical', 'ai.devops', 'education', 'memory', 'mobility']
```

These determine searchability, routing, and UI rendering.

## Modular Capabilities

Agents are composed of optional, hot-swappable modules:

| Module Name      | Description                                 |
| ---------------- | ------------------------------------------- |
| `MemoryCore`     | Long- and short-term semantic memory        |
| `SpeechIO`       | TTS + STT integration                       |
| `PersonaLayer`   | Emotion/personality modeling and tone       |
| `LangChainTools` | Tool abstraction for external APIs          |
| `SecurePrompt`   | Safe prompt template enforcement            |
| `PromptKindSync` | Agent-to-agent protocol manager             |
| `SchedulerUnit`  | Task and reminder tracking                  |
| `AgentShell`     | Terminal access via command wrapper         |
| `VisualMindMap`  | UI rendering of memory and intent graph     |
| `MicroOrch`      | Micro-task decomposition and agent spawning |

## Agent Declaration Format

Agents must define themselves in a `agent.meta.json`:

```json
{
  "id": "agent-finance-007",
  "class": "domain.specialist",
  "specializations": ["finance"],
  "authority": "linked.trust",
  "modules": ["LangChainTools", "SecurePrompt", "MemoryCore"]
}
```

## TypeScript Implementation

```typescript
interface AgentMetadata {
  id: string;
  class: 'system.core' | 'user.personal' | 'network.linker' | 'domain.specialist' | 'orchestrator' | 'utility.service';
  specializations: string[];
  authority: 'root.kernel' | 'trusted.user' | 'linked.trust' | 'restricted' | 'external';
  modules: string[];
  version?: string;
  created_at?: string;
  updated_at?: string;
}

interface AgentCapability {
  name: string;
  version: string;
  dependencies: string[];
  permissions: string[];
}

class AgentRegistry {
  private agents: Map<string, AgentMetadata> = new Map();
  
  registerAgent(metadata: AgentMetadata): boolean {
    if (!this.validateMetadata(metadata)) {
      throw new Error('Invalid agent metadata');
    }
    
    this.agents.set(metadata.id, metadata);
    return true;
  }
  
  findAgentsByClass(agentClass: string): AgentMetadata[] {
    return Array.from(this.agents.values())
      .filter(agent => agent.class === agentClass);
  }
  
  findAgentsBySpecialization(specialization: string): AgentMetadata[] {
    return Array.from(this.agents.values())
      .filter(agent => agent.specializations.includes(specialization));
  }
  
  private validateMetadata(metadata: AgentMetadata): boolean {
    const validClasses = ['system.core', 'user.personal', 'network.linker', 'domain.specialist', 'orchestrator', 'utility.service'];
    const validAuthorities = ['root.kernel', 'trusted.user', 'linked.trust', 'restricted', 'external'];
    
    return validClasses.includes(metadata.class) && 
           validAuthorities.includes(metadata.authority) &&
           metadata.id && metadata.id.length > 0;
  }
}
```

## Compatibility & Routing Rules

- `user.personal` agents may not invoke `external` without explicit user approval
- `system.core` may invoke any class, but only with logged audit trail
- Orchestrators must be able to deserialize all `agent.meta.json`
- `network.linker` agents must register in the TrustLinkGraph

## Future Considerations

- Decentralized Agent Certification (DAC)
- Automatic Class Evolution (self-reflective growth)
- Simulated Swarm Behavior Agents
- Companion/Embodied Agent Markup Standards

## Implementation Guidelines

1. **Agent Registration**: All agents must register with the AgentRegistry on startup
2. **Capability Declaration**: Modules must be explicitly declared and verified
3. **Authority Validation**: Authority levels must be cryptographically verified
4. **Routing Compliance**: Inter-agent communication must respect authority boundaries
5. **Audit Trail**: All agent interactions must be logged for trust verification

## Cross-References

- [Agent Hierarchy](agent-hierarchy.md) - Detailed hierarchy structures
- [Agent Lifecycle](agent-lifecycle-and-execution.md) - Lifecycle management
- [Agent Protocols](agent-protocols-and-hierarchy.md) - Communication protocols
- [Trust Protocols](../security/agent-trust-protocols.md) - Trust verification systems 