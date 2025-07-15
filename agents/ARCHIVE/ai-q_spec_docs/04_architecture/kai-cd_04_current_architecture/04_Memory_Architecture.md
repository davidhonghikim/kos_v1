---
title: "Memory Architecture"
description: "Current Kai-CD memory system with evolution path to kOS distributed memory"
category: "architecture"
subcategory: "memory"
context: "current_implementation"
implementation_status: "partial"
decision_scope: "high"
complexity: "high"
last_updated: "2025-01-20"
code_references:
  - "src/store/"
  - "src/utils/crypto.ts"
  - "src/components/VaultManager.tsx"
related_documents:
  - "./02_state-management.md"
  - "../../future/services/01_prompt-management.md"
  - "../../future/agents/02_memory-architecture.md"
dependencies: ["Chrome Storage API", "Zustand", "WebCrypto", "IndexedDB"]
breaking_changes: false
agent_notes: "Memory system architecture - understand current limitations and future multi-tier vision"
---

# Memory Architecture

## Agent Context
**For AI Agents**: Complete memory architecture covering current Chrome storage implementation and evolution to sophisticated multi-tier distributed memory system. Use this when implementing data persistence, understanding memory patterns, or planning storage systems. Critical foundation for all data storage and retrieval work.

**Implementation Notes**: Contains current Chrome storage patterns and future vector database integration with short-term, long-term, and global memory tiers. Includes working TypeScript interfaces and storage schemas.
**Quality Requirements**: Keep memory patterns and storage implementations synchronized with actual system. Maintain accuracy of evolution pathway to distributed memory.
**Integration Points**: Foundation for data persistence, links to state management, security vault, and future distributed memory systems.

---

## Quick Summary
Current Chrome storage-based memory system with evolution path to sophisticated multi-tier memory architecture including short-term, long-term, and global federated memory for kOS.

## Current Implementation (Kai-CD)

### Memory Tiers Overview

**Current State**: Single-tier Chrome storage with basic persistence
**Future Vision**: Multi-tier distributed memory system

#### 1. Current Chrome Storage
- **Storage**: `chrome.storage.local` with JSON serialization
- **Scope**: Per-extension instance, browser-bound
- **Persistence**: Survives browser restarts, lost on extension uninstall
- **Capacity**: Limited by Chrome's storage quotas (~10MB typical)
- **Access**: Synchronous/asynchronous via Zustand persistence

#### 2. Planned Memory Tiers (Future)

##### Short-Term Memory (STM)
- **Scope**: Session or transient memory
- **Lifetime**: Reset after session expiration or timeout
- **Storage**: In-memory (RAM, IndexedDB, Redis ephemeral)
- **Access Speed**: Ultra-fast
- **Use Cases**: Contextual backtracking, ongoing dialogue, temporary scratchpad

##### Long-Term Memory (LTM)  
- **Scope**: Persistent, agent-specific knowledge
- **Lifetime**: Durable across sessions
- **Storage**: Vector database (Qdrant/Chroma/Weaviate)
- **Access Speed**: Fast, indexed via embedding
- **Use Cases**: Remembering preferences, user data, task history, assistant training

##### Global Memory (GMEM)
- **Scope**: Shared, federated knowledge base
- **Lifetime**: Persistent, versioned
- **Storage**: Federated vector stores + graph stores
- **Access Speed**: Medium
- **Use Cases**: Swarm knowledge sharing, global common sense, system-wide coordination

## Current Storage Architecture

### Zustand Stores with Chrome Persistence

```typescript
// Current implementation pattern
interface MemoryStore {
  // Volatile state (resets on reload)
  sessionData: SessionData;
  
  // Persisted state (survives restarts)
  persistedMemories: Memory[];
  userPreferences: UserPrefs;
  serviceConfigurations: ServiceConfig[];
}
```

### Storage Locations

```
Chrome Extension Storage:
├── serviceStore          # Service definitions and health status
├── viewStateStore        # UI state and active selections  
├── settingsStore         # User preferences and configuration
├── logStore             # Application logs (limited retention)
├── vaultStore           # Encrypted credential storage
└── securityStateStore   # Security tools and vault state
```

### Current Limitations
- **No Vector Search**: No semantic similarity search capabilities
- **Limited Capacity**: Chrome storage quotas restrict data volume
- **No Federation**: Cannot share memory across instances
- **Basic Encryption**: Simple AES encryption without advanced key management
- **No Decay**: No automatic memory aging or cleanup policies

## Future Memory System Architecture

### Planned Directory Structure

```
memory/
├── stm/
│   ├── cache.ts               # In-memory short-term store
│   ├── context_tracker.ts     # Active dialogue and state tracking
│   └── timeout_manager.ts     # Auto-expiration routines
├── ltm/
│   ├── vector_store_qdrant.ts # Qdrant-backed persistent memory
│   ├── summarizer.ts          # Long-form text chunker + condenser
│   ├── metadata_indexer.ts    # Tagging and semantic search utilities
│   └── schema.ts              # User + content data models
├── gmem/
│   ├── sync_bridge.ts         # Federation protocol connector
│   ├── knowledge_graph.ts     # Shared RDF-style graph store
│   ├── peer_registry.ts       # Known agent memory contributors
│   └── sync_policy.yaml       # Access rules, merge policies
├── embeddings/
│   ├── generator_openai.ts    # API-based embedding client
│   ├── generator_local.ts     # On-device encoder (e.g., InstructorXL)
│   └── embed_router.ts        # Route queries to appropriate embedder
└── utils/
    ├── similarity.ts          # Cosine similarity, ranking
    ├── chunking.ts            # Adaptive token-length chunker
    └── hash.ts                # UUID + content integrity hashing
```

### Future Configuration Schema

```yaml
memory:
  short_term:
    max_items: 512
    expiration_sec: 1800
    enable_entity_tracking: true
  
  long_term:
    vector_backend: qdrant
    embedding_model: instructor-xl
    summarization: true
    max_tokens_per_item: 2048
  
  embedding:
    default_provider: local
    fallback: openai
    use_fp16: true
  
  global:
    federation: true
    trust_required: true
    default_access: read-only
    replication:
      interval_sec: 900
      sync_peers:
        - kind://agent.knowledge.alpha
        - kind://agent.memory.bridge01
```

## Memory Object Schemas

### Current Memory Record (Chrome Storage)

```typescript
interface CurrentMemoryRecord {
  id: string;
  timestamp: string;
  type: 'conversation' | 'preference' | 'service_config';
  content: string;
  metadata?: Record<string, any>;
}
```

### Future Memory Record (Vector-Based)

```typescript
interface FutureMemoryRecord {
  id: string;
  type: 'observation' | 'thought' | 'instruction';
  embedding: number[];
  metadata: {
    agentId: string;
    timestamp: string;
    tags: string[];
    importance: number;
    source: 'user' | 'agent' | 'external';
  };
  content: string;
}
```

## Memory Access Patterns

### Current Access (Zustand)

```typescript
// Current pattern - direct store access
const { memories, addMemory } = useMemoryStore();

// Add memory
await addMemory({
  type: 'conversation',
  content: 'User asked about hydroponics',
  timestamp: new Date().toISOString()
});

// Retrieve memories (basic filtering)
const relevantMemories = memories.filter(m => 
  m.content.includes('hydroponics')
);
```

### Future Access (Abstracted API)

```typescript
// Future pattern - semantic search
interface MemoryAdapter {
  store(record: MemoryRecord): Promise<void>;
  search(query: string, topK: number): Promise<MemoryRecord[]>;
  delete(id: string): Promise<void>;
  summarize(tags?: string[]): Promise<string>;
}

// Usage
const memory = new MemoryAdapter('qdrant');
await memory.store({
  type: 'observation',
  content: 'User interested in hydroponic setups',
  embedding: await generateEmbedding(content)
});

const matches = await memory.search('hydroponics', 5);
```

## Memory Security & Privacy

### Current Security
- **Encryption**: AES-256-GCM for vault storage
- **Access Control**: Browser-based isolation
- **Key Management**: User-derived keys with PBKDF2
- **Audit Trail**: Basic logging in logStore

### Future Security Enhancements
- **Access Scopes**: private, team, shared, public
- **Advanced Encryption**: AES-256 at rest, TLS in transit
- **Trust Tokens**: KLP (Kind Link Protocol) for secure memory federation
- **Comprehensive Audit**: All write/edit actions logged with signatures
- **Memory Permissions**: Role-based access control for different memory tiers

## Evolution Strategy

### Phase 1: Enhanced Local Memory (Current → Near-term)
1. **Implement Vector Search**: Add local embedding generation and similarity search
2. **Memory Categorization**: Organize memories by type and importance
3. **Retention Policies**: Implement memory aging and cleanup
4. **Enhanced Encryption**: Upgrade key management and storage security

### Phase 2: Distributed Memory (Near-term → Medium-term)
1. **External Vector DB**: Integration with Qdrant/Chroma for persistent memory
2. **Memory Synchronization**: Cross-device memory sync for same user
3. **Agent Memory**: Dedicated memory spaces for different agent personas
4. **Federation Prep**: Protocols for memory sharing across instances

### Phase 3: Federated Memory (Medium-term → Long-term)
1. **Global Memory**: Shared knowledge base across kOS network
2. **Trust-Based Access**: Memory sharing based on trust relationships
3. **Collaborative Learning**: Agents learning from shared experiences
4. **Decentralized Storage**: IPFS or similar for distributed memory storage

## Integration Points

### Current System Integration
- **Service Store**: Service configurations and health status
- **Vault Store**: Encrypted credentials and sensitive data
- **Settings Store**: User preferences and system configuration
- **Log Store**: Application events and debugging information

### Future System Integration
- **Agent Hierarchy**: Different memory access for different agent roles
- **KLP Protocol**: Secure memory federation via Kind Link Protocol
- **Governance System**: Trust-based memory access control
- **Prompt Management**: Centralized prompt storage and versioning

## Memory Query Patterns

### Current Query Patterns
```typescript
// Simple filtering and searching
const serviceMemories = memories.filter(m => m.type === 'service_config');
const recentMemories = memories.filter(m => 
  Date.now() - new Date(m.timestamp).getTime() < 86400000
);
```

### Future Query Patterns
```typescript
// Semantic search with embedding similarity
const relatedMemories = await memory.search({
  query: "machine learning deployment",
  filters: { agent_id: "planner-001", importance: { $gte: 0.7 } },
  limit: 10
});

// Multi-modal memory queries
const contextualMemories = await memory.searchWithContext({
  query: "previous conversation about APIs",
  context: currentConversation,
  timeRange: { days: 7 }
});
```

## Performance Considerations

### Current Performance
- **Latency**: ~1-5ms for Chrome storage access
- **Throughput**: Limited by JSON serialization overhead
- **Scalability**: Degrades with large datasets
- **Memory Usage**: All data loaded into memory

### Future Performance Targets
- **STM Latency**: <1ms for in-memory access
- **LTM Latency**: <50ms for vector similarity search
- **GMEM Latency**: <200ms for federated queries
- **Throughput**: 1000+ operations/second
- **Scalability**: Linear scaling with distributed storage

## Related Documentation

- [State Management](02_state-management.md) - Current Zustand store architecture
- [Prompt Management](../../future/services/01_prompt-management.md) - Future prompt storage
- [Security Framework](../security/01_security-framework.md) - Encryption and access control
- [Service Architecture](../services/01_service-architecture.md) - Service integration patterns

---

