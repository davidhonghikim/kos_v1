---
title: "kAI API and Socket Services"
version: "1.0.0"
last_updated: "2024-12-19"
status: "Specification"
type: "API Service"
tags: ["api", "websocket", "real-time", "multi-agent", "authentication"]
related_files: 
  - "28_agent-message-bus-event-pipeline.md"
  - "29_kind-link-protocol-specification.md"
  - "30_device-agent-bootstrap-protocol.md"
  - "32_agent-communication-protocols.md"
---

# kAI API and Socket Services

## Agent Context

**Primary Function**: Central API and WebSocket interface for kAI multi-agent system enabling real-time human-AI interaction, secure task orchestration, and agent lifecycle management.

**Integration Points**: 
- Client applications (web, desktop, mobile, CLI)
- Real-time agent coordination and communication
- File upload/download and blob storage
- Authentication and session management
- Task queue and background processing

**Dependencies**: FastAPI, WebSocket infrastructure, OAuth2/JWT, Celery, Redis, PostgreSQL, Qdrant, S3

## Overview

The kAI API and Socket Services provide the foundational interface layer for all client interactions with the kAI multi-agent system. This service enables secure authentication, real-time WebSocket communication, RESTful API access, file management, and comprehensive agent lifecycle operations.

## Core Technologies

- **Framework**: FastAPI (REST + async WebSocket support)
- **WebSockets**: `fastapi-websockets`, `socket.io`, fallback to `sse-starlette`
- **Authentication**: OAuth2, JWT, optional passwordless login with magic link
- **Task Queue**: Celery with Redis backend for asynchronous background tasks
- **Persistence**: PostgreSQL for user, agent, and session data
- **Storage**: Qdrant (vectors), Redis (cache), S3 (blobs), Local Filesystem

## API Architecture

### Base API Structure

```typescript
interface APIRoutes {
  auth: AuthRoutes;
  agents: AgentRoutes;
  commands: CommandRoutes;
  files: FileRoutes;
  config: ConfigRoutes;
  services: ServiceRoutes;
  websocket: WebSocketRoutes;
}

interface AuthRoutes {
  'POST /api/auth/login': (credentials: LoginCredentials) => Promise<AuthResponse>;
  'POST /api/auth/register': (userData: UserRegistration) => Promise<AuthResponse>;
  'POST /api/auth/logout': () => Promise<void>;
  'GET /api/auth/session': () => Promise<SessionInfo>;
  'POST /api/auth/verify-magic': (token: string) => Promise<AuthResponse>;
}

interface AgentRoutes {
  'GET /api/agents': () => Promise<Agent[]>;
  'POST /api/agents': (config: AgentConfig) => Promise<Agent>;
  'PUT /api/agents/:id': (id: string, config: Partial<AgentConfig>) => Promise<Agent>;
  'GET /api/agents/:id/status': (id: string) => Promise<AgentStatus>;
  'POST /api/agents/:id/restart': (id: string) => Promise<void>;
  'DELETE /api/agents/:id': (id: string) => Promise<void>;
}

interface CommandRoutes {
  'POST /api/agents/:id/command': (id: string, command: AgentCommand) => Promise<CommandResult>;
  'POST /api/agents/:id/upload': (id: string, file: File) => Promise<UploadResult>;
  'POST /api/agents/:id/stream-prompt': (id: string, prompt: StreamPrompt) => Promise<StreamResponse>;
  'POST /api/agents/:id/task': (id: string, task: TaskRequest) => Promise<TaskResponse>;
  'GET /api/agents/:id/logs': (id: string, options: LogOptions) => Promise<LogEntry[]>;
  'GET /api/tasks/:id/status': (id: string) => Promise<TaskStatus>;
}
```

### Authentication System

```typescript
class AuthenticationService {
  private jwtService: JWTService;
  private userRepository: UserRepository;
  private sessionManager: SessionManager;

  constructor() {
    this.jwtService = new JWTService();
    this.userRepository = new UserRepository();
    this.sessionManager = new SessionManager();
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const user = await this.userRepository.findByEmail(credentials.email);
    
    if (!user || !await this.verifyPassword(credentials.password, user.passwordHash)) {
      throw new UnauthorizedError('Invalid credentials');
    }

    const session = await this.sessionManager.createSession(user.id);
    const accessToken = await this.jwtService.generateAccessToken(user, session);
    const refreshToken = await this.jwtService.generateRefreshToken(user, session);

    return {
      accessToken,
      refreshToken,
      user: this.sanitizeUser(user),
      expiresAt: new Date(Date.now() + 3600000) // 1 hour
    };
  }

  async verifyToken(token: string): Promise<TokenPayload> {
    try {
      const payload = await this.jwtService.verifyToken(token);
      const session = await this.sessionManager.getSession(payload.sessionId);
      
      if (!session || session.expiresAt < new Date()) {
        throw new UnauthorizedError('Session expired');
      }

      return payload;
    } catch (error) {
      throw new UnauthorizedError('Invalid token');
    }
  }

  async logout(sessionId: string): Promise<void> {
    await this.sessionManager.invalidateSession(sessionId);
  }
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
  expiresAt: Date;
}

interface TokenPayload {
  userId: string;
  sessionId: string;
  permissions: string[];
  iat: number;
  exp: number;
}
```

### WebSocket Event System

```typescript
class WebSocketManager {
  private connections: Map<string, WebSocketConnection>;
  private eventHandlers: Map<string, EventHandler>;
  private messageQueue: MessageQueue;

  constructor() {
    this.connections = new Map();
    this.eventHandlers = new Map();
    this.messageQueue = new MessageQueue();
    this.setupEventHandlers();
  }

  async handleConnection(ws: WebSocket, agentId: string, userId: string): Promise<void> {
    const connectionId = generateUUID();
    const connection = new WebSocketConnection(ws, connectionId, agentId, userId);
    
    this.connections.set(connectionId, connection);
    
    // Set up message handlers
    ws.on('message', (data) => this.handleMessage(connectionId, data));
    ws.on('close', () => this.handleDisconnection(connectionId));
    ws.on('error', (error) => this.handleError(connectionId, error));

    // Send initial status
    await this.sendStatusUpdate(connectionId, agentId);
  }

  private async handleMessage(connectionId: string, data: string): Promise<void> {
    const connection = this.connections.get(connectionId);
    if (!connection) return;

    try {
      const message = JSON.parse(data) as WebSocketMessage;
      const handler = this.eventHandlers.get(message.type);
      
      if (handler) {
        await handler.handle(message, connection);
      } else {
        await this.sendError(connectionId, `Unknown message type: ${message.type}`);
      }
    } catch (error) {
      await this.sendError(connectionId, `Invalid message format: ${(error as Error).message}`);
    }
  }

  private setupEventHandlers(): void {
    this.eventHandlers.set('command', new CommandHandler());
    this.eventHandlers.set('upload', new UploadHandler());
    this.eventHandlers.set('heartbeat', new HeartbeatHandler());
    this.eventHandlers.set('stream_prompt', new StreamPromptHandler());
  }

  async broadcastToAgent(agentId: string, event: WebSocketEvent): Promise<void> {
    const agentConnections = Array.from(this.connections.values())
      .filter(conn => conn.agentId === agentId);

    await Promise.all(
      agentConnections.map(conn => this.sendEvent(conn.id, event))
    );
  }

  private async sendEvent(connectionId: string, event: WebSocketEvent): Promise<void> {
    const connection = this.connections.get(connectionId);
    if (connection && connection.ws.readyState === WebSocket.OPEN) {
      connection.ws.send(JSON.stringify(event));
    }
  }
}

interface WebSocketMessage {
  type: string;
  data: unknown;
  timestamp: number;
}

interface WebSocketEvent {
  type: 'status_update' | 'log' | 'stream_chunk' | 'error' | 'task_complete';
  data: unknown;
  timestamp: number;
}

class CommandHandler implements EventHandler {
  async handle(message: WebSocketMessage, connection: WebSocketConnection): Promise<void> {
    const command = message.data as AgentCommand;
    
    // Validate command
    if (!this.validateCommand(command)) {
      throw new Error('Invalid command format');
    }

    // Execute command
    const result = await this.executeCommand(connection.agentId, command);
    
    // Send response
    await connection.send({
      type: 'command_result',
      data: result,
      timestamp: Date.now()
    });
  }

  private validateCommand(command: AgentCommand): boolean {
    return command && typeof command.command === 'string' && command.params;
  }

  private async executeCommand(agentId: string, command: AgentCommand): Promise<CommandResult> {
    // Implementation would interact with agent management system
    return {
      success: true,
      result: 'Command executed successfully',
      timestamp: Date.now()
    };
  }
}
```

### Agent Management API

```typescript
class AgentManagementService {
  private agentRegistry: AgentRegistry;
  private agentLifecycle: AgentLifecycle;
  private permissionService: PermissionService;

  async createAgent(config: AgentConfig, userId: string): Promise<Agent> {
    // Validate permissions
    await this.permissionService.checkPermission(userId, 'agent.create');
    
    // Validate configuration
    await this.validateAgentConfig(config);
    
    // Create agent
    const agent = await this.agentLifecycle.createAgent(config);
    
    // Register agent
    await this.agentRegistry.registerAgent(agent);
    
    return agent;
  }

  async getAgentStatus(agentId: string, userId: string): Promise<AgentStatus> {
    await this.permissionService.checkPermission(userId, 'agent.read', agentId);
    
    const agent = await this.agentRegistry.getAgent(agentId);
    if (!agent) {
      throw new NotFoundError(`Agent ${agentId} not found`);
    }

    return {
      id: agent.id,
      status: agent.status,
      lastSeen: agent.lastSeen,
      health: await this.getAgentHealth(agentId),
      metrics: await this.getAgentMetrics(agentId),
      configuration: agent.configuration
    };
  }

  async restartAgent(agentId: string, userId: string): Promise<void> {
    await this.permissionService.checkPermission(userId, 'agent.restart', agentId);
    
    const agent = await this.agentRegistry.getAgent(agentId);
    if (!agent) {
      throw new NotFoundError(`Agent ${agentId} not found`);
    }

    await this.agentLifecycle.restartAgent(agentId);
  }

  async deleteAgent(agentId: string, userId: string): Promise<void> {
    await this.permissionService.checkPermission(userId, 'agent.delete', agentId);
    
    // Stop agent gracefully
    await this.agentLifecycle.stopAgent(agentId);
    
    // Remove from registry
    await this.agentRegistry.unregisterAgent(agentId);
    
    // Clean up resources
    await this.cleanupAgentResources(agentId);
  }

  private async validateAgentConfig(config: AgentConfig): Promise<void> {
    const schema = await this.getAgentConfigSchema();
    const validation = await this.validateSchema(config, schema);
    
    if (!validation.valid) {
      throw new ValidationError(`Invalid agent configuration: ${validation.errors.join(', ')}`);
    }
  }

  private async getAgentHealth(agentId: string): Promise<HealthStatus> {
    // Implementation would check agent health metrics
    return {
      status: 'healthy',
      uptime: 3600,
      memoryUsage: 0.45,
      cpuUsage: 0.23,
      responseTime: 150
    };
  }
}

interface AgentConfig {
  name: string;
  type: string;
  capabilities: string[];
  configuration: Record<string, unknown>;
  resources: ResourceRequirements;
}

interface ResourceRequirements {
  memory: string;
  cpu: string;
  storage: string;
  gpu?: boolean;
}

interface AgentStatus {
  id: string;
  status: 'running' | 'stopped' | 'error' | 'starting';
  lastSeen: Date;
  health: HealthStatus;
  metrics: AgentMetrics;
  configuration: Record<string, unknown>;
}

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  uptime: number;
  memoryUsage: number;
  cpuUsage: number;
  responseTime: number;
}
```

### File Management System

```typescript
class FileManagementService {
  private storageBackend: StorageBackend;
  private virusScanner: VirusScanner;
  private metadataStore: MetadataStore;

  async uploadFile(file: File, userId: string, agentId?: string): Promise<UploadResult> {
    // Validate file
    await this.validateFile(file);
    
    // Scan for viruses
    const scanResult = await this.virusScanner.scan(file);
    if (!scanResult.clean) {
      throw new SecurityError(`File contains malware: ${scanResult.threats.join(', ')}`);
    }

    // Generate file ID and metadata
    const fileId = generateUUID();
    const metadata: FileMetadata = {
      id: fileId,
      originalName: file.name,
      size: file.size,
      mimeType: file.type,
      uploadedBy: userId,
      uploadedAt: new Date(),
      agentId,
      checksum: await this.calculateChecksum(file)
    };

    // Store file
    const storagePath = await this.storageBackend.store(file, fileId);
    
    // Save metadata
    await this.metadataStore.save(fileId, { ...metadata, storagePath });

    return {
      fileId,
      url: this.generateFileUrl(fileId),
      metadata
    };
  }

  async downloadFile(fileId: string, userId: string): Promise<FileDownload> {
    const metadata = await this.metadataStore.get(fileId);
    if (!metadata) {
      throw new NotFoundError(`File ${fileId} not found`);
    }

    // Check permissions
    await this.checkFileAccess(fileId, userId);

    const fileStream = await this.storageBackend.retrieve(metadata.storagePath);
    
    return {
      stream: fileStream,
      metadata,
      headers: {
        'Content-Type': metadata.mimeType,
        'Content-Length': metadata.size.toString(),
        'Content-Disposition': `attachment; filename="${metadata.originalName}"`
      }
    };
  }

  async deleteFile(fileId: string, userId: string): Promise<void> {
    const metadata = await this.metadataStore.get(fileId);
    if (!metadata) {
      throw new NotFoundError(`File ${fileId} not found`);
    }

    // Check permissions
    await this.checkFileAccess(fileId, userId, 'delete');

    // Delete from storage
    await this.storageBackend.delete(metadata.storagePath);
    
    // Remove metadata
    await this.metadataStore.delete(fileId);
  }

  private async validateFile(file: File): Promise<void> {
    const maxSize = 100 * 1024 * 1024; // 100MB
    const allowedTypes = [
      'text/plain',
      'application/pdf',
      'image/jpeg',
      'image/png',
      'application/json'
    ];

    if (file.size > maxSize) {
      throw new ValidationError(`File size exceeds maximum allowed size of ${maxSize} bytes`);
    }

    if (!allowedTypes.includes(file.type)) {
      throw new ValidationError(`File type ${file.type} is not allowed`);
    }
  }
}

interface FileMetadata {
  id: string;
  originalName: string;
  size: number;
  mimeType: string;
  uploadedBy: string;
  uploadedAt: Date;
  agentId?: string;
  checksum: string;
  storagePath?: string;
}

interface UploadResult {
  fileId: string;
  url: string;
  metadata: FileMetadata;
}

interface FileDownload {
  stream: ReadableStream;
  metadata: FileMetadata;
  headers: Record<string, string>;
}
```

## Security & Permissions

```typescript
class SecurityManager {
  private roleBasedAccess: RoleBasedAccessControl;
  private rateLimiter: RateLimiter;
  private auditLogger: AuditLogger;

  async checkPermission(userId: string, action: string, resource?: string): Promise<boolean> {
    const user = await this.getUserWithRoles(userId);
    const hasPermission = await this.roleBasedAccess.checkPermission(user.roles, action, resource);
    
    // Log access attempt
    await this.auditLogger.log({
      userId,
      action,
      resource,
      granted: hasPermission,
      timestamp: new Date()
    });

    return hasPermission;
  }

  async enforceRateLimit(userId: string, endpoint: string): Promise<void> {
    const isAllowed = await this.rateLimiter.checkLimit(userId, endpoint);
    
    if (!isAllowed) {
      throw new RateLimitError('Rate limit exceeded');
    }
  }

  async validateAPIKey(apiKey: string): Promise<APIKeyInfo> {
    const keyInfo = await this.getAPIKeyInfo(apiKey);
    
    if (!keyInfo || keyInfo.expiresAt < new Date()) {
      throw new UnauthorizedError('Invalid or expired API key');
    }

    if (!keyInfo.active) {
      throw new UnauthorizedError('API key is disabled');
    }

    return keyInfo;
  }
}

interface PermissionMatrix {
  user: {
    'agent.create': boolean;
    'agent.read': boolean;
    'agent.restart': boolean;
    'file.upload': boolean;
    'file.download': boolean;
  };
  developer: {
    'agent.create': boolean;
    'agent.read': boolean;
    'agent.restart': boolean;
    'agent.delete': boolean;
    'file.upload': boolean;
    'file.download': boolean;
    'config.read': boolean;
  };
  admin: {
    'agent.*': boolean;
    'file.*': boolean;
    'config.*': boolean;
    'user.*': boolean;
    'system.*': boolean;
  };
}
```

## Task Queue & Background Processing

```typescript
class TaskQueueService {
  private celeryApp: CeleryApp;
  private taskRegistry: TaskRegistry;
  private resultBackend: ResultBackend;

  async enqueueTask(taskType: string, payload: unknown, options?: TaskOptions): Promise<string> {
    const taskId = generateUUID();
    const task: Task = {
      id: taskId,
      type: taskType,
      payload,
      status: 'pending',
      createdAt: new Date(),
      options: options || {}
    };

    await this.celeryApp.send_task(taskType, [payload], {
      task_id: taskId,
      ...options
    });

    return taskId;
  }

  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    const result = await this.resultBackend.get(taskId);
    
    if (!result) {
      throw new NotFoundError(`Task ${taskId} not found`);
    }

    return {
      id: taskId,
      status: result.status,
      result: result.result,
      error: result.error,
      progress: result.progress,
      startedAt: result.startedAt,
      completedAt: result.completedAt
    };
  }

  registerTaskHandler(taskType: string, handler: TaskHandler): void {
    this.taskRegistry.register(taskType, handler);
  }
}

interface Task {
  id: string;
  type: string;
  payload: unknown;
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: Date;
  options: TaskOptions;
}

interface TaskOptions {
  priority?: number;
  delay?: number;
  retries?: number;
  timeout?: number;
}

interface TaskStatus {
  id: string;
  status: string;
  result?: unknown;
  error?: string;
  progress?: number;
  startedAt?: Date;
  completedAt?: Date;
}
```

## Related Documentation

- **[Agent Message Bus & Event Pipeline](28_agent-message-bus-event-pipeline.md)** - Message routing infrastructure
- **[Kind Link Protocol Specification](29_kind-link-protocol-specification.md)** - Core communication protocol
- **[Device Agent Bootstrap Protocol](30_device-agent-bootstrap-protocol.md)** - Agent initialization
- **[Agent Communication Protocols](32_agent-communication-protocols.md)** - Communication patterns

## Implementation Status

- ✅ API architecture specification
- ✅ Authentication and authorization system
- ✅ WebSocket event handling
- ✅ Agent management interfaces
- ✅ File upload/download system
- 🔄 Task queue integration
- 🔄 Rate limiting and security
- ⏳ Monitoring and metrics
- ⏳ API documentation generation 