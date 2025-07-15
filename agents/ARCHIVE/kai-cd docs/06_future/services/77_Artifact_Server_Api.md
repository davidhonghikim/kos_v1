---
title: "Artifact Server API"
description: "REST and GraphQL API for artifact server operations"
type: "service"
status: "future"
priority: "medium"
last_updated: "2025-01-27"
related_docs: ["artifact-server-core.md", "artifact-management.md"]
implementation_status: "planned"
---

# Artifact Server API

## Agent Context
Comprehensive API specification for artifact server operations including REST endpoints, GraphQL schema, and WebSocket streaming for real-time updates.

## REST API Endpoints

```typescript
interface ArtifactAPI {
  // Artifact CRUD operations
  'POST /artifacts': (content: ArtifactUpload) => Promise<Artifact>;
  'GET /artifacts/:id': (id: string) => Promise<Artifact>;
  'PUT /artifacts/:id': (id: string, updates: ArtifactUpdate) => Promise<Artifact>;
  'DELETE /artifacts/:id': (id: string) => Promise<void>;
  
  // Search and query
  'GET /artifacts': (query: ArtifactQuery) => Promise<ArtifactSearchResult>;
  'POST /artifacts/search': (query: ComplexQuery) => Promise<ArtifactSearchResult>;
  
  // Version management
  'GET /artifacts/:id/versions': (id: string) => Promise<ArtifactVersion[]>;
  'POST /artifacts/:id/versions': (id: string, version: VersionCreate) => Promise<ArtifactVersion>;
  'GET /artifacts/:id/versions/:version': (id: string, version: number) => Promise<Artifact>;
  
  // Relationships
  'GET /artifacts/:id/relationships': (id: string) => Promise<ArtifactRelationship[]>;
  'POST /artifacts/:id/relationships': (id: string, rel: RelationshipCreate) => Promise<ArtifactRelationship>;
  'DELETE /relationships/:id': (id: string) => Promise<void>;
}
```

## API Implementation

```typescript
class ArtifactAPIServer {
  private storageEngine: ArtifactStorageEngine;
  private versionManager: ArtifactVersionManager;
  private relationshipManager: ArtifactRelationshipManager;

  constructor() {
    this.setupRoutes();
  }

  private setupRoutes(): void {
    // Upload artifact
    this.app.post('/artifacts', async (req, res) => {
      try {
        const upload = await this.parseUpload(req);
        const artifact = await this.storageEngine.storeArtifact(
          upload.content,
          upload.metadata,
          upload.options
        );
        
        res.status(201).json(artifact);
      } catch (error) {
        res.status(400).json({ error: error.message });
      }
    });

    // Get artifact
    this.app.get('/artifacts/:id', async (req, res) => {
      try {
        const artifact = await this.storageEngine.getArtifact(req.params.id);
        if (!artifact) {
          return res.status(404).json({ error: 'Artifact not found' });
        }
        
        // Check permissions
        const hasAccess = await this.checkReadAccess(req.user, artifact);
        if (!hasAccess) {
          return res.status(403).json({ error: 'Access denied' });
        }

        res.json(artifact);
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });

    // Search artifacts
    this.app.get('/artifacts', async (req, res) => {
      try {
        const query = this.parseQuery(req.query);
        const results = await this.storageEngine.queryArtifacts(query);
        
        // Filter results based on permissions
        const filteredResults = await this.filterByPermissions(req.user, results);
        
        res.json(filteredResults);
      } catch (error) {
        res.status(400).json({ error: error.message });
      }
    });

    // Create version
    this.app.post('/artifacts/:id/versions', async (req, res) => {
      try {
        const { content, changes } = req.body;
        const version = await this.versionManager.createVersion(
          req.params.id,
          content,
          changes
        );
        
        res.status(201).json(version);
      } catch (error) {
        res.status(400).json({ error: error.message });
      }
    });
  }

  private async parseUpload(req: any): Promise<ArtifactUpload> {
    if (req.is('multipart/form-data')) {
      return await this.parseMultipartUpload(req);
    } else if (req.is('application/json')) {
      return this.parseJSONUpload(req.body);
    } else {
      throw new Error('Unsupported content type');
    }
  }

  private async parseMultipartUpload(req: any): Promise<ArtifactUpload> {
    const form = new FormData();
    const fields = await form.parse(req);
    
    return {
      content: fields.file.buffer,
      metadata: JSON.parse(fields.metadata || '{}'),
      options: JSON.parse(fields.options || '{}')
    };
  }

  private parseJSONUpload(body: any): ArtifactUpload {
    return {
      content: body.content,
      metadata: body.metadata || {},
      options: body.options || {}
    };
  }
}
```

## GraphQL Schema

```graphql
type Artifact {
  id: ID!
  name: String!
  type: ArtifactType!
  content: ArtifactContent!
  metadata: ArtifactMetadata!
  versions: [ArtifactVersion!]!
  relationships: [ArtifactRelationship!]!
  created: DateTime!
  lastModified: DateTime!
}

type ArtifactContent {
  size: Int!
  checksum: String!
  encoding: String!
  compression: String
  # Content data is available through separate download endpoint
}

type ArtifactMetadata {
  creator: String!
  tags: [String!]!
  description: String
  mimeType: String!
  language: String
  schema: String
  annotations: JSON
}

type ArtifactVersion {
  version: Int!
  hash: String!
  created: DateTime!
  changes: String!
  parentVersion: Int
}

type ArtifactRelationship {
  id: ID!
  source: String!
  target: String!
  type: RelationshipType!
  metadata: JSON
  created: DateTime!
  strength: Float!
}

enum ArtifactType {
  CODE
  DOCUMENT
  IMAGE
  MODEL
  DATA
  CONFIGURATION
  TEMPLATE
  SCHEMA
}

enum RelationshipType {
  DERIVES_FROM
  DEPENDS_ON
  IMPLEMENTS
  EXTENDS
  REFERENCES
  CONTAINS
  GENERATED_BY
}

type Query {
  artifact(id: ID!): Artifact
  artifacts(
    query: String
    type: ArtifactType
    creator: String
    tags: [String!]
    limit: Int = 20
    offset: Int = 0
  ): ArtifactSearchResult!
  
  artifactVersions(id: ID!): [ArtifactVersion!]!
  artifactRelationships(id: ID!): [ArtifactRelationship!]!
  relatedArtifacts(
    id: ID!
    relationshipType: RelationshipType
    maxDepth: Int = 2
  ): RelatedArtifactsResult!
}

type Mutation {
  uploadArtifact(input: ArtifactUploadInput!): Artifact!
  updateArtifact(id: ID!, input: ArtifactUpdateInput!): Artifact!
  deleteArtifact(id: ID!): Boolean!
  
  createVersion(id: ID!, content: String!, changes: String!): ArtifactVersion!
  
  createRelationship(input: RelationshipCreateInput!): ArtifactRelationship!
  deleteRelationship(id: ID!): Boolean!
}

type Subscription {
  artifactUpdated(id: ID): Artifact!
  artifactCreated(creator: String): Artifact!
  relationshipCreated(artifactId: ID): ArtifactRelationship!
}

input ArtifactUploadInput {
  name: String!
  content: String!
  metadata: ArtifactMetadataInput!
  options: ArtifactOptionsInput
}

input ArtifactMetadataInput {
  tags: [String!]
  description: String
  mimeType: String!
  language: String
  schema: String
  annotations: JSON
}
```

## WebSocket API

```typescript
class ArtifactWebSocketAPI {
  private wss: WebSocketServer;
  private subscriptions: Map<string, Set<WebSocket>>;

  constructor() {
    this.wss = new WebSocketServer({ port: 8080 });
    this.subscriptions = new Map();
    this.setupWebSocketHandlers();
  }

  private setupWebSocketHandlers(): void {
    this.wss.on('connection', (ws: WebSocket, req: IncomingMessage) => {
      ws.on('message', async (data: Buffer) => {
        try {
          const message = JSON.parse(data.toString()) as WebSocketMessage;
          await this.handleMessage(ws, message);
        } catch (error) {
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message
          }));
        }
      });

      ws.on('close', () => {
        this.removeSubscriptions(ws);
      });
    });
  }

  private async handleMessage(ws: WebSocket, message: WebSocketMessage): Promise<void> {
    switch (message.type) {
      case 'subscribe':
        await this.handleSubscribe(ws, message);
        break;
      
      case 'unsubscribe':
        await this.handleUnsubscribe(ws, message);
        break;
      
      case 'query':
        await this.handleQuery(ws, message);
        break;
      
      default:
        ws.send(JSON.stringify({
          type: 'error',
          error: `Unknown message type: ${message.type}`
        }));
    }
  }

  private async handleSubscribe(ws: WebSocket, message: SubscribeMessage): Promise<void> {
    const { subscription } = message;
    
    switch (subscription.type) {
      case 'artifact_updates':
        this.subscribeToArtifactUpdates(ws, subscription.artifactId);
        break;
      
      case 'new_artifacts':
        this.subscribeToNewArtifacts(ws, subscription.creator);
        break;
      
      case 'relationship_changes':
        this.subscribeToRelationshipChanges(ws, subscription.artifactId);
        break;
    }

    ws.send(JSON.stringify({
      type: 'subscribed',
      subscription: subscription.type
    }));
  }

  async notifyArtifactUpdate(artifact: Artifact): Promise<void> {
    const subscribers = this.subscriptions.get(`artifact:${artifact.id}`);
    if (subscribers) {
      const notification = {
        type: 'artifact_updated',
        artifact
      };

      for (const ws of subscribers) {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(notification));
        }
      }
    }
  }

  async notifyNewArtifact(artifact: Artifact): Promise<void> {
    const subscribers = this.subscriptions.get(`creator:${artifact.metadata.creator}`);
    if (subscribers) {
      const notification = {
        type: 'artifact_created',
        artifact
      };

      for (const ws of subscribers) {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(notification));
        }
      }
    }
  }
}
```
