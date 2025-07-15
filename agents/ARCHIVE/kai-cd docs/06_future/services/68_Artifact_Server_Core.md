---
title: "Artifact Server Core"
description: "Core artifact storage and management system"
type: "service"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["artifact-server-api.md", "artifact-management.md"]
implementation_status: "planned"
---

# Artifact Server Core

## Agent Context
Core artifact storage system providing versioned, content-addressed storage for agent-generated artifacts with metadata indexing and retrieval capabilities.

## Artifact Architecture

```typescript
interface Artifact {
  id: string; // Content hash (SHA-256)
  name: string;
  type: ArtifactType;
  content: ArtifactContent;
  metadata: ArtifactMetadata;
  versions: ArtifactVersion[];
  relationships: ArtifactRelationship[];
  created: string;
  lastModified: string;
}

interface ArtifactContent {
  data: Buffer | string;
  encoding: 'binary' | 'base64' | 'utf8';
  compression?: 'gzip' | 'brotli';
  size: number;
  checksum: string;
}

interface ArtifactMetadata {
  creator: string; // Agent kID
  tags: string[];
  description?: string;
  mimeType: string;
  language?: string;
  schema?: string;
  annotations: Record<string, any>;
}

type ArtifactType = 
  | 'code'
  | 'document'
  | 'image'
  | 'model'
  | 'data'
  | 'configuration'
  | 'template'
  | 'schema';
```

## Storage Engine

```typescript
class ArtifactStorageEngine {
  private storage: StorageBackend;
  private index: ArtifactIndex;
  private cache: LRUCache<string, Artifact>;

  async storeArtifact(
    content: Buffer | string,
    metadata: ArtifactMetadata,
    options: StorageOptions = {}
  ): Promise<Artifact> {
    // Calculate content hash
    const contentHash = await this.calculateHash(content);
    
    // Check if artifact already exists
    const existing = await this.getArtifact(contentHash);
    if (existing && !options.forceNew) {
      // Update metadata if different
      if (this.metadataChanged(existing.metadata, metadata)) {
        return await this.updateArtifactMetadata(contentHash, metadata);
      }
      return existing;
    }

    // Compress content if beneficial
    const processedContent = await this.processContent(content, options);

    // Create artifact
    const artifact: Artifact = {
      id: contentHash,
      name: metadata.name || `artifact-${contentHash.substring(0, 8)}`,
      type: this.inferArtifactType(metadata, content),
      content: processedContent,
      metadata,
      versions: [{
        version: 1,
        hash: contentHash,
        created: new Date().toISOString(),
        changes: 'Initial version'
      }],
      relationships: [],
      created: new Date().toISOString(),
      lastModified: new Date().toISOString()
    };

    // Store artifact
    await this.storage.put(contentHash, artifact);
    
    // Update index
    await this.index.add(artifact);
    
    // Cache artifact
    this.cache.set(contentHash, artifact);

    return artifact;
  }

  async getArtifact(id: string): Promise<Artifact | null> {
    // Check cache first
    if (this.cache.has(id)) {
      return this.cache.get(id)!;
    }

    // Retrieve from storage
    const artifact = await this.storage.get(id);
    if (artifact) {
      this.cache.set(id, artifact);
    }

    return artifact;
  }

  async queryArtifacts(query: ArtifactQuery): Promise<ArtifactSearchResult> {
    const results = await this.index.search(query);
    
    // Load full artifacts for results
    const artifacts = await Promise.all(
      results.hits.map(hit => this.getArtifact(hit.id))
    );

    return {
      total: results.total,
      artifacts: artifacts.filter(a => a !== null) as Artifact[],
      facets: results.facets,
      took: results.took
    };
  }

  private async processContent(
    content: Buffer | string,
    options: StorageOptions
  ): Promise<ArtifactContent> {
    let data: Buffer;
    let encoding: 'binary' | 'base64' | 'utf8' = 'binary';

    if (typeof content === 'string') {
      data = Buffer.from(content, 'utf8');
      encoding = 'utf8';
    } else {
      data = content;
    }

    // Compress if content is large enough
    let compression: 'gzip' | 'brotli' | undefined;
    if (data.length > 1024 && options.compress !== false) {
      const gzipped = await this.compress(data, 'gzip');
      const brotlied = await this.compress(data, 'brotli');
      
      if (gzipped.length < data.length * 0.9) {
        data = gzipped;
        compression = 'gzip';
      } else if (brotlied.length < data.length * 0.9) {
        data = brotlied;
        compression = 'brotli';
      }
    }

    return {
      data: encoding === 'utf8' ? data.toString('utf8') : data,
      encoding,
      compression,
      size: data.length,
      checksum: await this.calculateHash(data)
    };
  }
}
```

## Version Management

```typescript
class ArtifactVersionManager {
  async createVersion(
    artifactId: string,
    newContent: Buffer | string,
    changes: string
  ): Promise<ArtifactVersion> {
    const artifact = await this.storageEngine.getArtifact(artifactId);
    if (!artifact) {
      throw new Error('Artifact not found');
    }

    const newHash = await this.calculateHash(newContent);
    const version: ArtifactVersion = {
      version: artifact.versions.length + 1,
      hash: newHash,
      created: new Date().toISOString(),
      changes,
      parentVersion: artifact.versions[artifact.versions.length - 1]?.version
    };

    // Store new version content
    const processedContent = await this.storageEngine.processContent(newContent, {});
    await this.storageEngine.storage.put(newHash, {
      ...artifact,
      id: newHash,
      content: processedContent,
      versions: [...artifact.versions, version],
      lastModified: new Date().toISOString()
    });

    // Update main artifact reference
    artifact.versions.push(version);
    artifact.lastModified = new Date().toISOString();
    await this.storageEngine.storage.put(artifactId, artifact);

    return version;
  }

  async getVersion(artifactId: string, version: number): Promise<Artifact | null> {
    const artifact = await this.storageEngine.getArtifact(artifactId);
    if (!artifact) {
      return null;
    }

    const versionInfo = artifact.versions.find(v => v.version === version);
    if (!versionInfo) {
      return null;
    }

    return await this.storageEngine.getArtifact(versionInfo.hash);
  }

  async compareVersions(
    artifactId: string,
    version1: number,
    version2: number
  ): Promise<VersionComparison> {
    const [v1, v2] = await Promise.all([
      this.getVersion(artifactId, version1),
      this.getVersion(artifactId, version2)
    ]);

    if (!v1 || !v2) {
      throw new Error('One or both versions not found');
    }

    return {
      artifact1: v1,
      artifact2: v2,
      differences: await this.calculateDifferences(v1, v2),
      similarity: await this.calculateSimilarity(v1, v2)
    };
  }
}
```

## Relationship Management

```typescript
class ArtifactRelationshipManager {
  async createRelationship(
    sourceId: string,
    targetId: string,
    type: RelationshipType,
    metadata?: Record<string, any>
  ): Promise<ArtifactRelationship> {
    const relationship: ArtifactRelationship = {
      id: crypto.randomUUID(),
      source: sourceId,
      target: targetId,
      type,
      metadata: metadata || {},
      created: new Date().toISOString(),
      strength: 1.0
    };

    // Update both artifacts
    await this.addRelationshipToArtifact(sourceId, relationship);
    
    // Create inverse relationship
    const inverseType = this.getInverseRelationshipType(type);
    if (inverseType) {
      const inverseRelationship: ArtifactRelationship = {
        ...relationship,
        id: crypto.randomUUID(),
        source: targetId,
        target: sourceId,
        type: inverseType
      };
      
      await this.addRelationshipToArtifact(targetId, inverseRelationship);
    }

    return relationship;
  }

  async findRelatedArtifacts(
    artifactId: string,
    relationshipType?: RelationshipType,
    maxDepth: number = 2
  ): Promise<RelatedArtifactsResult> {
    const visited = new Set<string>();
    const results: RelatedArtifact[] = [];
    
    await this.traverseRelationships(
      artifactId,
      relationshipType,
      maxDepth,
      0,
      visited,
      results
    );

    return {
      total: results.length,
      artifacts: results,
      maxDepth
    };
  }

  private async traverseRelationships(
    artifactId: string,
    relationshipType: RelationshipType | undefined,
    maxDepth: number,
    currentDepth: number,
    visited: Set<string>,
    results: RelatedArtifact[]
  ): Promise<void> {
    if (currentDepth >= maxDepth || visited.has(artifactId)) {
      return;
    }

    visited.add(artifactId);
    const artifact = await this.storageEngine.getArtifact(artifactId);
    
    if (!artifact) {
      return;
    }

    for (const relationship of artifact.relationships) {
      if (relationshipType && relationship.type !== relationshipType) {
        continue;
      }

      const relatedArtifact = await this.storageEngine.getArtifact(relationship.target);
      if (relatedArtifact) {
        results.push({
          artifact: relatedArtifact,
          relationship,
          depth: currentDepth + 1
        });

        // Recurse to find deeper relationships
        await this.traverseRelationships(
          relationship.target,
          relationshipType,
          maxDepth,
          currentDepth + 1,
          visited,
          results
        );
      }
    }
  }
}
```
