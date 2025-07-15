---
title: "Agent Memory Protocols"
description: "Comprehensive multi-modal memory architecture with temporary, episodic, semantic, and long-term storage integration for agent systems"
version: "2.1.0"
last_updated: "2024-12-28"
category: "Agents"
tags: ["memory", "storage", "retrieval", "episodic", "semantic", "protocols"]
author: "kAI Development Team"
status: "active"
---

# Agent Memory Protocols

## Agent Context
This document defines the complete memory architecture for agents within the kAI/kOS ecosystem, outlining the structure, protocols, storage, retrieval strategies, and integration requirements for multi-modal, multi-agent memory systems across various time scales. The system supports temporary session memory, episodic narrative events, semantic conceptual knowledge, long-term persistent storage, personalization data, and external memory integration with advanced retrieval strategies, memory lifecycle management, and cross-agent memory sharing protocols.

## Overview

The Agent Memory Protocols provide a comprehensive framework for managing agent memory across multiple dimensions and time scales, enabling sophisticated context awareness, learning, and knowledge retention for AI agents operating in complex environments.

## I. Memory Architecture Overview

```typescript
interface AgentMemorySystem {
  memoryCore: MemoryCore;
  shortTermMemory: ShortTermMemory;
  episodicMemory: EpisodicMemory;
  semanticMemory: SemanticMemory;
  longTermStorage: LongTermStorage;
  personalizationMemory: PersonalizationMemory;
  externalMemory: ExternalMemory;
  memoryRouter: MemoryRouter;
}

class MemoryCore {
  private readonly shortTermMemory: ShortTermMemory;
  private readonly episodicMemory: EpisodicMemory;
  private readonly semanticMemory: SemanticMemory;
  private readonly longTermStorage: LongTermStorage;
  private readonly personalizationMemory: PersonalizationMemory;
  private readonly externalMemory: ExternalMemory;
  private readonly memoryRouter: MemoryRouter;
  private readonly memoryEncoder: MemoryEncoder;
  private readonly memoryTagger: MemoryTagger;
  private readonly memoryVectorizer: MemoryVectorizer;
  private readonly memoryRetainer: MemoryRetainer;
  private readonly memoryCleaner: MemoryCleaner;

  constructor(config: MemoryConfig) {
    this.shortTermMemory = new ShortTermMemory(config.shortTerm);
    this.episodicMemory = new EpisodicMemory(config.episodic);
    this.semanticMemory = new SemanticMemory(config.semantic);
    this.longTermStorage = new LongTermStorage(config.longTerm);
    this.personalizationMemory = new PersonalizationMemory(config.personalization);
    this.externalMemory = new ExternalMemory(config.external);
    this.memoryRouter = new MemoryRouter(config.routing);
    this.memoryEncoder = new MemoryEncoder(config.encoding);
    this.memoryTagger = new MemoryTagger(config.tagging);
    this.memoryVectorizer = new MemoryVectorizer(config.vectorization);
    this.memoryRetainer = new MemoryRetainer(config.retention);
    this.memoryCleaner = new MemoryCleaner(config.cleanup);
  }

  async storeMemory(
    agentId: string,
    memoryRequest: MemoryStoreRequest
  ): Promise<MemoryStoreResult> {
    const memoryId = this.generateMemoryId();
    const startTime = Date.now();

    try {
      // Encode memory content
      const encodedMemory = await this.memoryEncoder.encode({
        content: memoryRequest.content,
        type: memoryRequest.type,
        context: memoryRequest.context,
        metadata: memoryRequest.metadata
      });

      // Generate tags
      const tags = await this.memoryTagger.generateTags({
        content: encodedMemory.content,
        type: memoryRequest.type,
        context: memoryRequest.context,
        existingTags: memoryRequest.tags || []
      });

      // Generate embeddings
      const embeddings = await this.memoryVectorizer.vectorize({
        content: encodedMemory.content,
        metadata: encodedMemory.metadata,
        tags: tags.generated
      });

      // Create memory record
      const memory: MemoryRecord = {
        id: memoryId,
        agentId,
        type: memoryRequest.type,
        content: encodedMemory.content,
        encodedData: encodedMemory.encoded,
        embeddings: embeddings.vector,
        tags: [...(memoryRequest.tags || []), ...tags.generated],
        metadata: {
          ...memoryRequest.metadata,
          importance: await this.calculateImportance(memoryRequest),
          createdAt: new Date().toISOString(),
          sourceType: memoryRequest.sourceType,
          sessionId: memoryRequest.sessionId
        },
        relationships: [],
        status: 'active'
      };

      // Route to appropriate storage
      const storageTargets = await this.memoryRouter.determineStorageTargets(memory);
      const storageResults: StorageResult[] = [];

      for (const target of storageTargets) {
        const result = await this.storeInTarget(target, memory);
        storageResults.push(result);
      }

      // Update memory relationships
      await this.updateMemoryRelationships(memory);

      // Set retention policy
      await this.memoryRetainer.setRetentionPolicy(memoryId, {
        type: memory.type,
        importance: memory.metadata.importance,
        agentId
      });

      return {
        success: true,
        memoryId,
        type: memory.type,
        storageTargets: storageTargets.map(t => t.type),
        importance: memory.metadata.importance,
        tags: memory.tags,
        storeTime: Date.now() - startTime,
        storedAt: memory.metadata.createdAt
      };
    } catch (error) {
      throw new MemoryStoreError(`Failed to store memory: ${error.message}`);
    }
  }

  async retrieveMemory(
    agentId: string,
    retrievalRequest: MemoryRetrievalRequest
  ): Promise<MemoryRetrievalResult> {
    const retrievalId = this.generateRetrievalId();
    const startTime = Date.now();

    try {
      // Determine retrieval strategy
      const strategy = await this.memoryRouter.determineRetrievalStrategy(retrievalRequest);

      // Execute retrieval based on strategy
      let results: MemoryRecord[] = [];
      
      switch (strategy.type) {
        case 'temporal':
          results = await this.executeTemporalRetrieval(agentId, retrievalRequest, strategy);
          break;
        case 'semantic':
          results = await this.executeSemanticRetrieval(agentId, retrievalRequest, strategy);
          break;
        case 'episodic':
          results = await this.executeEpisodicRetrieval(agentId, retrievalRequest, strategy);
          break;
        case 'hybrid':
          results = await this.executeHybridRetrieval(agentId, retrievalRequest, strategy);
          break;
        default:
          throw new UnsupportedRetrievalError(`Unsupported retrieval strategy: ${strategy.type}`);
      }

      // Apply filters and ranking
      const filteredResults = await this.applyRetrievalFilters(results, retrievalRequest.filters);
      const rankedResults = await this.rankRetrievalResults(filteredResults, retrievalRequest.ranking);

      // Limit results
      const limitedResults = rankedResults.slice(0, retrievalRequest.limit || 10);

      // Prepare context
      const context = await this.prepareRetrievalContext(limitedResults, retrievalRequest.contextType);

      return {
        success: true,
        retrievalId,
        strategy: strategy.type,
        totalFound: results.length,
        returned: limitedResults.length,
        memories: limitedResults.map(memory => ({
          id: memory.id,
          type: memory.type,
          content: memory.content,
          relevanceScore: memory.relevanceScore,
          importance: memory.metadata.importance,
          createdAt: memory.metadata.createdAt,
          tags: memory.tags
        })),
        context,
        retrievalTime: Date.now() - startTime,
        retrievedAt: new Date().toISOString()
      };
    } catch (error) {
      throw new MemoryRetrievalError(`Failed to retrieve memory: ${error.message}`);
    }
  }

  async queryMemory(
    agentId: string,
    query: MemoryQuery
  ): Promise<MemoryQueryResult> {
    const queryId = this.generateQueryId();
    const startTime = Date.now();

    try {
      // Parse and understand query
      const parsedQuery = await this.parseMemoryQuery(query);

      // Generate query embeddings if needed
      let queryEmbeddings: number[] | undefined;
      if (parsedQuery.requiresSemanticSearch) {
        const embeddingResult = await this.memoryVectorizer.vectorize({
          content: query.text,
          metadata: query.metadata || {}
        });
        queryEmbeddings = embeddingResult.vector;
      }

      // Execute multi-target search
      const searchResults = await Promise.all([
        this.searchShortTermMemory(agentId, parsedQuery, queryEmbeddings),
        this.searchEpisodicMemory(agentId, parsedQuery, queryEmbeddings),
        this.searchSemanticMemory(agentId, parsedQuery, queryEmbeddings),
        this.searchLongTermStorage(agentId, parsedQuery, queryEmbeddings),
        this.searchPersonalizationMemory(agentId, parsedQuery, queryEmbeddings)
      ]);

      // Merge and deduplicate results
      const mergedResults = await this.mergeSearchResults(searchResults);
      const deduplicatedResults = await this.deduplicateMemories(mergedResults);

      // Apply relevance scoring
      const scoredResults = await this.scoreMemoryRelevance(
        deduplicatedResults,
        parsedQuery,
        queryEmbeddings
      );

      // Sort by relevance and apply limits
      const sortedResults = scoredResults.sort((a, b) => b.relevanceScore - a.relevanceScore);
      const limitedResults = sortedResults.slice(0, query.limit || 20);

      // Generate memory summary if requested
      let summary: string | undefined;
      if (query.generateSummary) {
        summary = await this.generateMemorySummary(limitedResults, query.summaryType);
      }

      return {
        success: true,
        queryId,
        query: query.text,
        totalResults: sortedResults.length,
        returnedResults: limitedResults.length,
        memories: limitedResults,
        summary,
        searchTargets: searchResults.map(r => r.target),
        queryTime: Date.now() - startTime,
        queriedAt: new Date().toISOString()
      };
    } catch (error) {
      throw new MemoryQueryError(`Memory query failed: ${error.message}`);
    }
  }

  private async calculateImportance(request: MemoryStoreRequest): Promise<number> {
    let importance = 0.5; // Base importance

    // Adjust based on memory type
    switch (request.type) {
      case 'critical':
        importance += 0.3;
        break;
      case 'error':
      case 'warning':
        importance += 0.2;
        break;
      case 'success':
        importance += 0.1;
        break;
    }

    // Adjust based on source type
    if (request.sourceType === 'user_interaction') {
      importance += 0.2;
    } else if (request.sourceType === 'system_event') {
      importance += 0.1;
    }

    // Adjust based on content analysis
    if (request.content.length > 1000) {
      importance += 0.1; // Longer content might be more important
    }

    // Adjust based on explicit importance
    if (request.metadata?.explicitImportance) {
      importance = Math.max(importance, request.metadata.explicitImportance);
    }

    return Math.min(1.0, Math.max(0.0, importance));
  }
}
```

## II. Short-Term Memory Implementation

```typescript
class ShortTermMemory {
  private readonly sessionCache: SessionCache;
  private readonly workingMemory: WorkingMemory;
  private readonly attentionManager: AttentionManager;
  private readonly contextWindow: ContextWindow;

  constructor(config: ShortTermConfig) {
    this.sessionCache = new SessionCache(config.cache);
    this.workingMemory = new WorkingMemory(config.working);
    this.attentionManager = new AttentionManager(config.attention);
    this.contextWindow = new ContextWindow(config.context);
  }

  async store(
    agentId: string,
    sessionId: string,
    memory: ShortTermMemoryItem
  ): Promise<ShortTermStoreResult> {
    // Check capacity
    const currentSize = await this.sessionCache.getSize(agentId, sessionId);
    if (currentSize >= this.config.maxItems) {
      // Evict least important items
      await this.evictLeastImportant(agentId, sessionId);
    }

    // Store in session cache
    await this.sessionCache.store(agentId, sessionId, memory);

    // Update working memory
    await this.workingMemory.addItem(agentId, memory);

    // Update attention weights
    await this.attentionManager.updateAttention(agentId, memory);

    // Update context window
    await this.contextWindow.addToWindow(agentId, sessionId, memory);

    return {
      success: true,
      memoryId: memory.id,
      sessionId,
      storedAt: new Date().toISOString()
    };
  }

  async retrieve(
    agentId: string,
    sessionId: string,
    retrievalOptions: ShortTermRetrievalOptions
  ): Promise<ShortTermMemoryItem[]> {
    let items: ShortTermMemoryItem[] = [];

    switch (retrievalOptions.strategy) {
      case 'recent':
        items = await this.sessionCache.getRecent(
          agentId, 
          sessionId, 
          retrievalOptions.limit || 10
        );
        break;
      case 'important':
        items = await this.sessionCache.getByImportance(
          agentId, 
          sessionId, 
          retrievalOptions.limit || 10
        );
        break;
      case 'attention':
        items = await this.attentionManager.getHighAttentionItems(
          agentId, 
          retrievalOptions.limit || 10
        );
        break;
      case 'context':
        items = await this.contextWindow.getCurrentContext(agentId, sessionId);
        break;
    }

    // Apply filters
    if (retrievalOptions.filters) {
      items = await this.applyShortTermFilters(items, retrievalOptions.filters);
    }

    return items;
  }

  async consolidateToEpisodic(
    agentId: string,
    sessionId: string
  ): Promise<ConsolidationResult> {
    const items = await this.sessionCache.getAll(agentId, sessionId);
    
    // Group related items
    const groups = await this.groupRelatedItems(items);
    
    // Create episodic memories from groups
    const episodicMemories: EpisodicMemoryItem[] = [];
    for (const group of groups) {
      const episodicMemory = await this.createEpisodicFromGroup(group);
      episodicMemories.push(episodicMemory);
    }

    return {
      success: true,
      itemsProcessed: items.length,
      episodicMemoriesCreated: episodicMemories.length,
      consolidatedAt: new Date().toISOString()
    };
  }

  private async evictLeastImportant(
    agentId: string, 
    sessionId: string
  ): Promise<void> {
    const items = await this.sessionCache.getAll(agentId, sessionId);
    
    // Sort by importance and recency
    const sortedItems = items.sort((a, b) => {
      const importanceDiff = a.importance - b.importance;
      if (Math.abs(importanceDiff) < 0.1) {
        // If importance is similar, prefer more recent
        return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
      }
      return importanceDiff;
    });

    // Remove least important items
    const itemsToRemove = Math.ceil(sortedItems.length * 0.2); // Remove 20%
    for (let i = 0; i < itemsToRemove; i++) {
      await this.sessionCache.remove(agentId, sessionId, sortedItems[i].id);
    }
  }
}

interface ShortTermMemoryItem {
  id: string;
  content: string;
  type: 'message' | 'action' | 'observation' | 'thought';
  importance: number;
  attention: number;
  createdAt: string;
  metadata: Record<string, any>;
}

interface ShortTermRetrievalOptions {
  strategy: 'recent' | 'important' | 'attention' | 'context';
  limit?: number;
  filters?: ShortTermFilter[];
}
```

## III. Episodic Memory Implementation

```typescript
class EpisodicMemory {
  private readonly episodeStore: EpisodeStore;
  private readonly timelineManager: TimelineManager;
  private readonly narrativeEngine: NarrativeEngine;
  private readonly eventLinker: EventLinker;

  constructor(config: EpisodicConfig) {
    this.episodeStore = new EpisodeStore(config.storage);
    this.timelineManager = new TimelineManager(config.timeline);
    this.narrativeEngine = new NarrativeEngine(config.narrative);
    this.eventLinker = new EventLinker(config.linking);
  }

  async storeEpisode(
    agentId: string,
    episode: EpisodeCreationRequest
  ): Promise<EpisodeStoreResult> {
    const episodeId = this.generateEpisodeId();
    const startTime = Date.now();

    try {
      // Create episode record
      const episodeRecord: Episode = {
        id: episodeId,
        agentId,
        title: episode.title,
        summary: episode.summary,
        events: episode.events,
        timeline: await this.timelineManager.createTimeline(episode.events),
        narrative: await this.narrativeEngine.generateNarrative(episode.events),
        participants: episode.participants || [],
        location: episode.location,
        metadata: {
          ...episode.metadata,
          createdAt: new Date().toISOString(),
          importance: await this.calculateEpisodeImportance(episode),
          duration: this.calculateEpisodeDuration(episode.events)
        },
        tags: episode.tags || [],
        relationships: [],
        status: 'active'
      };

      // Store episode
      await this.episodeStore.store(episodeId, episodeRecord);

      // Link to related episodes
      await this.eventLinker.linkRelatedEpisodes(episodeRecord);

      // Update timeline
      await this.timelineManager.addToTimeline(agentId, episodeRecord);

      // Generate embeddings for semantic search
      const embeddings = await this.generateEpisodeEmbeddings(episodeRecord);
      await this.episodeStore.storeEmbeddings(episodeId, embeddings);

      return {
        success: true,
        episodeId,
        timeline: episodeRecord.timeline,
        importance: episodeRecord.metadata.importance,
        linkedEpisodes: episodeRecord.relationships.length,
        storeTime: Date.now() - startTime,
        storedAt: episodeRecord.metadata.createdAt
      };
    } catch (error) {
      throw new EpisodeStoreError(`Failed to store episode: ${error.message}`);
    }
  }

  async retrieveEpisodes(
    agentId: string,
    retrievalRequest: EpisodeRetrievalRequest
  ): Promise<EpisodeRetrievalResult> {
    let episodes: Episode[] = [];

    switch (retrievalRequest.strategy) {
      case 'chronological':
        episodes = await this.episodeStore.getChronological(
          agentId,
          retrievalRequest.timeRange,
          retrievalRequest.limit
        );
        break;
      case 'importance':
        episodes = await this.episodeStore.getByImportance(
          agentId,
          retrievalRequest.importanceThreshold,
          retrievalRequest.limit
        );
        break;
      case 'narrative':
        episodes = await this.narrativeEngine.findNarrativeThreads(
          agentId,
          retrievalRequest.narrativeQuery,
          retrievalRequest.limit
        );
        break;
      case 'participants':
        episodes = await this.episodeStore.getByParticipants(
          agentId,
          retrievalRequest.participants,
          retrievalRequest.limit
        );
        break;
      case 'location':
        episodes = await this.episodeStore.getByLocation(
          agentId,
          retrievalRequest.location,
          retrievalRequest.limit
        );
        break;
    }

    // Apply additional filters
    if (retrievalRequest.filters) {
      episodes = await this.applyEpisodeFilters(episodes, retrievalRequest.filters);
    }

    // Reconstruct narratives if requested
    if (retrievalRequest.includeNarrative) {
      for (const episode of episodes) {
        episode.reconstructedNarrative = await this.narrativeEngine.reconstructNarrative(
          episode,
          retrievalRequest.narrativeDetail
        );
      }
    }

    return {
      success: true,
      strategy: retrievalRequest.strategy,
      totalFound: episodes.length,
      episodes: episodes.map(episode => ({
        id: episode.id,
        title: episode.title,
        summary: episode.summary,
        timeline: episode.timeline,
        importance: episode.metadata.importance,
        participants: episode.participants,
        narrative: episode.reconstructedNarrative || episode.narrative
      })),
      retrievedAt: new Date().toISOString()
    };
  }

  async generateEpisodeFromEvents(
    agentId: string,
    events: MemoryEvent[],
    episodeRequest: EpisodeGenerationRequest
  ): Promise<Episode> {
    // Analyze events to determine episode boundaries
    const episodeBoundaries = await this.analyzeEpisodeBoundaries(events);
    
    // Group events into episodes
    const eventGroups = await this.groupEventsByBoundaries(events, episodeBoundaries);
    
    // Generate episode metadata
    const episodes: Episode[] = [];
    for (const group of eventGroups) {
      const episode = await this.createEpisodeFromEventGroup(agentId, group, episodeRequest);
      episodes.push(episode);
    }

    // If multiple episodes, create a meta-episode
    if (episodes.length > 1) {
      return await this.createMetaEpisode(agentId, episodes, episodeRequest);
    }

    return episodes[0];
  }

  private async calculateEpisodeImportance(episode: EpisodeCreationRequest): Promise<number> {
    let importance = 0.5; // Base importance

    // Factor in number of participants
    importance += Math.min(0.2, episode.participants?.length * 0.05 || 0);

    // Factor in event types
    const criticalEvents = episode.events.filter(e => e.type === 'critical' || e.type === 'error');
    importance += Math.min(0.2, criticalEvents.length * 0.1);

    // Factor in duration
    const duration = this.calculateEpisodeDuration(episode.events);
    if (duration > 3600000) { // More than 1 hour
      importance += 0.1;
    }

    // Factor in explicit importance
    if (episode.metadata?.explicitImportance) {
      importance = Math.max(importance, episode.metadata.explicitImportance);
    }

    return Math.min(1.0, Math.max(0.0, importance));
  }

  private calculateEpisodeDuration(events: MemoryEvent[]): number {
    if (events.length === 0) return 0;
    
    const timestamps = events.map(e => new Date(e.timestamp).getTime());
    return Math.max(...timestamps) - Math.min(...timestamps);
  }
}

interface Episode {
  id: string;
  agentId: string;
  title: string;
  summary: string;
  events: MemoryEvent[];
  timeline: Timeline;
  narrative: string;
  participants: string[];
  location?: string;
  metadata: EpisodeMetadata;
  tags: string[];
  relationships: EpisodeRelationship[];
  status: 'active' | 'archived' | 'deleted';
  reconstructedNarrative?: string;
}

interface MemoryEvent {
  id: string;
  type: 'message' | 'action' | 'observation' | 'decision' | 'error' | 'critical';
  content: string;
  timestamp: string;
  participants: string[];
  metadata: Record<string, any>;
}

interface Timeline {
  startTime: string;
  endTime: string;
  duration: number;
  keyMoments: TimelineEvent[];
  phases: TimelinePhase[];
}
```

## IV. Semantic Memory Implementation

```typescript
class SemanticMemory {
  private readonly conceptStore: ConceptStore;
  private readonly knowledgeGraph: KnowledgeGraph;
  private readonly ontologyManager: OntologyManager;
  private readonly inferenceEngine: InferenceEngine;

  constructor(config: SemanticConfig) {
    this.conceptStore = new ConceptStore(config.concepts);
    this.knowledgeGraph = new KnowledgeGraph(config.graph);
    this.ontologyManager = new OntologyManager(config.ontology);
    this.inferenceEngine = new InferenceEngine(config.inference);
  }

  async storeConcept(
    agentId: string,
    conceptRequest: ConceptCreationRequest
  ): Promise<ConceptStoreResult> {
    const conceptId = this.generateConceptId();
    const startTime = Date.now();

    try {
      // Create concept record
      const concept: Concept = {
        id: conceptId,
        agentId,
        name: conceptRequest.name,
        definition: conceptRequest.definition,
        category: conceptRequest.category,
        properties: conceptRequest.properties || {},
        relationships: [],
        examples: conceptRequest.examples || [],
        metadata: {
          ...conceptRequest.metadata,
          createdAt: new Date().toISOString(),
          confidence: conceptRequest.confidence || 0.8,
          source: conceptRequest.source
        },
        embeddings: await this.generateConceptEmbeddings(conceptRequest),
        status: 'active'
      };

      // Store concept
      await this.conceptStore.store(conceptId, concept);

      // Add to knowledge graph
      await this.knowledgeGraph.addConcept(concept);

      // Establish relationships
      if (conceptRequest.relatedConcepts) {
        await this.establishConceptRelationships(concept, conceptRequest.relatedConcepts);
      }

      // Update ontology
      await this.ontologyManager.integrateNewConcept(concept);

      // Run inference to discover new relationships
      const inferredRelationships = await this.inferenceEngine.inferRelationships(concept);
      await this.addInferredRelationships(conceptId, inferredRelationships);

      return {
        success: true,
        conceptId,
        category: concept.category,
        relationshipsEstablished: concept.relationships.length,
        inferredRelationships: inferredRelationships.length,
        storeTime: Date.now() - startTime,
        storedAt: concept.metadata.createdAt
      };
    } catch (error) {
      throw new ConceptStoreError(`Failed to store concept: ${error.message}`);
    }
  }

  async queryConcepts(
    agentId: string,
    query: ConceptQuery
  ): Promise<ConceptQueryResult> {
    const queryId = this.generateQueryId();
    const startTime = Date.now();

    try {
      let concepts: Concept[] = [];

      switch (query.type) {
        case 'semantic':
          concepts = await this.executeSemanticConceptSearch(agentId, query);
          break;
        case 'categorical':
          concepts = await this.conceptStore.getByCategory(agentId, query.category);
          break;
        case 'relational':
          concepts = await this.knowledgeGraph.findRelatedConcepts(
            query.baseConcept,
            query.relationshipType,
            query.depth || 2
          );
          break;
        case 'inferential':
          concepts = await this.inferenceEngine.findConceptsByInference(
            agentId,
            query.inferenceRules
          );
          break;
      }

      // Apply filters
      if (query.filters) {
        concepts = await this.applyConceptFilters(concepts, query.filters);
      }

      // Sort by relevance
      const sortedConcepts = await this.sortConceptsByRelevance(concepts, query);

      // Limit results
      const limitedConcepts = sortedConcepts.slice(0, query.limit || 20);

      // Generate knowledge summary if requested
      let knowledgeSummary: string | undefined;
      if (query.generateSummary) {
        knowledgeSummary = await this.generateKnowledgeSummary(limitedConcepts);
      }

      return {
        success: true,
        queryId,
        queryType: query.type,
        totalFound: concepts.length,
        returned: limitedConcepts.length,
        concepts: limitedConcepts.map(concept => ({
          id: concept.id,
          name: concept.name,
          definition: concept.definition,
          category: concept.category,
          confidence: concept.metadata.confidence,
          relationships: concept.relationships.length,
          relevanceScore: concept.relevanceScore
        })),
        knowledgeSummary,
        queryTime: Date.now() - startTime,
        queriedAt: new Date().toISOString()
      };
    } catch (error) {
      throw new ConceptQueryError(`Concept query failed: ${error.message}`);
    }
  }

  async updateConceptFromExperience(
    conceptId: string,
    experience: ConceptExperience
  ): Promise<ConceptUpdateResult> {
    const concept = await this.conceptStore.get(conceptId);
    if (!concept) {
      throw new ConceptNotFoundError(`Concept ${conceptId} not found`);
    }

    // Analyze experience for concept updates
    const updates = await this.analyzeExperienceForUpdates(concept, experience);

    // Apply updates
    if (updates.definitionUpdate) {
      concept.definition = await this.mergeDefinitions(
        concept.definition,
        updates.definitionUpdate
      );
    }

    if (updates.propertyUpdates) {
      concept.properties = { ...concept.properties, ...updates.propertyUpdates };
    }

    if (updates.newExamples) {
      concept.examples.push(...updates.newExamples);
    }

    // Update confidence based on experience
    concept.metadata.confidence = await this.updateConfidence(
      concept.metadata.confidence,
      experience.outcome
    );

    // Store updated concept
    await this.conceptStore.update(conceptId, concept);

    // Update knowledge graph
    await this.knowledgeGraph.updateConcept(concept);

    return {
      success: true,
      conceptId,
      updatesApplied: Object.keys(updates).length,
      newConfidence: concept.metadata.confidence,
      updatedAt: new Date().toISOString()
    };
  }

  private async executeSemanticConceptSearch(
    agentId: string,
    query: ConceptQuery
  ): Promise<Concept[]> {
    // Generate query embeddings
    const queryEmbeddings = await this.generateConceptEmbeddings({
      name: query.searchTerm,
      definition: query.searchTerm,
      category: 'query'
    });

    // Search by semantic similarity
    const similarConcepts = await this.conceptStore.searchSimilar({
      agentId,
      embeddings: queryEmbeddings,
      threshold: query.similarityThreshold || 0.7,
      limit: query.limit || 20
    });

    return similarConcepts;
  }
}

interface Concept {
  id: string;
  agentId: string;
  name: string;
  definition: string;
  category: string;
  properties: Record<string, any>;
  relationships: ConceptRelationship[];
  examples: string[];
  metadata: ConceptMetadata;
  embeddings: number[];
  status: 'active' | 'deprecated' | 'archived';
  relevanceScore?: number;
}

interface ConceptRelationship {
  id: string;
  type: 'is-a' | 'part-of' | 'related-to' | 'causes' | 'enables' | 'conflicts-with';
  targetConceptId: string;
  strength: number;
  metadata: Record<string, any>;
}

interface ConceptQuery {
  type: 'semantic' | 'categorical' | 'relational' | 'inferential';
  searchTerm?: string;
  category?: string;
  baseConcept?: string;
  relationshipType?: string;
  depth?: number;
  inferenceRules?: InferenceRule[];
  filters?: ConceptFilter[];
  limit?: number;
  similarityThreshold?: number;
  generateSummary?: boolean;
}
```

## Cross-References

- **Related Systems**: [Prompt Management System](../services/prompt-management-system-advanced.md), [Context Window Management](../services/context-window-management.md)
- **Implementation Guides**: [Memory Configuration](../current/memory-configuration.md), [Agent Integration](../current/agent-integration.md)
- **Configuration**: [Memory Settings](../current/memory-settings.md), [Storage Configuration](../current/storage-configuration.md)

## Changelog

- **v2.1.0** (2024-12-28): Complete TypeScript implementation with multi-modal memory architecture
- **v2.0.0** (2024-12-27): Enhanced with semantic memory and knowledge graphs
- **v1.0.0** (2024-06-20): Initial agent memory protocols

---

*This document is part of the Kind AI Documentation System - providing comprehensive memory management for agent systems.*
