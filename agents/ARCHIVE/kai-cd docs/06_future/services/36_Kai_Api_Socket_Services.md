---
title: "kAI API and Socket Services"
description: "Comprehensive architecture for kAI API and real-time WebSocket services enabling multi-agent coordination and human-AI interaction"
version: "2.1.0"
last_updated: "2024-12-28"
category: "Services"
tags: ["api", "websockets", "real-time", "multi-agent", "coordination"]
author: "kAI Development Team"
status: "active"
---

# kAI API and Socket Services

## Agent Context
This document defines the complete architecture, routes, data contracts, and implementation layers of the kAI (Kind AI) API and real-time WebSocket services. These services provide the central interface for real-time multi-agent coordination, human-AI interaction, secure task orchestration, and agent lifecycle management through comprehensive REST endpoints, bidirectional WebSocket communication, secure authentication, session management, and advanced features including command handling, file uploads, prompt streaming, and agent registration with full security and performance optimization.

## Overview

The kAI API and Socket Services provide the foundational interface layer that enables seamless interaction between client applications and the multi-agent kAI system through RESTful APIs and real-time WebSocket connections, supporting comprehensive agent management, task orchestration, and real-time communication.

## I. Service Architecture Overview

```typescript
interface ServiceArchitecture {
  restApi: RESTAPILayer;
  webSocketService: WebSocketLayer;
  authenticationSystem: AuthenticationLayer;
  taskQueue: TaskQueueSystem;
  persistence: PersistenceLayer;
  blobStorage: BlobStorageLayer;
}

class KAIAPIService {
  private readonly app: FastAPIApplication;
  private readonly webSocketManager: WebSocketManager;
  private readonly authManager: AuthenticationManager;
  private readonly taskQueue: TaskQueueManager;
  private readonly agentRegistry: AgentRegistry;
  private readonly fileManager: FileManager;
  private readonly configManager: ConfigurationManager;

  constructor(config: KAIAPIConfig) {
    this.app = new FastAPIApplication(config.api);
    this.webSocketManager = new WebSocketManager(config.websocket);
    this.authManager = new AuthenticationManager(config.auth);
    this.taskQueue = new TaskQueueManager(config.tasks);
    this.agentRegistry = new AgentRegistry(config.agents);
    this.fileManager = new FileManager(config.files);
    this.configManager = new ConfigurationManager(config.configuration);
  }

  async initialize(): Promise<ServiceInitializationResult> {
    // Initialize core components
    await this.authManager.initialize();
    await this.taskQueue.initialize();
    await this.agentRegistry.initialize();
    await this.fileManager.initialize();

    // Setup API routes
    this.setupAPIRoutes();
    
    // Setup WebSocket handlers
    this.setupWebSocketHandlers();
    
    // Start health monitoring
    await this.startHealthMonitoring();

    return {
      success: true,
      apiEndpoint: this.app.getBaseURL(),
      webSocketEndpoint: this.webSocketManager.getEndpoint(),
      registeredRoutes: this.app.getRouteCount(),
      activeWebSocketHandlers: this.webSocketManager.getHandlerCount()
    };
  }

  private setupAPIRoutes(): void {
    // Authentication routes
    this.setupAuthRoutes();
    
    // Agent management routes
    this.setupAgentRoutes();
    
    // Task and command routes
    this.setupTaskRoutes();
    
    // File handling routes
    this.setupFileRoutes();
    
    // Configuration routes
    this.setupConfigRoutes();
    
    // Service management routes
    this.setupServiceRoutes();
  }
}
```

## II. REST API Implementation

### A. Authentication Routes

```typescript
class AuthenticationRoutes {
  constructor(
    private authManager: AuthenticationManager,
    private sessionManager: SessionManager
  ) {}

  setupRoutes(app: FastAPIApplication): void {
    // Login endpoint
    app.post('/api/auth/login', async (req: LoginRequest): Promise<LoginResponse> => {
      const validation = await this.validateLoginRequest(req);
      if (!validation.valid) {
        throw new BadRequestError('Invalid login request', validation.errors);
      }

      const authResult = await this.authManager.authenticate(req.credentials);
      if (!authResult.success) {
        throw new UnauthorizedError('Authentication failed');
      }

      const session = await this.sessionManager.createSession(authResult.user);
      const tokens = await this.authManager.generateTokens(authResult.user, session);

      return {
        success: true,
        user: authResult.user,
        tokens,
        session: session.id,
        expiresAt: tokens.accessToken.expiresAt
      };
    });

    // Registration endpoint
    app.post('/api/auth/register', async (req: RegisterRequest): Promise<RegisterResponse> => {
      const validation = await this.validateRegistrationRequest(req);
      if (!validation.valid) {
        throw new BadRequestError('Invalid registration request', validation.errors);
      }

      const registrationResult = await this.authManager.registerUser(req.userData);
      if (!registrationResult.success) {
        throw new ConflictError('Registration failed', registrationResult.reason);
      }

      // Send verification email if required
      if (registrationResult.requiresVerification) {
        await this.sendVerificationEmail(registrationResult.user);
      }

      return {
        success: true,
        user: registrationResult.user,
        requiresVerification: registrationResult.requiresVerification,
        message: 'Registration successful'
      };
    });

    // Session validation
    app.get('/api/auth/session', async (req: AuthenticatedRequest): Promise<SessionResponse> => {
      const session = await this.sessionManager.getSession(req.sessionId);
      if (!session || session.expired) {
        throw new UnauthorizedError('Invalid or expired session');
      }

      return {
        valid: true,
        session,
        user: session.user,
        permissions: session.permissions,
        expiresAt: session.expiresAt
      };
    });

    // Magic link verification
    app.post('/api/auth/verify-magic', async (req: MagicLinkRequest): Promise<MagicLinkResponse> => {
      const verification = await this.authManager.verifyMagicLink(req.token);
      if (!verification.valid) {
        throw new BadRequestError('Invalid or expired magic link');
      }

      const session = await this.sessionManager.createSession(verification.user);
      const tokens = await this.authManager.generateTokens(verification.user, session);

      return {
        success: true,
        user: verification.user,
        tokens,
        session: session.id
      };
    });

    // Logout
    app.post('/api/auth/logout', async (req: AuthenticatedRequest): Promise<LogoutResponse> => {
      await this.sessionManager.invalidateSession(req.sessionId);
      await this.authManager.revokeTokens(req.tokens);

      return {
        success: true,
        message: 'Logout successful'
      };
    });
  }
}
```

### B. Agent Management Routes

```typescript
class AgentManagementRoutes {
  constructor(
    private agentRegistry: AgentRegistry,
    private agentManager: AgentManager,
    private authManager: AuthenticationManager
  ) {}

  setupRoutes(app: FastAPIApplication): void {
    // Get all agents
    app.get('/api/agents', async (req: AuthenticatedRequest): Promise<AgentsListResponse> => {
      await this.validatePermission(req.user, 'agents:read');
      
      const agents = await this.agentRegistry.getUserAgents(req.user.id);
      const agentDetails = await Promise.all(
        agents.map(agent => this.enrichAgentDetails(agent))
      );

      return {
        agents: agentDetails,
        total: agentDetails.length,
        timestamp: new Date().toISOString()
      };
    });

    // Create new agent
    app.post('/api/agents', async (req: CreateAgentRequest): Promise<CreateAgentResponse> => {
      await this.validatePermission(req.user, 'agents:create');
      
      const validation = await this.validateAgentCreationRequest(req);
      if (!validation.valid) {
        throw new BadRequestError('Invalid agent creation request', validation.errors);
      }

      const creationResult = await this.agentManager.createAgent({
        ...req.agentData,
        ownerId: req.user.id
      });

      if (!creationResult.success) {
        throw new InternalServerError('Agent creation failed', creationResult.reason);
      }

      return {
        success: true,
        agent: creationResult.agent,
        agentId: creationResult.agent.id,
        status: creationResult.agent.status
      };
    });

    // Update agent
    app.put('/api/agents/:agentId', async (req: UpdateAgentRequest): Promise<UpdateAgentResponse> => {
      await this.validateAgentAccess(req.user, req.params.agentId, 'write');
      
      const updateResult = await this.agentManager.updateAgent(
        req.params.agentId,
        req.updates
      );

      if (!updateResult.success) {
        throw new InternalServerError('Agent update failed', updateResult.reason);
      }

      return {
        success: true,
        agent: updateResult.agent,
        updatedFields: Object.keys(req.updates)
      };
    });

    // Get agent status
    app.get('/api/agents/:agentId/status', async (req: AgentStatusRequest): Promise<AgentStatusResponse> => {
      await this.validateAgentAccess(req.user, req.params.agentId, 'read');
      
      const status = await this.agentManager.getAgentStatus(req.params.agentId);
      const metrics = await this.agentManager.getAgentMetrics(req.params.agentId);

      return {
        agentId: req.params.agentId,
        status: status.current,
        health: status.health,
        metrics,
        lastUpdate: status.lastUpdate,
        uptime: status.uptime
      };
    });

    // Restart agent
    app.post('/api/agents/:agentId/restart', async (req: RestartAgentRequest): Promise<RestartAgentResponse> => {
      await this.validateAgentAccess(req.user, req.params.agentId, 'manage');
      
      const restartResult = await this.agentManager.restartAgent(
        req.params.agentId,
        req.options
      );

      return {
        success: restartResult.success,
        agentId: req.params.agentId,
        previousStatus: restartResult.previousStatus,
        currentStatus: restartResult.currentStatus,
        restartTime: restartResult.restartTime
      };
    });

    // Delete agent
    app.delete('/api/agents/:agentId', async (req: DeleteAgentRequest): Promise<DeleteAgentResponse> => {
      await this.validateAgentAccess(req.user, req.params.agentId, 'delete');
      
      const deletionResult = await this.agentManager.deleteAgent(
        req.params.agentId,
        req.options
      );

      return {
        success: deletionResult.success,
        agentId: req.params.agentId,
        deletedAt: deletionResult.deletedAt,
        backupCreated: deletionResult.backupCreated
      };
    });
  }

  private async enrichAgentDetails(agent: Agent): Promise<EnrichedAgent> {
    const [status, metrics, capabilities] = await Promise.all([
      this.agentManager.getAgentStatus(agent.id),
      this.agentManager.getAgentMetrics(agent.id),
      this.agentManager.getAgentCapabilities(agent.id)
    ]);

    return {
      ...agent,
      status: status.current,
      health: status.health,
      metrics,
      capabilities,
      lastActivity: status.lastActivity
    };
  }
}
```

### C. Task and Command Routes

```typescript
class TaskCommandRoutes {
  constructor(
    private taskQueue: TaskQueueManager,
    private commandProcessor: CommandProcessor,
    private streamManager: StreamManager
  ) {}

  setupRoutes(app: FastAPIApplication): void {
    // Send command to agent
    app.post('/api/agents/:agentId/command', async (req: CommandRequest): Promise<CommandResponse> => {
      await this.validateAgentAccess(req.user, req.params.agentId, 'command');
      
      const command = await this.commandProcessor.createCommand({
        agentId: req.params.agentId,
        command: req.command,
        parameters: req.parameters,
        userId: req.user.id,
        expectsResponse: req.expectsResponse !== false
      });

      const executionResult = await this.commandProcessor.executeCommand(command);

      return {
        success: executionResult.success,
        commandId: command.id,
        result: executionResult.result,
        executionTime: executionResult.executionTime,
        agentResponse: executionResult.agentResponse
      };
    });

    // Upload file to agent
    app.post('/api/agents/:agentId/upload', async (req: FileUploadRequest): Promise<FileUploadResponse> => {
      await this.validateAgentAccess(req.user, req.params.agentId, 'upload');
      
      const uploadResult = await this.fileManager.uploadFile({
        agentId: req.params.agentId,
        file: req.file,
        metadata: req.metadata,
        userId: req.user.id
      });

      if (!uploadResult.success) {
        throw new InternalServerError('File upload failed', uploadResult.reason);
      }

      return {
        success: true,
        fileId: uploadResult.fileId,
        filename: uploadResult.filename,
        size: uploadResult.size,
        uploadedAt: uploadResult.uploadedAt
      };
    });

    // Stream prompt to agent
    app.post('/api/agents/:agentId/stream-prompt', async (req: StreamPromptRequest): Promise<StreamResponse> => {
      await this.validateAgentAccess(req.user, req.params.agentId, 'prompt');
      
      const stream = await this.streamManager.createPromptStream({
        agentId: req.params.agentId,
        prompt: req.prompt,
        context: req.context,
        userId: req.user.id,
        streamOptions: req.options
      });

      return {
        streamId: stream.id,
        streamUrl: stream.url,
        expiresAt: stream.expiresAt
      };
    });

    // Create task
    app.post('/api/agents/:agentId/task', async (req: CreateTaskRequest): Promise<CreateTaskResponse> => {
      await this.validateAgentAccess(req.user, req.params.agentId, 'task');
      
      const task = await this.taskQueue.createTask({
        agentId: req.params.agentId,
        taskType: req.taskType,
        parameters: req.parameters,
        priority: req.priority || 'medium',
        userId: req.user.id
      });

      const queueResult = await this.taskQueue.enqueueTask(task);

      return {
        success: queueResult.success,
        taskId: task.id,
        queuePosition: queueResult.position,
        estimatedStartTime: queueResult.estimatedStartTime
      };
    });

    // Get agent logs
    app.get('/api/agents/:agentId/logs', async (req: GetLogsRequest): Promise<GetLogsResponse> => {
      await this.validateAgentAccess(req.user, req.params.agentId, 'logs');
      
      const logs = await this.agentManager.getAgentLogs(req.params.agentId, {
        startTime: req.query.startTime,
        endTime: req.query.endTime,
        level: req.query.level,
        limit: req.query.limit || 100,
        offset: req.query.offset || 0
      });

      return {
        logs: logs.entries,
        total: logs.total,
        hasMore: logs.hasMore,
        nextOffset: logs.nextOffset
      };
    });

    // Get task status
    app.get('/api/tasks/:taskId/status', async (req: TaskStatusRequest): Promise<TaskStatusResponse> => {
      const task = await this.taskQueue.getTask(req.params.taskId);
      if (!task) {
        throw new NotFoundError('Task not found');
      }

      await this.validateTaskAccess(req.user, task);

      return {
        taskId: task.id,
        status: task.status,
        progress: task.progress,
        result: task.result,
        createdAt: task.createdAt,
        startedAt: task.startedAt,
        completedAt: task.completedAt,
        estimatedCompletion: task.estimatedCompletion
      };
    });
  }
}
```

## III. WebSocket Implementation

### A. WebSocket Event System

```typescript
class WebSocketManager {
  private readonly connections = new Map<string, WebSocketConnection>();
  private readonly eventHandlers = new Map<string, EventHandler>();
  private readonly authValidator: AuthValidator;
  private readonly rateLimiter: RateLimiter;

  constructor(config: WebSocketConfig) {
    this.authValidator = new AuthValidator(config.auth);
    this.rateLimiter = new RateLimiter(config.rateLimit);
  }

  setupWebSocketHandlers(): void {
    // Agent status updates
    this.registerHandler('status_update', new StatusUpdateHandler());
    
    // Log streaming
    this.registerHandler('log_stream', new LogStreamHandler());
    
    // Prompt streaming
    this.registerHandler('stream_chunk', new StreamChunkHandler());
    
    // Command execution
    this.registerHandler('command_execute', new CommandExecuteHandler());
    
    // File upload progress
    this.registerHandler('upload_progress', new UploadProgressHandler());
    
    // Heartbeat
    this.registerHandler('heartbeat', new HeartbeatHandler());
  }

  async handleConnection(socket: WebSocket, agentId: string): Promise<void> {
    // Authenticate connection
    const authResult = await this.authValidator.validateWebSocketAuth(socket);
    if (!authResult.valid) {
      socket.close(1008, 'Authentication failed');
      return;
    }

    // Validate agent access
    const accessResult = await this.validateAgentAccess(authResult.user, agentId);
    if (!accessResult.allowed) {
      socket.close(1008, 'Access denied');
      return;
    }

    // Create connection
    const connection = new WebSocketConnection(socket, authResult.user, agentId);
    this.connections.set(connection.id, connection);

    // Setup event listeners
    this.setupConnectionEventListeners(connection);

    // Send initial status
    await this.sendInitialStatus(connection);
  }

  private setupConnectionEventListeners(connection: WebSocketConnection): void {
    connection.socket.on('message', async (data) => {
      try {
        // Rate limiting
        const rateLimitResult = await this.rateLimiter.checkLimit(connection.user.id);
        if (!rateLimitResult.allowed) {
          connection.send({
            type: 'error',
            error: 'Rate limit exceeded',
            retryAfter: rateLimitResult.retryAfter
          });
          return;
        }

        // Parse message
        const message = JSON.parse(data.toString());
        
        // Handle message
        await this.handleMessage(connection, message);
      } catch (error) {
        connection.send({
          type: 'error',
          error: 'Invalid message format'
        });
      }
    });

    connection.socket.on('close', () => {
      this.connections.delete(connection.id);
    });

    connection.socket.on('error', (error) => {
      console.error(`WebSocket error for connection ${connection.id}:`, error);
      this.connections.delete(connection.id);
    });
  }

  private async handleMessage(connection: WebSocketConnection, message: WebSocketMessage): Promise<void> {
    const handler = this.eventHandlers.get(message.type);
    if (!handler) {
      connection.send({
        type: 'error',
        error: `Unknown message type: ${message.type}`
      });
      return;
    }

    try {
      await handler.handle(connection, message);
    } catch (error) {
      connection.send({
        type: 'error',
        error: 'Message handling failed',
        details: error.message
      });
    }
  }

  async broadcastToAgent(agentId: string, event: WebSocketEvent): Promise<void> {
    const agentConnections = Array.from(this.connections.values())
      .filter(conn => conn.agentId === agentId);

    await Promise.all(
      agentConnections.map(conn => conn.send(event))
    );
  }
}

class StatusUpdateHandler implements EventHandler {
  async handle(connection: WebSocketConnection, message: WebSocketMessage): Promise<void> {
    // Status updates are server-to-client only
    connection.send({
      type: 'error',
      error: 'Status updates are read-only'
    });
  }
}

class CommandExecuteHandler implements EventHandler {
  constructor(private commandProcessor: CommandProcessor) {}

  async handle(connection: WebSocketConnection, message: WebSocketMessage): Promise<void> {
    const { command, params } = message.data;
    
    const commandObj = await this.commandProcessor.createCommand({
      agentId: connection.agentId,
      command,
      parameters: params,
      userId: connection.user.id,
      expectsResponse: true
    });

    // Execute command asynchronously
    this.commandProcessor.executeCommand(commandObj).then(result => {
      connection.send({
        type: 'command_result',
        commandId: commandObj.id,
        result: result.result,
        success: result.success,
        executionTime: result.executionTime
      });
    }).catch(error => {
      connection.send({
        type: 'command_error',
        commandId: commandObj.id,
        error: error.message
      });
    });

    // Send immediate acknowledgment
    connection.send({
      type: 'command_acknowledged',
      commandId: commandObj.id
    });
  }
}
```

## IV. Security and Permissions

```typescript
class SecurityManager {
  private readonly roleManager: RoleManager;
  private readonly permissionValidator: PermissionValidator;
  private readonly auditLogger: AuditLogger;

  constructor(config: SecurityConfig) {
    this.roleManager = new RoleManager(config.roles);
    this.permissionValidator = new PermissionValidator(config.permissions);
    this.auditLogger = new AuditLogger(config.audit);
  }

  async validatePermission(
    user: User,
    permission: string,
    resource?: string
  ): Promise<PermissionValidation> {
    // Get user roles
    const userRoles = await this.roleManager.getUserRoles(user.id);
    
    // Check permission
    const hasPermission = await this.permissionValidator.hasPermission(
      userRoles,
      permission,
      resource
    );

    // Log access attempt
    await this.auditLogger.logAccess({
      userId: user.id,
      permission,
      resource,
      granted: hasPermission,
      timestamp: new Date().toISOString()
    });

    if (!hasPermission) {
      throw new ForbiddenError(`Insufficient permissions: ${permission}`);
    }

    return {
      granted: true,
      permission,
      resource,
      roles: userRoles
    };
  }

  createPermissionMatrix(): PermissionMatrix {
    return {
      user: {
        'agents:read': true,
        'agents:create': true,
        'agents:update': true,
        'agents:delete': false,
        'agents:command': true,
        'files:upload': true,
        'config:read': true,
        'config:update': false
      },
      developer: {
        'agents:read': true,
        'agents:create': true,
        'agents:update': true,
        'agents:delete': true,
        'agents:command': true,
        'files:upload': true,
        'config:read': true,
        'config:update': true,
        'services:read': true,
        'services:restart': true
      },
      agent: {
        'agents:read': false,
        'agents:create': false,
        'agents:update': false,
        'agents:delete': false,
        'agents:command': false,
        'files:upload': true,
        'config:read': false,
        'config:update': false
      },
      admin: {
        'agents:read': true,
        'agents:create': true,
        'agents:update': true,
        'agents:delete': true,
        'agents:command': true,
        'files:upload': true,
        'config:read': true,
        'config:update': true,
        'services:read': true,
        'services:restart': true,
        'services:stop': true,
        'system:admin': true
      }
    };
  }
}
```

## Cross-References

- **Related Systems**: [Message Bus](./33_agent-message-bus-system.md), [Communication Protocols](./37_agent-communication-protocols.md)
- **Implementation Guides**: [KLP Protocol](./34_klp-kind-link-protocol.md), [Device Bootstrap](./35_device-agent-bootstrap.md)
- **Configuration**: [API Configuration](../current/api-configuration.md), [Service Settings](../current/service-settings.md)

## Changelog

- **v2.1.0** (2024-12-28): Complete TypeScript implementation with WebSocket management and security
- **v2.0.0** (2024-12-27): Enhanced with real-time features and comprehensive API coverage
- **v1.0.0** (2024-06-20): Initial API and socket service architecture

---

*This document is part of the Kind AI Documentation System - providing comprehensive API and real-time communication services for the kAI ecosystem.*