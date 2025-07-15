---
title: "Prompt Management System"
description: "Comprehensive modular prompt storage, sync, and enrichment engine for kAI/kOS ecosystem"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2025-01-03"
related_docs: ["agent-communication-protocols-core.md", "language-router-and-prompt-linking-engine.md"]
implementation_status: "planned"
---

# Prompt Management System

## Agent Context

This document defines the complete architecture, storage schema, and protocol interfaces for the Prompt Management System (PMS) within the kAI/kOS ecosystem. The PMS manages all prompt templates, prompt runs, versions, metadata, and enrichment routines for both agents and users. Agents must understand the full technical complexity of prompt lifecycle management, versioning, and execution tracing.

## System Architecture

The PMS provides centralized prompt repository with namespacing and versioning, full metadata schema for each prompt execution, runtime prompt interpolation and context injection, agent-aware prompt traceability and debugging, and distributed synchronization via KLP.

### Directory Structure

```
kOS/core/prompt/
├── engine/
│   ├── linker.py               # Link prompts to capabilities
│   ├── enricher.py             # Inject context/memory/meta
│   └── validators.py           # Prompt validation logic
├── models/
│   ├── prompt_model.py         # SQLAlchemy prompt table schema
│   ├── prompt_version.py       # Versioned prompts
│   └── prompt_meta.py          # Tags, source, notes, user/agent
├── api/
│   ├── routes.py               # FastAPI endpoints for CRUD
│   ├── schemas.py              # Pydantic schemas
│   └── permissions.py          # Role-based prompt access
├── store/
│   ├── db_interface.py         # Read/write interface
│   └── indexer.py              # Index and tag enrichment
├── cli/
│   └── manage_prompts.py       # CLI tooling for prompt audit/import/export
└── __init__.py
```

## Data Models

### Core Prompt Schema

```typescript
interface Prompt {
  id: string; // UUID
  title: string;
  scope: 'user' | 'agent' | 'global';
  owner: string; // User or agent id
  created_at: string; // ISO date
  updated_at: string; // ISO date
  tags: string[];
  source: string; // origin (system/gen/human/file)
  description: string;
  category: string;
  priority: number;
  status: 'active' | 'deprecated' | 'draft';
}

interface PromptVersion {
  id: string; // UUID
  prompt_id: string; // UUID
  version_number: number;
  content: string;
  diff_hash: string; // checksum for change tracking
  notes: string;
  created_at: string; // ISO date
  author: string;
  changelog: string;
  parameters: PromptParameter[];
  validation_rules: ValidationRule[];
}

interface PromptParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  required: boolean;
  default_value?: any;
  description: string;
  validation_pattern?: string;
}

interface PromptLink {
  prompt_id: string; // UUID
  capability: string; // e.g. 'summarize', 'code_review'
  agent_id: string; // UUID
  priority: number; // order of execution if multiple apply
  conditions: LinkCondition[];
  context_requirements: string[];
}

interface LinkCondition {
  field: string;
  operator: 'equals' | 'contains' | 'matches' | 'greater_than' | 'less_than';
  value: any;
  description: string;
}
```

### Execution Tracking

```typescript
interface PromptExecution {
  id: string; // UUID
  prompt_id: string;
  version_number: number;
  agent_id: string;
  user_id: string;
  timestamp: string; // ISO date
  input_context: Record<string, any>;
  interpolated_text: string;
  output_summary: string;
  execution_time_ms: number;
  success: boolean;
  error_message?: string;
  metadata: ExecutionMetadata;
}

interface ExecutionMetadata {
  session_id: string;
  conversation_id: string;
  model_used: string;
  token_count: {
    input: number;
    output: number;
    total: number;
  };
  performance_metrics: {
    latency_ms: number;
    memory_usage_mb: number;
    cpu_usage_percent: number;
  };
  quality_scores: {
    relevance: number;
    coherence: number;
    accuracy: number;
  };
}
```

## Core Implementation

### Prompt Repository Manager

```typescript
class PromptRepository {
  private db: Database;
  private cache: Map<string, Prompt>;
  private indexer: PromptIndexer;

  constructor(dbConfig: DatabaseConfig) {
    this.db = new Database(dbConfig);
    this.cache = new Map();
    this.indexer = new PromptIndexer();
  }

  async createPrompt(prompt: CreatePromptRequest): Promise<Prompt> {
    // Validate prompt structure
    await this.validatePrompt(prompt);

    // Generate unique ID
    const id = this.generatePromptId();

    // Create initial version
    const initialVersion: PromptVersion = {
      id: this.generateVersionId(),
      prompt_id: id,
      version_number: 1,
      content: prompt.content,
      diff_hash: await this.calculateHash(prompt.content),
      notes: 'Initial version',
      created_at: new Date().toISOString(),
      author: prompt.author,
      changelog: 'Initial creation',
      parameters: prompt.parameters || [],
      validation_rules: prompt.validation_rules || []
    };

    // Store in database
    const newPrompt: Prompt = {
      id,
      title: prompt.title,
      scope: prompt.scope,
      owner: prompt.owner,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      tags: prompt.tags || [],
      source: prompt.source || 'manual',
      description: prompt.description,
      category: prompt.category,
      priority: prompt.priority || 0,
      status: 'active'
    };

    await this.db.transaction(async (tx) => {
      await tx.insert('prompts', newPrompt);
      await tx.insert('prompt_versions', initialVersion);
    });

    // Update cache and index
    this.cache.set(id, newPrompt);
    await this.indexer.indexPrompt(newPrompt, initialVersion);

    return newPrompt;
  }

  async updatePrompt(id: string, updates: UpdatePromptRequest): Promise<Prompt> {
    const existing = await this.getPrompt(id);
    if (!existing) {
      throw new Error(`Prompt not found: ${id}`);
    }

    // Create new version if content changed
    if (updates.content && updates.content !== existing.content) {
      await this.createVersion(id, {
        content: updates.content,
        notes: updates.notes || 'Content update',
        author: updates.author
      });
    }

    // Update prompt metadata
    const updated: Prompt = {
      ...existing,
      ...updates,
      updated_at: new Date().toISOString()
    };

    await this.db.update('prompts', { id }, updated);
    this.cache.set(id, updated);

    return updated;
  }

  async createVersion(promptId: string, versionData: CreateVersionRequest): Promise<PromptVersion> {
    const prompt = await this.getPrompt(promptId);
    if (!prompt) {
      throw new Error(`Prompt not found: ${promptId}`);
    }

    // Get current version number
    const versions = await this.getVersions(promptId);
    const nextVersion = Math.max(...versions.map(v => v.version_number)) + 1;

    const newVersion: PromptVersion = {
      id: this.generateVersionId(),
      prompt_id: promptId,
      version_number: nextVersion,
      content: versionData.content,
      diff_hash: await this.calculateHash(versionData.content),
      notes: versionData.notes,
      created_at: new Date().toISOString(),
      author: versionData.author,
      changelog: versionData.changelog || '',
      parameters: versionData.parameters || [],
      validation_rules: versionData.validation_rules || []
    };

    await this.db.insert('prompt_versions', newVersion);
    await this.indexer.indexVersion(newVersion);

    return newVersion;
  }

  async linkToCapability(link: PromptLink): Promise<void> {
    // Validate capability exists
    await this.validateCapability(link.capability);

    // Check for conflicts
    const existing = await this.getLinksForCapability(link.capability);
    const conflicts = existing.filter(l => 
      l.agent_id === link.agent_id && l.priority === link.priority
    );

    if (conflicts.length > 0) {
      throw new Error(`Priority conflict for capability ${link.capability}`);
    }

    await this.db.insert('prompt_links', link);
  }
}
```

### Runtime Interpolation Engine

```typescript
class PromptInterpolator {
  private contextProviders: Map<string, ContextProvider>;
  private validators: Map<string, ParameterValidator>;

  constructor() {
    this.contextProviders = new Map();
    this.validators = new Map();
    this.initializeBuiltinProviders();
  }

  async interpolatePrompt(
    promptId: string,
    version?: number,
    context: Record<string, any> = {}
  ): Promise<InterpolationResult> {
    // Load prompt and version
    const prompt = await this.loadPrompt(promptId);
    const promptVersion = await this.loadVersion(promptId, version);

    if (!prompt || !promptVersion) {
      throw new Error(`Prompt or version not found: ${promptId}:${version}`);
    }

    // Validate parameters
    await this.validateParameters(promptVersion.parameters, context);

    // Gather context from providers
    const enrichedContext = await this.enrichContext(context, promptVersion);

    // Perform interpolation
    const interpolated = await this.performInterpolation(
      promptVersion.content,
      enrichedContext
    );

    // Validate result
    await this.validateResult(interpolated, promptVersion.validation_rules);

    return {
      prompt_id: promptId,
      version_number: promptVersion.version_number,
      original_content: promptVersion.content,
      interpolated_content: interpolated,
      context_used: enrichedContext,
      timestamp: new Date().toISOString()
    };
  }

  private async enrichContext(
    baseContext: Record<string, any>,
    version: PromptVersion
  ): Promise<Record<string, any>> {
    const enriched = { ...baseContext };

    // Add system context
    enriched.$timestamp = new Date().toISOString();
    enriched.$version = version.version_number;

    // Run context providers
    for (const [name, provider] of this.contextProviders) {
      try {
        const additionalContext = await provider.getContext(baseContext);
        Object.assign(enriched, additionalContext);
      } catch (error) {
        console.warn(`Context provider ${name} failed:`, error);
      }
    }

    return enriched;
  }

  private async performInterpolation(
    template: string,
    context: Record<string, any>
  ): Promise<string> {
    let result = template;

    // Replace simple variables: ${variable}
    result = result.replace(/\$\{([^}]+)\}/g, (match, key) => {
      const value = this.getNestedValue(context, key);
      return value !== undefined ? String(value) : match;
    });

    // Replace conditional blocks: {{#if condition}}...{{/if}}
    result = await this.processConditionals(result, context);

    // Replace loops: {{#each items}}...{{/each}}
    result = await this.processLoops(result, context);

    return result;
  }

  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }
}
```

### Execution Audit System

```typescript
class PromptAuditLogger {
  private db: Database;
  private logBuffer: PromptExecution[];
  private bufferSize = 100;

  constructor(db: Database) {
    this.db = db;
    this.logBuffer = [];
    this.startPeriodicFlush();
  }

  async logExecution(execution: PromptExecution): Promise<void> {
    // Add to buffer
    this.logBuffer.push(execution);

    // Flush if buffer is full
    if (this.logBuffer.length >= this.bufferSize) {
      await this.flushBuffer();
    }
  }

  async queryExecutions(query: ExecutionQuery): Promise<PromptExecution[]> {
    let sql = 'SELECT * FROM prompt_executions WHERE 1=1';
    const params: any[] = [];

    if (query.prompt_id) {
      sql += ' AND prompt_id = ?';
      params.push(query.prompt_id);
    }

    if (query.agent_id) {
      sql += ' AND agent_id = ?';
      params.push(query.agent_id);
    }

    if (query.start_date) {
      sql += ' AND timestamp >= ?';
      params.push(query.start_date);
    }

    if (query.end_date) {
      sql += ' AND timestamp <= ?';
      params.push(query.end_date);
    }

    if (query.success !== undefined) {
      sql += ' AND success = ?';
      params.push(query.success);
    }

    sql += ' ORDER BY timestamp DESC';

    if (query.limit) {
      sql += ' LIMIT ?';
      params.push(query.limit);
    }

    return await this.db.query(sql, params);
  }

  async generateReport(reportType: 'performance' | 'usage' | 'errors'): Promise<ExecutionReport> {
    switch (reportType) {
      case 'performance':
        return this.generatePerformanceReport();
      case 'usage':
        return this.generateUsageReport();
      case 'errors':
        return this.generateErrorReport();
      default:
        throw new Error(`Unknown report type: ${reportType}`);
    }
  }

  private async generatePerformanceReport(): Promise<PerformanceReport> {
    const sql = `
      SELECT 
        prompt_id,
        COUNT(*) as execution_count,
        AVG(execution_time_ms) as avg_execution_time,
        MIN(execution_time_ms) as min_execution_time,
        MAX(execution_time_ms) as max_execution_time,
        AVG(JSON_EXTRACT(metadata, '$.performance_metrics.latency_ms')) as avg_latency,
        SUM(JSON_EXTRACT(metadata, '$.token_count.total')) as total_tokens
      FROM prompt_executions
      WHERE timestamp >= datetime('now', '-7 days')
      GROUP BY prompt_id
      ORDER BY execution_count DESC
    `;

    const results = await this.db.query(sql);
    return {
      type: 'performance',
      generated_at: new Date().toISOString(),
      period: '7 days',
      data: results
    };
  }

  private startPeriodicFlush(): void {
    setInterval(async () => {
      if (this.logBuffer.length > 0) {
        await this.flushBuffer();
      }
    }, 30000); // Flush every 30 seconds
  }

  private async flushBuffer(): Promise<void> {
    if (this.logBuffer.length === 0) return;

    const toFlush = [...this.logBuffer];
    this.logBuffer.length = 0;

    try {
      await this.db.insertBatch('prompt_executions', toFlush);
    } catch (error) {
      console.error('Failed to flush execution log buffer:', error);
      // Re-add to buffer for retry
      this.logBuffer.unshift(...toFlush);
    }
  }
}
```

## API Implementation

### REST API Routes

```typescript
class PromptAPI {
  private repository: PromptRepository;
  private interpolator: PromptInterpolator;
  private auditLogger: PromptAuditLogger;

  constructor(
    repository: PromptRepository,
    interpolator: PromptInterpolator,
    auditLogger: PromptAuditLogger
  ) {
    this.repository = repository;
    this.interpolator = interpolator;
    this.auditLogger = auditLogger;
  }

  // GET /api/prompts/
  async listPrompts(req: Request): Promise<PromptListResponse> {
    const { page = 1, limit = 20, scope, tags, search } = req.query;
    
    const filters: PromptFilters = {
      scope: scope as string,
      tags: tags ? (tags as string).split(',') : undefined,
      search: search as string
    };

    const prompts = await this.repository.listPrompts(filters, {
      page: Number(page),
      limit: Number(limit)
    });

    return {
      prompts: prompts.items,
      pagination: {
        page: prompts.page,
        limit: prompts.limit,
        total: prompts.total,
        pages: Math.ceil(prompts.total / prompts.limit)
      }
    };
  }

  // GET /api/prompts/:id
  async getPrompt(req: Request): Promise<PromptDetailResponse> {
    const { id } = req.params;
    const { include_versions = false } = req.query;

    const prompt = await this.repository.getPrompt(id);
    if (!prompt) {
      throw new NotFoundError(`Prompt not found: ${id}`);
    }

    const response: PromptDetailResponse = { prompt };

    if (include_versions === 'true') {
      response.versions = await this.repository.getVersions(id);
    }

    return response;
  }

  // POST /api/prompts/
  async createPrompt(req: Request): Promise<CreatePromptResponse> {
    const promptData = req.body as CreatePromptRequest;
    
    // Validate permissions
    await this.validateCreatePermission(req.user, promptData.scope);

    const prompt = await this.repository.createPrompt(promptData);
    
    return { prompt };
  }

  // POST /api/prompts/:id/version
  async createVersion(req: Request): Promise<CreateVersionResponse> {
    const { id } = req.params;
    const versionData = req.body as CreateVersionRequest;

    // Validate permissions
    await this.validateUpdatePermission(req.user, id);

    const version = await this.repository.createVersion(id, versionData);
    
    return { version };
  }

  // POST /api/prompts/enrich
  async enrichPrompt(req: Request): Promise<EnrichmentResponse> {
    const { prompt_id, version, context } = req.body;

    const result = await this.interpolator.interpolatePrompt(
      prompt_id,
      version,
      context
    );

    // Log execution
    const execution: PromptExecution = {
      id: generateId(),
      prompt_id,
      version_number: result.version_number,
      agent_id: req.user.agent_id,
      user_id: req.user.user_id,
      timestamp: new Date().toISOString(),
      input_context: context,
      interpolated_text: result.interpolated_content,
      output_summary: 'Enrichment successful',
      execution_time_ms: 0, // Set by middleware
      success: true,
      metadata: {
        session_id: req.session.id,
        conversation_id: req.headers['x-conversation-id'],
        model_used: 'interpolation-engine',
        token_count: {
          input: result.original_content.length,
          output: result.interpolated_content.length,
          total: result.original_content.length + result.interpolated_content.length
        },
        performance_metrics: {
          latency_ms: 0,
          memory_usage_mb: 0,
          cpu_usage_percent: 0
        },
        quality_scores: {
          relevance: 1.0,
          coherence: 1.0,
          accuracy: 1.0
        }
      }
    };

    await this.auditLogger.logExecution(execution);

    return result;
  }
}
```

## Synchronization & Federation

### KLP Integration

```typescript
class PromptSyncManager {
  private klpClient: KLPClient;
  private repository: PromptRepository;
  private syncConfig: SyncConfig;

  constructor(klpClient: KLPClient, repository: PromptRepository, config: SyncConfig) {
    this.klpClient = klpClient;
    this.repository = repository;
    this.syncConfig = config;
  }

  async syncPrompts(): Promise<SyncResult> {
    const localPrompts = await this.repository.getPromptsForSync();
    const remotePrompts = await this.klpClient.fetchPrompts();

    const conflicts: ConflictInfo[] = [];
    const synced: string[] = [];

    for (const local of localPrompts) {
      const remote = remotePrompts.find(r => r.id === local.id);
      
      if (!remote) {
        // Local only - push to remote
        await this.pushPrompt(local);
        synced.push(local.id);
      } else if (local.updated_at > remote.updated_at) {
        // Local is newer - push to remote
        await this.pushPrompt(local);
        synced.push(local.id);
      } else if (remote.updated_at > local.updated_at) {
        // Remote is newer - pull from remote
        await this.pullPrompt(remote);
        synced.push(local.id);
      } else {
        // Conflict - needs resolution
        conflicts.push({
          prompt_id: local.id,
          local_version: local.updated_at,
          remote_version: remote.updated_at,
          resolution_strategy: this.syncConfig.conflict_resolution
        });
      }
    }

    return {
      synced_count: synced.length,
      conflict_count: conflicts.length,
      conflicts,
      timestamp: new Date().toISOString()
    };
  }

  private async pushPrompt(prompt: Prompt): Promise<void> {
    const versions = await this.repository.getVersions(prompt.id);
    const links = await this.repository.getLinks(prompt.id);

    const syncPayload: PromptSyncPayload = {
      prompt,
      versions,
      links,
      signature: await this.signPayload({ prompt, versions, links })
    };

    await this.klpClient.send({
      type: 'prompt_sync',
      target: 'klp://mesh/prompts',
      payload: syncPayload
    });
  }
}
```

## CLI Tools

### Command Line Interface

```typescript
class PromptCLI {
  private repository: PromptRepository;
  private interpolator: PromptInterpolator;

  constructor(repository: PromptRepository, interpolator: PromptInterpolator) {
    this.repository = repository;
    this.interpolator = interpolator;
  }

  async list(options: CLIListOptions): Promise<void> {
    const prompts = await this.repository.listPrompts({
      scope: options.scope,
      tags: options.tags?.split(','),
      search: options.search
    });

    console.table(prompts.items.map(p => ({
      ID: p.id.substring(0, 8),
      Title: p.title,
      Scope: p.scope,
      Tags: p.tags.join(', '),
      Updated: new Date(p.updated_at).toLocaleDateString()
    })));
  }

  async import(filePath: string): Promise<void> {
    const content = await fs.readFile(filePath, 'utf-8');
    const prompts = JSON.parse(content) as ImportPromptData[];

    for (const promptData of prompts) {
      try {
        await this.repository.createPrompt(promptData);
        console.log(`✅ Imported: ${promptData.title}`);
      } catch (error) {
        console.error(`❌ Failed to import ${promptData.title}:`, error.message);
      }
    }
  }

  async export(options: CLIExportOptions): Promise<void> {
    const prompts = await this.repository.listPrompts({
      scope: options.scope
    });

    const exportData = await Promise.all(
      prompts.items.map(async (prompt) => {
        const versions = await this.repository.getVersions(prompt.id);
        return { prompt, versions };
      })
    );

    await fs.writeFile(
      options.output || 'prompts-export.json',
      JSON.stringify(exportData, null, 2)
    );

    console.log(`✅ Exported ${prompts.items.length} prompts`);
  }

  async test(promptId: string, context: Record<string, any>): Promise<void> {
    try {
      const result = await this.interpolator.interpolatePrompt(promptId, undefined, context);
      
      console.log('🔍 Prompt Test Results');
      console.log('='.repeat(50));
      console.log('Original:');
      console.log(result.original_content);
      console.log('\nInterpolated:');
      console.log(result.interpolated_content);
      console.log('\nContext Used:');
      console.log(JSON.stringify(result.context_used, null, 2));
      
    } catch (error) {
      console.error('❌ Test failed:', error.message);
    }
  }
}
```

## Implementation Status

- **Core Architecture**: ✅ Designed
- **Data Models**: ✅ Complete
- **Repository Layer**: ✅ Specified
- **Interpolation Engine**: ✅ Specified
- **Audit System**: ✅ Specified
- **API Layer**: ✅ Complete
- **CLI Tools**: ✅ Specified
- **KLP Integration**: ✅ Specified

---

*This document provides the complete technical specification for the Prompt Management System with full TypeScript implementations for all core components and comprehensive audit trails.*
