---
version: "1.0.0"
last_updated: "2025-01-27"
status: "draft"
type: "specification"
category: "services"
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

## Prompt Repository Structure

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
    // Create default directory structure
    await this.createDirectoryStructure();
    
    // Load registry
    await this.loadRegistry();
    
    // Initialize default templates
    await this.createDefaultTemplates();
    
    // Setup sync if enabled
    await this.repository.syncManager.initialize();
  }

  private async createDirectoryStructure(): Promise<void> {
    const structure = {
      'default/': {
        'agent_init.md': '',
        'agent_summary.md': '',
        'persona/': {
          'kind_helper.md': '',
          'researcher.md': ''
        }
      },
      'system/': {
        'system_orchestrator.md': '',
        'trust_verifier.md': ''
      },
      'projects/': {},
      'registry.json': '{}'
    };

    // Implementation would create actual file structure
    console.log('Created prompt repository structure');
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

    // Validate template
    await this.validateTemplate(template);

    // Store in namespace
    const ns = this.getOrCreateNamespace(namespace);
    ns.templates.set(templateId, template);

    // Update registry
    await this.repository.registry.registerTemplate(template);

    // Save to filesystem
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

    // Validate context against parameters
    this.validateContext(template, context);

    // Interpolate template
    const interpolatedContent = await this.interpolationEngine.interpolate(
      template.content,
      context
    );

    // Create execution record
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

    // Log execution
    await this.executionTracker.logExecution(execution);

    // Return result
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

  private estimateTokens(content: string): number {
    // Rough estimation: ~4 characters per token
    return Math.ceil(content.length / 4);
  }

  private countTokens(content: string): number {
    // More accurate token counting would use tiktoken or similar
    return Math.ceil(content.length / 4);
  }

  private async validateTemplate(template: PromptTemplate): Promise<void> {
    // Validate required fields
    if (!template.id || !template.content) {
      throw new Error('Template must have id and content');
    }

    // Validate version format
    if (!this.isValidSemver(template.version)) {
      throw new Error('Invalid version format');
    }

    // Validate parameters match content
    const contentParams = this.extractParameters(template.content);
    const declaredParams = template.parameters.map(p => p.name);
    
    for (const param of contentParams) {
      if (!declaredParams.includes(param.name)) {
        console.warn(`Undeclared parameter found: ${param.name}`);
      }
    }
  }

  private validateContext(template: PromptTemplate, context: Record<string, any>): void {
    for (const param of template.parameters) {
      if (param.required && !(param.name in context)) {
        throw new Error(`Required parameter missing: ${param.name}`);
      }

      if (param.name in context && param.validation) {
        this.validateParameterValue(context[param.name], param);
      }
    }
  }

  private validateParameterValue(value: any, param: PromptParameter): void {
    // Type validation
    const actualType = typeof value;
    if (param.type !== 'object' && param.type !== 'array' && actualType !== param.type) {
      throw new Error(`Parameter ${param.name} expected ${param.type}, got ${actualType}`);
    }

    // Custom validation rules
    if (param.validation) {
      // Implementation would apply validation rules
    }
  }

  private isValidSemver(version: string): boolean {
    const semverRegex = /^(\d+)\.(\d+)\.(\d+)(-[a-zA-Z0-9-]+)?(\+[a-zA-Z0-9-]+)?$/;
    return semverRegex.test(version);
  }

  private getOrCreateNamespace(name: string): PromptNamespace {
    if (!this.repository.namespaces.has(name)) {
      this.repository.namespaces.set(name, {
        name,
        description: `Namespace: ${name}`,
        templates: new Map(),
        permissions: { read: ['*'], write: ['admin'], sync: true },
        syncEnabled: true
      });
    }
    return this.repository.namespaces.get(name)!;
  }

  private async getTemplate(templateId: string): Promise<PromptTemplate | null> {
    // Search across all namespaces
    for (const namespace of this.repository.namespaces.values()) {
      if (namespace.templates.has(templateId)) {
        return namespace.templates.get(templateId)!;
      }
    }
    return null;
  }

  private async saveTemplate(namespace: string, template: PromptTemplate): Promise<void> {
    const filePath = `${this.repository.basePath}/${namespace}/${template.id}.md`;
    // Implementation would save to filesystem
    console.log(`Saved template to ${filePath}`);
  }
}
```

## Prompt Interpolation Engine

```typescript
interface InterpolationContext {
  variables: Record<string, any>;
  functions: Record<string, Function>;
  conditionals: boolean;
  loops: boolean;
}

class PromptInterpolationEngine {
  private functionRegistry: Map<string, Function> = new Map();

  constructor() {
    this.registerBuiltinFunctions();
  }

  async interpolate(template: string, context: Record<string, any>): Promise<string> {
    const interpolationContext: InterpolationContext = {
      variables: context,
      functions: Object.fromEntries(this.functionRegistry),
      conditionals: true,
      loops: true
    };

    let result = template;

    // Simple variable substitution
    result = this.substituteVariables(result, context);

    // Function calls
    result = await this.executeFunctions(result, interpolationContext);

    // Conditionals
    result = this.processConditionals(result, context);

    // Loops
    result = this.processLoops(result, context);

    return result;
  }

  private substituteVariables(template: string, context: Record<string, any>): string {
    return template.replace(/\$\{?([a-zA-Z_][a-zA-Z0-9_]*)\}?/g, (match, varName) => {
      if (varName in context) {
        const value = context[varName];
        return typeof value === 'string' ? value : JSON.stringify(value);
      }
      return match; // Keep original if not found
    });
  }

  private async executeFunctions(template: string, context: InterpolationContext): Promise<string> {
    const functionRegex = /\$\{([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)\}/g;
    
    let result = template;
    let match;
    
    while ((match = functionRegex.exec(template)) !== null) {
      const [fullMatch, funcName, argsStr] = match;
      
      if (funcName in context.functions) {
        try {
          const args = this.parseArguments(argsStr, context.variables);
          const value = await context.functions[funcName](...args);
          result = result.replace(fullMatch, String(value));
        } catch (error) {
          console.error(`Function execution error: ${funcName}`, error);
          result = result.replace(fullMatch, `[ERROR: ${funcName}]`);
        }
      }
    }

    return result;
  }

  private processConditionals(template: string, context: Record<string, any>): string {
    const conditionalRegex = /\{\{#if\s+([^}]+)\}\}(.*?)\{\{\/if\}\}/gs;
    
    return template.replace(conditionalRegex, (match, condition, content) => {
      if (this.evaluateCondition(condition, context)) {
        return content;
      }
      return '';
    });
  }

  private processLoops(template: string, context: Record<string, any>): string {
    const loopRegex = /\{\{#each\s+([^}]+)\s+as\s+([^}]+)\}\}(.*?)\{\{\/each\}\}/gs;
    
    return template.replace(loopRegex, (match, arrayExpr, itemVar, content) => {
      const array = this.evaluateExpression(arrayExpr, context);
      if (!Array.isArray(array)) {
        return '';
      }

      return array.map(item => {
        const itemContext = { ...context, [itemVar]: item };
        return this.substituteVariables(content, itemContext);
      }).join('');
    });
  }

  private parseArguments(argsStr: string, context: Record<string, any>): any[] {
    if (!argsStr.trim()) return [];
    
    // Simple argument parsing - would need more sophisticated parser for complex cases
    return argsStr.split(',').map(arg => {
      const trimmed = arg.trim();
      
      // String literal
      if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
        return trimmed.slice(1, -1);
      }
      
      // Number literal
      if (/^\d+(\.\d+)?$/.test(trimmed)) {
        return parseFloat(trimmed);
      }
      
      // Variable reference
      if (trimmed in context) {
        return context[trimmed];
      }
      
      return trimmed;
    });
  }

  private evaluateCondition(condition: string, context: Record<string, any>): boolean {
    // Simple condition evaluation - would need expression parser for complex conditions
    const trimmed = condition.trim();
    
    if (trimmed in context) {
      return Boolean(context[trimmed]);
    }
    
    // Simple equality check
    const eqMatch = trimmed.match(/^([^=]+)==(.+)$/);
    if (eqMatch) {
      const [, left, right] = eqMatch;
      const leftVal = left.trim() in context ? context[left.trim()] : left.trim();
      const rightVal = right.trim() in context ? context[right.trim()] : right.trim();
      return leftVal === rightVal;
    }
    
    return false;
  }

  private evaluateExpression(expr: string, context: Record<string, any>): any {
    const trimmed = expr.trim();
    return trimmed in context ? context[trimmed] : null;
  }

  private registerBuiltinFunctions(): void {
    this.functionRegistry.set('now', () => new Date().toISOString());
    this.functionRegistry.set('uuid', () => crypto.randomUUID());
    this.functionRegistry.set('upper', (str: string) => str.toUpperCase());
    this.functionRegistry.set('lower', (str: string) => str.toLowerCase());
    this.functionRegistry.set('length', (arr: any[]) => arr.length);
    this.functionRegistry.set('join', (arr: any[], separator: string = ',') => arr.join(separator));
  }

  registerFunction(name: string, func: Function): void {
    this.functionRegistry.set(name, func);
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
    // Add to memory cache
    this.auditLog.push(execution);

    // Append to JSONL file
    await this.appendToAuditFile(execution);

    // Trigger sync if enabled
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
    // Implementation would append to actual file
    console.log(`Logged execution: ${execution.executionId}`);
  }

  private async syncExecution(execution: PromptExecution): Promise<void> {
    // Implementation would sync via KLP if enabled
  }
}
```

## Versioning & Registry System

```typescript
interface VersionInfo {
  version: string;
  previousVersion?: string;
  changes: string[];
  breaking: boolean;
  deprecated: boolean;
  migrationGuide?: string;
}

class PromptRegistry {
  private templates: Map<string, Map<string, PromptTemplate>> = new Map();
  private versions: Map<string, VersionInfo[]> = new Map();

  async registerTemplate(template: PromptTemplate): Promise<void> {
    const templateId = template.id;
    
    if (!this.templates.has(templateId)) {
      this.templates.set(templateId, new Map());
      this.versions.set(templateId, []);
    }

    const templateVersions = this.templates.get(templateId)!;
    const versionHistory = this.versions.get(templateId)!;

    // Check if version already exists
    if (templateVersions.has(template.version)) {
      throw new Error(`Template ${templateId} version ${template.version} already exists`);
    }

    // Add version
    templateVersions.set(template.version, template);

    // Create version info
    const previousVersions = Array.from(templateVersions.keys()).sort(this.compareVersions);
    const previousVersion = previousVersions.length > 1 ? 
      previousVersions[previousVersions.length - 2] : undefined;

    const versionInfo: VersionInfo = {
      version: template.version,
      previousVersion,
      changes: [], // Would be populated from git or manual input
      breaking: this.isBreakingChange(template, previousVersion ? templateVersions.get(previousVersion) : undefined),
      deprecated: false
    };

    versionHistory.push(versionInfo);
  }

  async getTemplate(templateId: string, version?: string): Promise<PromptTemplate | null> {
    const templateVersions = this.templates.get(templateId);
    if (!templateVersions) return null;

    if (version) {
      return templateVersions.get(version) || null;
    }

    // Get latest version
    const versions = Array.from(templateVersions.keys()).sort(this.compareVersions);
    const latestVersion = versions[versions.length - 1];
    return templateVersions.get(latestVersion) || null;
  }

  async getVersionHistory(templateId: string): Promise<VersionInfo[]> {
    return this.versions.get(templateId) || [];
  }

  async deprecateVersion(templateId: string, version: string, reason: string): Promise<void> {
    const versionHistory = this.versions.get(templateId);
    if (!versionHistory) return;

    const versionInfo = versionHistory.find(v => v.version === version);
    if (versionInfo) {
      versionInfo.deprecated = true;
      versionInfo.migrationGuide = reason;
    }
  }

  private compareVersions(a: string, b: string): number {
    const aParts = a.split('.').map(Number);
    const bParts = b.split('.').map(Number);

    for (let i = 0; i < Math.max(aParts.length, bParts.length); i++) {
      const aPart = aParts[i] || 0;
      const bPart = bParts[i] || 0;

      if (aPart < bPart) return -1;
      if (aPart > bPart) return 1;
    }

    return 0;
  }

  private isBreakingChange(newTemplate: PromptTemplate, oldTemplate?: PromptTemplate): boolean {
    if (!oldTemplate) return false;

    // Check if required parameters were added
    const oldRequiredParams = oldTemplate.parameters.filter(p => p.required).map(p => p.name);
    const newRequiredParams = newTemplate.parameters.filter(p => p.required).map(p => p.name);

    const addedRequiredParams = newRequiredParams.filter(p => !oldRequiredParams.includes(p));
    if (addedRequiredParams.length > 0) return true;

    // Check if parameter types changed
    for (const newParam of newTemplate.parameters) {
      const oldParam = oldTemplate.parameters.find(p => p.name === newParam.name);
      if (oldParam && oldParam.type !== newParam.type) return true;
    }

    return false;
  }
}
```

## CLI Tools & Testing

```typescript
class PromptTester {
  private promptManager: PromptManager;

  constructor(promptManager: PromptManager) {
    this.promptManager = promptManager;
  }

  async testTemplate(
    templateId: string,
    testContext: Record<string, any>,
    options: TestOptions = {}
  ): Promise<TestResult> {
    const startTime = Date.now();
    
    try {
      const result = await this.promptManager.executeTemplate(
        templateId,
        testContext,
        options.agentId || 'test-agent'
      );

      const endTime = Date.now();
      const executionTime = endTime - startTime;

      return {
        success: true,
        result,
        executionTime,
        tokenCount: result.metadata.tokenCount,
        errors: []
      };
    } catch (error) {
      return {
        success: false,
        result: null,
        executionTime: Date.now() - startTime,
        tokenCount: 0,
        errors: [error instanceof Error ? error.message : String(error)]
      };
    }
  }

  async runTestSuite(templateId: string, testCases: TestCase[]): Promise<TestSuiteResult> {
    const results: TestResult[] = [];
    
    for (const testCase of testCases) {
      const result = await this.testTemplate(templateId, testCase.context, testCase.options);
      results.push(result);
    }

    const successCount = results.filter(r => r.success).length;
    const totalTokens = results.reduce((sum, r) => sum + r.tokenCount, 0);
    const avgExecutionTime = results.reduce((sum, r) => sum + r.executionTime, 0) / results.length;

    return {
      templateId,
      totalTests: testCases.length,
      passedTests: successCount,
      failedTests: testCases.length - successCount,
      successRate: successCount / testCases.length,
      totalTokens,
      avgExecutionTime,
      results
    };
  }

  generateDiffReport(templateId: string, version1: string, version2: string): Promise<DiffReport> {
    // Implementation would generate diff between template versions
    return Promise.resolve({
      templateId,
      version1,
      version2,
      changes: [],
      breaking: false,
      recommendations: []
    });
  }
}
```

This comprehensive prompt management system provides enterprise-grade template management, execution tracking, versioning, and testing capabilities essential for maintaining consistent and auditable AI agent interactions across the kOS ecosystem. 