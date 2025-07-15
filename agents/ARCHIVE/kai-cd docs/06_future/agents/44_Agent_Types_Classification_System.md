---
title: "Agent Types & Classification System"
description: "Comprehensive taxonomy of agents in the Kind ecosystem, detailing core types, behavioral classes, modular capabilities, and interoperability requirements"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2024-12-28"
related_docs: [
  "documentation/future/agents/42_agent-lifecycle-management-orchestration.md",
  "documentation/future/agents/38_agent-protocols-hierarchy-complete.md",
  "documentation/future/security/43_agent-attestation-verification-audit-trails.md"
]
implementation_status: "planned"
---

# Agent Types & Classification System

## Agent Context
**For AI Agents**: This document defines the complete taxonomy for agent classification in the kOS ecosystem. When implementing agent functionality, use these classifications to determine capabilities, permissions, and interaction patterns. All agents must declare their class, specialization, authority type, and modular capabilities in their manifest. Use the provided TypeScript interfaces as implementation contracts for agent metadata and compatibility checking.

## Purpose

To standardize how agents are categorized, declared, deployed, and evolved across the ecosystem:

- Provide semantic clarity between types of agents
- Enable programmatic filtering, access control, and routing
- Encourage modular reuse and composability
- Support autonomy, safety, and chain-of-trust guarantees

## Classification Framework

Each agent must declare:

- **Agent Class** — Role in the system
- **Specialization** — Field or domain of expertise
- **Authority Type** — Trust level and permissions
- **Modular Capabilities** — Loadable behaviors

```typescript
interface AgentClassification {
  agentClass: AgentClass;
  specializations: string[];
  authorityType: AuthorityType;
  capabilities: string[];
  compatibilityLevel: CompatibilityLevel;
}

type AgentClass = 
  | 'system.core'
  | 'user.personal'
  | 'network.linker'
  | 'domain.specialist'
  | 'orchestrator'
  | 'utility.service';

type AuthorityType = 
  | 'root.kernel'
  | 'trusted.user'
  | 'linked.trust'
  | 'restricted'
  | 'external';

type CompatibilityLevel = 
  | 'kOS-native'         // Fully integrated kOS agent
  | 'kOS-compatible'     // External agent with kOS adapters
  | 'legacy-wrapped'     // Legacy system with wrapper
  | 'experimental';      // Development/testing phase
```

## Core Agent Classes

### 1. `system.core`

**Purpose**: Responsible for platform integrity and essential system functions.

```typescript
interface SystemCoreAgent extends BaseAgent {
  class: 'system.core';
  systemPrivileges: {
    kernelAccess: boolean;
    resourceManagement: boolean;
    securityEnforcement: boolean;
    systemConfiguration: boolean;
  };
  criticalityLevel: 'essential' | 'important' | 'optional';
  failoverStrategy: 'restart' | 'fallback' | 'manual';
}
```

**Examples**:
- **SchedulerAgent**: Task and resource scheduling
- **ConfigManager**: System configuration management
- **KernelSupervisor**: Core system monitoring
- **SecurityEnforcer**: Policy enforcement
- **ResourceMonitor**: System resource tracking

**Characteristics**:
- Highest trust level required
- Direct access to system APIs
- Cannot be terminated by user agents
- Automatic failover mechanisms
- Comprehensive audit logging

### 2. `user.personal`

**Purpose**: Dedicated to a specific user with private, memory-retentive, long-running characteristics.

```typescript
interface UserPersonalAgent extends BaseAgent {
  class: 'user.personal';
  userId: string;                    // Owning user identifier
  personalityProfile: PersonalityProfile;
  memoryPersistence: {
    longTerm: boolean;
    crossSession: boolean;
    userPrivate: boolean;
  };
  adaptationLevel: 'static' | 'learning' | 'evolving';
}

interface PersonalityProfile {
  traits: Record<string, number>;    // Personality trait scores
  communicationStyle: 'formal' | 'casual' | 'adaptive';
  emotionalRange: 'minimal' | 'moderate' | 'expressive';
  learningPreference: 'conservative' | 'balanced' | 'aggressive';
}
```

**Examples**:
- **DailyAssistant**: Personal productivity and scheduling
- **GoalPlanner**: Long-term objective tracking
- **MemoryKeeper**: Personal information management
- **CompanionAgent**: Emotional support and conversation
- **PreferenceManager**: User preference learning and adaptation

**Characteristics**:
- Single-user ownership
- Persistent memory across sessions
- Adaptive learning capabilities
- Privacy-first design
- Emotional intelligence features

### 3. `network.linker`

**Purpose**: Broker between multiple agents, handling routing, delegation, and interoperability.

```typescript
interface NetworkLinkerAgent extends BaseAgent {
  class: 'network.linker';
  routingCapabilities: {
    protocols: string[];             // Supported protocols
    bridging: string[];              // Bridged systems
    translation: string[];           // Protocol translations
  };
  federationLevel: 'local' | 'mesh' | 'global';
  trustBroker: boolean;              // Can establish trust relationships
}
```

**Examples**:
- **TrustBridge**: Cross-agent trust establishment
- **MeshRouter**: Peer-to-peer agent communication
- **ProxyExecutor**: Remote agent invocation
- **ProtocolTranslator**: Cross-protocol communication
- **FederationManager**: Multi-network coordination

**Characteristics**:
- Multi-agent communication
- Protocol bridging capabilities
- Trust relationship management
- Network topology awareness
- Federation support

### 4. `domain.specialist`

**Purpose**: Expert in a narrow field, activated per-query or by scheduler.

```typescript
interface DomainSpecialistAgent extends BaseAgent {
  class: 'domain.specialist';
  expertiseDomain: string;
  knowledgeBase: {
    sources: string[];              // Knowledge source identifiers
    lastUpdated: string;
    confidence: number;             // 0.0 - 1.0
  };
  activationPattern: 'on-demand' | 'scheduled' | 'event-driven';
  consultationMode: 'expert' | 'advisor' | 'teacher';
}
```

**Examples**:
- **FinancialAdvisor**: Financial planning and analysis
- **LegalParser**: Legal document analysis
- **WellnessCoach**: Health and wellness guidance
- **TechnicalDiagnostic**: System troubleshooting
- **CreativeDirector**: Creative project guidance

**Characteristics**:
- Deep domain expertise
- Specialized knowledge bases
- Context-aware activation
- Expert consultation modes
- Continuous learning from domain updates

### 5. `orchestrator`

**Purpose**: Coordinates other agents, maintains workflow state and dependencies.

```typescript
interface OrchestratorAgent extends BaseAgent {
  class: 'orchestrator';
  orchestrationScope: {
    managedAgents: string[];        // Agent IDs under management
    workflowTypes: string[];        // Supported workflow patterns
    coordinationLevel: 'basic' | 'advanced' | 'intelligent';
  };
  stateManagement: {
    persistent: boolean;
    distributed: boolean;
    rollback: boolean;
  };
}
```

**Examples**:
- **CreativeStudioCoordinator**: Multi-agent creative workflows
- **CareNetworkManager**: Healthcare coordination
- **ProjectManager**: Multi-phase project execution
- **WorkflowEngine**: Complex business process management
- **SwarmCoordinator**: Large-scale agent coordination

**Characteristics**:
- Multi-agent coordination
- Workflow state management
- Complex decision making
- Resource allocation
- Failure recovery mechanisms

### 6. `utility.service`

**Purpose**: Stateless or fast-spawning tasks for background operations.

```typescript
interface UtilityServiceAgent extends BaseAgent {
  class: 'utility.service';
  serviceType: 'stateless' | 'ephemeral' | 'background';
  executionModel: {
    spawnable: boolean;
    concurrent: boolean;
    pooled: boolean;
  };
  resourceConstraints: {
    maxMemory: number;              // MB
    maxCpu: number;                 // Percentage
    maxRuntime: number;             // Seconds
  };
}
```

**Examples**:
- **Transcoder**: Media format conversion
- **Notifier**: Message and alert delivery
- **Cleaner**: System maintenance tasks
- **Indexer**: Content indexing and search
- **Validator**: Data validation services

**Characteristics**:
- Lightweight execution
- Fast startup/shutdown
- Resource-constrained
- High concurrency support
- Minimal state requirements

## Authority Types

```typescript
interface AuthorityDefinition {
  type: AuthorityType;
  permissions: Permission[];
  constraints: Constraint[];
  verificationRequired: boolean;
  auditLevel: 'minimal' | 'standard' | 'comprehensive';
}

interface Permission {
  resource: string;
  actions: ('read' | 'write' | 'execute' | 'delete' | 'admin')[];
  scope: string;                    // Resource scope
  conditions?: string[];            // Additional conditions
}

interface Constraint {
  type: 'time' | 'resource' | 'network' | 'data' | 'user';
  specification: any;
  enforceLevel: 'warning' | 'block' | 'quarantine';
}
```

### Authority Matrix

| Authority Level | Description | Permissions | Verification |
| --------------- | ----------- | ----------- | ------------ |
| `root.kernel` | Full system access | All resources, admin actions | Multi-factor, attestation required |
| `trusted.user` | Verified personal assistant | User data, user services | User verification, regular re-auth |
| `linked.trust` | Federated agent with chain-of-trust proof | Cross-agent communication | Chain verification |
| `restricted` | Untrusted or sandboxed task agent | Limited resources, read-only | Continuous monitoring |
| `external` | Third-party or open network agent | Minimal access, external only | External validation |

```typescript
const authorityDefinitions: Record<AuthorityType, AuthorityDefinition> = {
  'root.kernel': {
    type: 'root.kernel',
    permissions: [
      {
        resource: '*',
        actions: ['read', 'write', 'execute', 'delete', 'admin'],
        scope: 'system'
      }
    ],
    constraints: [
      {
        type: 'time',
        specification: { maxSessionDuration: 3600 },  // 1 hour
        enforceLevel: 'block'
      }
    ],
    verificationRequired: true,
    auditLevel: 'comprehensive'
  },
  
  'trusted.user': {
    type: 'trusted.user',
    permissions: [
      {
        resource: 'user.*',
        actions: ['read', 'write', 'execute'],
        scope: 'user-owned'
      },
      {
        resource: 'services.user',
        actions: ['read', 'write'],
        scope: 'user-services'
      }
    ],
    constraints: [
      {
        type: 'user',
        specification: { requiresUserPresent: true },
        enforceLevel: 'block'
      }
    ],
    verificationRequired: true,
    auditLevel: 'standard'
  },
  
  'restricted': {
    type: 'restricted',
    permissions: [
      {
        resource: 'public.*',
        actions: ['read'],
        scope: 'public-only'
      },
      {
        resource: 'temp.*',
        actions: ['read', 'write'],
        scope: 'temporary'
      }
    ],
    constraints: [
      {
        type: 'resource',
        specification: { maxMemory: 100, maxCpu: 10 },
        enforceLevel: 'quarantine'
      }
    ],
    verificationRequired: false,
    auditLevel: 'minimal'
  }
};
```

## Specializations (Domain Tags)

```typescript
type DomainSpecialization = 
  | 'finance'              // Financial services and analysis
  | 'legal'                // Legal document processing
  | 'medical'              // Healthcare and medical advice
  | 'education'            // Learning and teaching
  | 'ai.devops'            // AI/ML operations and deployment
  | 'memory'               // Memory management and retrieval
  | 'mobility'             // Transportation and logistics
  | 'creativity'           // Creative tasks and content generation
  | 'communication'        // Messaging and social interaction
  | 'analytics'            // Data analysis and insights
  | 'security'             // Security and threat detection
  | 'productivity'         // Task management and optimization
  | 'entertainment'        // Gaming and media
  | 'research'             // Information gathering and synthesis
  | 'automation'           // Process automation
  | 'collaboration';       // Team coordination

interface SpecializationProfile {
  primary: DomainSpecialization;
  secondary: DomainSpecialization[];
  expertiseLevel: 'novice' | 'intermediate' | 'expert' | 'master';
  certifications?: string[];
  knowledgeSources: string[];
  lastTrainingUpdate: string;
}
```

## Modular Capabilities

Agents are composed of optional, hot-swappable modules:

```typescript
interface CapabilityModule {
  name: string;
  version: string;
  description: string;
  dependencies: string[];
  exports: string[];               // Exported functions/classes
  compatibility: {
    agentClasses: AgentClass[];
    authorityRequired: AuthorityType;
    resources: ResourceRequirement[];
  };
}

interface ResourceRequirement {
  type: 'memory' | 'cpu' | 'storage' | 'network';
  amount: number;
  unit: string;
  optional: boolean;
}
```

### Core Capability Modules

```typescript
const coreModules: Record<string, CapabilityModule> = {
  MemoryCore: {
    name: 'MemoryCore',
    version: '1.0.0',
    description: 'Long- and short-term semantic memory',
    dependencies: ['VectorDB', 'Encryption'],
    exports: ['MemoryManager', 'SemanticSearch', 'MemoryGraph'],
    compatibility: {
      agentClasses: ['user.personal', 'domain.specialist', 'orchestrator'],
      authorityRequired: 'trusted.user',
      resources: [
        { type: 'memory', amount: 50, unit: 'MB', optional: false },
        { type: 'storage', amount: 100, unit: 'MB', optional: false }
      ]
    }
  },
  
  SpeechIO: {
    name: 'SpeechIO',
    version: '1.0.0',
    description: 'Text-to-speech and speech-to-text integration',
    dependencies: ['AudioProcessing'],
    exports: ['TTSEngine', 'STTEngine', 'VoiceProfile'],
    compatibility: {
      agentClasses: ['user.personal', 'utility.service'],
      authorityRequired: 'trusted.user',
      resources: [
        { type: 'memory', amount: 25, unit: 'MB', optional: false },
        { type: 'cpu', amount: 15, unit: 'percent', optional: true }
      ]
    }
  },
  
  PersonaLayer: {
    name: 'PersonaLayer',
    version: '1.0.0',
    description: 'Emotion/personality modeling and tone',
    dependencies: ['MemoryCore'],
    exports: ['PersonalityEngine', 'EmotionModel', 'ToneAdapter'],
    compatibility: {
      agentClasses: ['user.personal', 'domain.specialist'],
      authorityRequired: 'trusted.user',
      resources: [
        { type: 'memory', amount: 30, unit: 'MB', optional: false }
      ]
    }
  },
  
  LangChainTools: {
    name: 'LangChainTools',
    version: '1.0.0',
    description: 'Tool abstraction for external APIs',
    dependencies: ['APIClient', 'SecurePrompt'],
    exports: ['ToolRegistry', 'ToolExecutor', 'ToolValidator'],
    compatibility: {
      agentClasses: ['domain.specialist', 'orchestrator', 'utility.service'],
      authorityRequired: 'restricted',
      resources: [
        { type: 'network', amount: 10, unit: 'connections', optional: false }
      ]
    }
  },
  
  SecurePrompt: {
    name: 'SecurePrompt',
    version: '1.0.0',
    description: 'Safe prompt template enforcement',
    dependencies: ['SecurityValidator'],
    exports: ['PromptValidator', 'TemplateEngine', 'SafetyFilter'],
    compatibility: {
      agentClasses: ['system.core', 'domain.specialist', 'orchestrator'],
      authorityRequired: 'trusted.user',
      resources: [
        { type: 'cpu', amount: 5, unit: 'percent', optional: false }
      ]
    }
  },
  
  PromptKindSync: {
    name: 'PromptKindSync',
    version: '1.0.0',
    description: 'Agent-to-agent protocol manager',
    dependencies: ['KLPRouter', 'IdentityManager'],
    exports: ['KLPClient', 'SyncManager', 'FederationHandler'],
    compatibility: {
      agentClasses: ['network.linker', 'orchestrator'],
      authorityRequired: 'linked.trust',
      resources: [
        { type: 'network', amount: 5, unit: 'connections', optional: false }
      ]
    }
  }
};
```

## Agent Declaration Format

```typescript
interface AgentMetadata {
  id: string;
  name: string;
  version: string;
  classification: AgentClassification;
  capabilities: string[];          // Module names
  manifest: AgentManifest;
  compatibility: CompatibilityMatrix;
}

interface CompatibilityMatrix {
  klpVersion: string;              // Supported KLP version
  agentProtocol: string;           // Agent protocol version
  requiredModules: string[];       // Must-have capability modules
  optionalModules: string[];       // Nice-to-have modules
  incompatibleWith: string[];      // Conflicting agents/modules
}

// Example Agent Declaration
const exampleAgent: AgentMetadata = {
  id: "agent-finance-007",
  name: "Personal Financial Advisor",
  version: "2.1.3",
  classification: {
    agentClass: "domain.specialist",
    specializations: ["finance", "analytics"],
    authorityType: "trusted.user",
    capabilities: ["MemoryCore", "LangChainTools", "SecurePrompt"],
    compatibilityLevel: "kOS-native"
  },
  capabilities: ["MemoryCore", "LangChainTools", "SecurePrompt"],
  manifest: {
    // ... (full manifest from lifecycle document)
  },
  compatibility: {
    klpVersion: "1.0",
    agentProtocol: "2.1",
    requiredModules: ["MemoryCore", "LangChainTools"],
    optionalModules: ["PersonaLayer", "SpeechIO"],
    incompatibleWith: ["legacy-financial-bot"]
  }
};
```

## Compatibility & Routing Rules

```typescript
class AgentCompatibilityEngine {
  canCommunicate(agentA: AgentMetadata, agentB: AgentMetadata): boolean {
    // Authority compatibility check
    if (!this.checkAuthorityCompatibility(agentA.classification.authorityType, agentB.classification.authorityType)) {
      return false;
    }
    
    // Protocol version compatibility
    if (!this.checkProtocolCompatibility(agentA.compatibility, agentB.compatibility)) {
      return false;
    }
    
    // Explicit incompatibility check
    if (agentA.compatibility.incompatibleWith.includes(agentB.id) ||
        agentB.compatibility.incompatibleWith.includes(agentA.id)) {
      return false;
    }
    
    return true;
  }
  
  private checkAuthorityCompatibility(
    authorityA: AuthorityType,
    authorityB: AuthorityType
  ): boolean {
    const compatibilityMatrix: Record<AuthorityType, AuthorityType[]> = {
      'root.kernel': ['root.kernel', 'trusted.user', 'linked.trust', 'restricted'],
      'trusted.user': ['trusted.user', 'linked.trust', 'restricted'],
      'linked.trust': ['trusted.user', 'linked.trust', 'restricted'],
      'restricted': ['restricted'],
      'external': ['external']
    };
    
    return compatibilityMatrix[authorityA].includes(authorityB);
  }
  
  private checkProtocolCompatibility(
    compatA: CompatibilityMatrix,
    compatB: CompatibilityMatrix
  ): boolean {
    // Semantic version comparison
    return this.isVersionCompatible(compatA.klpVersion, compatB.klpVersion) &&
           this.isVersionCompatible(compatA.agentProtocol, compatB.agentProtocol);
  }
}
```

### Communication Rules

1. **`user.personal` agents** may not invoke `external` without explicit user approval
2. **`system.core` agents** may invoke any class, but only with logged audit trail
3. **Orchestrators** must be able to deserialize all `agent.meta.json`
4. **`network.linker` agents** must register in the TrustLinkGraph
5. **Authority escalation** requires user confirmation and audit logging

```typescript
class AgentCommunicationRules {
  async validateCommunication(
    from: AgentMetadata,
    to: AgentMetadata,
    messageType: string
  ): Promise<ValidationResult> {
    const rules = [
      this.checkAuthorityEscalation,
      this.checkCrossClassCommunication,
      this.checkExternalCommunication,
      this.checkSystemIntegrity
    ];
    
    for (const rule of rules) {
      const result = await rule(from, to, messageType);
      if (!result.allowed) {
        return result;
      }
    }
    
    return { allowed: true };
  }
  
  private async checkExternalCommunication(
    from: AgentMetadata,
    to: AgentMetadata,
    messageType: string
  ): Promise<ValidationResult> {
    if (from.classification.agentClass === 'user.personal' && 
        to.classification.authorityType === 'external') {
      
      const userApproval = await this.requestUserApproval(from, to, messageType);
      return {
        allowed: userApproval,
        reason: userApproval ? undefined : 'User approval required for external communication'
      };
    }
    
    return { allowed: true };
  }
}

interface ValidationResult {
  allowed: boolean;
  reason?: string;
  requiresApproval?: boolean;
  auditRequired?: boolean;
}
```

## Future Considerations

### Planned Extensions

1. **Decentralized Agent Certification (DAC)**
   - Blockchain-based agent verification
   - Community-driven certification process
   - Reputation scoring system

2. **Automatic Class Evolution**
   - Self-reflective growth capabilities
   - Performance-based class upgrades
   - Dynamic capability acquisition

3. **Simulated Swarm Behavior Agents**
   - Collective intelligence patterns
   - Emergent behavior modeling
   - Swarm optimization algorithms

4. **Companion/Embodied Agent Markup Standards**
   - Physical interaction capabilities
   - Sensory input processing
   - Spatial awareness and navigation

### Research Areas

```typescript
interface FutureAgentCapabilities {
  selfModification: boolean;       // Can modify own code/behavior
  consciousness: boolean;          // Self-awareness capabilities
  creativity: boolean;             // Creative problem solving
  empathy: boolean;               // Emotional understanding
  intuition: boolean;             // Pattern recognition beyond training
}

interface SwarmBehavior {
  collectiveIntelligence: boolean;
  emergentBehaviors: string[];
  consensusMechanisms: string[];
  distributedDecisionMaking: boolean;
}
```

## Implementation Status

- **Core Classification System**: Specification complete
- **Authority Framework**: Architecture defined
- **Capability Module System**: Interface designed
- **Compatibility Engine**: Rules specified
- **Communication Framework**: Protocols defined
- **Reference Implementation**: Planned for kOS v1.0

## Changelog

- **2024-12-28**: Comprehensive taxonomy specification with TypeScript interfaces
- **2024-06-20**: Initial taxonomy draft by agent (legacy reference) 