---
title: "Agent Memory and Vector Database System"
description: "Comprehensive memory architecture for kAI agents with vector database integration, semantic search, and persistent context management"
type: "implementation"
status: "future"
priority: "high"
last_updated: "2025-01-20"
related_docs: ["memory-architecture.md", "service-architecture.md", "ai-agent-framework-and-capabilities.md"]
implementation_status: "planned"
complexity: "high"
decision_scope: "system-wide"
code_references: ["src/memory/", "src/memory/providers/", "src/memory/agents/"]
---

# Agent Memory and Vector Database System

## Agent Context
This document defines the comprehensive memory architecture for kAI agents, enabling persistent, queryable memory through vector database integration. Agents should understand this as their long-term memory system that allows storage, retrieval, and reasoning over contextual information, documents, and interactions. The system provides semantic search capabilities and supports multiple vector database providers.

## Purpose and Capabilities

The Agent Memory System enables agents to:

- **Store Contextual Memories**: Persistent storage of conversations, decisions, and learned information
- **Semantic Search**: Vector-based similarity search over historical knowledge and interactions
- **Dynamic Retrieval**: Context-aware retrieval of relevant information during task execution
- **Document Indexing**: Automatic indexing and embedding of documents, files, and external content
- **Experience Learning**: Accumulation of experience and patterns from repeated interactions
- **Cross-Agent Knowledge**: Shared knowledge bases and collaborative memory systems

## Architecture Overview

```text
┌─────────────────────────────────────────┐
│            Agent Memory API             │ ← Unified interface for all agents
├─────────────────────────────────────────┤
│          Memory Orchestrator            │ ← Memory lifecycle and coordination
├─────────────────────────────────────────┤
│         Embedding Generation            │ ← Multi-model embedding pipeline
├─────────────────────────────────────────┤
│        Vector Database Layer            │ ← Provider-agnostic vector operations
├─────────────────────────────────────────┤
│         Provider Adapters               │ ← Chroma, Qdrant, Weaviate, Pinecone
├─────────────────────────────────────────┤
│        Memory Classification            │ ← Namespace and category management
└─────────────────────────────────────────┘
```

## Directory Structure

```text
src/
└── memory/
    ├── index.ts                      # Unified memory interface and exports
    ├── core/
    │   ├── MemoryOrchestrator.ts     # Central memory coordination
    │   ├── MemoryManager.ts          # High-level memory operations
    │   ├── EmbeddingPipeline.ts      # Embedding generation and caching
    │   └── MemorySearch.ts           # Advanced search and retrieval
    ├── providers/
    │   ├── BaseProvider.ts           # Abstract provider interface
    │   ├── ChromaProvider.ts         # Chroma database adapter
    │   ├── QdrantProvider.ts         # Qdrant database adapter
    │   ├── WeaviateProvider.ts       # Weaviate database adapter
    │   ├── PineconeProvider.ts       # Pinecone cloud adapter
    │   └── LocalProvider.ts          # Local file-based fallback
    ├── agents/
    │   ├── MemoryAgent.ts            # Base class for memory-enabled agents
    │   ├── MemoryIndexer.ts          # Background indexing worker
    │   ├── ContextManager.ts         # Context window and relevance management
    │   └── KnowledgeGraph.ts         # Relationship and graph-based memory
    ├── types/
    │   ├── MemoryTypes.ts            # Core memory type definitions
    │   ├── ProviderTypes.ts          # Provider-specific interfaces
    │   └── SearchTypes.ts            # Search and retrieval types
    ├── utils/
    │   ├── EmbeddingUtils.ts         # Embedding generation utilities
    │   ├── MemorySchema.ts           # Memory object validation
    │   ├── ChunkingStrategy.ts       # Document chunking algorithms
    │   └── MemoryOptimizer.ts        # Performance and storage optimization
    └── config/
        ├── memory.config.ts          # Memory system configuration
        ├── providers.config.ts       # Provider-specific configurations
        └── embedding.config.ts       # Embedding model configurations
```

## Memory Object Schema and Types

```typescript
// src/memory/types/MemoryTypes.ts
interface MemoryObject {
  id: string;                          // Unique memory identifier
  agentId: string;                     // Originating agent identifier
  namespace: MemoryNamespace;          // Memory category classification
  content: MemoryContent;              // Memory content and metadata
  embedding: number[];                 // Precomputed vector embedding
  metadata: MemoryMetadata;            // Additional contextual information
  relationships: MemoryRelationship[]; // Connections to other memories
  timestamp: string;                   // Creation timestamp (ISO8601)
  lastAccessed: string;                // Last access timestamp
  accessCount: number;                 // Access frequency counter
  importance: number;                  // Importance score (0-1)
  retention: RetentionPolicy;          // Memory retention configuration
}

interface MemoryContent {
  text: string;                        // Primary textual content
  summary?: string;                    // Optional content summary
  keywords: string[];                  // Extracted keywords and tags
  entities: ExtractedEntity[];         // Named entities and concepts
  sentiment?: SentimentAnalysis;       // Emotional context
  language: string;                    // Content language code
  contentType: ContentType;            // Type classification
}

interface MemoryMetadata {
  source: MemorySource;                // Origin of the memory
  context: ContextInformation;         // Situational context
  quality: QualityMetrics;             // Content quality assessment
  privacy: PrivacyLevel;               // Privacy and sharing settings
  tags: string[];                      // User-defined tags
  customFields: Record<string, any>;   // Extensible metadata
}

enum MemoryNamespace {
  CONVERSATION = 'conversation',       // Chat interactions and dialogue
  DOCUMENTS = 'documents',             // Indexed documents and files
  TASKS = 'tasks',                     // Task execution and planning
  DECISIONS = 'decisions',             // Decision-making processes
  LEARNING = 'learning',               // Acquired knowledge and insights
  CONTEXT = 'context',                 // Environmental and situational context
  RELATIONSHIPS = 'relationships',     // Social and entity relationships
  PROCEDURES = 'procedures',           // Learned procedures and workflows
  OBSERVATIONS = 'observations',       // Environmental observations
  GOALS = 'goals'                      // Objectives and intentions
}

enum ContentType {
  TEXT = 'text',
  CONVERSATION = 'conversation',
  DOCUMENT = 'document',
  CODE = 'code',
  DECISION = 'decision',
  OBSERVATION = 'observation',
  PLAN = 'plan',
  REFLECTION = 'reflection'
}

interface MemoryRelationship {
  targetId: string;                    // Related memory ID
  type: RelationshipType;              // Relationship classification
  strength: number;                    // Relationship strength (0-1)
  metadata: Record<string, any>;       // Relationship-specific data
}

enum RelationshipType {
  CAUSAL = 'causal',                   // Cause-effect relationship
  TEMPORAL = 'temporal',               // Time-based sequence
  SIMILARITY = 'similarity',           // Content similarity
  CONTRADICTION = 'contradiction',     // Conflicting information
  ELABORATION = 'elaboration',         // Additional details
  REFERENCE = 'reference',             // Cross-reference
  DEPENDENCY = 'dependency'            // Logical dependency
}
```

## Vector Database Provider Support

### Supported Providers

| Provider | Local | Cloud | Authentication | Features |
|----------|-------|-------|----------------|----------|
| Chroma | ✅ | ✅ | None / API Token | Open source, Python-native |
| Qdrant | ✅ | ✅ | API Key | High performance, Rust-based |
| Weaviate | ✅ | ✅ | API Key / Bearer | GraphQL, hybrid search |
| Pinecone | ❌ | ✅ | API Key | Managed service, enterprise |
| Local | ✅ | ❌ | None | File-based fallback |

### Provider Implementation

```typescript
// src/memory/providers/BaseProvider.ts
interface VectorProvider {
  id: string;
  name: string;
  isLocal: boolean;
  capabilities: ProviderCapabilities;
  
  // Connection management
  connect(config: ProviderConfig): Promise<void>;
  disconnect(): Promise<void>;
  healthCheck(): Promise<HealthStatus>;
  
  // Collection management
  createCollection(name: string, config: CollectionConfig): Promise<void>;
  deleteCollection(name: string): Promise<void>;
  listCollections(): Promise<string[]>;
  
  // Memory operations
  store(memories: MemoryObject[]): Promise<void>;
  retrieve(ids: string[]): Promise<MemoryObject[]>;
  delete(ids: string[]): Promise<void>;
  update(memories: Partial<MemoryObject>[]): Promise<void>;
  
  // Search operations
  search(query: SearchQuery): Promise<SearchResult[]>;
  similaritySearch(embedding: number[], options: SearchOptions): Promise<SearchResult[]>;
  hybridSearch(textQuery: string, embedding: number[], options: HybridSearchOptions): Promise<SearchResult[]>;
  
  // Batch operations
  batchStore(memories: MemoryObject[], batchSize?: number): Promise<BatchResult>;
  batchDelete(ids: string[], batchSize?: number): Promise<BatchResult>;
}

// src/memory/providers/QdrantProvider.ts
class QdrantProvider implements VectorProvider {
  private client: QdrantClient;
  private config: QdrantConfig;

  constructor(config: QdrantConfig) {
    this.config = config;
    this.client = new QdrantClient({
      url: config.url,
      apiKey: config.apiKey,
      timeout: config.timeout || 30000
    });
  }

  async connect(): Promise<void> {
    try {
      await this.client.getCollections();
      this.logger.info('Connected to Qdrant successfully');
    } catch (error) {
      throw new ProviderConnectionError(`Failed to connect to Qdrant: ${error.message}`);
    }
  }

  async search(query: SearchQuery): Promise<SearchResult[]> {
    const searchRequest: QdrantSearchRequest = {
      collection_name: this.getCollectionName(query.namespace),
      vector: query.embedding,
      limit: query.limit || 10,
      score_threshold: query.threshold || 0.7,
      with_payload: true,
      with_vector: false
    };

    if (query.filter) {
      searchRequest.filter = this.buildQdrantFilter(query.filter);
    }

    const response = await this.client.search(searchRequest);
    
    return response.map(result => ({
      memory: this.parseQdrantPayload(result.payload),
      score: result.score,
      metadata: {
        provider: 'qdrant',
        searchTime: Date.now()
      }
    }));
  }

  private buildQdrantFilter(filter: MemoryFilter): QdrantFilter {
    const conditions: QdrantCondition[] = [];

    if (filter.agentId) {
      conditions.push({
        key: 'agentId',
        match: { value: filter.agentId }
      });
    }

    if (filter.namespace) {
      conditions.push({
        key: 'namespace',
        match: { value: filter.namespace }
      });
    }

    if (filter.timeRange) {
      conditions.push({
        key: 'timestamp',
        range: {
          gte: filter.timeRange.start,
          lte: filter.timeRange.end
        }
      });
    }

    if (filter.tags && filter.tags.length > 0) {
      conditions.push({
        key: 'tags',
        match: { any: filter.tags }
      });
    }

    return { must: conditions };
  }
}
```

## Embedding Generation Pipeline

```typescript
// src/memory/core/EmbeddingPipeline.ts
interface EmbeddingProvider {
  id: string;
  name: string;
  model: string;
  dimensions: number;
  maxTokens: number;
  costPerToken: number;
  
  generateEmbedding(text: string): Promise<number[]>;
  generateBatchEmbeddings(texts: string[]): Promise<number[][]>;
}

class EmbeddingPipeline {
  private providers: Map<string, EmbeddingProvider>;
  private cache: EmbeddingCache;
  private optimizer: EmbeddingOptimizer;

  constructor(config: EmbeddingConfig) {
    this.providers = new Map();
    this.cache = new EmbeddingCache(config.cache);
    this.optimizer = new EmbeddingOptimizer();
    this.initializeProviders(config.providers);
  }

  async generateEmbedding(
    text: string, 
    options: EmbeddingOptions = {}
  ): Promise<EmbeddingResult> {
    // Check cache first
    const cacheKey = this.generateCacheKey(text, options);
    const cached = await this.cache.get(cacheKey);
    if (cached) {
      return { embedding: cached.embedding, fromCache: true, provider: cached.provider };
    }

    // Select optimal provider
    const provider = await this.selectProvider(text, options);
    
    // Optimize text for embedding
    const optimizedText = await this.optimizer.optimizeText(text, provider);
    
    // Generate embedding
    const embedding = await provider.generateEmbedding(optimizedText);
    
    // Cache result
    await this.cache.set(cacheKey, {
      embedding,
      provider: provider.id,
      timestamp: Date.now()
    });

    return {
      embedding,
      fromCache: false,
      provider: provider.id,
      optimizedText,
      metadata: {
        originalLength: text.length,
        optimizedLength: optimizedText.length,
        dimensions: embedding.length
      }
    };
  }

  private async selectProvider(
    text: string, 
    options: EmbeddingOptions
  ): Promise<EmbeddingProvider> {
    // Use specified provider if given
    if (options.provider) {
      const provider = this.providers.get(options.provider);
      if (!provider) {
        throw new Error(`Unknown embedding provider: ${options.provider}`);
      }
      return provider;
    }

    // Select based on text characteristics and requirements
    const textLength = text.length;
    const requiresLocal = options.requireLocal || false;
    const maxCost = options.maxCost || Infinity;

    const candidates = Array.from(this.providers.values()).filter(provider => {
      if (requiresLocal && !provider.isLocal) return false;
      if (textLength > provider.maxTokens * 4) return false; // Rough token estimation
      
      const estimatedCost = (textLength / 4) * provider.costPerToken; // Rough estimation
      if (estimatedCost > maxCost) return false;
      
      return true;
    });

    if (candidates.length === 0) {
      throw new Error('No suitable embedding provider found for the given constraints');
    }

    // Select best provider based on performance and cost
    return candidates.reduce((best, current) => {
      const bestScore = this.calculateProviderScore(best, textLength);
      const currentScore = this.calculateProviderScore(current, textLength);
      return currentScore > bestScore ? current : best;
    });
  }

  private initializeProviders(configs: EmbeddingProviderConfig[]): void {
    for (const config of configs) {
      let provider: EmbeddingProvider;

      switch (config.type) {
        case 'openai':
          provider = new OpenAIEmbeddingProvider(config);
          break;
        case 'ollama':
          provider = new OllamaEmbeddingProvider(config);
          break;
        case 'huggingface':
          provider = new HuggingFaceEmbeddingProvider(config);
          break;
        case 'cohere':
          provider = new CohereEmbeddingProvider(config);
          break;
        default:
          throw new Error(`Unknown embedding provider type: ${config.type}`);
      }

      this.providers.set(provider.id, provider);
    }
  }
}
```

## Memory-Enabled Agent Base Class

```typescript
// src/memory/agents/MemoryAgent.ts
abstract class MemoryAgent {
  protected memoryManager: MemoryManager;
  protected contextManager: ContextManager;
  protected agentId: string;

  constructor(agentId: string, memoryConfig: MemoryConfig) {
    this.agentId = agentId;
    this.memoryManager = new MemoryManager(memoryConfig);
    this.contextManager = new ContextManager(this.memoryManager, agentId);
  }

  // Memory storage operations
  async storeMemory(content: string, namespace: MemoryNamespace, metadata?: Partial<MemoryMetadata>): Promise<string> {
    const memory: MemoryObject = {
      id: this.generateMemoryId(),
      agentId: this.agentId,
      namespace,
      content: await this.processContent(content),
      embedding: await this.generateEmbedding(content),
      metadata: {
        source: { type: 'agent', id: this.agentId },
        context: await this.captureContext(),
        quality: await this.assessContentQuality(content),
        privacy: PrivacyLevel.PRIVATE,
        tags: metadata?.tags || [],
        customFields: metadata?.customFields || {},
        ...metadata
      },
      relationships: [],
      timestamp: new Date().toISOString(),
      lastAccessed: new Date().toISOString(),
      accessCount: 0,
      importance: this.calculateImportance(content, namespace),
      retention: this.getRetentionPolicy(namespace)
    };

    await this.memoryManager.store(memory);
    return memory.id;
  }

  // Memory retrieval operations
  async retrieveRelevantMemories(
    query: string, 
    namespace?: MemoryNamespace, 
    options: RetrievalOptions = {}
  ): Promise<MemoryObject[]> {
    const searchQuery: SearchQuery = {
      text: query,
      embedding: await this.generateEmbedding(query),
      namespace,
      agentId: this.agentId,
      limit: options.limit || 10,
      threshold: options.threshold || 0.7,
      filter: options.filter
    };

    const results = await this.memoryManager.search(searchQuery);
    
    // Update access counts and timestamps
    const memories = results.map(result => result.memory);
    await this.updateAccessMetrics(memories);
    
    return memories;
  }

  // Context-aware memory integration
  async enhanceWithMemory(prompt: string, maxMemories: number = 5): Promise<string> {
    const relevantMemories = await this.retrieveRelevantMemories(prompt, undefined, {
      limit: maxMemories,
      threshold: 0.6
    });

    if (relevantMemories.length === 0) {
      return prompt;
    }

    const memoryContext = relevantMemories
      .map(memory => `[Memory] ${memory.content.text}`)
      .join('\n');

    return `${prompt}\n\nRelevant context from memory:\n${memoryContext}`;
  }

  // Memory-based decision making
  async makeMemoryInformedDecision(
    situation: string, 
    options: string[]
  ): Promise<DecisionResult> {
    // Retrieve relevant past decisions and outcomes
    const pastDecisions = await this.retrieveRelevantMemories(
      situation, 
      MemoryNamespace.DECISIONS,
      { limit: 10 }
    );

    // Retrieve relevant experiences
    const experiences = await this.retrieveRelevantMemories(
      situation,
      MemoryNamespace.LEARNING,
      { limit: 5 }
    );

    // Analyze patterns and make informed decision
    const analysis = await this.analyzeMemoryPatterns(pastDecisions, experiences);
    const decision = await this.selectBestOption(options, analysis);

    // Store the decision for future reference
    await this.storeMemory(
      `Decision: ${decision.choice} for situation: ${situation}. Reasoning: ${decision.reasoning}`,
      MemoryNamespace.DECISIONS,
      {
        tags: ['decision', 'automated'],
        customFields: {
          situation,
          options,
          confidence: decision.confidence,
          factors: decision.factors
        }
      }
    );

    return decision;
  }

  // Abstract methods for subclasses to implement
  protected abstract processContent(content: string): Promise<MemoryContent>;
  protected abstract captureContext(): Promise<ContextInformation>;
  protected abstract calculateImportance(content: string, namespace: MemoryNamespace): number;
  protected abstract analyzeMemoryPatterns(decisions: MemoryObject[], experiences: MemoryObject[]): Promise<PatternAnalysis>;
  protected abstract selectBestOption(options: string[], analysis: PatternAnalysis): Promise<DecisionResult>;
}
```

## Memory Optimization and Maintenance

```typescript
// src/memory/utils/MemoryOptimizer.ts
class MemoryOptimizer {
  private compressionThreshold = 0.8; // Compress when 80% full
  private importanceDecayRate = 0.95; // 5% decay per week
  private accessFrequencyWeight = 0.3;

  async optimizeMemoryStorage(agentId: string): Promise<OptimizationResult> {
    const startTime = Date.now();
    let operations = 0;

    // 1. Remove expired memories
    const expiredCount = await this.removeExpiredMemories(agentId);
    operations += expiredCount;

    // 2. Compress old memories
    const compressedCount = await this.compressOldMemories(agentId);
    operations += compressedCount;

    // 3. Update importance scores
    const updatedCount = await this.updateImportanceScores(agentId);
    operations += updatedCount;

    // 4. Consolidate similar memories
    const consolidatedCount = await this.consolidateSimilarMemories(agentId);
    operations += consolidatedCount;

    // 5. Rebuild indexes if necessary
    const indexRebuilt = await this.rebuildIndexesIfNeeded(agentId);

    return {
      duration: Date.now() - startTime,
      operations,
      expired: expiredCount,
      compressed: compressedCount,
      updated: updatedCount,
      consolidated: consolidatedCount,
      indexRebuilt
    };
  }

  private async consolidateSimilarMemories(agentId: string): Promise<number> {
    const memories = await this.memoryManager.getMemoriesByAgent(agentId);
    const clusters = await this.clusterSimilarMemories(memories);
    let consolidatedCount = 0;

    for (const cluster of clusters) {
      if (cluster.length > 1) {
        const consolidatedMemory = await this.mergeMemories(cluster);
        await this.memoryManager.store(consolidatedMemory);
        await this.memoryManager.delete(cluster.map(m => m.id));
        consolidatedCount += cluster.length - 1;
      }
    }

    return consolidatedCount;
  }
}
```

## API and Integration

```typescript
// Memory API endpoints
interface MemoryAPI {
  // Memory management
  'POST /api/memory/store': (memory: CreateMemoryRequest) => Promise<MemoryObject>;
  'GET /api/memory/:id': (id: string) => Promise<MemoryObject>;
  'PUT /api/memory/:id': (id: string, updates: UpdateMemoryRequest) => Promise<MemoryObject>;
  'DELETE /api/memory/:id': (id: string) => Promise<void>;

  // Search and retrieval
  'POST /api/memory/search': (query: SearchQuery) => Promise<SearchResult[]>;
  'POST /api/memory/similar': (request: SimilarityRequest) => Promise<MemoryObject[]>;
  'GET /api/memory/agent/:agentId': (agentId: string, options: RetrievalOptions) => Promise<MemoryObject[]>;

  // Analytics and optimization
  'GET /api/memory/analytics/:agentId': (agentId: string) => Promise<MemoryAnalytics>;
  'POST /api/memory/optimize/:agentId': (agentId: string) => Promise<OptimizationResult>;
  'GET /api/memory/health': () => Promise<MemorySystemHealth>;
}
```

## Implementation Status

- **Current**: Basic memory storage and retrieval with local providers
- **Planned**: Full vector database integration, advanced search, memory optimization
- **Future**: Graph-based memory relationships, AI-powered memory consolidation, federated memory networks

This memory system provides agents with sophisticated long-term memory capabilities, enabling them to learn, remember, and make informed decisions based on accumulated experience and knowledge.

