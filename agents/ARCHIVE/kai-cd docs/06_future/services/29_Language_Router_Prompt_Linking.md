---
title: "Language Router and Prompt Linking Engine"
last_updated: "2025-01-27"
version: "1.0"
status: "future"
complexity: "high"
decision_scope: "system-wide"
implementation_status: "specification"
code_references:
  - "language-router.ts"
  - "prompt-linker.ts"
  - "intent-classifier.ts"
related_documents:
  - "documentation/future/services/28_distributed-search-indexing.md"
  - "documentation/future/protocols/07_federated-mesh-protocols.md"
  - "documentation/future/services/06_prompt-management-system.md"
external_references:
  - "https://spacy.io/"
  - "https://huggingface.co/models"
  - "https://github.com/LibreTranslate/LibreTranslate"
---

# Language Router and Prompt Linking Engine

## Agent Context

This document specifies the Language Router and Prompt Linking Engine (LRPLE) for AI agents operating in multilingual environments. Agents should understand that this system handles multilingual input normalization, cross-language coordination, and dynamic prompt-link chaining. The system enables users to interact in any supported language while providing intelligent translation, routing, and linking based on intention, persona, task, and protocol requirements.

## I. System Overview

The Language Router and Prompt Linking Engine serves as the multilingual coordination system for kAI/kOS, enabling seamless communication across languages while maintaining semantic integrity and context awareness.

### Core Responsibilities
- **Multilingual Processing**: Accept and normalize user prompts in any supported language
- **Intent Detection**: Classify input intent, syntax, and contextual cues
- **Semantic Translation**: Translate prompts while preserving meaning and cultural nuance
- **Intelligent Routing**: Route to appropriate agents/services based on unified routing configuration
- **Prompt Chain Linking**: Support prompt chain linking using tags, embeddings, and intent scores

## II. Architecture Components

### A. Language Detection and Sentiment Analysis Engine

```typescript
interface LanguageDetectionEngine {
  detector: LanguageDetector;
  sentiment_analyzer: SentimentAnalyzer;
  dialect_detector: DialectDetector;
  confidence_threshold: number;
}

interface LanguageDetectionResult {
  language_code: string; // ISO 639 format
  confidence_score: number;
  dialect?: string;
  regional_hints: string[];
  tone_profile: ToneProfile;
  sentiment: SentimentAnalysis;
}

interface ToneProfile {
  formality: number; // 0-1 scale
  emotion: EmotionType;
  urgency: number; // 0-1 scale
  politeness: number; // 0-1 scale
}

enum EmotionType {
  NEUTRAL = "neutral",
  POSITIVE = "positive",
  NEGATIVE = "negative",
  EXCITED = "excited",
  FRUSTRATED = "frustrated",
  CURIOUS = "curious"
}

interface SentimentAnalysis {
  polarity: number; // -1 to 1
  subjectivity: number; // 0 to 1
  confidence: number;
  emotions: EmotionScore[];
}

class LanguageDetectionService {
  private detectors: Map<string, LanguageDetector>;
  private sentimentAnalyzer: SentimentAnalyzer;

  async detectLanguage(input: string): Promise<LanguageDetectionResult> {
    // Multi-model language detection for higher accuracy
    const detection_results = await Promise.all([
      this.detectors.get('fasttext').detect(input),
      this.detectors.get('langdetect').detect(input),
      this.detectors.get('spacy').detect(input)
    ]);

    // Ensemble voting for final decision
    const consensus_result = this.calculateConsensus(detection_results);
    
    // Analyze sentiment and tone
    const sentiment = await this.sentimentAnalyzer.analyze(input, consensus_result.language_code);
    const tone_profile = await this.analyzeTone(input, consensus_result.language_code);

    return {
      language_code: consensus_result.language_code,
      confidence_score: consensus_result.confidence,
      dialect: consensus_result.dialect,
      regional_hints: consensus_result.regional_hints,
      tone_profile,
      sentiment
    };
  }

  private calculateConsensus(results: DetectionResult[]): ConsensusResult {
    const language_votes = new Map<string, number>();
    const confidence_sum = new Map<string, number>();

    for (const result of results) {
      const current_votes = language_votes.get(result.language) || 0;
      const current_confidence = confidence_sum.get(result.language) || 0;
      
      language_votes.set(result.language, current_votes + 1);
      confidence_sum.set(result.language, current_confidence + result.confidence);
    }

    // Find language with highest vote count and confidence
    let best_language = '';
    let best_score = 0;

    for (const [language, votes] of language_votes) {
      const avg_confidence = confidence_sum.get(language) / votes;
      const composite_score = votes * 0.6 + avg_confidence * 0.4;
      
      if (composite_score > best_score) {
        best_score = composite_score;
        best_language = language;
      }
    }

    return {
      language_code: best_language,
      confidence: confidence_sum.get(best_language) / language_votes.get(best_language),
      dialect: this.detectDialect(best_language),
      regional_hints: this.extractRegionalHints(best_language)
    };
  }
}
```

### B. Semantic Preserving Translator

```typescript
interface TranslationEngine {
  primary_engine: TranslationProvider;
  fallback_engines: TranslationProvider[];
  quality_threshold: number;
  cache_enabled: boolean;
}

enum TranslationProvider {
  MARIAN_MT = "marian_mt",
  M2M_100 = "m2m_100",
  GPT4_TURBO = "gpt4_turbo",
  LIBRE_TRANSLATE = "libre_translate",
  CUSTOM_MODEL = "custom_model"
}

interface TranslationRequest {
  source_text: string;
  source_language: string;
  target_language: string;
  preserve_tone: boolean;
  preserve_cultural_context: boolean;
  agent_preferences?: AgentTranslationPrefs;
}

interface TranslationResult {
  translated_text: string;
  source_text: string;
  quality_score: number;
  translation_engine: TranslationProvider;
  cultural_adaptations: CulturalAdaptation[];
  tone_preservation_score: number;
  processing_time_ms: number;
}

class SemanticPreservingTranslator {
  private engines: Map<TranslationProvider, TranslationEngine>;
  private qualityAssessor: TranslationQualityAssessor;
  private culturalAdapter: CulturalAdapter;

  async translatePrompt(request: TranslationRequest): Promise<TranslationResult> {
    // 1. Determine optimal translation engine
    const selected_engine = await this.selectTranslationEngine(request);
    
    // 2. Perform initial translation
    const initial_translation = await this.performTranslation(request, selected_engine);
    
    // 3. Assess translation quality
    const quality_assessment = await this.qualityAssessor.assess(initial_translation);
    
    // 4. Apply cultural adaptations if needed
    const culturally_adapted = await this.culturalAdapter.adapt(
      initial_translation,
      request.source_language,
      request.target_language
    );

    // 5. Preserve tone and style
    const tone_preserved = await this.preserveTone(
      culturally_adapted,
      request.source_text,
      request.target_language
    );

    return {
      translated_text: tone_preserved.text,
      source_text: request.source_text,
      quality_score: quality_assessment.score,
      translation_engine: selected_engine,
      cultural_adaptations: culturally_adapted.adaptations,
      tone_preservation_score: tone_preserved.preservation_score,
      processing_time_ms: Date.now() - request.start_time.getTime()
    };
  }

  private async selectTranslationEngine(request: TranslationRequest): Promise<TranslationProvider> {
    const language_pair = `${request.source_language}-${request.target_language}`;
    
    // Check engine capabilities for language pair
    const capable_engines = await this.getCapableEngines(language_pair);
    
    // Select based on quality requirements and availability
    if (request.preserve_cultural_context && capable_engines.includes(TranslationProvider.GPT4_TURBO)) {
      return TranslationProvider.GPT4_TURBO;
    }
    
    if (capable_engines.includes(TranslationProvider.M2M_100)) {
      return TranslationProvider.M2M_100;
    }
    
    return capable_engines[0] || TranslationProvider.LIBRE_TRANSLATE;
  }
}
```

### C. Intent Classification and Routing

```typescript
interface IntentClassifier {
  model_type: IntentModelType;
  confidence_threshold: number;
  supported_intents: IntentType[];
  fallback_strategy: FallbackStrategy;
}

enum IntentModelType {
  FASTTEXT = "fasttext",
  BERT = "bert",
  CUSTOM_LLM = "custom_llm",
  ENSEMBLE = "ensemble"
}

enum IntentType {
  GENERATE = "generate",
  SUMMARIZE = "summarize",
  TRANSLATE = "translate",
  ROUTE = "route",
  FETCH = "fetch",
  RECALL = "recall",
  ANALYZE = "analyze",
  CREATE = "create",
  MODIFY = "modify",
  DELETE = "delete"
}

interface IntentClassificationResult {
  primary_intent: IntentType;
  confidence_score: number;
  secondary_intents: IntentScore[];
  domain: string;
  complexity_level: ComplexityLevel;
  routing_target: RoutingTarget;
}

interface RoutingTarget {
  target_type: TargetType;
  target_id: string;
  routing_confidence: number;
  fallback_targets: string[];
}

enum TargetType {
  AGENT = "agent",
  SERVICE = "service",
  SYSTEM = "system",
  SEARCH = "search",
  TOOL_CHAIN = "tool_chain"
}

class IntentClassificationRouter {
  private classifier: IntentClassifier;
  private routingRegistry: RoutingRegistry;
  private agentRegistry: AgentRegistry;

  async classifyAndRoute(prompt: ProcessedPrompt): Promise<RoutingResult> {
    // 1. Classify intent
    const intent_result = await this.classifyIntent(prompt);
    
    // 2. Determine routing target
    const routing_target = await this.determineRoutingTarget(intent_result, prompt);
    
    // 3. Apply routing rules
    const routing_decision = await this.applyRoutingRules(routing_target, prompt);
    
    // 4. Validate target availability
    const validated_target = await this.validateTarget(routing_decision);

    return {
      prompt_id: prompt.id,
      intent_classification: intent_result,
      routing_decision: validated_target,
      routing_timestamp: new Date(),
      processing_time_ms: Date.now() - prompt.received_at.getTime()
    };
  }

  private async determineRoutingTarget(intent: IntentClassificationResult, prompt: ProcessedPrompt): Promise<RoutingTarget> {
    const routing_config = await this.routingRegistry.getRoutingConfig();
    
    // Language-specific routing
    if (routing_config.language_routing[prompt.language]) {
      const language_rules = routing_config.language_routing[prompt.language];
      
      for (const rule of language_rules) {
        if (this.matchesRule(intent, rule)) {
          return {
            target_type: rule.target_type,
            target_id: rule.target_id,
            routing_confidence: rule.confidence,
            fallback_targets: rule.fallback_targets
          };
        }
      }
    }

    // Intent-based routing
    const intent_rules = routing_config.intent_routing[intent.primary_intent];
    if (intent_rules) {
      return this.selectBestIntentTarget(intent_rules, prompt);
    }

    // Default fallback routing
    return routing_config.default_routing;
  }
}
```

### D. Prompt Link Graph Engine

```typescript
interface PromptLinkGraph {
  storage: PromptLinkStorage;
  embedding_service: EmbeddingService;
  graph_engine: GraphEngine;
  lineage_tracker: LineageTracker;
}

interface PromptLink {
  link_id: string;
  source_prompt_id: string;
  target_prompt_id: string;
  link_type: LinkType;
  relationship_strength: number;
  created_at: Date;
  metadata: LinkMetadata;
}

enum LinkType {
  FOLLOW_UP = "follow_up",
  CLARIFICATION = "clarification",
  EXPANSION = "expansion",
  CONTRADICTION = "contradiction",
  REFERENCE = "reference",
  CONTEXT = "context",
  CHAIN = "chain"
}

interface PromptLineage {
  prompt_id: string;
  lineage_hash: string;
  parent_prompts: string[];
  child_prompts: string[];
  conversation_thread: string;
  topic_evolution: TopicEvolution[];
  semantic_drift: number;
}

class PromptLinkGraphEngine {
  private storage: PromptLinkStorage;
  private embeddingService: EmbeddingService;
  private similarityThreshold: number = 0.75;

  async linkPrompt(source_prompt: ProcessedPrompt, context: LinkingContext): Promise<LinkingResult> {
    // 1. Generate prompt embeddings
    const prompt_embedding = await this.embeddingService.generateEmbedding(source_prompt.content);
    
    // 2. Find related prompts
    const related_prompts = await this.findRelatedPrompts(prompt_embedding, context);
    
    // 3. Create explicit links
    const explicit_links = await this.createExplicitLinks(source_prompt, related_prompts);
    
    // 4. Infer implicit relationships
    const implicit_links = await this.inferImplicitLinks(source_prompt, context);
    
    // 5. Update conversation lineage
    const lineage_update = await this.updatePromptLineage(source_prompt, explicit_links);

    // 6. Store links in graph
    const all_links = [...explicit_links, ...implicit_links];
    await this.storage.storeLinks(all_links);

    return {
      prompt_id: source_prompt.id,
      links_created: all_links.length,
      explicit_links: explicit_links.length,
      implicit_links: implicit_links.length,
      lineage_updated: lineage_update.success,
      processing_time_ms: Date.now() - context.start_time.getTime()
    };
  }

  async queryPromptGraph(query: PromptGraphQuery): Promise<PromptGraphResult> {
    // 1. Parse graph query
    const parsed_query = await this.parseGraphQuery(query);
    
    // 2. Execute graph traversal
    const traversal_result = await this.executeGraphTraversal(parsed_query);
    
    // 3. Rank and filter results
    const ranked_results = await this.rankGraphResults(traversal_result, query);

    return {
      query,
      prompt_paths: ranked_results,
      total_paths: traversal_result.paths.length,
      max_depth_reached: traversal_result.max_depth,
      execution_time_ms: Date.now() - query.start_time.getTime()
    };
  }

  private async findRelatedPrompts(embedding: number[], context: LinkingContext): Promise<RelatedPrompt[]> {
    // Vector similarity search
    const similar_prompts = await this.embeddingService.findSimilar(
      embedding,
      this.similarityThreshold,
      context.max_results
    );

    // Temporal proximity search
    const temporal_prompts = await this.findTemporallyRelated(context);

    // Conversation thread search
    const thread_prompts = await this.findThreadRelated(context);

    // Merge and deduplicate
    return this.mergeRelatedPrompts(similar_prompts, temporal_prompts, thread_prompts);
  }

  private async createExplicitLinks(source_prompt: ProcessedPrompt, related_prompts: RelatedPrompt[]): Promise<PromptLink[]> {
    const links: PromptLink[] = [];

    for (const related of related_prompts) {
      const link_type = this.determineLinkType(source_prompt, related);
      const relationship_strength = this.calculateRelationshipStrength(source_prompt, related);

      if (relationship_strength > 0.5) {
        links.push({
          link_id: this.generateLinkId(),
          source_prompt_id: source_prompt.id,
          target_prompt_id: related.prompt_id,
          link_type,
          relationship_strength,
          created_at: new Date(),
          metadata: {
            similarity_score: related.similarity_score,
            temporal_distance: related.temporal_distance,
            context_overlap: related.context_overlap
          }
        });
      }
    }

    return links;
  }
}
```

## III. Routing Configuration

### A. Dynamic Routing Registry

```typescript
interface RoutingRegistry {
  language_routing: LanguageRoutingConfig;
  intent_routing: IntentRoutingConfig;
  fallback_routing: FallbackRoutingConfig;
  agent_preferences: AgentPreferencesConfig;
}

interface LanguageRoutingConfig {
  [language_code: string]: RoutingRule[];
}

interface RoutingRule {
  condition: RoutingCondition;
  target_type: TargetType;
  target_id: string;
  confidence: number;
  fallback_targets: string[];
  priority: number;
}

interface RoutingCondition {
  intent_types?: IntentType[];
  confidence_threshold?: number;
  sentiment_range?: SentimentRange;
  complexity_level?: ComplexityLevel;
  user_preferences?: UserPreferences;
}

const ROUTING_CONFIGURATION: RoutingRegistry = {
  language_routing: {
    "ja": [
      {
        condition: { intent_types: [IntentType.TRANSLATE, IntentType.GENERATE] },
        target_type: TargetType.AGENT,
        target_id: "nihon_helper",
        confidence: 0.9,
        fallback_targets: ["general_assistant"],
        priority: 1
      }
    ],
    "es": [
      {
        condition: { intent_types: [IntentType.GENERATE] },
        target_type: TargetType.AGENT,
        target_id: "spanish_teacher",
        confidence: 0.8,
        fallback_targets: ["general_assistant"],
        priority: 2
      }
    ]
  },
  intent_routing: {
    [IntentType.TRANSLATE]: [
      {
        condition: { confidence_threshold: 0.8 },
        target_type: TargetType.SERVICE,
        target_id: "translation_service",
        confidence: 0.95,
        fallback_targets: ["general_assistant"],
        priority: 1
      }
    ],
    [IntentType.ANALYZE]: [
      {
        condition: { complexity_level: ComplexityLevel.HIGH },
        target_type: TargetType.AGENT,
        target_id: "analysis_specialist",
        confidence: 0.85,
        fallback_targets: ["general_assistant"],
        priority: 1
      }
    ]
  },
  fallback_routing: {
    default_agent: "general_assistant",
    escalation_threshold: 3,
    timeout_ms: 30000
  },
  agent_preferences: {
    translation_opt_out: ["privacy_focused_agent"],
    local_only: ["secure_agent"],
    multilingual_capable: ["global_assistant", "translator_agent"]
  }
};
```

## IV. Implementation Status

- **Language Detection**: Multi-model ensemble approach specified, implementation required
- **Translation Engine**: Semantic preservation framework defined, cultural adaptation needed
- **Intent Classification**: Classification architecture complete, model training required  
- **Prompt Linking**: Graph-based linking system designed, storage implementation needed
- **Routing Registry**: Configuration framework complete, dynamic rule engine required

This language router and prompt linking system enables seamless multilingual interaction while maintaining semantic integrity and contextual awareness across the kAI/kOS ecosystem. 