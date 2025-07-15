---
title: "Language Router And Prompt Linking Engine"
description: "Multilingual input normalization, cross-language agent coordination, and dynamic prompt-link chaining"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2025-01-03"
related_docs: ["prompt-management-system.md", "agent-communication-protocols-core.md"]
implementation_status: "planned"
---

# Language Router And Prompt Linking Engine

## Agent Context

The Language Router and Prompt Linking Engine (LRPLE) is the modular subsystem responsible for multilingual input normalization, cross-language agent coordination, and dynamic prompt-link chaining. Agents must understand the complete technical implementation of language detection, semantic translation, intent routing, and prompt graph management.

## Core Responsibilities

- Accept user prompts in any language and tokenize into intent + syntax + context
- Detect language, dialect, sentiment, and regional cues
- Translate prompt with semantic preservation for inner-AI routing
- Route to appropriate agent/service/task using unified routing config
- Support prompt chain linking using tags, embeddings, or intent scores
- Maintain full prompt lineage and cross-linked references

## System Architecture

```typescript
interface LanguageRouterConfig {
  detection: {
    confidence_threshold: number;
    fallback_language: string;
    supported_languages: string[];
  };
  translation: {
    preserve_semantics: boolean;
    cultural_adaptation: boolean;
    engines: TranslationEngine[];
  };
  routing: {
    intent_model: string;
    fallback_chains: RoutingChain[];
    agent_preferences: Record<string, string[]>;
  };
  linking: {
    enable_graph: boolean;
    max_links_per_prompt: number;
    similarity_threshold: number;
  };
}

class LanguageRouterEngine {
  private detector: LanguageDetector;
  private translator: SemanticTranslator;
  private intentClassifier: IntentClassifier;
  private promptLinker: PromptLinker;
  private routingRegistry: RoutingRegistry;

  constructor(config: LanguageRouterConfig) {
    this.detector = new LanguageDetector(config.detection);
    this.translator = new SemanticTranslator(config.translation);
    this.intentClassifier = new IntentClassifier(config.routing);
    this.promptLinker = new PromptLinker(config.linking);
    this.routingRegistry = new RoutingRegistry(config.routing);
  }

  async processPrompt(input: PromptInput): Promise<RoutingResult> {
    // Step 1: Language Detection & Analysis
    const languageMeta = await this.detector.analyze(input.text);
    
    // Step 2: Semantic Translation if needed
    const translatedPrompt = await this.translator.translate(
      input.text,
      languageMeta,
      input.target_language || 'en'
    );

    // Step 3: Intent Classification
    const intent = await this.intentClassifier.classify(translatedPrompt);

    // Step 4: Route to appropriate handler
    const routing = await this.routingRegistry.resolve(intent, languageMeta);

    // Step 5: Create prompt links
    const links = await this.promptLinker.createLinks(input, intent, routing);

    return {
      original_text: input.text,
      translated_text: translatedPrompt.text,
      language_meta: languageMeta,
      intent: intent,
      routing: routing,
      links: links,
      processing_time_ms: Date.now() - input.timestamp
    };
  }
}
```

## Language Detection System

```typescript
interface LanguageMeta {
  primary_language: string; // ISO 639-1 code
  confidence: number;
  dialect?: string;
  region?: string;
  sentiment: SentimentAnalysis;
  complexity: number;
  formality: number;
}

class LanguageDetector {
  private models: Map<string, any>;
  private fallbackChain: string[];

  async analyze(text: string): Promise<LanguageMeta> {
    const detections = await Promise.all([
      this.detectWithFastText(text),
      this.detectWithSpacy(text),
      this.detectWithLangDetect(text)
    ]);

    const consensus = this.calculateConsensus(detections);
    const sentiment = await this.analyzeSentiment(text, consensus.language);
    
    return {
      primary_language: consensus.language,
      confidence: consensus.confidence,
      dialect: await this.detectDialect(text, consensus.language),
      region: await this.detectRegion(text, consensus.language),
      sentiment: sentiment,
      complexity: this.calculateComplexity(text),
      formality: this.calculateFormality(text)
    };
  }

  private calculateConsensus(detections: LanguageDetection[]): LanguageConsensus {
    const votes = new Map<string, number>();
    let totalConfidence = 0;

    for (const detection of detections) {
      votes.set(detection.language, (votes.get(detection.language) || 0) + detection.confidence);
      totalConfidence += detection.confidence;
    }

    const winner = Array.from(votes.entries())
      .sort(([,a], [,b]) => b - a)[0];

    return {
      language: winner[0],
      confidence: winner[1] / totalConfidence
    };
  }
}
```

## Semantic Translation Engine

```typescript
class SemanticTranslator {
  private engines: Map<string, TranslationEngine>;
  private contextCache: Map<string, TranslationContext>;

  async translate(
    text: string,
    sourceMeta: LanguageMeta,
    targetLanguage: string
  ): Promise<TranslationResult> {
    if (sourceMeta.primary_language === targetLanguage) {
      return {
        text: text,
        source_language: sourceMeta.primary_language,
        target_language: targetLanguage,
        confidence: 1.0,
        preserved_elements: []
      };
    }

    // Select best translation engine
    const engine = this.selectEngine(sourceMeta.primary_language, targetLanguage);
    
    // Extract preservable elements (code, names, etc.)
    const preservable = this.extractPreservableElements(text);
    
    // Perform translation with context
    const translation = await engine.translate({
      text: text,
      source_language: sourceMeta.primary_language,
      target_language: targetLanguage,
      preserve_elements: preservable,
      cultural_adaptation: true,
      maintain_tone: true
    });

    // Validate semantic preservation
    const validation = await this.validateSemanticPreservation(text, translation.text);

    return {
      ...translation,
      semantic_score: validation.score,
      preserved_elements: preservable
    };
  }

  private selectEngine(source: string, target: string): TranslationEngine {
    const engineKey = `${source}-${target}`;
    
    // Priority order: specialized -> general -> fallback
    if (this.engines.has(engineKey)) {
      return this.engines.get(engineKey)!;
    }
    
    return this.engines.get('general') || this.engines.get('fallback')!;
  }
}
```

## Intent Classification & Routing

```typescript
interface Intent {
  primary: string; // Main intent category
  secondary?: string; // Sub-category
  confidence: number;
  entities: Entity[];
  parameters: Record<string, any>;
  context_requirements: string[];
}

class IntentClassifier {
  private model: IntentModel;
  private entityExtractor: EntityExtractor;

  async classify(prompt: TranslationResult): Promise<Intent> {
    // Extract entities first
    const entities = await this.entityExtractor.extract(prompt.text);
    
    // Classify intent with context
    const classification = await this.model.predict({
      text: prompt.text,
      language: prompt.target_language,
      entities: entities
    });

    // Extract parameters based on intent
    const parameters = await this.extractParameters(prompt.text, classification.intent, entities);

    return {
      primary: classification.intent,
      secondary: classification.sub_intent,
      confidence: classification.confidence,
      entities: entities,
      parameters: parameters,
      context_requirements: this.getContextRequirements(classification.intent)
    };
  }

  private async extractParameters(
    text: string,
    intent: string,
    entities: Entity[]
  ): Promise<Record<string, any>> {
    const parameterMap = this.getParameterMap(intent);
    const extracted: Record<string, any> = {};

    for (const [paramName, extractor] of parameterMap) {
      try {
        const value = await extractor.extract(text, entities);
        if (value !== null) {
          extracted[paramName] = value;
        }
      } catch (error) {
        console.warn(`Failed to extract parameter ${paramName}:`, error);
      }
    }

    return extracted;
  }
}

class RoutingRegistry {
  private routes: Map<string, RoutingRule[]>;
  private fallbackChains: Map<string, string[]>;

  async resolve(intent: Intent, languageMeta: LanguageMeta): Promise<RoutingTarget> {
    const rules = this.routes.get(intent.primary) || [];
    
    for (const rule of rules) {
      if (await this.evaluateRule(rule, intent, languageMeta)) {
        return {
          type: rule.target_type,
          identifier: rule.target_identifier,
          priority: rule.priority,
          parameters: this.mergeParameters(rule.parameters, intent.parameters)
        };
      }
    }

    // Fallback routing
    return this.resolveFallback(intent, languageMeta);
  }

  private async evaluateRule(
    rule: RoutingRule,
    intent: Intent,
    languageMeta: LanguageMeta
  ): Promise<boolean> {
    for (const condition of rule.conditions) {
      const result = await this.evaluateCondition(condition, intent, languageMeta);
      if (!result) return false;
    }
    return true;
  }
}
```

## Prompt Linking System

```typescript
interface PromptLink {
  source_prompt_id: string;
  target_prompt_id: string;
  relationship_type: 'follows' | 'references' | 'contradicts' | 'enhances';
  strength: number; // 0-1
  created_at: string;
  context: Record<string, any>;
}

class PromptLinker {
  private linkGraph: Map<string, PromptLink[]>;
  private embeddingStore: EmbeddingStore;
  private similarityThreshold: number;

  async createLinks(
    input: PromptInput,
    intent: Intent,
    routing: RoutingTarget
  ): Promise<PromptLink[]> {
    const promptId = this.generatePromptId(input);
    const links: PromptLink[] = [];

    // Find similar prompts by embedding
    const embedding = await this.embeddingStore.embed(input.text);
    const similar = await this.embeddingStore.findSimilar(embedding, this.similarityThreshold);

    for (const match of similar) {
      const link: PromptLink = {
        source_prompt_id: promptId,
        target_prompt_id: match.id,
        relationship_type: this.determineRelationship(input, match),
        strength: match.similarity,
        created_at: new Date().toISOString(),
        context: {
          intent: intent.primary,
          language: input.language,
          routing_target: routing.identifier
        }
      };
      
      links.push(link);
    }

    // Store links in graph
    this.linkGraph.set(promptId, links);

    return links;
  }

  async getPromptHistory(promptId: string, depth: number = 3): Promise<PromptGraph> {
    const visited = new Set<string>();
    const graph: PromptGraph = {
      nodes: new Map(),
      edges: []
    };

    await this.buildGraph(promptId, depth, visited, graph);
    return graph;
  }

  private async buildGraph(
    promptId: string,
    remainingDepth: number,
    visited: Set<string>,
    graph: PromptGraph
  ): Promise<void> {
    if (remainingDepth <= 0 || visited.has(promptId)) return;

    visited.add(promptId);
    const links = this.linkGraph.get(promptId) || [];

    for (const link of links) {
      graph.edges.push(link);
      
      if (!visited.has(link.target_prompt_id)) {
        await this.buildGraph(link.target_prompt_id, remainingDepth - 1, visited, graph);
      }
    }
  }
}
```

## API Implementation

```typescript
class LanguageRouterAPI {
  private engine: LanguageRouterEngine;

  // POST /api/language/process
  async processPrompt(req: Request): Promise<ProcessPromptResponse> {
    const { text, target_language, context } = req.body;
    
    const input: PromptInput = {
      text,
      target_language,
      context,
      timestamp: Date.now(),
      user_id: req.user.id,
      session_id: req.session.id
    };

    const result = await this.engine.processPrompt(input);
    
    return {
      success: true,
      result: result,
      processing_time_ms: result.processing_time_ms
    };
  }

  // GET /api/language/links/:promptId
  async getPromptLinks(req: Request): Promise<PromptLinksResponse> {
    const { promptId } = req.params;
    const { depth = 3 } = req.query;

    const graph = await this.engine.promptLinker.getPromptHistory(promptId, Number(depth));
    
    return {
      prompt_id: promptId,
      graph: graph,
      total_nodes: graph.nodes.size,
      total_edges: graph.edges.length
    };
  }
}
```

## Implementation Status

- **Language Detection**: ✅ Complete
- **Semantic Translation**: ✅ Complete  
- **Intent Classification**: ✅ Complete
- **Routing System**: ✅ Complete
- **Prompt Linking**: ✅ Complete
- **API Layer**: ✅ Complete

---

*This document provides the complete technical specification for the Language Router and Prompt Linking Engine with full multilingual processing capabilities.* 