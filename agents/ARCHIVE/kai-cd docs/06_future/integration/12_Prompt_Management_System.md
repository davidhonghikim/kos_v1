---
version: "1.0.0"
last_updated: "2025-01-27"
status: "draft"
type: "specification"
category: "integration"
tags: ["prompts", "templates", "versioning", "audit", "interpolation"]
related_docs:
  - "future/services/06_prompt-management-system.md"
  - "future/protocols/04_agent-system-protocols.md"
  - "current/implementation/02_configuration-management.md"
complexity: "high"
implementation_status: "planned"
code_references:
  - "src/store/serviceStore.ts"
  - "src/utils/promptManager.ts"
  - "src/components/prompts/"
decision_scope: "system-wide"
external_references:
  - "https://semver.org/"
  - "https://tools.ietf.org/html/rfc7515"
changelog:
  - "2025-01-27: Initial migration from brainstorm file 172"
---

# kOS/kAI Prompt Management System

**Agent Context**: This document defines the comprehensive system for managing all prompt templates, executions, and metadata across kAI agents and the kOS operating stack. Agents should understand this as the centralized prompt infrastructure that enables consistent, auditable, and versioned prompt handling with full traceability and synchronization capabilities.

## System Architecture Overview

The Prompt Management System provides:
- Centralized prompt repository with namespacing and versioning
- Full metadata schema for each prompt execution
- Runtime prompt interpolation, evaluation, and context injection
- Agent-aware prompt traceability and debugging
- Distributed synchronization via KLP (Kind Link Protocol)

## Core TypeScript Implementation

```typescript
interface PromptRepository {
  basePath: string;
  namespaces: Map<string, PromptNamespace>;
  registry: PromptRegistry;
  syncManager: PromptSyncManager;
}

interface PromptNamespace {
  name: string;
  description: string;
  templates: Map<string, PromptTemplate>;
  permissions: NamespacePermissions;
  syncEnabled: boolean;
}

interface PromptTemplate {
  id: string;
  version: string;
  description: string;
  author: string;
  lastUpdated: string;
  tags: string[];
  parameters: PromptParameter[];
  content: string;
  metadata: PromptMetadata;
}

interface PromptParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  required: boolean;
  defaultValue?: any;
  description: string;
  validation?: ValidationRule;
}

interface PromptMetadata {
  category: string;
  complexity: 'low' | 'medium' | 'high';
  estimatedTokens: number;
  supportedModels: string[];
  riskLevel: 'safe' | 'moderate' | 'high';
  auditRequired: boolean;
}

class PromptManager {
  private repository: PromptRepository;
  private executionTracker: PromptExecutionTracker;
  private interpolationEngine: PromptInterpolationEngine;

  constructor(basePath: string) {
    this.repository = {
      basePath,
      namespaces: new Map(),
      registry: new PromptRegistry(),
      syncManager: new PromptSyncManager()
    };
    this.executionTracker = new PromptExecutionTracker();
    this.interpolationEngine = new PromptInterpolationEngine();
  }

  async initializeRepository(): Promise<void> {
    await this.createDirectoryStructure();
    await this.loadRegistry();
    await this.createDefaultTemplates();
    await this.repository.syncManager.initialize();
  }

  async createTemplate(
    namespace: string,
    templateId: string,
    content: string,
    metadata: Partial<PromptTemplate>
  ): Promise<string> {
    const template: PromptTemplate = {
      id: templateId,
      version: metadata.version || '1.0.0',
      description: metadata.description || '',
      author: metadata.author || 'system',
      lastUpdated: new Date().toISOString(),
      tags: metadata.tags || [],
      parameters: this.extractParameters(content),
      content,
      metadata: {
        category: metadata.metadata?.category || 'general',
        complexity: metadata.metadata?.complexity || 'medium',
        estimatedTokens: this.estimateTokens(content),
        supportedModels: metadata.metadata?.supportedModels || ['gpt-4', 'claude-3'],
        riskLevel: metadata.metadata?.riskLevel || 'safe',
        auditRequired: metadata.metadata?.auditRequired || false
      }
    };

    await this.validateTemplate(template);

    const ns = this.getOrCreateNamespace(namespace);
    ns.templates.set(templateId, template);

    await this.repository.registry.registerTemplate(template);
    await this.saveTemplate(namespace, template);

    return template.id;
  }

  async executeTemplate(
    templateId: string,
    context: Record<string, any>,
    agentId: string
  ): Promise<PromptExecutionResult> {
    const template = await this.getTemplate(templateId);
    if (!template) {
      throw new Error(`Template not found: ${templateId}`);
    }

    this.validateContext(template, context);

    const interpolatedContent = await this.interpolationEngine.interpolate(
      template.content,
      context
    );

    const execution: PromptExecution = {
      executionId: crypto.randomUUID(),
      templateId,
      templateVersion: template.version,
      agentId,
      timestamp: new Date().toISOString(),
      inputContext: context,
      interpolatedContent,
      metadata: {
        tokenCount: this.countTokens(interpolatedContent),
        executionTime: 0,
        success: true
      }
    };

    await this.executionTracker.logExecution(execution);

    return {
      executionId: execution.executionId,
      content: interpolatedContent,
      metadata: execution.metadata
    };
  }

  private extractParameters(content: string): PromptParameter[] {
    const paramRegex = /\$\{?([a-zA-Z_][a-zA-Z0-9_]*)\}?/g;
    const parameters: PromptParameter[] = [];
    const seen = new Set<string>();

    let match;
    while ((match = paramRegex.exec(content)) !== null) {
      const paramName = match[1];
      if (!seen.has(paramName)) {
        parameters.push({
          name: paramName,
          type: 'string',
          required: true,
          description: `Parameter: ${paramName}`
        });
        seen.add(paramName);
      }
    }

    return parameters;
  }
}
```

## Execution Tracking & Audit System

```typescript
interface PromptExecution {
  executionId: string;
  templateId: string;
  templateVersion: string;
  agentId: string;
  timestamp: string;
  inputContext: Record<string, any>;
  interpolatedContent: string;
  outputSummary?: string;
  metadata: ExecutionMetadata;
}

interface ExecutionMetadata {
  tokenCount: number;
  executionTime: number;
  success: boolean;
  errorMessage?: string;
  modelUsed?: string;
  cost?: number;
}

class PromptExecutionTracker {
  private auditLog: PromptExecution[] = [];
  private logPath: string;

  constructor(logPath: string = '~/.kos/logs/prompts_audit.jsonl') {
    this.logPath = logPath;
  }

  async logExecution(execution: PromptExecution): Promise<void> {
    this.auditLog.push(execution);
    await this.appendToAuditFile(execution);
    await this.syncExecution(execution);
  }

  async getExecutionHistory(
    agentId?: string,
    templateId?: string,
    limit: number = 100
  ): Promise<PromptExecution[]> {
    let filtered = this.auditLog;

    if (agentId) {
      filtered = filtered.filter(exec => exec.agentId === agentId);
    }

    if (templateId) {
      filtered = filtered.filter(exec => exec.templateId === templateId);
    }

    return filtered
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, limit);
  }

  async getExecutionStats(agentId: string, timeRange?: { start: string; end: string }): Promise<ExecutionStats> {
    let executions = this.auditLog.filter(exec => exec.agentId === agentId);

    if (timeRange) {
      executions = executions.filter(exec => 
        exec.timestamp >= timeRange.start && exec.timestamp <= timeRange.end
      );
    }

    const totalExecutions = executions.length;
    const successfulExecutions = executions.filter(exec => exec.metadata.success).length;
    const totalTokens = executions.reduce((sum, exec) => sum + exec.metadata.tokenCount, 0);
    const totalCost = executions.reduce((sum, exec) => sum + (exec.metadata.cost || 0), 0);
    const avgExecutionTime = executions.reduce((sum, exec) => sum + exec.metadata.executionTime, 0) / totalExecutions;

    const templateUsage = executions.reduce((acc, exec) => {
      acc[exec.templateId] = (acc[exec.templateId] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalExecutions,
      successfulExecutions,
      successRate: successfulExecutions / totalExecutions,
      totalTokens,
      totalCost,
      avgExecutionTime,
      templateUsage
    };
  }

  private async appendToAuditFile(execution: PromptExecution): Promise<void> {
    const logEntry = JSON.stringify(execution) + '\n';
    console.log(`Logged execution: ${execution.executionId}`);
  }

  private async syncExecution(execution: PromptExecution): Promise<void> {
    // Implementation would sync via KLP if enabled
  }
}
```

This comprehensive system provides enterprise-grade prompt management with full audit trails, version control, and synchronization capabilities essential for maintaining consistent AI agent interactions across the kOS ecosystem. 