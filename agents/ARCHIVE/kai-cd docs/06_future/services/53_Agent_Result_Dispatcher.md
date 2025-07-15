---
title: "Agent Result Dispatcher"
description: "Centralized service for distributing and routing agent task results"
type: "service"
status: "future"
priority: "medium"
last_updated: "2025-01-27"
related_docs: ["artifact-server-core.md", "agent-lifecycle-management.md"]
implementation_status: "planned"
---

# Agent Result Dispatcher

## Agent Context
Centralized service for efficiently distributing, logging, and routing completed task results from agent modules to designated destinations with consistent formatting, traceability, and secure delivery across various channels.

## Dispatcher Architecture

```typescript
interface AgentResult {
  id: string;
  agentId: string;
  taskId: string;
  timestamp: string;
  type: ResultType;
  data: ResultData;
  metadata: ResultMetadata;
  trace?: ExecutionTrace;
  attachments?: Attachment[];
  sourceDoc?: string;
}

interface ResultData {
  content: any;
  format: DataFormat;
  size: number;
  checksum: string;
  encoding?: string;
}

interface ResultMetadata {
  confidence?: number;
  quality?: number;
  processingTime: number;
  resourceUsage: ResourceUsage;
  tags?: string[];
  classification?: string;
}

type ResultType = 
  | 'text'
  | 'code'
  | 'image'
  | 'audio'
  | 'video'
  | 'data'
  | 'analysis'
  | 'decision';

type DestinationType = 
  | 'ui'
  | 'artifact'
  | 'log'
  | 'validator'
  | 'webhook'
  | 'notification';
```

## Result Dispatcher Engine

```typescript
class ResultDispatcher {
  private routes: Map<string, DispatchRoute[]>;
  private validator: ResultValidator;
  private router: DestinationRouter;
  private transformPipeline: TransformPipeline;
  private auditLogger: AuditLogger;

  constructor(config: DispatcherConfig) {
    this.routes = this.loadRoutes(config.routesPath);
    this.validator = new ResultValidator(config.validationSchema);
    this.router = new DestinationRouter(this.routes);
    this.transformPipeline = new TransformPipeline(config.transforms);
    this.auditLogger = new AuditLogger(config.auditPath);
  }

  async dispatch(result: AgentResult): Promise<DispatchResult> {
    const dispatchId = crypto.randomUUID();
    const startTime = Date.now();

    try {
      // Step 1: Validate result format
      const validation = await this.validator.validate(result);
      if (!validation.valid) {
        throw new InvalidResultFormatError(validation.errors);
      }

      // Step 2: Apply transformation hooks
      const transformedResult = await this.transformPipeline.process(result);

      // Step 3: Determine routing destinations
      const destinations = await this.router.getDestinations(transformedResult);
      
      if (destinations.length === 0) {
        console.warn(`No destinations found for result ${result.id}`);
        destinations.push({ type: 'log', priority: 'low' });
      }

      // Step 4: Dispatch to all destinations
      const dispatchPromises = destinations.map(destination =>
        this.dispatchToDestination(transformedResult, destination)
      );

      const results = await Promise.allSettled(dispatchPromises);
      
      // Step 5: Collect dispatch results
      const successful = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.filter(r => r.status === 'rejected').length;

      const dispatchResult: DispatchResult = {
        id: dispatchId,
        resultId: result.id,
        agentId: result.agentId,
        destinations: destinations.length,
        successful,
        failed,
        processingTime: Date.now() - startTime,
        timestamp: new Date().toISOString()
      };

      // Step 6: Log dispatch outcome
      await this.auditLogger.logDispatch(dispatchResult, results);

      return dispatchResult;

    } catch (error) {
      const errorResult: DispatchResult = {
        id: dispatchId,
        resultId: result.id,
        agentId: result.agentId,
        destinations: 0,
        successful: 0,
        failed: 1,
        error: error.message,
        processingTime: Date.now() - startTime,
        timestamp: new Date().toISOString()
      };

      await this.auditLogger.logDispatchError(errorResult, error);
      throw error;
    }
  }

  private async dispatchToDestination(
    result: AgentResult,
    destination: DispatchDestination
  ): Promise<DestinationResult> {
    const startTime = Date.now();
    
    try {
      let dispatchResult: any;

      switch (destination.type) {
        case 'ui':
          dispatchResult = await this.routeToUI(result, destination);
          break;
        
        case 'artifact':
          dispatchResult = await this.routeToArtifactStore(result, destination);
          break;
        
        case 'log':
          dispatchResult = await this.routeToLog(result, destination);
          break;
        
        case 'validator':
          dispatchResult = await this.routeToValidator(result, destination);
          break;
        
        case 'webhook':
          dispatchResult = await this.routeToWebhook(result, destination);
          break;
        
        case 'notification':
          dispatchResult = await this.routeToNotification(result, destination);
          break;
        
        default:
          throw new Error(`Unknown destination type: ${destination.type}`);
      }

      return {
        destination: destination.type,
        success: true,
        processingTime: Date.now() - startTime,
        result: dispatchResult
      };

    } catch (error) {
      return {
        destination: destination.type,
        success: false,
        processingTime: Date.now() - startTime,
        error: error.message
      };
    }
  }

  private async routeToUI(
    result: AgentResult,
    destination: DispatchDestination
  ): Promise<UIDispatchResult> {
    const uiPayload = await this.formatForUI(result, destination.options);
    
    // Send via WebSocket to connected UI clients
    const connectedClients = await this.getConnectedUIClients(result.agentId);
    const deliveryPromises = connectedClients.map(client =>
      this.sendToUIClient(client, uiPayload)
    );

    const deliveryResults = await Promise.allSettled(deliveryPromises);
    const delivered = deliveryResults.filter(r => r.status === 'fulfilled').length;

    return {
      type: 'ui',
      clientsTargeted: connectedClients.length,
      clientsDelivered: delivered,
      payload: uiPayload
    };
  }

  private async routeToArtifactStore(
    result: AgentResult,
    destination: DispatchDestination
  ): Promise<ArtifactDispatchResult> {
    const artifact = await this.createArtifact(result, destination.options);
    
    const artifactClient = await this.getArtifactClient();
    const storedArtifact = await artifactClient.store(artifact);

    return {
      type: 'artifact',
      artifactId: storedArtifact.id,
      url: storedArtifact.url,
      size: storedArtifact.size
    };
  }

  private async routeToValidator(
    result: AgentResult,
    destination: DispatchDestination
  ): Promise<ValidatorDispatchResult> {
    const validationRequest = {
      resultId: result.id,
      agentId: result.agentId,
      data: result.data,
      metadata: result.metadata,
      validationRules: destination.options?.validationRules || []
    };

    const validatorClient = await this.getValidatorClient();
    const validationJob = await validatorClient.submitValidation(validationRequest);

    return {
      type: 'validator',
      validationJobId: validationJob.id,
      estimatedCompletion: validationJob.estimatedCompletion
    };
  }

  private async routeToWebhook(
    result: AgentResult,
    destination: DispatchDestination
  ): Promise<WebhookDispatchResult> {
    const webhookPayload = await this.formatForWebhook(result, destination.options);
    
    const response = await fetch(destination.options.url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'kAI-ResultDispatcher/1.0',
        ...destination.options.headers
      },
      body: JSON.stringify(webhookPayload),
      timeout: destination.options.timeout || 30000
    });

    if (!response.ok) {
      throw new Error(`Webhook failed: ${response.status} ${response.statusText}`);
    }

    return {
      type: 'webhook',
      url: destination.options.url,
      statusCode: response.status,
      responseSize: parseInt(response.headers.get('content-length') || '0')
    };
  }

  private async createArtifact(
    result: AgentResult,
    options: any
  ): Promise<Artifact> {
    return {
      id: crypto.randomUUID(),
      type: this.mapResultTypeToArtifactType(result.type),
      content: result.data.content,
      metadata: {
        ...result.metadata,
        sourceAgent: result.agentId,
        sourceTask: result.taskId,
        created: new Date().toISOString()
      },
      tags: options?.tags || [],
      access: options?.access || 'private'
    };
  }
}
```

## Routing Configuration

```typescript
class DestinationRouter {
  private routes: Map<string, DispatchRoute[]>;
  private defaultRoutes: DispatchRoute[];

  constructor(routes: Map<string, DispatchRoute[]>) {
    this.routes = routes;
    this.defaultRoutes = [
      { type: 'log', priority: 'low', conditions: [] }
    ];
  }

  async getDestinations(result: AgentResult): Promise<DispatchDestination[]> {
    const destinations: DispatchDestination[] = [];
    
    // Check agent-specific routes
    const agentRoutes = this.routes.get(result.agentId) || [];
    for (const route of agentRoutes) {
      if (await this.matchesRoute(result, route)) {
        destinations.push(this.createDestination(route));
      }
    }

    // Check type-specific routes
    const typeRoutes = this.routes.get(`type:${result.type}`) || [];
    for (const route of typeRoutes) {
      if (await this.matchesRoute(result, route)) {
        destinations.push(this.createDestination(route));
      }
    }

    // Check tag-based routes
    if (result.metadata.tags) {
      for (const tag of result.metadata.tags) {
        const tagRoutes = this.routes.get(`tag:${tag}`) || [];
        for (const route of tagRoutes) {
          if (await this.matchesRoute(result, route)) {
            destinations.push(this.createDestination(route));
          }
        }
      }
    }

    // Apply default routes if no specific routes matched
    if (destinations.length === 0) {
      destinations.push(...this.defaultRoutes.map(route => this.createDestination(route)));
    }

    // Remove duplicates and sort by priority
    return this.deduplicateAndSort(destinations);
  }

  private async matchesRoute(result: AgentResult, route: DispatchRoute): Promise<boolean> {
    for (const condition of route.conditions) {
      const matches = await this.evaluateCondition(result, condition);
      if (!matches) {
        return false;
      }
    }
    return true;
  }

  private async evaluateCondition(result: AgentResult, condition: RouteCondition): Promise<boolean> {
    switch (condition.type) {
      case 'confidence_threshold':
        return (result.metadata.confidence || 0) >= condition.value;
      
      case 'result_size':
        return result.data.size <= condition.value;
      
      case 'processing_time':
        return result.metadata.processingTime <= condition.value;
      
      case 'agent_type':
        const agentInfo = await this.getAgentInfo(result.agentId);
        return agentInfo?.type === condition.value;
      
      case 'has_tag':
        return result.metadata.tags?.includes(condition.value) || false;
      
      case 'time_of_day':
        const hour = new Date().getHours();
        return hour >= condition.value.start && hour <= condition.value.end;
      
      default:
        console.warn(`Unknown condition type: ${condition.type}`);
        return true;
    }
  }
}
```

## Transform Pipeline

```typescript
class TransformPipeline {
  private transforms: Map<string, Transform>;
  private hooks: TransformHook[];

  async process(result: AgentResult): Promise<AgentResult> {
    let processedResult = { ...result };

    // Apply global transforms
    for (const hook of this.hooks) {
      if (await hook.shouldApply(processedResult)) {
        processedResult = await hook.transform(processedResult);
      }
    }

    // Apply result-type specific transforms
    const typeTransform = this.transforms.get(result.type);
    if (typeTransform) {
      processedResult = await typeTransform.apply(processedResult);
    }

    return processedResult;
  }

  addTransform(name: string, transform: Transform): void {
    this.transforms.set(name, transform);
  }

  addHook(hook: TransformHook): void {
    this.hooks.push(hook);
  }
}

class EncryptionTransform implements TransformHook {
  private encryptionKey: CryptoKey;

  async shouldApply(result: AgentResult): boolean {
    return result.metadata.classification === 'confidential' ||
           result.metadata.classification === 'secret';
  }

  async transform(result: AgentResult): Promise<AgentResult> {
    const encryptedData = await this.encrypt(result.data.content);
    
    return {
      ...result,
      data: {
        ...result.data,
        content: encryptedData,
        encoding: 'encrypted'
      },
      metadata: {
        ...result.metadata,
        encrypted: true,
        encryptionAlgorithm: 'AES-256-GCM'
      }
    };
  }

  private async encrypt(data: any): Promise<string> {
    const dataString = typeof data === 'string' ? data : JSON.stringify(data);
    const dataBytes = new TextEncoder().encode(dataString);
    
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      this.encryptionKey,
      dataBytes
    );

    const result = new Uint8Array(iv.length + encrypted.byteLength);
    result.set(iv);
    result.set(new Uint8Array(encrypted), iv.length);
    
    return btoa(String.fromCharCode(...result));
  }
}

class SanitizationTransform implements TransformHook {
  private sensitivePatterns: RegExp[];

  async shouldApply(result: AgentResult): boolean {
    return result.type === 'text' || result.type === 'code';
  }

  async transform(result: AgentResult): Promise<AgentResult> {
    let content = result.data.content;
    
    if (typeof content === 'string') {
      content = this.sanitizeContent(content);
    }

    return {
      ...result,
      data: {
        ...result.data,
        content
      },
      metadata: {
        ...result.metadata,
        sanitized: true
      }
    };
  }

  private sanitizeContent(content: string): string {
    let sanitized = content;
    
    for (const pattern of this.sensitivePatterns) {
      sanitized = sanitized.replace(pattern, '[REDACTED]');
    }

    return sanitized;
  }
}
```
