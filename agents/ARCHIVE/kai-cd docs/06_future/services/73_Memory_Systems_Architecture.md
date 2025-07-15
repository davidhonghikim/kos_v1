---
title: "Memory Systems Architecture"
description: "Complete architecture for volatile, long-term, and immutable memory systems across kAI and kOS with modular, scalable components"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["agent-memory-vector-database.md", "data-storage-and-security.md"]
implementation_status: "planned"
---

# Memory Systems Architecture (Volatile, Long-Term, Immutable)

This document outlines the architecture, component breakdown, data schema, and protocol interfaces for memory systems within `kAI` and `kOS`. Memory types include volatile (session), long-term (persistent), and immutable (auditable).

## Agent Context
**For AI Agents:** Use the three-tier memory system appropriately: volatile for session context, long-term for persistent learning, and immutable for audit trails. Follow the SQL schema exactly, implement proper embedding storage, and maintain memory integrity through hash chains.

## Memory Tiers Overview

### A. Volatile Memory (Short-Term / Session-Based)

- **Storage:** In-memory only (RAM, IndexedDB, Redis ephemeral)
- **Scope:** Per session / per request / temporary context
- **Access:** Fast, high-availability cache layer
- **Use Cases:** Ongoing conversations, temp computations, context injection

### B. Long-Term Memory (Persistent)

- **Storage:** PostgreSQL, SQLite, Redis (durable), Qdrant
- **Scope:** Per agent, per user, system-wide
- **Access:** SQL / API / indexed semantic search
- **Use Cases:** Agent training, history reconstruction, user behavior modeling

### C. Immutable Memory (Audit / Historical / Blockchain-Synced)

- **Storage:** IPFS, Git-based snapshots, Write-once logs, Blockchain (optional)
- **Scope:** Shared/public or sensitive logs
- **Access:** Merkle-hashed references, read-only APIs
- **Use Cases:** Compliance, provenance, high-integrity logs, zero-trust operations

## Long-Term Memory Schema

### A. Relational (PostgreSQL)

```sql
CREATE TABLE agent_memory (
  id UUID PRIMARY KEY,
  agent_id TEXT,
  user_id TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  memory_type TEXT, -- factual, experiential, narrative
  content TEXT,
  embedding VECTOR(1536),
  source TEXT,
  tags TEXT[],
  trust_score FLOAT
);
```

### B. Vector Index (Qdrant)

- **Collection Name:** `kai-agent-memories`
- **Metadata Schema:**

```json
{
  "agent_id": "planner-001",
  "user_id": "stone",
  "tags": ["nutrition", "health"],
  "source": "user-input"
}
```

## TypeScript Implementation

```typescript
interface MemoryEntry {
  id: string;
  agent_id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  memory_type: 'factual' | 'experiential' | 'narrative';
  content: string;
  embedding?: number[];
  source: string;
  tags: string[];
  trust_score: number;
}

interface VolatileSession {
  session_id: string;
  messages: Array<{
    role: 'user' | 'agent' | 'system';
    text: string;
    timestamp: string;
  }>;
  token_budget: number;
  context_snapshot?: any;
}

class MemoryManager {
  private volatile: Map<string, VolatileSession> = new Map();
  private longTerm: LongTermMemoryStore;
  private immutable: ImmutableMemoryStore;
  
  constructor() {
    this.longTerm = new LongTermMemoryStore();
    this.immutable = new ImmutableMemoryStore();
  }
  
  // Volatile Memory Operations
  async createSession(sessionId: string): Promise<void> {
    this.volatile.set(sessionId, {
      session_id: sessionId,
      messages: [],
      token_budget: 4000
    });
  }
  
  async addToSession(sessionId: string, message: any): Promise<void> {
    const session = this.volatile.get(sessionId);
    if (session) {
      session.messages.push(message);
    }
  }
  
  // Long-Term Memory Operations
  async saveMemory(entry: Omit<MemoryEntry, 'id' | 'created_at' | 'updated_at'>): Promise<string> {
    const memoryEntry: MemoryEntry = {
      ...entry,
      id: this.generateId(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    await this.longTerm.store(memoryEntry);
    
    // Also create immutable record
    await this.immutable.append({
      action: 'save_memory',
      memory_id: memoryEntry.id,
      timestamp: memoryEntry.created_at,
      hash: this.calculateHash(memoryEntry)
    });
    
    return memoryEntry.id;
  }
  
  async recallMemory(query: string, agentId: string): Promise<MemoryEntry[]> {
    return await this.longTerm.search(query, { agent_id: agentId });
  }
  
  // Memory Integrity
  async verifyMemoryIntegrity(): Promise<boolean> {
    const memories = await this.longTerm.getAllMemories();
    
    for (const memory of memories) {
      const currentHash = this.calculateHash(memory);
      const immutableRecord = await this.immutable.getRecord(memory.id);
      
      if (immutableRecord?.hash !== currentHash) {
        return false; // Integrity violation detected
      }
    }
    
    return true;
  }
  
  private generateId(): string {
    return `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  private calculateHash(entry: MemoryEntry): string {
    const crypto = require('crypto');
    return crypto.createHash('sha256').update(JSON.stringify(entry)).digest('hex');
  }
}

class LongTermMemoryStore {
  async store(entry: MemoryEntry): Promise<void> {
    // Store in PostgreSQL and vector database
  }
  
  async search(query: string, filters: any): Promise<MemoryEntry[]> {
    // Perform semantic search using embeddings
    return [];
  }
  
  async getAllMemories(): Promise<MemoryEntry[]> {
    // Retrieve all memories for integrity checking
    return [];
  }
}

class ImmutableMemoryStore {
  async append(record: any): Promise<void> {
    // Append to immutable log (IPFS, Git, blockchain)
  }
  
  async getRecord(id: string): Promise<any> {
    // Retrieve immutable record by ID
    return null;
  }
}
```

## Memory Management Protocols

### A. Save Memory

```http
POST /api/agent/memory
{
  "content": "User asked about vitamin D.",
  "tags": ["health", "vitamins"],
  "source": "chat",
  "memory_type": "factual"
}
```

### B. Recall Memory

```http
GET /api/agent/memory?query=vitamin%20D&agent_id=health-coach
```

### C. Memory Integrity Check

- Scheduled hashing validation
- `agent --audit-memory`
- Result: diff of expected vs current hash chain

## Access Control

- **RBAC:** Role-based access for agents/users
- **Granular Permissions:**
  - Read-only
  - Append-only
  - Full access
- **Token-Scoped:** JWT claims define allowed memory tier access

## Future Features

- **Federated Memory Graph:** Shared memory across mesh agents
- **Decay Modeling:** Older memories lose recall weight unless reinforced
- **Sentiment Drift:** Tag memories with emotional weight
- **Memory Compression:** Periodic summarization of redundant records

## Cross-References

- [Agent Memory Vector Database](agent-memory-vector-database.md) - Vector storage details
- [Data Storage Security](../security/data-storage-and-security.md) - Security protocols 