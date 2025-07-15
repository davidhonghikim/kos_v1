---
title: "Entity Taxonomy Model - Standard Classification for kAI/kOS"
description: "Complete low-level taxonomy for classifying all participants in the kOS ecosystem"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: 
  - "protocols/klp-kind-link-protocol.md"
  - "security/agent-trust-protocols.md"
implementation_status: "planned"
---

# Entity Taxonomy Model – Standard Classification for kAI/kOS

This document defines the complete, low-level taxonomy used to classify all participants in the kOS ecosystem. Entities may be AI agents, human users, services, systems, or hybrid collectives.

## Agent Context

**For AI Agents**: This taxonomy is the foundation for all entity classification and permission systems. Use the `EntityType` enum and `EntityRecord` interface exactly as specified. All agent registration must follow this schema.

**Implementation Priority**: Core system requirement - implement EntityRegistry first, then classification engine.

---

## I. Root Classification Tree

```text
Entity
├── Agent
│   ├── AI_Agent
│   │   ├── kAI_Core
│   │   ├── Assistant
│   │   ├── Coordinator
│   │   ├── Sentinel
│   │   ├── Artisan
│   │   └── DevOpsAgent
│   └── Human_Proxy
├── Human
│   ├── Owner
│   ├── Member
│   ├── Guest
│   ├── Guardian
│   └── Operator
├── Service
│   ├── LLM_Service
│   ├── VectorDB
│   ├── Object_Store
│   └── Orchestration
├── Device
│   ├── Wearable
│   ├── Appliance
│   ├── Sensor
│   ├── Robot
│   └── Terminal
└── Collective
    ├── AgentSwarm
    ├── DAO
    └── Flock
```

## II. Metadata Schema for Each Entity

Every entity is registered with the following structure:

```typescript
interface EntityRecord {
  id: string;              // DID or unique entity ID
  type: EntityType;        // See classification above
  label?: string;          // Optional friendly name
  trustScore: number;      // Dynamic trust rating
  capabilities: string[];  // Enumerated abilities
  lastSeen: string;        // ISO date
  state?: object;          // Optional dynamic state
  version?: string;        // For services and agents
  parent?: string;         // Parent entity (hierarchical lineage)
  isActive: boolean;
  registrationTime: string;
  authMethods: string[];   // ['JWT', 'OAuth2', 'DID-Auth', etc.]
}
```

## III. Purpose of Entity Taxonomy

### A. Role Resolution
- Quickly resolve entity authority levels
- Match service requests to permission levels

### B. Routing & Access Control
- Route messages based on entity type
- Prevent unauthorized cross-domain access

### C. Logging & Analytics
- Annotate system events with typed entity tags
- Enable dashboards of agent vs human activity

### D. Behavior Profiling
- Detect anomalies across entity categories
- Apply ML models to classify behavior consistency

## IV. Integration with KLP and Registry

- Each entity record links into the KLP Trust Graph
- Entity types inform capability negotiation
- Discovery packets are typed using taxonomy constants
- New entities must register their type on link initiation

## V. Maintenance & Extension

- New entity types must follow proposal process via governance
- Local extensions are allowed but must not conflict with core types
- Versioned schemas to allow evolution of definitions over time

## VI. Implementation Roadmap

| Phase | Features | Timeline |
|-------|----------|----------|
| Phase 1 | Core EntityRegistry, basic classification | Q1 2025 |
| Phase 2 | KLP integration, trust scoring | Q2 2025 |
| Phase 3 | Advanced permissions, behavior profiling | Q3 2025 |
| Phase 4 | Federated taxonomy, governance voting | Q4 2025 |

## VII. Security Considerations

- Entity registration requires cryptographic proof of identity
- Trust scores are tamper-evident through audit trails
- Permission escalation requires multi-party validation
- Regular security audits of classification logic

---

This entity taxonomy serves as the foundational classification system for all kOS ecosystem participants, enabling secure, scalable, and intelligent routing of capabilities and permissions across the distributed agent mesh. 