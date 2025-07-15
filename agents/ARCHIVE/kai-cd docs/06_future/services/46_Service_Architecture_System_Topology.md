---
title: "Service Architecture and System Topology"
description: "Complete modular service architecture of kOS and kAI platform, including low-level breakdowns of system components, communication protocols, software modules, and deployment models"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2024-12-28"
related_docs: [
  "documentation/future/architecture/08_kos-system-architecture-complete.md",
  "documentation/future/services/40_system-services-fullstack-complete.md",
  "documentation/current/services/01_service-architecture.md"
]
implementation_status: "planned"
---

# Service Architecture and System Topology

## Agent Context
**For AI Agents**: This document defines the complete service architecture for both kOS and kAI platforms. When implementing services, follow the modular architecture with clear separation between User Layer, Control Layer, and Infrastructure Layer. Use the specified communication protocols (WebSocket, REST, gRPC) and ensure all services register with the Agent Mesh Runtime. Pay attention to the deployment models and security components for proper implementation.

## Architectural Layers

### User Layer (Client Interfaces)

```typescript
interface UserLayerArchitecture {
  webApp: 'kAI Web App (kai-cd)';
  terminal: 'kAI Terminal Interface (CLI)';
  mobile: 'Mobile Client (Planned)';
  desktop: 'Desktop App (Future)';
}

// kAI Web App (kai-cd) Specification
interface KaiWebApp {
  framework: 'React + TypeScript';
  styling: 'Tailwind CSS';
  features: {
    themeEngine: boolean;
    accessibilityLayer: boolean;
    pluginUIs: boolean;
    iframeSandbox: boolean;
    realTimeInteraction: boolean;
  };
  targets: {
    chromeExtension: boolean;
    tab: boolean;
    popup: boolean;
    sidepanel: boolean;
  };
  communication: {
    webSocket: 'Real-time API';
    rest: 'REST API client';
    eventStream: 'Server-sent events';
  };
}

// Terminal Interface Specification
interface KaiTerminalInterface {
  runtime: 'Node.js REPL + Python fallback';
  features: {
    agentControl: boolean;
    diagnosticTools: boolean;
    encryptedConfig: boolean;
    vaultIntegration: boolean;
  };
  commands: {
    'kai agent list': 'List all active agents';
    'kai agent start <name>': 'Start specific agent';
    'kai agent stop <name>': 'Stop specific agent';
    'kai config set <key> <value>': 'Update configuration';
    'kai vault unlock': 'Unlock secure vault';
    'kai logs tail': 'Stream application logs';
    'kai status': 'System health overview';
  };
}

// Mobile Client (Planned)
interface KaiMobileApp {
  framework: 'React Native';
  features: {
    pushNotifications: boolean;
    cameraSensors: boolean;
    microphoneSensors: boolean;
    offlineMode: boolean;
    biometricAuth: boolean;
  };
  platforms: ['iOS', 'Android'];
  capabilities: {
    voiceInput: boolean;
    imageCapture: boolean;
    locationServices: boolean;
    backgroundSync: boolean;
  };
}
```

### Control Layer

```typescript
interface ControlLayerArchitecture {
  agentMeshRuntime: 'Agent orchestration and management';
  orchestrationBus: 'Central communication hub';
  apiGateway: 'Request routing and authentication';
}

// Agent Mesh Runtime
interface AgentMeshRuntime {
  orchestrator: 'kCore';
  registration: {
    manifestRequired: boolean;
    authMethod: 'Ed25519 identity keys';
    discoveryProtocol: 'mDNS + KLP';
  };
  deployment: {
    localhost: boolean;
    lan: boolean;
    cloud: boolean;
  };
  communication: {
    protocol: 'KLP (Kind Link Protocol)';
    transport: ['WebSocket', 'gRPC', 'HTTP/3'];
    encryption: 'TLS 1.3 + Ed25519 signatures';
  };
}

class AgentMeshRuntime {
  private agents: Map<string, AgentInstance> = new Map();
  private kCore: KCoreOrchestrator;
  
  async registerAgent(manifest: AgentManifest): Promise<void> {
    // Validate manifest and identity
    await this.validateAgentManifest(manifest);
    
    // Create agent instance
    const instance = new AgentInstance(manifest);
    await instance.initialize();
    
    // Register with kCore orchestrator
    await this.kCore.registerAgent(instance);
    
    this.agents.set(manifest.id, instance);
  }
  
  async routeMessage(message: KLPMessage): Promise<KLPMessage> {
    const targetAgent = this.agents.get(message.to);
    if (!targetAgent) {
      throw new Error(`Agent ${message.to} not found`);
    }
    
    return targetAgent.handleMessage(message);
  }
  
  getAgentHealth(): Record<string, AgentHealthStatus> {
    const health: Record<string, AgentHealthStatus> = {};
    
    for (const [id, agent] of this.agents) {
      health[id] = agent.getHealthStatus();
    }
    
    return health;
  }
}

// Central Orchestration Bus
interface OrchestrationBus {
  pubsub: 'Redis pub/sub or NATS';
  websocketRelay: 'Browser <-> Backend messaging';
  eventStream: 'Server-sent events for real-time updates';
}

class OrchestrationBus {
  private pubsub: PubSubClient;
  private websocketServer: WebSocketServer;
  private eventStream: EventStreamManager;
  
  async publishEvent(event: SystemEvent): Promise<void> {
    await this.pubsub.publish(event.channel, event);
    
    // Also send to connected WebSocket clients
    this.websocketServer.broadcast(event);
    
    // And push to event stream subscribers
    this.eventStream.push(event);
  }
  
  async subscribeToEvents(
    channels: string[], 
    handler: (event: SystemEvent) => void
  ): Promise<void> {
    await this.pubsub.subscribe(channels, handler);
  }
}

// API Gateway
interface APIGateway {
  implementation: 'FastAPI / Envoy / Nginx';
  features: {
    authentication: boolean;
    rateLimit: boolean;
    loadBalancing: boolean;
    requestRouting: boolean;
    responseTransformation: boolean;
  };
  protocols: ['HTTP/1.1', 'HTTP/2', 'HTTP/3', 'WebSocket', 'gRPC'];
}
```

### Infrastructure Layer

```typescript
interface InfrastructureLayerArchitecture {
  backendServices: BackendServicesSpec;
  dataStores: DataStoresSpec;
  llmProviderInterfaces: LLMProviderSpec;
  security: SecurityInfrastructure;
}

// Backend Services
interface BackendServicesSpec {
  coreAPI: {
    framework: 'FastAPI';
    features: ['async/await', 'automatic OpenAPI', 'dependency injection'];
    endpoints: APIEndpointSpec[];
  };
  orchestration: {
    framework: 'LangChain';
    purpose: 'Agent chaining and workflow management';
    features: ['tool integration', 'memory management', 'prompt templates'];
  };
  asyncTasks: {
    framework: 'Celery';
    broker: 'Redis';
    features: ['distributed execution', 'result backend', 'task scheduling'];
  };
  vectorStore: {
    manager: 'Vector Store Manager';
    backends: ['Chroma', 'Qdrant', 'Weaviate', 'Pinecone'];
    features: ['semantic search', 'embedding management', 'metadata filtering'];
  };
  secureVault: {
    encryption: 'AES-256';
    keyManagement: 'local or remote KMS';
    features: ['secret storage', 'key rotation', 'access policies'];
  };
}

// API Endpoint Specifications
interface APIEndpointSpec {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  description: string;
  authentication: boolean;
  rateLimit?: number;
}

const coreAPIEndpoints: APIEndpointSpec[] = [
  {
    path: '/agent/task',
    method: 'POST',
    description: 'Submit new goal or subtask',
    authentication: true,
    rateLimit: 100
  },
  {
    path: '/agent/status',
    method: 'GET',
    description: 'List agent health and state',
    authentication: true
  },
  {
    path: '/vault/encrypt',
    method: 'POST',
    description: 'Encrypt data using vault',
    authentication: true,
    rateLimit: 50
  },
  {
    path: '/vault/decrypt',
    method: 'POST',
    description: 'Decrypt data using vault',
    authentication: true,
    rateLimit: 50
  },
  {
    path: '/artifact/upload',
    method: 'POST',
    description: 'Upload file or artifact',
    authentication: true,
    rateLimit: 20
  },
  {
    path: '/artifact/:id',
    method: 'GET',
    description: 'Retrieve artifact by ID',
    authentication: true
  },
  {
    path: '/memory/search',
    method: 'GET',
    description: 'Search semantic memory',
    authentication: true,
    rateLimit: 200
  },
  {
    path: '/planner/plan',
    method: 'POST',
    description: 'Generate execution plan',
    authentication: true,
    rateLimit: 30
  }
];

// Data Stores
interface DataStoresSpec {
  primary: {
    database: 'PostgreSQL';
    purpose: 'Primary structured data';
    features: ['ACID compliance', 'JSON support', 'full-text search'];
  };
  cache: {
    database: 'Redis';
    purpose: 'Cache and short-term memory';
    features: ['pub/sub', 'streams', 'clustering'];
  };
  objectStorage: {
    services: ['S3', 'GCS', 'Azure Blob'];
    purpose: 'File and artifact storage';
    features: ['versioning', 'encryption', 'CDN integration'];
  };
  vector: {
    databases: ['Chroma', 'Qdrant', 'Weaviate'];
    purpose: 'Embedding storage and similarity search';
    features: ['HNSW indexing', 'metadata filtering', 'distributed deployment'];
  };
}

// LLM Provider Interfaces
interface LLMProviderSpec {
  local: {
    runners: ['Ollama', 'llama.cpp', 'vLLM', 'text-generation-inference'];
    models: ['Llama 2', 'Code Llama', 'Mistral', 'Phi-3'];
    features: ['GPU acceleration', 'quantization', 'batching'];
  };
  remote: {
    providers: ['OpenAI', 'Anthropic', 'Google', 'HuggingFace'];
    apis: ['Chat Completions', 'Embeddings', 'Fine-tuning'];
    features: ['streaming', 'function calling', 'vision'];
  };
  unified: {
    interface: 'LangChain LLM abstraction';
    features: ['provider switching', 'fallback handling', 'cost tracking'];
  };
}
```

## Component Breakdown (by Subsystem)

### Prompt Management System

```typescript
interface PromptManagementSystem {
  structure: {
    'components/prompt_manager/': {
      'PromptStore.ts': 'IndexedDB local prompt history';
      'PromptProfile.ts': 'Named context templates';
      'PromptEditor.tsx': 'WYSIWYG + markdown hybrid editor';
      'PromptRenderer.ts': 'Runtime variable injection';
      'PromptVaultAdapter.ts': 'Secure vault integration';
    };
  };
  features: {
    versioning: boolean;
    templates: boolean;
    contextInjection: boolean;
    secureStorage: boolean;
    collaboration: boolean;
  };
}

class PromptStore {
  private db: IDBDatabase;
  
  async savePrompt(prompt: PromptRecord): Promise<string> {
    const transaction = this.db.transaction(['prompts'], 'readwrite');
    const store = transaction.objectStore('prompts');
    
    const promptWithMetadata = {
      ...prompt,
      id: prompt.id || generateUUID(),
      createdAt: new Date().toISOString(),
      version: prompt.version || 1
    };
    
    await store.put(promptWithMetadata);
    return promptWithMetadata.id;
  }
  
  async getPrompt(id: string): Promise<PromptRecord | null> {
    const transaction = this.db.transaction(['prompts'], 'readonly');
    const store = transaction.objectStore('prompts');
    
    return store.get(id);
  }
  
  async searchPrompts(query: string, filters?: PromptFilters): Promise<PromptRecord[]> {
    const transaction = this.db.transaction(['prompts'], 'readonly');
    const store = transaction.objectStore('prompts');
    
    // Implement full-text search with filters
    const results = await store.getAll();
    
    return results.filter(prompt => 
      prompt.content.toLowerCase().includes(query.toLowerCase()) &&
      this.matchesFilters(prompt, filters)
    );
  }
}
```

### Agent Mesh

```typescript
interface AgentMeshStructure {
  'services/agents/': {
    'kCore/': 'Orchestrator runtime';
    'kPlanner/': 'Goal decomposition';
    'kExecutor/': 'Task runners';
    'kReviewer/': 'QA and test evaluation';
    'kSentinel/': 'Monitoring and intrusion detection';
    'kMemory/': 'Memory graph and embedding';
    'kPersona/': 'Persona config and modulation';
    'kBridge/': 'API proxies and adapters';
  };
}

// kCore Orchestrator
class KCoreOrchestrator {
  private agents: Map<string, AgentProxy> = new Map();
  private taskQueue: TaskQueue;
  private scheduler: TaskScheduler;
  
  async orchestrateTask(task: Task): Promise<TaskResult> {
    // Decompose task into subtasks
    const plan = await this.planTask(task);
    
    // Assign subtasks to appropriate agents
    const assignments = await this.assignTasks(plan.subtasks);
    
    // Execute tasks with dependency management
    const results = await this.executePlan(assignments);
    
    // Aggregate and validate results
    return this.aggregateResults(results);
  }
  
  private async planTask(task: Task): Promise<ExecutionPlan> {
    const kPlanner = this.agents.get('kPlanner');
    if (!kPlanner) {
      throw new Error('kPlanner agent not available');
    }
    
    return kPlanner.invoke('decompose', { task });
  }
  
  private async assignTasks(subtasks: SubTask[]): Promise<TaskAssignment[]> {
    const assignments: TaskAssignment[] = [];
    
    for (const subtask of subtasks) {
      const suitableAgents = this.findSuitableAgents(subtask);
      const selectedAgent = this.selectBestAgent(suitableAgents, subtask);
      
      assignments.push({
        subtask,
        agent: selectedAgent,
        priority: subtask.priority,
        dependencies: subtask.dependencies
      });
    }
    
    return assignments;
  }
}

// kMemory Agent
class KMemoryAgent {
  private vectorStore: VectorStore;
  private graphStore: GraphDatabase;
  
  async storeMemory(memory: MemoryRecord): Promise<string> {
    // Generate embeddings
    const embedding = await this.generateEmbedding(memory.content);
    
    // Store in vector database
    const vectorId = await this.vectorStore.insert({
      id: memory.id,
      embedding,
      metadata: memory.metadata
    });
    
    // Store relationships in graph
    if (memory.relationships) {
      await this.graphStore.createRelationships(memory.id, memory.relationships);
    }
    
    return vectorId;
  }
  
  async searchMemory(query: string, filters?: MemoryFilters): Promise<MemoryRecord[]> {
    // Generate query embedding
    const queryEmbedding = await this.generateEmbedding(query);
    
    // Search vector store
    const vectorResults = await this.vectorStore.search(queryEmbedding, {
      limit: filters?.limit || 10,
      threshold: filters?.threshold || 0.7
    });
    
    // Enhance with graph relationships
    const enhancedResults = await Promise.all(
      vectorResults.map(result => this.enhanceWithRelationships(result))
    );
    
    return enhancedResults;
  }
}
```

### Artifact Manager

```typescript
interface ArtifactManagerStructure {
  'services/artifact_manager/': {
    'ArtifactIndex.ts': 'Metadata and hash database';
    'UploadHandler.ts': 'File and blob intake';
    'PreviewRenderer.tsx': 'Markdown, image, and PDF rendering';
    'ShareLink.ts': 'Temporary signed URLs';
    'SignatureVerifier.ts': 'Blockchain-backed checksum (planned)';
  };
}

class ArtifactManager {
  private storage: ObjectStorage;
  private index: ArtifactIndex;
  private previewRenderer: PreviewRenderer;
  
  async uploadArtifact(
    file: File | Buffer,
    metadata: ArtifactMetadata
  ): Promise<ArtifactRecord> {
    // Generate content hash
    const contentHash = await this.generateHash(file);
    
    // Check for duplicates
    const existingArtifact = await this.index.findByHash(contentHash);
    if (existingArtifact) {
      return existingArtifact;
    }
    
    // Upload to storage
    const storageKey = await this.storage.upload(file, {
      contentType: metadata.contentType,
      encryption: metadata.encrypted
    });
    
    // Create artifact record
    const artifact: ArtifactRecord = {
      id: generateUUID(),
      name: metadata.name,
      contentType: metadata.contentType,
      size: file instanceof File ? file.size : file.length,
      contentHash,
      storageKey,
      uploadedAt: new Date().toISOString(),
      uploadedBy: metadata.uploadedBy,
      tags: metadata.tags || [],
      encrypted: metadata.encrypted || false
    };
    
    // Index artifact
    await this.index.store(artifact);
    
    return artifact;
  }
  
  async generatePreview(artifactId: string): Promise<PreviewData> {
    const artifact = await this.index.get(artifactId);
    if (!artifact) {
      throw new Error(`Artifact ${artifactId} not found`);
    }
    
    // Download content
    const content = await this.storage.download(artifact.storageKey);
    
    // Generate preview based on content type
    return this.previewRenderer.render(content, artifact.contentType);
  }
  
  async createShareLink(
    artifactId: string,
    options: ShareLinkOptions
  ): Promise<string> {
    const artifact = await this.index.get(artifactId);
    if (!artifact) {
      throw new Error(`Artifact ${artifactId} not found`);
    }
    
    // Generate signed URL
    const signedUrl = await this.storage.generateSignedUrl(
      artifact.storageKey,
      {
        expiresIn: options.expiresIn || 3600, // 1 hour default
        permissions: options.permissions || ['read']
      }
    );
    
    return signedUrl;
  }
}
```

### Config and Vault System

```typescript
interface ConfigVaultStructure {
  'config/': {
    'system_config.json': 'Global toggles, logging, themes';
    'user_config.json': 'Local overrides, profile info';
    'vault/': {
      'secrets.db': 'AES-encrypted SQLite store';
      'policy.json': 'Access rules and TTL config';
    };
  };
}

class SecureVault {
  private db: Database;
  private encryption: EncryptionService;
  private policy: VaultPolicy;
  
  async storeSecret(
    key: string,
    value: string,
    metadata: SecretMetadata
  ): Promise<void> {
    // Encrypt value
    const encryptedValue = await this.encryption.encrypt(value);
    
    // Store with metadata
    await this.db.run(`
      INSERT INTO secrets (key, encrypted_value, metadata, created_at, expires_at)
      VALUES (?, ?, ?, ?, ?)
    `, [
      key,
      encryptedValue,
      JSON.stringify(metadata),
      new Date().toISOString(),
      metadata.expiresAt
    ]);
  }
  
  async retrieveSecret(key: string, requestContext: RequestContext): Promise<string> {
    // Check access policy
    await this.policy.checkAccess(key, requestContext);
    
    // Retrieve from database
    const row = await this.db.get(`
      SELECT encrypted_value, expires_at FROM secrets 
      WHERE key = ? AND (expires_at IS NULL OR expires_at > datetime('now'))
    `, [key]);
    
    if (!row) {
      throw new Error(`Secret ${key} not found or expired`);
    }
    
    // Decrypt and return
    return this.encryption.decrypt(row.encrypted_value);
  }
  
  async rotateKeys(): Promise<void> {
    // Generate new encryption key
    const newKey = await this.encryption.generateKey();
    
    // Re-encrypt all secrets with new key
    const secrets = await this.db.all('SELECT id, encrypted_value FROM secrets');
    
    for (const secret of secrets) {
      const decryptedValue = await this.encryption.decrypt(secret.encrypted_value);
      const reencryptedValue = await this.encryption.encryptWithKey(decryptedValue, newKey);
      
      await this.db.run(
        'UPDATE secrets SET encrypted_value = ? WHERE id = ?',
        [reencryptedValue, secret.id]
      );
    }
    
    // Update active key
    await this.encryption.setActiveKey(newKey);
  }
}
```

## Core Protocols and Service APIs

### WebSocket Message Structure

```typescript
interface WebSocketMessage {
  type: MessageType;
  agent?: string;
  taskId?: string;
  payload: any;
  timestamp: string;
  correlationId?: string;
}

type MessageType = 
  | 'AGENT_RESULT'
  | 'AGENT_ERROR'
  | 'TASK_PROGRESS'
  | 'SYSTEM_STATUS'
  | 'USER_NOTIFICATION'
  | 'CONFIG_UPDATE'
  | 'HEARTBEAT';

// Example messages
const exampleMessages: WebSocketMessage[] = [
  {
    type: 'AGENT_RESULT',
    agent: 'kExecutor:webscraper',
    taskId: 'xyz123',
    payload: {
      status: 'success',
      data: { url: 'https://example.com', content: '...' }
    },
    timestamp: '2025-06-20T23:05:00Z',
    correlationId: 'user-request-456'
  },
  {
    type: 'TASK_PROGRESS',
    agent: 'kPlanner',
    taskId: 'abc789',
    payload: {
      progress: 0.75,
      currentStep: 'Analyzing requirements',
      estimatedCompletion: '2025-06-20T23:10:00Z'
    },
    timestamp: '2025-06-20T23:05:30Z'
  },
  {
    type: 'SYSTEM_STATUS',
    payload: {
      activeAgents: 5,
      queuedTasks: 2,
      systemLoad: 0.45,
      memoryUsage: 0.62
    },
    timestamp: '2025-06-20T23:06:00Z'
  }
];
```

### Internal Service APIs

```typescript
// Service API client
class ServiceAPIClient {
  private baseUrl: string;
  private auth: AuthenticationService;
  
  // Agent management
  async submitTask(task: TaskRequest): Promise<TaskResponse> {
    return this.post('/agent/task', task);
  }
  
  async getAgentStatus(): Promise<AgentStatusResponse> {
    return this.get('/agent/status');
  }
  
  // Vault operations
  async encryptData(data: string): Promise<EncryptionResponse> {
    return this.post('/vault/encrypt', { data });
  }
  
  async decryptData(encryptedData: string): Promise<DecryptionResponse> {
    return this.post('/vault/decrypt', { encryptedData });
  }
  
  // Artifact management
  async uploadArtifact(file: File, metadata: ArtifactMetadata): Promise<ArtifactResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));
    
    return this.postFormData('/artifact/upload', formData);
  }
  
  async getArtifact(id: string): Promise<ArtifactRecord> {
    return this.get(`/artifact/${id}`);
  }
  
  // Memory operations
  async searchMemory(query: string, filters?: MemoryFilters): Promise<MemorySearchResponse> {
    const params = new URLSearchParams({ q: query });
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        params.append(key, String(value));
      });
    }
    
    return this.get(`/memory/search?${params.toString()}`);
  }
  
  // Planning
  async generatePlan(goal: string, context?: PlanningContext): Promise<ExecutionPlan> {
    return this.post('/planner/plan', { goal, context });
  }
  
  private async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': await this.auth.getAuthHeader()
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  private async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        'Authorization': await this.auth.getAuthHeader()
      }
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }
    
    return response.json();
  }
}
```

## Deployment Models

### Localhost (Developer Mode)

```typescript
interface LocalhostDeployment {
  description: 'All services and agents run on a single machine';
  stack: {
    database: 'SQLite';
    llm: 'Ollama';
    api: 'FastAPI';
    frontend: 'React dev server';
  };
  urls: {
    frontend: 'http://localhost:3000';
    api: 'http://localhost:8000';
    websocket: 'ws://localhost:8000/ws';
  };
  setup: {
    requirements: ['Node.js 18+', 'Python 3.9+', 'Docker (optional)'];
    installation: string[];
  };
}

const localhostSetup: LocalhostDeployment['setup']['installation'] = [
  'git clone https://github.com/kind-ai/kai-cd.git',
  'cd kai-cd',
  'npm install',
  'pip install -r requirements.txt',
  'npm run dev',
  'python -m uvicorn main:app --reload'
];
```

### Home Server (Self-Hosted Node)

```typescript
interface HomeServerDeployment {
  description: 'Docker Compose with shared volumes';
  architecture: {
    containers: {
      'kai-frontend': 'React app with Nginx';
      'kai-api': 'FastAPI backend';
      'kai-agents': 'Agent mesh runtime';
      'postgres': 'Primary database';
      'redis': 'Cache and pub/sub';
      'ollama': 'Local LLM server';
    };
    volumes: {
      'kai-data': 'Persistent application data';
      'kai-models': 'LLM models storage';
      'kai-artifacts': 'File uploads and artifacts';
    };
    networks: {
      'kai-internal': 'Internal service communication';
      'kai-external': 'External access (optional)';
    };
  };
  features: {
    tunnel: 'Optional public tunnel (ngrok, tailscale)';
    ssl: 'Let\'s Encrypt certificates';
    backup: 'Automated data backup';
    monitoring: 'Prometheus + Grafana';
  };
}

// Docker Compose example
const dockerComposeConfig = `
version: '3.8'
services:
  kai-frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - API_URL=http://kai-api:8000
    networks:
      - kai-internal

  kai-api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/kai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    networks:
      - kai-internal

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=kai
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - kai-data:/var/lib/postgresql/data
    networks:
      - kai-internal

  redis:
    image: redis:7
    networks:
      - kai-internal

  ollama:
    image: ollama/ollama
    volumes:
      - kai-models:/root/.ollama
    networks:
      - kai-internal

volumes:
  kai-data:
  kai-models:
  kai-artifacts:

networks:
  kai-internal:
    driver: bridge
`;
```

### Multi-Tenant Cloud

```typescript
interface CloudDeployment {
  orchestration: 'Kubernetes or Nomad';
  infrastructure: {
    compute: 'Auto-scaling node pools';
    storage: 'S3, Postgres, Redis in HA mode';
    networking: 'Load balancers, service mesh';
    monitoring: 'Prometheus, Grafana, Jaeger';
  };
  features: {
    tenantIsolation: boolean;
    autoScaling: boolean;
    multiRegion: boolean;
    disasterRecovery: boolean;
    compliance: string[];
  };
  adminUI: 'Central admin UI for tenant control';
}

// Kubernetes deployment example
const kubernetesManifest = `
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kai-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kai-api
  template:
    metadata:
      labels:
        app: kai-api
    spec:
      containers:
      - name: kai-api
        image: kai/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: kai-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: kai-api-service
spec:
  selector:
    app: kai-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
`;
```

### Federated Mesh (Planned)

```typescript
interface FederatedMeshDeployment {
  description: 'Peered mesh of kCore nodes';
  features: {
    peerDiscovery: 'mDNS + KLP protocol';
    consensusMechanism: 'Raft or PBFT';
    dataSync: 'IPFS or custom RAG-2';
    loadDistribution: 'Dynamic task routing';
  };
  governance: {
    nodeVoting: boolean;
    resourceSharing: boolean;
    trustManagement: boolean;
  };
  protocols: {
    communication: 'KLP over multiple transports';
    consensus: 'Byzantine fault tolerant';
    synchronization: 'Vector clocks + CRDTs';
  };
}
```

## Security Components

```typescript
interface SecurityInfrastructure {
  vault: VaultSecurity;
  authentication: AuthenticationSecurity;
  communication: CommunicationSecurity;
  runtime: RuntimeSecurity;
  monitoring: SecurityMonitoring;
}

interface VaultSecurity {
  encryption: 'AES-256 + PBKDF2 local, or KMS cloud mode';
  keyRotation: 'Automatic with configurable intervals';
  accessControl: 'Role-based with audit logging';
  backup: 'Encrypted backup with recovery procedures';
}

interface AuthenticationSecurity {
  userAuth: 'JWT / OAuth2 for user tokens';
  agentAuth: 'Ed25519 signatures for agent communication';
  sessionManagement: 'Secure session handling with refresh tokens';
  multiFactorAuth: 'TOTP and WebAuthn support';
}

interface CommunicationSecurity {
  transport: 'TLS 1.3 for all external communication';
  internal: 'mTLS for service-to-service communication';
  messageIntegrity: 'Ed25519 signatures via KLP';
  encryption: 'End-to-end encryption for sensitive data';
}

interface RuntimeSecurity {
  sandboxing: 'WebWorker or nsjail-based plugin isolation';
  codeExecution: 'Sandboxed execution environments';
  resourceLimits: 'CPU, memory, and network constraints';
  permissionModel: 'Capability-based security';
}

interface SecurityMonitoring {
  sentinel: 'kSentinel agent for threat detection';
  features: {
    rateLimiting: boolean;
    anomalyDetection: boolean;
    executionTracing: boolean;
    resourceMonitoring: boolean;
  };
  alerting: 'Real-time security alerts and notifications';
  forensics: 'Detailed audit trails and investigation tools';
}
```

## System Observability

```typescript
interface ObservabilityStack {
  logging: {
    aggregation: 'Grafana + Loki';
    structured: 'JSON formatted logs';
    correlation: 'Trace ID propagation';
  };
  metrics: {
    collection: 'Prometheus';
    visualization: 'Grafana dashboards';
    alerting: 'AlertManager integration';
  };
  tracing: {
    distributed: 'Jaeger';
    sampling: 'Configurable sampling rates';
    correlation: 'Cross-service request tracing';
  };
  debugging: {
    local: 'SQLite log adapter for development';
    remote: 'Centralized logging for production';
    realtime: 'Live log streaming';
  };
}

class ObservabilityManager {
  private logger: Logger;
  private metrics: MetricsCollector;
  private tracer: Tracer;
  
  async logEvent(event: SystemEvent): Promise<void> {
    // Structured logging with correlation
    await this.logger.info({
      message: event.message,
      level: event.level,
      timestamp: event.timestamp,
      service: event.service,
      traceId: event.traceId,
      metadata: event.metadata
    });
  }
  
  recordMetric(name: string, value: number, labels?: Record<string, string>): void {
    this.metrics.record(name, value, labels);
  }
  
  startTrace(operationName: string): Span {
    return this.tracer.startSpan(operationName);
  }
  
  async getSystemHealth(): Promise<SystemHealthStatus> {
    const metrics = await this.metrics.getCurrentMetrics();
    const activeTraces = await this.tracer.getActiveTraces();
    
    return {
      status: this.calculateOverallHealth(metrics),
      services: this.getServiceHealthStatus(metrics),
      performance: this.getPerformanceMetrics(metrics),
      errors: this.getErrorSummary(activeTraces)
    };
  }
}
```

## Naming Conventions & Structure

```typescript
interface NamingConventions {
  serviceRoutes: 'Follow pattern: /service_name/function';
  agentIDs: 'Follow pattern: kClass:name (e.g., kExecutor:webscraper)';
  logging: 'All internal logs tagged with task ID and plan ID';
  configuration: 'Config file overrides resolved via deep merge';
  files: 'Use kebab-case for file names, PascalCase for classes';
  apis: 'RESTful conventions with clear resource naming';
}

// Examples
const namingExamples = {
  serviceRoutes: [
    '/agent/task',
    '/memory/search',
    '/artifact/upload',
    '/vault/encrypt'
  ],
  agentIDs: [
    'kCore:orchestrator',
    'kPlanner:main',
    'kExecutor:webscraper',
    'kMemory:semantic-search',
    'kSentinel:security-monitor'
  ],
  logTags: {
    taskId: 'task-uuid-12345',
    planId: 'plan-uuid-67890',
    agentId: 'kExecutor:webscraper',
    userId: 'user-uuid-abcde'
  }
};
```

## Implementation Status

- **Core Architecture**: Specification complete
- **Agent Mesh Runtime**: Framework defined
- **API Gateway**: Interface designed
- **Security Infrastructure**: Protocols specified
- **Deployment Models**: All models documented
- **Observability Stack**: Monitoring framework planned
- **Reference Implementation**: Active development in Kai-CD

## Migration Path

For existing Kai-CD to kOS evolution:
1. **Phase 1**: Implement Agent Mesh Runtime alongside current service architecture
2. **Phase 2**: Migrate existing services to KLP communication protocol
3. **Phase 3**: Deploy federated mesh capabilities
4. **Phase 4**: Full kOS ecosystem integration

## Changelog

- **2024-12-28**: Comprehensive service architecture specification with TypeScript implementations
- **2025-06-21**: Initial full version of complete service architecture, agents, protocols, and deployment modes (legacy reference) 