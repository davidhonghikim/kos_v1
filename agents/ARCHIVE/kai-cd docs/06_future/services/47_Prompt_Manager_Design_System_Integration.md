---
title: "Prompt Manager Design and System Integration"
description: "Complete technical specification for the Prompt Manager subsystem responsible for prompt lifecycle management, agent conditioning, context injection, dynamic synthesis, security, and audit"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2024-12-28"
related_docs: [
  "documentation/future/services/48_prompt-transformer-engine-specification.md",
  "documentation/future/services/49_prompt-validator-specification.md",
  "documentation/future/agents/42_agent-lifecycle-management-orchestration.md"
]
implementation_status: "planned"
---

# Prompt Manager Design and System Integration

## Agent Context
**For AI Agents**: This document defines the complete Prompt Manager subsystem for kAI and kOS. When implementing prompt-related functionality, use this central hub for all prompt operations. All prompts must go through the validation, compilation, and security layers defined here. Use the provided TypeScript interfaces for prompt storage, composition, and context injection. Pay attention to the security filters and audit logging requirements.

## Purpose and Scope

The Prompt Manager acts as the central hub for all prompt-related operations within the kAI and kOS ecosystems:

- **Stores and versions prompts** with complete lifecycle management
- **Dynamically constructs composite prompts** based on task, persona, and system configuration
- **Applies security filters and compliance checks** to prevent harmful or inappropriate content
- **Injects relevant memory/context** from the agent's knowledge base
- **Serves prompts to local and remote agents** via API or file mounts
- **Maintains audit trails** for all prompt operations and usage

## Architecture & Directory Structure

```typescript
interface PromptManagerArchitecture {
  core: {
    'src/core/prompt/': {
      'PromptStore.ts': 'Central store for prompt records';
      'PromptCompiler.ts': 'Logic for building final prompts from templates';
      'PromptValidator.ts': 'Sanity checks, PII scrub, policy filters';
      'PromptTransformer.ts': 'Context injection, summarization, translation';
      'PromptRouter.ts': 'Routes prompt requests to correct subsystem';
      'PromptAccessLog.ts': 'Tracks prompt usage and agent access';
    };
  };
  templates: {
    'templates/': {
      'default_persona.md': 'Base persona template';
      'system_guidelines.md': 'kAI system policy preamble';
      'task_templates/': {
        'summarizer.md': 'Text summarization template';
        'codegen.md': 'Code generation template';
        'translator.md': 'Language translation template';
        'analyzer.md': 'Data analysis template';
        'creative.md': 'Creative writing template';
      };
    };
  };
  storage: {
    database: 'SQLite or PostgreSQL';
    cache: 'Redis for compiled prompts';
    files: 'File system for template storage';
  };
}
```

## Prompt Data Model

```typescript
interface PromptRecord {
  id: string;                    // UUID v4
  name: string;                  // Human-readable name
  type: PromptType;              // Classification
  tags: string[];                // Searchable tags
  body: string;                  // Template content
  version: number;               // Version number
  createdAt: string;             // ISO 8601 timestamp
  modifiedAt: string;            // ISO 8601 timestamp
  createdBy: string;             // User or agent ID
  isProtected: boolean;          // System-level protection
  linkedTasks?: string[];        // Associated task types
  language?: string;             // Primary language
  metadata: PromptMetadata;      // Additional properties
}

type PromptType = 
  | 'system'                     // System-level prompts
  | 'persona'                    // Personality and tone templates
  | 'task'                       // Task-specific templates
  | 'chain'                      // Multi-step prompt chains
  | 'context'                    // Context injection templates
  | 'safety'                     // Safety and compliance prompts
  | 'custom';                    // User-defined prompts

interface PromptMetadata {
  description?: string;          // Detailed description
  author?: string;               // Original author
  category?: string;             // Categorization
  complexity: 'low' | 'medium' | 'high' | 'expert';
  estimatedTokens?: number;      // Approximate token count
  requiredContext?: string[];    // Required context types
  outputFormat?: string;         // Expected output format
  safetyLevel: 'safe' | 'moderate' | 'restricted';
  usage: {
    count: number;               // Usage statistics
    lastUsed?: string;           // Last usage timestamp
    avgRating?: number;          // User ratings
  };
}

// Storage implementation
class PromptStore {
  private db: Database;
  private cache: CacheService;
  
  constructor(db: Database, cache: CacheService) {
    this.db = db;
    this.cache = cache;
  }
  
  async createPrompt(prompt: Omit<PromptRecord, 'id' | 'createdAt' | 'version'>): Promise<string> {
    const promptRecord: PromptRecord = {
      ...prompt,
      id: generateUUID(),
      createdAt: new Date().toISOString(),
      modifiedAt: new Date().toISOString(),
      version: 1,
      metadata: {
        ...prompt.metadata,
        usage: { count: 0 }
      }
    };
    
    await this.db.run(`
      INSERT INTO prompts (
        id, name, type, tags, body, version, created_at, modified_at, 
        created_by, is_protected, linked_tasks, language, metadata
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      promptRecord.id,
      promptRecord.name,
      promptRecord.type,
      JSON.stringify(promptRecord.tags),
      promptRecord.body,
      promptRecord.version,
      promptRecord.createdAt,
      promptRecord.modifiedAt,
      promptRecord.createdBy,
      promptRecord.isProtected,
      JSON.stringify(promptRecord.linkedTasks || []),
      promptRecord.language,
      JSON.stringify(promptRecord.metadata)
    ]);
    
    // Cache the prompt
    await this.cache.set(`prompt:${promptRecord.id}`, promptRecord, 3600);
    
    return promptRecord.id;
  }
  
  async getPrompt(id: string): Promise<PromptRecord | null> {
    // Try cache first
    const cached = await this.cache.get(`prompt:${id}`);
    if (cached) {
      return cached;
    }
    
    // Fetch from database
    const row = await this.db.get('SELECT * FROM prompts WHERE id = ?', [id]);
    if (!row) {
      return null;
    }
    
    const prompt = this.rowToPromptRecord(row);
    
    // Cache for future use
    await this.cache.set(`prompt:${id}`, prompt, 3600);
    
    return prompt;
  }
  
  async searchPrompts(query: PromptSearchQuery): Promise<PromptRecord[]> {
    let sql = 'SELECT * FROM prompts WHERE 1=1';
    const params: any[] = [];
    
    if (query.text) {
      sql += ' AND (name LIKE ? OR body LIKE ?)';
      params.push(`%${query.text}%`, `%${query.text}%`);
    }
    
    if (query.type) {
      sql += ' AND type = ?';
      params.push(query.type);
    }
    
    if (query.tags && query.tags.length > 0) {
      const tagConditions = query.tags.map(() => 'tags LIKE ?').join(' AND ');
      sql += ` AND (${tagConditions})`;
      query.tags.forEach(tag => params.push(`%"${tag}"%`));
    }
    
    if (query.createdBy) {
      sql += ' AND created_by = ?';
      params.push(query.createdBy);
    }
    
    sql += ' ORDER BY modified_at DESC';
    
    if (query.limit) {
      sql += ' LIMIT ?';
      params.push(query.limit);
    }
    
    const rows = await this.db.all(sql, params);
    return rows.map(row => this.rowToPromptRecord(row));
  }
  
  async updatePrompt(id: string, updates: Partial<PromptRecord>): Promise<void> {
    const existingPrompt = await this.getPrompt(id);
    if (!existingPrompt) {
      throw new Error(`Prompt ${id} not found`);
    }
    
    if (existingPrompt.isProtected && !updates.isProtected) {
      throw new Error('Cannot modify protected prompt');
    }
    
    const updatedPrompt: PromptRecord = {
      ...existingPrompt,
      ...updates,
      id: existingPrompt.id, // Preserve ID
      version: existingPrompt.version + 1,
      modifiedAt: new Date().toISOString()
    };
    
    await this.db.run(`
      UPDATE prompts SET 
        name = ?, type = ?, tags = ?, body = ?, version = ?, 
        modified_at = ?, linked_tasks = ?, language = ?, metadata = ?
      WHERE id = ?
    `, [
      updatedPrompt.name,
      updatedPrompt.type,
      JSON.stringify(updatedPrompt.tags),
      updatedPrompt.body,
      updatedPrompt.version,
      updatedPrompt.modifiedAt,
      JSON.stringify(updatedPrompt.linkedTasks || []),
      updatedPrompt.language,
      JSON.stringify(updatedPrompt.metadata),
      id
    ]);
    
    // Update cache
    await this.cache.set(`prompt:${id}`, updatedPrompt, 3600);
    
    // Archive previous version
    await this.archivePromptVersion(existingPrompt);
  }
  
  private async archivePromptVersion(prompt: PromptRecord): Promise<void> {
    await this.db.run(`
      INSERT INTO prompt_versions (
        prompt_id, version, body, metadata, archived_at
      ) VALUES (?, ?, ?, ?, ?)
    `, [
      prompt.id,
      prompt.version,
      prompt.body,
      JSON.stringify(prompt.metadata),
      new Date().toISOString()
    ]);
  }
}

interface PromptSearchQuery {
  text?: string;                 // Full-text search
  type?: PromptType;             // Filter by type
  tags?: string[];               // Filter by tags
  createdBy?: string;            // Filter by creator
  language?: string;             // Filter by language
  limit?: number;                // Result limit
  offset?: number;               // Pagination offset
}
```

## Prompt Composition Pipeline

```typescript
interface PromptCompositionPipeline {
  steps: [
    'Request Analysis',
    'Template Selection',
    'Context Injection',
    'Variable Resolution',
    'Validation & Security',
    'Final Assembly'
  ];
}

class PromptCompiler {
  private store: PromptStore;
  private transformer: PromptTransformer;
  private validator: PromptValidator;
  private contextInjector: ContextInjector;
  
  async compilePrompt(request: PromptCompilationRequest): Promise<CompiledPrompt> {
    // Step 1: Analyze request and select templates
    const templates = await this.selectTemplates(request);
    
    // Step 2: Inject context and memory
    const contextualizedTemplates = await this.injectContext(templates, request.context);
    
    // Step 3: Resolve variables
    const resolvedTemplates = await this.resolveVariables(contextualizedTemplates, request.variables);
    
    // Step 4: Apply transformations
    const transformedPrompt = await this.transformer.transform(resolvedTemplates, request.transformations);
    
    // Step 5: Validate and apply security filters
    const validatedPrompt = await this.validator.validate(transformedPrompt, request.securityContext);
    
    // Step 6: Assemble final prompt
    const finalPrompt = await this.assembleFinalPrompt(validatedPrompt);
    
    // Step 7: Cache and log
    await this.cacheCompiledPrompt(finalPrompt, request);
    await this.logPromptUsage(finalPrompt, request);
    
    return finalPrompt;
  }
  
  private async selectTemplates(request: PromptCompilationRequest): Promise<PromptTemplate[]> {
    const templates: PromptTemplate[] = [];
    
    // System template (always included)
    const systemTemplate = await this.store.getPrompt('system-guidelines');
    if (systemTemplate) {
      templates.push({
        type: 'system',
        content: systemTemplate.body,
        priority: 1
      });
    }
    
    // Persona template
    if (request.persona) {
      const personaTemplate = await this.findPersonaTemplate(request.persona);
      if (personaTemplate) {
        templates.push({
          type: 'persona',
          content: personaTemplate.body,
          priority: 2
        });
      }
    }
    
    // Task template
    if (request.taskType) {
      const taskTemplate = await this.findTaskTemplate(request.taskType);
      if (taskTemplate) {
        templates.push({
          type: 'task',
          content: taskTemplate.body,
          priority: 3
        });
      }
    }
    
    // Custom templates
    if (request.customTemplates) {
      for (const templateId of request.customTemplates) {
        const template = await this.store.getPrompt(templateId);
        if (template) {
          templates.push({
            type: 'custom',
            content: template.body,
            priority: 4
          });
        }
      }
    }
    
    return templates.sort((a, b) => a.priority - b.priority);
  }
  
  private async injectContext(
    templates: PromptTemplate[], 
    context: PromptContext
  ): Promise<PromptTemplate[]> {
    return Promise.all(templates.map(async template => {
      const injectedContent = await this.contextInjector.inject(template.content, context);
      return {
        ...template,
        content: injectedContent
      };
    }));
  }
  
  private async resolveVariables(
    templates: PromptTemplate[],
    variables: Record<string, any>
  ): Promise<PromptTemplate[]> {
    const resolver = new VariableResolver(variables);
    
    return templates.map(template => ({
      ...template,
      content: resolver.resolve(template.content)
    }));
  }
  
  private async assembleFinalPrompt(templates: PromptTemplate[]): Promise<CompiledPrompt> {
    const sections = templates.map(template => template.content);
    const finalContent = sections.join('\n\n---\n\n');
    
    return {
      id: generateUUID(),
      content: finalContent,
      metadata: {
        compiledAt: new Date().toISOString(),
        templateCount: templates.length,
        estimatedTokens: this.estimateTokenCount(finalContent),
        checksum: await this.calculateChecksum(finalContent)
      },
      templates: templates.map(t => ({ type: t.type, priority: t.priority }))
    };
  }
}

interface PromptCompilationRequest {
  taskType?: string;             // Type of task being performed
  persona?: string;              // Persona configuration
  context: PromptContext;        // Context to inject
  variables: Record<string, any>; // Variables to resolve
  customTemplates?: string[];    // Additional template IDs
  transformations?: TransformationConfig[]; // Applied transformations
  securityContext: SecurityContext; // Security and validation context
  cacheKey?: string;             // Optional cache key
}

interface PromptContext {
  memory?: MemoryContext;        // Relevant memories
  conversation?: ConversationContext; // Chat history
  documents?: DocumentContext;   // Related documents
  user?: UserContext;            // User information
  agent?: AgentContext;          // Agent information
  task?: TaskContext;            // Task-specific context
}

interface CompiledPrompt {
  id: string;
  content: string;
  metadata: {
    compiledAt: string;
    templateCount: number;
    estimatedTokens: number;
    checksum: string;
  };
  templates: Array<{
    type: string;
    priority: number;
  }>;
}
```

## Context Injection Engine

```typescript
class ContextInjector {
  private memoryService: MemoryService;
  private documentService: DocumentService;
  private summarizer: TextSummarizer;
  
  async inject(template: string, context: PromptContext): Promise<string> {
    let injectedTemplate = template;
    
    // Inject memory context
    if (context.memory) {
      injectedTemplate = await this.injectMemoryContext(injectedTemplate, context.memory);
    }
    
    // Inject conversation history
    if (context.conversation) {
      injectedTemplate = await this.injectConversationContext(injectedTemplate, context.conversation);
    }
    
    // Inject document context
    if (context.documents) {
      injectedTemplate = await this.injectDocumentContext(injectedTemplate, context.documents);
    }
    
    // Inject user context
    if (context.user) {
      injectedTemplate = await this.injectUserContext(injectedTemplate, context.user);
    }
    
    return injectedTemplate;
  }
  
  private async injectMemoryContext(template: string, memoryContext: MemoryContext): Promise<string> {
    if (!template.includes('{{MEMORY}}')) {
      return template;
    }
    
    // Retrieve relevant memories
    const memories = await this.memoryService.search(memoryContext.query, {
      limit: memoryContext.limit || 5,
      threshold: memoryContext.threshold || 0.7,
      filters: memoryContext.filters
    });
    
    // Format memories for injection
    let memoryText = '';
    if (memories.length > 0) {
      memoryText = 'Relevant memories:\n';
      memories.forEach((memory, index) => {
        memoryText += `${index + 1}. ${memory.content}\n`;
      });
    } else {
      memoryText = 'No relevant memories found.';
    }
    
    // Apply summarization if content is too long
    if (memoryText.length > (memoryContext.maxLength || 2000)) {
      memoryText = await this.summarizer.summarize(memoryText, {
        maxLength: memoryContext.maxLength || 2000,
        preserveStructure: true
      });
    }
    
    return template.replace('{{MEMORY}}', memoryText);
  }
  
  private async injectConversationContext(
    template: string, 
    conversationContext: ConversationContext
  ): Promise<string> {
    if (!template.includes('{{CONVERSATION}}')) {
      return template;
    }
    
    const messages = conversationContext.messages.slice(-(conversationContext.limit || 10));
    
    let conversationText = 'Recent conversation:\n';
    messages.forEach(message => {
      conversationText += `${message.role}: ${message.content}\n`;
    });
    
    // Summarize if too long
    if (conversationText.length > (conversationContext.maxLength || 1500)) {
      conversationText = await this.summarizer.summarize(conversationText, {
        maxLength: conversationContext.maxLength || 1500,
        preserveDialogue: true
      });
    }
    
    return template.replace('{{CONVERSATION}}', conversationText);
  }
  
  private async injectDocumentContext(
    template: string, 
    documentContext: DocumentContext
  ): Promise<string> {
    if (!template.includes('{{DOCUMENTS}}')) {
      return template;
    }
    
    const documents = await Promise.all(
      documentContext.documentIds.map(id => this.documentService.getDocument(id))
    );
    
    let documentText = 'Relevant documents:\n';
    documents.forEach((doc, index) => {
      if (doc) {
        documentText += `${index + 1}. ${doc.title}: ${doc.summary || doc.content.substring(0, 200)}...\n`;
      }
    });
    
    // Summarize if too long
    if (documentText.length > (documentContext.maxLength || 2000)) {
      documentText = await this.summarizer.summarize(documentText, {
        maxLength: documentContext.maxLength || 2000,
        preserveStructure: true
      });
    }
    
    return template.replace('{{DOCUMENTS}}', documentText);
  }
}

interface MemoryContext {
  query: string;
  limit?: number;
  threshold?: number;
  maxLength?: number;
  filters?: Record<string, any>;
}

interface ConversationContext {
  messages: Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: string;
  }>;
  limit?: number;
  maxLength?: number;
}

interface DocumentContext {
  documentIds: string[];
  maxLength?: number;
  summaryMode?: 'extract' | 'abstract' | 'full';
}
```

## API & Interface

### REST API Implementation

```typescript
class PromptManagerAPI {
  private compiler: PromptCompiler;
  private store: PromptStore;
  private accessLog: PromptAccessLog;
  
  // Get specific prompt
  async getPrompt(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const prompt = await this.store.getPrompt(id);
      
      if (!prompt) {
        res.status(404).json({ error: 'Prompt not found' });
        return;
      }
      
      // Log access
      await this.accessLog.logAccess(id, req.user.id, 'read');
      
      res.json(prompt);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
  
  // Compile prompt with inputs
  async compilePrompt(req: Request, res: Response): Promise<void> {
    try {
      const request: PromptCompilationRequest = req.body;
      
      // Add security context from request
      request.securityContext = {
        userId: req.user.id,
        permissions: req.user.permissions,
        ipAddress: req.ip,
        userAgent: req.headers['user-agent']
      };
      
      const compiledPrompt = await this.compiler.compilePrompt(request);
      
      res.json(compiledPrompt);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
  
  // Get full prompt stack for agent
  async getAgentPromptStack(req: Request, res: Response): Promise<void> {
    try {
      const { agentName } = req.params;
      
      // Find prompts associated with this agent
      const prompts = await this.store.searchPrompts({
        tags: [agentName, 'agent'],
        type: 'system'
      });
      
      res.json({
        agent: agentName,
        prompts: prompts,
        stackSize: prompts.length
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
  
  // Create new prompt
  async createPrompt(req: Request, res: Response): Promise<void> {
    try {
      const promptData = {
        ...req.body,
        createdBy: req.user.id
      };
      
      const promptId = await this.store.createPrompt(promptData);
      
      res.status(201).json({ id: promptId });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
  
  // Update existing prompt
  async updatePrompt(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const updates = req.body;
      
      await this.store.updatePrompt(id, updates);
      
      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
  
  // Archive prompt (soft delete)
  async archivePrompt(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      
      await this.store.updatePrompt(id, { 
        isProtected: false,
        metadata: {
          ...await this.store.getPrompt(id).then(p => p?.metadata),
          archived: true,
          archivedAt: new Date().toISOString(),
          archivedBy: req.user.id
        }
      });
      
      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
}

// API routes setup
const setupPromptRoutes = (app: Express, api: PromptManagerAPI) => {
  app.get('/api/prompts/:id', authenticate, api.getPrompt.bind(api));
  app.post('/api/prompts/compile', authenticate, api.compilePrompt.bind(api));
  app.get('/api/prompts/agent/:agentName', authenticate, api.getAgentPromptStack.bind(api));
  app.post('/api/prompts/new', authenticate, api.createPrompt.bind(api));
  app.put('/api/prompts/:id', authenticate, api.updatePrompt.bind(api));
  app.delete('/api/prompts/:id', authenticate, api.archivePrompt.bind(api));
};
```

### Agent SDK Methods

```typescript
class PromptManagerSDK {
  private apiClient: APIClient;
  private cache: Map<string, CompiledPrompt> = new Map();
  
  async compilePrompt(options: PromptCompilationOptions): Promise<CompiledPrompt> {
    // Check cache first
    const cacheKey = this.generateCacheKey(options);
    const cached = this.cache.get(cacheKey);
    
    if (cached && this.isCacheValid(cached)) {
      return cached;
    }
    
    // Compile new prompt
    const request: PromptCompilationRequest = {
      taskType: options.task,
      persona: options.persona,
      context: options.context || {},
      variables: options.variables || {},
      customTemplates: options.templates,
      transformations: options.transformations,
      securityContext: options.securityContext || {}
    };
    
    const compiledPrompt = await this.apiClient.post('/api/prompts/compile', request);
    
    // Cache result
    this.cache.set(cacheKey, compiledPrompt);
    
    return compiledPrompt;
  }
  
  async getPromptTemplate(id: string): Promise<PromptRecord> {
    return this.apiClient.get(`/api/prompts/${id}`);
  }
  
  async searchPrompts(query: PromptSearchQuery): Promise<PromptRecord[]> {
    const params = new URLSearchParams();
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, Array.isArray(value) ? value.join(',') : String(value));
      }
    });
    
    return this.apiClient.get(`/api/prompts/search?${params.toString()}`);
  }
  
  private generateCacheKey(options: PromptCompilationOptions): string {
    const keyData = {
      task: options.task,
      persona: options.persona,
      variables: options.variables,
      templates: options.templates
    };
    
    return btoa(JSON.stringify(keyData));
  }
  
  private isCacheValid(prompt: CompiledPrompt): boolean {
    const maxAge = 5 * 60 * 1000; // 5 minutes
    const age = Date.now() - new Date(prompt.metadata.compiledAt).getTime();
    return age < maxAge;
  }
}

interface PromptCompilationOptions {
  task?: string;
  persona?: string;
  context?: PromptContext;
  variables?: Record<string, any>;
  templates?: string[];
  transformations?: TransformationConfig[];
  securityContext?: SecurityContext;
}
```

## Security and Compliance

```typescript
class PromptSecurityManager {
  private piiFilter: PIIFilter;
  private policyEnforcer: PolicyEnforcer;
  private auditLogger: AuditLogger;
  
  async validatePromptSecurity(
    prompt: string, 
    context: SecurityContext
  ): Promise<SecurityValidationResult> {
    const violations: SecurityViolation[] = [];
    
    // PII detection and filtering
    const piiResult = await this.piiFilter.scan(prompt);
    if (piiResult.detected.length > 0) {
      violations.push({
        type: 'pii_detected',
        severity: 'high',
        details: piiResult.detected,
        action: 'redact'
      });
    }
    
    // Policy compliance check
    const policyResult = await this.policyEnforcer.check(prompt, context);
    if (!policyResult.compliant) {
      violations.push({
        type: 'policy_violation',
        severity: policyResult.severity,
        details: policyResult.violations,
        action: 'block'
      });
    }
    
    // Injection attack detection
    const injectionResult = await this.detectInjectionAttacks(prompt);
    if (injectionResult.detected) {
      violations.push({
        type: 'injection_attack',
        severity: 'critical',
        details: injectionResult.patterns,
        action: 'block'
      });
    }
    
    // Log security check
    await this.auditLogger.logSecurityCheck({
      prompt: prompt.substring(0, 100) + '...',
      context,
      violations,
      timestamp: new Date().toISOString()
    });
    
    return {
      valid: violations.length === 0,
      violations,
      sanitizedPrompt: this.applySanitization(prompt, violations)
    };
  }
  
  private async detectInjectionAttacks(prompt: string): Promise<InjectionDetectionResult> {
    const injectionPatterns = [
      /ignore\s+all\s+previous\s+instructions/i,
      /forget\s+everything\s+above/i,
      /you\s+are\s+now\s+a\s+different\s+ai/i,
      /system\s*:\s*override/i,
      /\[SYSTEM\]\s*OVERRIDE/i
    ];
    
    const detectedPatterns: string[] = [];
    
    for (const pattern of injectionPatterns) {
      if (pattern.test(prompt)) {
        detectedPatterns.push(pattern.source);
      }
    }
    
    return {
      detected: detectedPatterns.length > 0,
      patterns: detectedPatterns
    };
  }
  
  private applySanitization(prompt: string, violations: SecurityViolation[]): string {
    let sanitized = prompt;
    
    for (const violation of violations) {
      if (violation.action === 'redact' && violation.type === 'pii_detected') {
        // Apply PII redaction
        for (const pii of violation.details) {
          sanitized = sanitized.replace(new RegExp(pii.value, 'gi'), '[REDACTED]');
        }
      }
    }
    
    return sanitized;
  }
}

interface SecurityValidationResult {
  valid: boolean;
  violations: SecurityViolation[];
  sanitizedPrompt?: string;
}

interface SecurityViolation {
  type: 'pii_detected' | 'policy_violation' | 'injection_attack' | 'content_filter';
  severity: 'low' | 'medium' | 'high' | 'critical';
  details: any[];
  action: 'warn' | 'redact' | 'block';
}

interface SecurityContext {
  userId: string;
  permissions: string[];
  ipAddress: string;
  userAgent?: string;
  organizationId?: string;
  complianceLevel?: 'standard' | 'strict' | 'enterprise';
}
```

## Logging & Auditing

```typescript
class PromptAccessLog {
  private db: Database;
  private analytics: AnalyticsService;
  
  async logAccess(
    promptId: string, 
    userId: string, 
    action: PromptAccessAction,
    metadata?: Record<string, any>
  ): Promise<void> {
    const logEntry: PromptAccessLogEntry = {
      id: generateUUID(),
      promptId,
      userId,
      action,
      timestamp: new Date().toISOString(),
      metadata: metadata || {},
      ipAddress: metadata?.ipAddress,
      userAgent: metadata?.userAgent
    };
    
    // Store in database
    await this.db.run(`
      INSERT INTO prompt_access_log (
        id, prompt_id, user_id, action, timestamp, metadata, ip_address, user_agent
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      logEntry.id,
      logEntry.promptId,
      logEntry.userId,
      logEntry.action,
      logEntry.timestamp,
      JSON.stringify(logEntry.metadata),
      logEntry.ipAddress,
      logEntry.userAgent
    ]);
    
    // Send to analytics
    await this.analytics.track('prompt_access', logEntry);
  }
  
  async getPromptUsageStats(promptId: string): Promise<PromptUsageStats> {
    const stats = await this.db.get(`
      SELECT 
        COUNT(*) as total_accesses,
        COUNT(DISTINCT user_id) as unique_users,
        MAX(timestamp) as last_accessed,
        MIN(timestamp) as first_accessed
      FROM prompt_access_log 
      WHERE prompt_id = ?
    `, [promptId]);
    
    const actionBreakdown = await this.db.all(`
      SELECT action, COUNT(*) as count
      FROM prompt_access_log 
      WHERE prompt_id = ?
      GROUP BY action
    `, [promptId]);
    
    return {
      promptId,
      totalAccesses: stats.total_accesses,
      uniqueUsers: stats.unique_users,
      lastAccessed: stats.last_accessed,
      firstAccessed: stats.first_accessed,
      actionBreakdown: Object.fromEntries(
        actionBreakdown.map(row => [row.action, row.count])
      )
    };
  }
  
  async generateUsageReport(
    startDate: string, 
    endDate: string
  ): Promise<PromptUsageReport> {
    const topPrompts = await this.db.all(`
      SELECT 
        p.name,
        p.type,
        COUNT(l.id) as access_count,
        COUNT(DISTINCT l.user_id) as unique_users
      FROM prompts p
      JOIN prompt_access_log l ON p.id = l.prompt_id
      WHERE l.timestamp BETWEEN ? AND ?
      GROUP BY p.id, p.name, p.type
      ORDER BY access_count DESC
      LIMIT 10
    `, [startDate, endDate]);
    
    const userActivity = await this.db.all(`
      SELECT 
        user_id,
        COUNT(*) as total_accesses,
        COUNT(DISTINCT prompt_id) as unique_prompts
      FROM prompt_access_log
      WHERE timestamp BETWEEN ? AND ?
      GROUP BY user_id
      ORDER BY total_accesses DESC
      LIMIT 10
    `, [startDate, endDate]);
    
    return {
      period: { start: startDate, end: endDate },
      topPrompts,
      userActivity,
      generatedAt: new Date().toISOString()
    };
  }
}

type PromptAccessAction = 
  | 'read'
  | 'compile'
  | 'create'
  | 'update'
  | 'delete'
  | 'search';

interface PromptAccessLogEntry {
  id: string;
  promptId: string;
  userId: string;
  action: PromptAccessAction;
  timestamp: string;
  metadata: Record<string, any>;
  ipAddress?: string;
  userAgent?: string;
}

interface PromptUsageStats {
  promptId: string;
  totalAccesses: number;
  uniqueUsers: number;
  lastAccessed: string;
  firstAccessed: string;
  actionBreakdown: Record<string, number>;
}
```

## Future Features

| Feature | Description | Target Version | Implementation Status |
| ------- | ----------- | -------------- | -------------------- |
| Prompt Diff Viewer | Visual comparison of prompt versions | v1.1 | Planned |
| Prompt Mutation Engine | AI-powered prompt optimization | v1.2 | Research |
| Prompt Debug Mode | Step-by-step compilation debugging | v1.2 | Planned |
| Prompt Evaluation Bench | Automated prompt performance testing | v1.3 | Planned |
| Prompt Clustering & Tags | AI-powered prompt categorization | v1.4 | Research |
| Persona-Prompt Optimizer | Automatic persona-prompt matching | v2.0 | Future |
| Collaborative Prompt Editing | Real-time collaborative editing | v2.1 | Future |
| A/B Testing Framework | Prompt performance comparison | v2.2 | Future |

## Implementation Status

- **Core Prompt Store**: Database schema and API designed
- **Compilation Pipeline**: Architecture and interfaces defined
- **Context Injection**: Framework and implementation planned
- **Security & Validation**: Comprehensive security model specified
- **API Layer**: REST API and SDK interfaces complete
- **Audit System**: Logging and analytics framework ready
- **Reference Implementation**: Planned for kOS v1.0

## Integration Points

- **Agent Lifecycle Management**: Prompts integrated into agent initialization and task execution
- **Memory System**: Context injection from semantic memory and conversation history
- **Security Framework**: Integration with vault and authentication systems
- **Analytics Platform**: Usage tracking and performance monitoring
- **Configuration Management**: Template and policy configuration via config system

## Changelog

- **2024-12-28**: Comprehensive prompt manager specification with TypeScript implementations
- **2025-06-20**: Initial detailed spec with full-stack APIs, context system, and templates (legacy reference) 