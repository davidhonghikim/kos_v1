---
title: "Artifact Storage & Retrieval System"
description: "Comprehensive artifact management system for uploads, indexing, hosting, and lifecycle management with multi-backend support"
version: "2.1.0"
last_updated: "2024-12-28"
category: "Services"
tags: ["storage", "artifacts", "media", "files", "lifecycle", "indexing"]
author: "kAI Development Team"
status: "active"
---

# Artifact Storage & Retrieval System

## Agent Context
This document defines the comprehensive artifact storage and retrieval system for the kAI/kOS ecosystem, handling all media and file assets produced, referenced, or used by agents and users. The system supports multiple storage backends (local, S3, IPFS, Firebase), metadata indexing, retrieval strategies, caching, expiration policies, and automated lifecycle management with security scanning, deduplication, and role-based access control.

## Overview

The Artifact Storage & Retrieval System manages all digital assets within the kAI ecosystem, providing reliable storage, discoverability, integrity verification, and automated lifecycle management for various artifact types including LLM-generated media, user uploads, logs, transcriptions, and execution results.

## I. System Architecture

```typescript
interface ArtifactStorageSystem {
  storageManager: StorageManager;
  indexer: ArtifactIndexer;
  metadataEngine: MetadataEngine;
  expiryManager: ExpiryManager;
  securityScanner: SecurityScanner;
  deduplicationEngine: DeduplicationEngine;
  accessController: AccessController;
}

class ArtifactManager {
  private readonly storageManager: StorageManager;
  private readonly indexer: ArtifactIndexer;
  private readonly metadataEngine: MetadataEngine;
  private readonly expiryManager: ExpiryManager;
  private readonly securityScanner: SecurityScanner;
  private readonly deduplicationEngine: DeduplicationEngine;
  private readonly accessController: AccessController;
  private readonly previewGenerator: PreviewGenerator;
  private readonly auditLogger: AuditLogger;

  constructor(config: ArtifactConfig) {
    this.storageManager = new StorageManager(config.storage);
    this.indexer = new ArtifactIndexer(config.indexing);
    this.metadataEngine = new MetadataEngine(config.metadata);
    this.expiryManager = new ExpiryManager(config.expiry);
    this.securityScanner = new SecurityScanner(config.security);
    this.deduplicationEngine = new DeduplicationEngine(config.deduplication);
    this.accessController = new AccessController(config.access);
    this.previewGenerator = new PreviewGenerator(config.preview);
    this.auditLogger = new AuditLogger(config.audit);
  }

  async uploadArtifact(
    uploadRequest: ArtifactUploadRequest,
    metadata: ArtifactMetadata
  ): Promise<ArtifactUploadResult> {
    const uploadId = this.generateUploadId();
    const startTime = Date.now();

    try {
      // Security scanning
      const securityScan = await this.securityScanner.scanArtifact(
        uploadRequest.file,
        uploadRequest.fileName
      );
      if (!securityScan.safe) {
        throw new SecurityViolationError('Artifact failed security scan', securityScan.threats);
      }

      // File validation
      const validation = await this.validateArtifact(uploadRequest);
      if (!validation.valid) {
        throw new ValidationError('Artifact validation failed', validation.errors);
      }

      // Deduplication check
      const fileHash = await this.deduplicationEngine.calculateHash(uploadRequest.file);
      const existingArtifact = await this.deduplicationEngine.findDuplicate(fileHash);
      if (existingArtifact && uploadRequest.allowDuplicates !== true) {
        return {
          success: true,
          artifactId: existingArtifact.id,
          duplicate: true,
          existingUrl: existingArtifact.url,
          uploadTime: Date.now() - startTime
        };
      }

      // Generate artifact ID and metadata
      const artifactId = this.generateArtifactId();
      const enrichedMetadata = await this.metadataEngine.enrichMetadata({
        ...metadata,
        id: artifactId,
        fileName: uploadRequest.fileName,
        fileSize: uploadRequest.file.size,
        mimeType: uploadRequest.mimeType,
        hash: fileHash,
        uploadedAt: new Date().toISOString(),
        uploadedBy: uploadRequest.uploadedBy,
        securityScan: securityScan.summary
      });

      // Store artifact
      const storageResult = await this.storageManager.store({
        id: artifactId,
        file: uploadRequest.file,
        metadata: enrichedMetadata,
        storageOptions: uploadRequest.storageOptions
      });

      // Generate preview if applicable
      let previewUrl: string | undefined;
      if (this.shouldGeneratePreview(enrichedMetadata.type)) {
        const preview = await this.previewGenerator.generatePreview(
          artifactId,
          uploadRequest.file,
          enrichedMetadata
        );
        previewUrl = preview.url;
      }

      // Index artifact
      await this.indexer.indexArtifact({
        id: artifactId,
        metadata: enrichedMetadata,
        searchableContent: await this.extractSearchableContent(uploadRequest.file, enrichedMetadata),
        tags: uploadRequest.tags || [],
        fullTextContent: await this.extractFullText(uploadRequest.file, enrichedMetadata)
      });

      // Set expiry if configured
      if (uploadRequest.expiryPolicy) {
        await this.expiryManager.setExpiry(artifactId, uploadRequest.expiryPolicy);
      }

      // Log upload
      await this.auditLogger.logUpload({
        artifactId,
        uploadId,
        metadata: enrichedMetadata,
        uploadedBy: uploadRequest.uploadedBy,
        timestamp: new Date().toISOString()
      });

      return {
        success: true,
        artifactId,
        url: storageResult.url,
        previewUrl,
        metadata: enrichedMetadata,
        hash: fileHash,
        duplicate: false,
        uploadTime: Date.now() - startTime,
        expiresAt: uploadRequest.expiryPolicy?.expiresAt
      };
    } catch (error) {
      await this.auditLogger.logUploadFailure({
        uploadId,
        error: error.message,
        metadata,
        timestamp: new Date().toISOString()
      });
      throw error;
    }
  }

  async getArtifact(
    artifactId: string,
    accessRequest: ArtifactAccessRequest
  ): Promise<ArtifactGetResult> {
    // Check access permissions
    const accessCheck = await this.accessController.checkAccess(
      artifactId,
      accessRequest.requestedBy,
      accessRequest.accessType
    );
    if (!accessCheck.allowed) {
      throw new AccessDeniedError('Access denied to artifact', accessCheck.reason);
    }

    // Get artifact metadata
    const metadata = await this.indexer.getMetadata(artifactId);
    if (!metadata) {
      throw new ArtifactNotFoundError(`Artifact ${artifactId} not found`);
    }

    // Check expiry
    const expiryStatus = await this.expiryManager.checkExpiry(artifactId);
    if (expiryStatus.expired) {
      throw new ArtifactExpiredError(`Artifact ${artifactId} has expired`);
    }

    // Get storage URL (signed if necessary)
    const storageUrl = await this.storageManager.getAccessUrl({
      artifactId,
      metadata,
      accessType: accessRequest.accessType,
      expiryDuration: accessRequest.urlExpiryDuration
    });

    // Log access
    await this.auditLogger.logAccess({
      artifactId,
      accessedBy: accessRequest.requestedBy,
      accessType: accessRequest.accessType,
      timestamp: new Date().toISOString()
    });

    return {
      success: true,
      artifactId,
      metadata,
      url: storageUrl.url,
      signedUrl: storageUrl.signed,
      expiresAt: storageUrl.expiresAt,
      accessGranted: accessCheck.permissions
    };
  }

  async searchArtifacts(
    searchRequest: ArtifactSearchRequest
  ): Promise<ArtifactSearchResult> {
    // Check search permissions
    const searchPermissions = await this.accessController.getSearchPermissions(
      searchRequest.requestedBy
    );

    // Execute search
    const searchResults = await this.indexer.search({
      query: searchRequest.query,
      filters: {
        ...searchRequest.filters,
        accessibleBy: searchRequest.requestedBy
      },
      permissions: searchPermissions,
      limit: searchRequest.limit || 20,
      offset: searchRequest.offset || 0,
      sortBy: searchRequest.sortBy || 'relevance'
    });

    // Enrich results with access URLs if requested
    if (searchRequest.includeAccessUrls) {
      for (const result of searchResults.artifacts) {
        try {
          const accessUrl = await this.storageManager.getAccessUrl({
            artifactId: result.id,
            metadata: result.metadata,
            accessType: 'read',
            expiryDuration: '1h'
          });
          result.accessUrl = accessUrl.url;
        } catch (error) {
          // Skip if access denied
          continue;
        }
      }
    }

    return {
      success: true,
      artifacts: searchResults.artifacts,
      totalCount: searchResults.totalCount,
      searchTime: searchResults.searchTime,
      searchId: searchResults.searchId
    };
  }

  private async validateArtifact(uploadRequest: ArtifactUploadRequest): Promise<ValidationResult> {
    const errors: string[] = [];
    const warnings: string[] = [];

    // File size validation
    if (uploadRequest.file.size > this.config.maxFileSizeMB * 1024 * 1024) {
      errors.push(`File size exceeds maximum of ${this.config.maxFileSizeMB}MB`);
    }

    // MIME type validation
    if (!this.isAllowedMimeType(uploadRequest.mimeType)) {
      errors.push(`MIME type ${uploadRequest.mimeType} not allowed`);
    }

    // File extension validation
    const extension = this.extractFileExtension(uploadRequest.fileName);
    if (!this.isAllowedExtension(extension)) {
      errors.push(`File extension ${extension} not allowed`);
    }

    // Filename validation
    if (!this.isValidFilename(uploadRequest.fileName)) {
      errors.push('Invalid filename format');
    }

    // Content validation for specific types
    if (uploadRequest.mimeType.startsWith('image/')) {
      const imageValidation = await this.validateImageContent(uploadRequest.file);
      if (!imageValidation.valid) {
        errors.push(...imageValidation.errors);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }
}
```

## II. Storage Backends

### A. Multi-Backend Storage Manager

```typescript
class StorageManager {
  private readonly backends: Map<string, StorageBackend>;
  private readonly defaultBackend: string;
  private readonly routingEngine: StorageRoutingEngine;

  constructor(config: StorageConfig) {
    this.backends = new Map();
    this.defaultBackend = config.defaultBackend;
    this.routingEngine = new StorageRoutingEngine(config.routing);
    
    // Initialize backends
    this.initializeBackends(config.backends);
  }

  private initializeBackends(backendConfigs: BackendConfig[]): void {
    for (const config of backendConfigs) {
      switch (config.type) {
        case 'local':
          this.backends.set(config.name, new LocalStorageBackend(config));
          break;
        case 's3':
          this.backends.set(config.name, new S3StorageBackend(config));
          break;
        case 'ipfs':
          this.backends.set(config.name, new IPFSStorageBackend(config));
          break;
        case 'firebase':
          this.backends.set(config.name, new FirebaseStorageBackend(config));
          break;
        default:
          throw new UnsupportedBackendError(`Backend type ${config.type} not supported`);
      }
    }
  }

  async store(storeRequest: StorageStoreRequest): Promise<StorageStoreResult> {
    // Determine backend based on routing rules
    const backendName = await this.routingEngine.selectBackend({
      artifactId: storeRequest.id,
      metadata: storeRequest.metadata,
      fileSize: storeRequest.file.size,
      mimeType: storeRequest.metadata.mimeType
    });

    const backend = this.backends.get(backendName);
    if (!backend) {
      throw new BackendNotFoundError(`Backend ${backendName} not found`);
    }

    // Store in selected backend
    const result = await backend.store(storeRequest);

    // Store backup if configured
    if (this.shouldCreateBackup(storeRequest.metadata)) {
      await this.createBackup(storeRequest, result);
    }

    return {
      ...result,
      backend: backendName,
      backupCreated: this.shouldCreateBackup(storeRequest.metadata)
    };
  }

  async getAccessUrl(accessRequest: AccessUrlRequest): Promise<AccessUrlResult> {
    const backend = await this.getBackendForArtifact(accessRequest.artifactId);
    return await backend.getAccessUrl(accessRequest);
  }
}

// Local Filesystem Backend
class LocalStorageBackend implements StorageBackend {
  private readonly rootDir: string;
  private readonly urlPrefix: string;
  private readonly compressionEnabled: boolean;

  constructor(config: LocalBackendConfig) {
    this.rootDir = config.rootDir;
    this.urlPrefix = config.urlPrefix || '/artifacts';
    this.compressionEnabled = config.compression || false;
    this.ensureDirectoryExists(this.rootDir);
  }

  async store(request: StorageStoreRequest): Promise<StorageStoreResult> {
    const relativePath = this.generatePath(request.id, request.metadata);
    const fullPath = path.join(this.rootDir, relativePath);
    
    // Ensure directory exists
    await fs.ensureDir(path.dirname(fullPath));
    
    // Compress if enabled and applicable
    let fileData = request.file;
    if (this.compressionEnabled && this.shouldCompress(request.metadata.mimeType)) {
      fileData = await this.compressFile(request.file, request.metadata.mimeType);
    }
    
    // Write file with atomic operation
    const tempPath = `${fullPath}.tmp`;
    await fs.writeFile(tempPath, fileData);
    await fs.rename(tempPath, fullPath);
    
    // Set file permissions
    await fs.chmod(fullPath, 0o644);
    
    // Generate public URL
    const url = `${this.urlPrefix}/${relativePath}`;
    
    return {
      success: true,
      url,
      path: relativePath,
      size: fileData.length,
      compressed: this.compressionEnabled && this.shouldCompress(request.metadata.mimeType),
      storedAt: new Date().toISOString()
    };
  }

  async getAccessUrl(request: AccessUrlRequest): Promise<AccessUrlResult> {
    const relativePath = await this.getPathForArtifact(request.artifactId);
    const fullPath = path.join(this.rootDir, relativePath);
    
    // Check if file exists
    const exists = await fs.pathExists(fullPath);
    if (!exists) {
      throw new ArtifactNotFoundError(`Artifact file not found: ${request.artifactId}`);
    }
    
    const url = `${this.urlPrefix}/${relativePath}`;
    
    return {
      url,
      signed: false,
      expiresAt: null
    };
  }

  async deleteArtifact(artifactId: string): Promise<DeleteResult> {
    const relativePath = await this.getPathForArtifact(artifactId);
    const fullPath = path.join(this.rootDir, relativePath);
    
    try {
      await fs.remove(fullPath);
      return {
        success: true,
        artifactId,
        deletedAt: new Date().toISOString()
      };
    } catch (error) {
      return {
        success: false,
        artifactId,
        error: error.message
      };
    }
  }

  private generatePath(artifactId: string, metadata: ArtifactMetadata): string {
    const typeDir = this.getTypeDirectory(metadata.type);
    const dateDir = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const hashPrefix = metadata.hash.substring(0, 2); // First 2 chars of hash for distribution
    const filename = `${artifactId}${this.getFileExtension(metadata.fileName)}`;
    
    return path.join(typeDir, dateDir, hashPrefix, filename);
  }

  private shouldCompress(mimeType: string): boolean {
    const compressibleTypes = [
      'text/',
      'application/json',
      'application/xml',
      'application/javascript',
      'application/css'
    ];
    return compressibleTypes.some(type => mimeType.startsWith(type));
  }
}

// S3 Backend with Advanced Features
class S3StorageBackend implements StorageBackend {
  private readonly s3Client: S3Client;
  private readonly bucket: string;
  private readonly region: string;
  private readonly cdnDomain?: string;
  private readonly encryptionEnabled: boolean;

  constructor(config: S3BackendConfig) {
    this.s3Client = new S3Client({
      region: config.region,
      credentials: {
        accessKeyId: config.accessKeyId,
        secretAccessKey: config.secretAccessKey
      }
    });
    this.bucket = config.bucket;
    this.region = config.region;
    this.cdnDomain = config.cdnDomain;
    this.encryptionEnabled = config.encryption || true;
  }

  async store(request: StorageStoreRequest): Promise<StorageStoreResult> {
    const key = this.generateKey(request.id, request.metadata);
    
    // Prepare upload parameters
    const uploadParams: PutObjectCommandInput = {
      Bucket: this.bucket,
      Key: key,
      Body: request.file,
      ContentType: request.metadata.mimeType,
      Metadata: {
        artifactId: request.id,
        uploadedBy: request.metadata.uploadedBy,
        uploadedAt: request.metadata.uploadedAt,
        originalName: request.metadata.fileName
      }
    };

    // Add encryption
    if (this.encryptionEnabled) {
      uploadParams.ServerSideEncryption = 'AES256';
    }

    // Set storage class based on access pattern
    uploadParams.StorageClass = this.determineStorageClass(request.metadata);

    // Set cache control headers
    uploadParams.CacheControl = this.getCacheControlHeader(request.metadata.type);

    // Upload to S3
    await this.s3Client.send(new PutObjectCommand(uploadParams));

    // Generate URL (CDN if available, otherwise direct S3)
    const url = this.cdnDomain 
      ? `https://${this.cdnDomain}/${key}`
      : `https://${this.bucket}.s3.${this.region}.amazonaws.com/${key}`;

    return {
      success: true,
      url,
      path: key,
      size: request.file.length,
      storageClass: uploadParams.StorageClass,
      encrypted: this.encryptionEnabled,
      storedAt: new Date().toISOString()
    };
  }

  async getAccessUrl(request: AccessUrlRequest): Promise<AccessUrlResult> {
    const key = await this.getKeyForArtifact(request.artifactId);
    
    if (request.accessType === 'public' && this.cdnDomain) {
      const url = `https://${this.cdnDomain}/${key}`;
      return { url, signed: false, expiresAt: null };
    }

    // Generate signed URL
    const command = new GetObjectCommand({
      Bucket: this.bucket,
      Key: key
    });

    const expirySeconds = this.parseExpiryDuration(request.expiryDuration || '1h');
    const signedUrl = await getSignedUrl(this.s3Client, command, {
      expiresIn: expirySeconds
    });

    return {
      url: signedUrl,
      signed: true,
      expiresAt: new Date(Date.now() + expirySeconds * 1000).toISOString()
    };
  }

  private determineStorageClass(metadata: ArtifactMetadata): string {
    // Frequently accessed files
    if (metadata.type === 'image' || metadata.type === 'video') {
      return 'STANDARD';
    }
    // Archive data
    if (metadata.type === 'archive' || metadata.fileName.includes('backup')) {
      return 'STANDARD_IA';
    }
    return 'STANDARD';
  }

  private getCacheControlHeader(type: string): string {
    switch (type) {
      case 'image':
      case 'video':
      case 'audio':
        return 'max-age=31536000, immutable'; // 1 year
      case 'document':
        return 'max-age=86400'; // 1 day
      default:
        return 'max-age=3600'; // 1 hour
    }
  }
}

// IPFS Backend with Pinning Services
class IPFSStorageBackend implements StorageBackend {
  private readonly ipfsClient: IPFSHTTPClient;
  private readonly gatewayUrl: string;
  private readonly pinningServices: PinningService[];
  private readonly replicationFactor: number;

  constructor(config: IPFSBackendConfig) {
    this.ipfsClient = create({ url: config.nodeUrl });
    this.gatewayUrl = config.gatewayUrl;
    this.pinningServices = config.pinningServices?.map(ps => new PinningService(ps)) || [];
    this.replicationFactor = config.replicationFactor || 3;
  }

  async store(request: StorageStoreRequest): Promise<StorageStoreResult> {
    // Add to IPFS with metadata
    const addResult = await this.ipfsClient.add(request.file, {
      pin: true,
      wrapWithDirectory: false,
      cidVersion: 1
    });

    const cid = addResult.cid.toString();

    // Replicate to pinning services
    const pinningResults = await this.replicateToPinningServices(cid, {
      name: `artifact-${request.id}`,
      metadata: request.metadata,
      replicationFactor: this.replicationFactor
    });

    // Generate multiple gateway URLs for redundancy
    const urls = [
      `${this.gatewayUrl}/ipfs/${cid}`,
      ...pinningResults.map(pr => pr.gatewayUrl).filter(Boolean)
    ];

    return {
      success: true,
      url: urls[0], // Primary URL
      alternativeUrls: urls.slice(1),
      path: cid,
      size: request.file.length,
      replications: pinningResults.length,
      storedAt: new Date().toISOString()
    };
  }

  async getAccessUrl(request: AccessUrlRequest): Promise<AccessUrlResult> {
    const cid = await this.getCIDForArtifact(request.artifactId);
    
    // Check availability across gateways
    const availableGateways = await this.checkGatewayAvailability(cid);
    
    if (availableGateways.length === 0) {
      throw new ArtifactUnavailableError(`Artifact ${request.artifactId} not available on any gateway`);
    }

    // Return fastest available gateway
    const url = availableGateways[0];
    
    return {
      url,
      signed: false,
      expiresAt: null,
      alternativeUrls: availableGateways.slice(1)
    };
  }

  private async replicateToPinningServices(
    cid: string, 
    options: PinningOptions
  ): Promise<PinningResult[]> {
    const results: PinningResult[] = [];
    
    // Pin to multiple services for redundancy
    const servicesToUse = this.pinningServices.slice(0, options.replicationFactor);
    
    const pinPromises = servicesToUse.map(async (service) => {
      try {
        const result = await service.pin(cid, options);
        return { service: service.name, success: true, result };
      } catch (error) {
        return { service: service.name, success: false, error: error.message };
      }
    });

    const pinResults = await Promise.allSettled(pinPromises);
    
    for (const result of pinResults) {
      if (result.status === 'fulfilled') {
        results.push(result.value);
      }
    }

    return results;
  }
}
```

## III. Artifact Indexing & Search

```typescript
class ArtifactIndexer {
  private readonly searchEngine: SearchEngine;
  private readonly metadataStore: MetadataStore;
  private readonly fullTextExtractor: FullTextExtractor;
  private readonly embeddingGenerator: EmbeddingGenerator;

  constructor(config: IndexingConfig) {
    this.searchEngine = new SearchEngine(config.search);
    this.metadataStore = new MetadataStore(config.metadata);
    this.fullTextExtractor = new FullTextExtractor(config.extraction);
    this.embeddingGenerator = new EmbeddingGenerator(config.embeddings);
  }

  async indexArtifact(indexRequest: ArtifactIndexRequest): Promise<IndexResult> {
    const startTime = Date.now();

    try {
      // Store metadata
      await this.metadataStore.store(indexRequest.id, indexRequest.metadata);

      // Generate embeddings for semantic search
      const embeddings = await this.embeddingGenerator.generateEmbeddings({
        text: indexRequest.searchableContent,
        metadata: indexRequest.metadata
      });

      // Create search document
      const searchDocument: SearchDocument = {
        id: indexRequest.id,
        title: indexRequest.metadata.fileName,
        content: indexRequest.fullTextContent,
        searchableContent: indexRequest.searchableContent,
        metadata: indexRequest.metadata,
        tags: indexRequest.tags,
        embeddings: embeddings.vector,
        createdAt: indexRequest.metadata.uploadedAt,
        type: indexRequest.metadata.type,
        mimeType: indexRequest.metadata.mimeType,
        fileSize: indexRequest.metadata.fileSize,
        uploadedBy: indexRequest.metadata.uploadedBy
      };

      // Index in search engine
      await this.searchEngine.index(searchDocument);

      return {
        success: true,
        artifactId: indexRequest.id,
        indexTime: Date.now() - startTime,
        embeddingGenerated: true,
        indexedAt: new Date().toISOString()
      };
    } catch (error) {
      return {
        success: false,
        artifactId: indexRequest.id,
        error: error.message,
        indexTime: Date.now() - startTime
      };
    }
  }

  async search(searchRequest: SearchRequest): Promise<SearchResult> {
    const startTime = Date.now();

    // Build search query
    const query = await this.buildSearchQuery(searchRequest);

    // Execute search
    const results = await this.searchEngine.search(query);

    // Apply access filtering
    const filteredResults = await this.applyAccessFiltering(
      results,
      searchRequest.permissions
    );

    // Enhance results with metadata
    const enhancedResults = await this.enhanceSearchResults(filteredResults);

    return {
      artifacts: enhancedResults,
      totalCount: results.totalCount,
      searchTime: Date.now() - startTime,
      searchId: this.generateSearchId(),
      facets: results.facets
    };
  }

  private async buildSearchQuery(request: SearchRequest): Promise<SearchQuery> {
    const query: SearchQuery = {
      text: request.query,
      filters: [],
      sort: request.sortBy || 'relevance',
      limit: request.limit || 20,
      offset: request.offset || 0
    };

    // Add filters
    if (request.filters.type) {
      query.filters.push({ field: 'type', value: request.filters.type });
    }
    if (request.filters.mimeType) {
      query.filters.push({ field: 'mimeType', value: request.filters.mimeType });
    }
    if (request.filters.uploadedBy) {
      query.filters.push({ field: 'uploadedBy', value: request.filters.uploadedBy });
    }
    if (request.filters.tags && request.filters.tags.length > 0) {
      query.filters.push({ field: 'tags', value: request.filters.tags, operator: 'in' });
    }
    if (request.filters.dateRange) {
      query.filters.push({
        field: 'createdAt',
        value: request.filters.dateRange,
        operator: 'range'
      });
    }

    // Generate embeddings for semantic search if query provided
    if (request.query && request.query.length > 0) {
      const embeddings = await this.embeddingGenerator.generateEmbeddings({
        text: request.query
      });
      query.embeddings = embeddings.vector;
    }

    return query;
  }
}
```

## IV. Expiry & Lifecycle Management

```typescript
class ExpiryManager {
  private readonly expiryStore: ExpiryStore;
  private readonly storageManager: StorageManager;
  private readonly archiveManager: ArchiveManager;
  private readonly notificationService: NotificationService;
  private readonly scheduler: TaskScheduler;

  constructor(config: ExpiryConfig) {
    this.expiryStore = new ExpiryStore(config.storage);
    this.storageManager = new StorageManager(config.storage);
    this.archiveManager = new ArchiveManager(config.archive);
    this.notificationService = new NotificationService(config.notifications);
    this.scheduler = new TaskScheduler(config.scheduler);
    
    // Schedule cleanup tasks
    this.scheduleCleanupTasks();
  }

  async setExpiry(
    artifactId: string,
    expiryPolicy: ExpiryPolicy
  ): Promise<ExpirySetResult> {
    const expiryRecord: ExpiryRecord = {
      artifactId,
      expiresAt: expiryPolicy.expiresAt,
      policy: expiryPolicy.policy,
      actions: expiryPolicy.actions || ['delete'],
      notifications: expiryPolicy.notifications || [],
      createdAt: new Date().toISOString(),
      status: 'active'
    };

    await this.expiryStore.setExpiry(artifactId, expiryRecord);

    // Schedule notification reminders
    if (expiryPolicy.notifications) {
      await this.scheduleNotifications(artifactId, expiryPolicy.notifications);
    }

    return {
      success: true,
      artifactId,
      expiresAt: expiryPolicy.expiresAt,
      scheduledAt: new Date().toISOString()
    };
  }

  async runCleanupTask(): Promise<CleanupResult> {
    const startTime = Date.now();
    const expiredArtifacts = await this.expiryStore.getExpiredArtifacts();
    
    const results: CleanupItemResult[] = [];

    for (const artifact of expiredArtifacts) {
      try {
        const itemResult = await this.processExpiredArtifact(artifact);
        results.push(itemResult);
      } catch (error) {
        results.push({
          artifactId: artifact.artifactId,
          success: false,
          error: error.message,
          actions: []
        });
      }
    }

    const successCount = results.filter(r => r.success).length;
    const failureCount = results.length - successCount;

    return {
      success: true,
      processedCount: results.length,
      successCount,
      failureCount,
      results,
      executionTime: Date.now() - startTime,
      executedAt: new Date().toISOString()
    };
  }

  private async processExpiredArtifact(
    expiryRecord: ExpiryRecord
  ): Promise<CleanupItemResult> {
    const actions: string[] = [];

    // Archive if specified
    if (expiryRecord.actions.includes('archive')) {
      await this.archiveManager.archiveArtifact(expiryRecord.artifactId);
      actions.push('archived');
    }

    // Delete if specified
    if (expiryRecord.actions.includes('delete')) {
      await this.storageManager.deleteArtifact(expiryRecord.artifactId);
      actions.push('deleted');
    }

    // Send final notification
    if (expiryRecord.notifications.length > 0) {
      await this.notificationService.sendExpiryNotification({
        artifactId: expiryRecord.artifactId,
        actions,
        recipients: expiryRecord.notifications
      });
      actions.push('notified');
    }

    // Update expiry record
    await this.expiryStore.markProcessed(expiryRecord.artifactId);

    return {
      artifactId: expiryRecord.artifactId,
      success: true,
      actions,
      processedAt: new Date().toISOString()
    };
  }

  private scheduleCleanupTasks(): void {
    // Daily cleanup at 2 AM
    this.scheduler.schedule('0 2 * * *', async () => {
      await this.runCleanupTask();
    });

    // Weekly archive cleanup
    this.scheduler.schedule('0 3 * * 0', async () => {
      await this.archiveManager.runArchiveCleanup();
    });
  }
}
```

## Cross-References

- **Related Systems**: [Agent Memory Protocols](./agent-memory-protocols.md), [Prompt Management System](./prompt-management-system.md)
- **Implementation Guides**: [Storage Configuration](../current/storage-configuration.md), [Security Scanning](../current/security-scanning.md)
- **Configuration**: [Artifact Settings](../current/artifact-settings.md), [Storage Backends](../current/storage-backends.md)

## Changelog

- **v2.1.0** (2024-12-28): Complete TypeScript implementation with multi-backend support
- **v2.0.0** (2024-12-27): Enhanced with security scanning and lifecycle management
- **v1.0.0** (2024-06-20): Initial artifact storage system

---

*This document is part of the Kind AI Documentation System - providing comprehensive artifact management for the kAI ecosystem.* 