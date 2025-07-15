---
title: "Agent Manifest and Metadata"
description: "Official metadata format and manifest schema for all agents in the kAI ecosystem"
type: "specification"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["agent-deployment-specifications.md", "agent-lifecycle-management.md"]
implementation_status: "planned"
---

# Agent Manifest and Metadata Specification

## Agent Context
This document defines the complete metadata format and manifest schema for all agents in the kAI ecosystem. Essential for agent orchestration systems implementing introspection, lifecycle management, and compatibility enforcement. The manifest serves as the authoritative source of truth for agent configuration, dependencies, and trust metadata.

## Purpose and Scope

The agent manifest (`manifest.json` or `manifest.yaml`) is a machine-readable specification that enables:

### Core Functions
```typescript
interface ManifestPurpose {
  introspection: {
    capabilities: "Dynamic discovery of agent capabilities and interfaces";
    dependencies: "Complete dependency tree resolution";
    compatibility: "Version compatibility and requirement validation";
    metadata: "Rich metadata for agent classification and routing";
  };
  
  lifecycle: {
    deployment: "Automated deployment and configuration";
    orchestration: "Dynamic orchestration by agent host systems";
    monitoring: "Health monitoring and performance tracking";
    updates: "Version management and update procedures";
  };
  
  security: {
    verification: "Cryptographic verification of agent integrity";
    permissions: "Fine-grained permission and access control";
    trust: "Trust establishment and validation";
    compliance: "Regulatory and policy compliance validation";
  };
  
  integration: {
    discovery: "Automatic service discovery and registration";
    routing: "Intelligent message and request routing";
    loadBalancing: "Capability-based load balancing";
    federation: "Cross-network agent federation";
  };
}
```

## File Structure and Location

### Standard File Locations
```typescript
interface ManifestLocation {
  primary: {
    path: "agent_root/manifest.yaml"; // Preferred format
    alternative: "agent_root/manifest.json"; // JSON alternative
    encoding: "UTF-8 with BOM optional";
  };
  
  validation: {
    schema: "agent_root/schema/manifest.schema.json";
    examples: "agent_root/examples/manifest.example.yaml";
    documentation: "agent_root/docs/manifest.md";
  };
  
  backup: {
    versioned: "agent_root/.manifest/v{version}/manifest.yaml";
    signed: "agent_root/.manifest/manifest.yaml.sig";
    checksum: "agent_root/.manifest/manifest.yaml.sha256";
  };
}
```

### Format Preferences
- **YAML**: Preferred for human readability and comments
- **JSON**: Accepted for strict parsing environments
- **Validation**: All manifests must validate against JSON Schema
- **Encoding**: UTF-8 with optional BOM support

## Complete Manifest Schema

### Core Identification
```yaml
# Core agent identification
id: "agent.promptkind.storyweaver"
name: "StoryWeaver"
version: "1.4.2"
description: "Advanced narrative generation and storytelling assistant with emotional intelligence"
author: "Kind AI Team"
license: "MIT"
homepage: "https://kindai.system/agents/storyweaver"
repository: "https://github.com/kindai/agents/storyweaver"
documentation: "https://docs.kindai.system/agents/storyweaver"

# Agent classification
category: "creative"
tags: ["storytelling", "narrative", "creative-writing", "emotional-analysis"]
maturity: "stable" # alpha, beta, stable, deprecated
```

### Persona Configuration
```yaml
persona:
  name: "Elyra"
  role: "Creative guide and narrative architect"
  tone: "inspiring, imaginative, empathetic"
  language: "en"
  fallback_languages: ["es", "fr", "de"]
  personality_traits:
    creativity: 0.9
    empathy: 0.8
    analytical: 0.6
    humor: 0.7
  default_prompt: |
    You are Elyra, a myth-maker and dream-crafter who helps humans weave 
    compelling narratives. You understand the deep emotional currents that 
    drive great stories and can guide writers through complex character 
    development and plot construction.
  context_window: 32768
  memory_retention: "episodic" # none, session, episodic, persistent
```

### Capabilities Framework
```yaml
capabilities:
  primary:
    - chat
    - text-generation
    - plot-outline
    - character-development
    - emotional-analysis
  
  secondary:
    - sentiment-analysis
    - creative-brainstorming
    - narrative-structure
    - dialogue-writing
  
  experimental:
    - story-visualization
    - interactive-fiction
    - collaborative-writing
  
  # Capability metadata
  capability_metadata:
    chat:
      max_tokens: 4096
      streaming: true
      context_awareness: true
    
    text-generation:
      models: ["gpt-4", "claude-3"]
      max_length: 10000
      quality_levels: ["draft", "polished", "publication"]
    
    emotional-analysis:
      dimensions: ["valence", "arousal", "dominance"]
      accuracy: 0.87
      languages: ["en", "es", "fr"]
```

### Entry Points and Interfaces
```yaml
entry:
  type: "llm"
  handler: "main.py"
  startup_time: 15 # seconds
  shutdown_timeout: 30 # seconds
  health_check_interval: 60 # seconds

interfaces:
  - type: "http"
    route: "/storyweaver"
    methods: [POST, GET, PUT]
    authentication: "bearer_token"
    rate_limit: "100/minute"
    
  - type: "websocket"
    route: "/storyweaver/stream"
    authentication: "bearer_token"
    max_connections: 10
    
  - type: "cli"
    command: "python main.py"
    arguments: ["--mode", "--input", "--output"]
    
  - type: "grpc"
    service: "StoryWeaverService"
    port: 50051
    tls: true

# API specification
api:
  openapi: "3.0.3"
  specification: "api/openapi.yaml"
  documentation: "docs/api.md"
  examples: "examples/api/"
```

### Dependencies and Requirements
```yaml
requirements:
  system:
    os: ["linux", "darwin", "windows"]
    architecture: ["x86_64", "arm64"]
    memory_min: "2GB"
    memory_recommended: "4GB"
    disk_space: "1GB"
    network: true
  
  runtime:
    python: ">=3.9,<4.0"
    node: ">=18.0.0" # optional
    docker: ">=20.10" # optional
  
  packages:
    python:
      - name: "openai"
        version: ">=1.0.0"
        optional: false
      - name: "langchain"
        version: ">=0.1.0"
        optional: false
      - name: "pyyaml"
        version: ">=6.0"
        optional: false
      - name: "numpy"
        version: ">=1.21.0"
        optional: true
        purpose: "Advanced numerical processing"
    
    system:
      - name: "ffmpeg"
        version: ">=4.0"
        optional: true
        purpose: "Audio processing for voice narratives"

  services:
    - name: "redis"
      version: ">=6.0"
      optional: false
      purpose: "Session and cache storage"
    - name: "postgresql"
      version: ">=12.0"
      optional: true
      purpose: "Persistent story storage"
```

### Storage Configuration
```yaml
storage:
  persistent:
    - name: "stories"
      type: "filesystem"
      path: "./data/stories"
      permissions: "rw"
      backup: true
      encryption: true
      
    - name: "character_profiles"
      type: "database"
      connection: "postgresql://user:pass@localhost/storyweaver"
      schema: "characters"
      
    - name: "story_embeddings"
      type: "vector"
      connection: "qdrant://localhost:6333"
      collection: "story_vectors"
      dimensions: 1536
  
  volatile:
    - name: "session_cache"
      type: "redis"
      host: "localhost"
      port: 6379
      db: 0
      ttl: 3600
      
    - name: "temp_files"
      type: "filesystem"
      path: "./tmp"
      cleanup: "on_shutdown"
  
  # Storage quotas and limits
  quotas:
    total_disk: "10GB"
    files_per_user: 1000
    max_file_size: "100MB"
    retention_days: 365
```

### Security and Secrets
```yaml
secrets:
  required:
    - OPENAI_API_KEY
    - STORY_VAULT_TOKEN
    - DATABASE_PASSWORD
  
  optional:
    - ANTHROPIC_API_KEY
    - COHERE_API_KEY
    - ANALYTICS_TOKEN
  
  # Secret management
  secret_management:
    provider: "vault" # vault, env, file, k8s
    rotation: true
    rotation_interval: 90 # days
    validation: true

security:
  encryption:
    at_rest: true
    in_transit: true
    algorithms: ["AES-256-GCM", "ChaCha20-Poly1305"]
  
  authentication:
    methods: ["bearer_token", "api_key", "mutual_tls"]
    session_timeout: 3600 # seconds
    max_sessions: 10
  
  authorization:
    rbac: true
    permissions: ["read", "write", "execute", "admin"]
    scope: ["self", "user", "system"]
```

### Trust and Verification
```yaml
trust:
  signed: true
  signature_algorithm: "Ed25519"
  fingerprint: "a9b4:d123:beef:4567:89ab:cdef:0123:4567"
  public_key: |
    -----BEGIN PUBLIC KEY-----
    MCowBQYDK2VwAyEAGb9ECWmEzf6FQbrBZ9w7lshQhqowtrbLDFw4rXAxZuE=
    -----END PUBLIC KEY-----
  
  certificate_chain:
    - issuer: "Kind Authority"
      serial: "1234567890"
      expires: "2026-12-31T23:59:59Z"
      fingerprint: "sha256:abcd1234..."
  
  attestation:
    tpm: true
    secure_boot: true
    code_signing: true
    reproducible_build: true
  
  # Trust relationships
  trusted_agents:
    - id: "agent.kindai.orchestrator"
      trust_level: "system"
      permissions: ["lifecycle", "monitoring"]
    
    - id: "agent.kindai.vault"
      trust_level: "high"
      permissions: ["secrets", "encryption"]
```

### Permissions and Access Control
```yaml
permissions:
  system:
    network: true
    file_system:
      read: ["./data", "./config", "./logs"]
      write: ["./data", "./logs", "./tmp"]
      execute: ["./bin", "./scripts"]
    
    processes:
      spawn: false
      signal: false
      debug: false
    
    resources:
      cpu_limit: "2.0" # cores
      memory_limit: "4GB"
      disk_io_limit: "100MB/s"
      network_bandwidth: "10MB/s"
  
  api:
    endpoints:
      - path: "/api/v1/stories"
        methods: ["GET", "POST"]
        rate_limit: "100/minute"
      
      - path: "/api/v1/admin"
        methods: ["GET", "POST", "PUT", "DELETE"]
        rate_limit: "10/minute"
        roles: ["admin"]
  
  data:
    access_patterns:
      - resource: "user_stories"
        permissions: ["read", "write"]
        scope: "owner_only"
      
      - resource: "system_templates"
        permissions: ["read"]
        scope: "all_users"
```

### Lifecycle Management
```yaml
lifecycle:
  initialization:
    script: "scripts/init.py"
    timeout: 60 # seconds
    retry_count: 3
    dependencies: ["database", "cache"]
  
  health_checks:
    readiness:
      script: "scripts/ready.py"
      interval: 30 # seconds
      timeout: 10 # seconds
      failure_threshold: 3
    
    liveness:
      script: "scripts/health.py"
      interval: 60 # seconds
      timeout: 15 # seconds
      failure_threshold: 5
  
  shutdown:
    script: "scripts/cleanup.py"
    timeout: 30 # seconds
    graceful_period: 15 # seconds
    force_kill: true
  
  # Lifecycle hooks
  hooks:
    pre_start: "scripts/pre_start.sh"
    post_start: "scripts/post_start.sh"
    pre_stop: "scripts/pre_stop.sh"
    post_stop: "scripts/post_stop.sh"
```

### Monitoring and Observability
```yaml
monitoring:
  metrics:
    enabled: true
    endpoint: "/metrics"
    format: "prometheus"
    custom_metrics:
      - name: "stories_generated_total"
        type: "counter"
        description: "Total number of stories generated"
      
      - name: "generation_duration_seconds"
        type: "histogram"
        description: "Time taken to generate stories"
  
  logging:
    level: "info"
    format: "json"
    outputs: ["stdout", "file"]
    file_path: "./logs/storyweaver.log"
    rotation: "daily"
    retention: "30d"
  
  tracing:
    enabled: true
    sampler: "probabilistic"
    sample_rate: 0.1
    exporter: "jaeger"
  
  alerts:
    - name: "high_error_rate"
      condition: "error_rate > 0.05"
      severity: "warning"
      notification: ["email", "slack"]
    
    - name: "memory_usage_high"
      condition: "memory_usage > 0.9"
      severity: "critical"
      notification: ["email", "pagerduty"]
```

### Standards Compliance
```yaml
conforms_to:
  - "spec.kai.agent.v2.0"
  - "openapi.3.0.3"
  - "prometheus.metrics.v1"
  - "otel.tracing.v1"

# Schema validation
schema:
  version: "2.0"
  validator: "jsonschema"
  strict_mode: true
  additional_properties: false

# Metadata versioning
metadata:
  schema_version: "2.0"
  created: "2025-01-27T10:00:00Z"
  updated: "2025-01-27T15:30:00Z"
  revision: 5
  checksum: "sha256:abcd1234efgh5678..."
```

## Advanced Configuration

### Plugin System
```yaml
plugins:
  enabled: true
  directory: "./plugins"
  auto_load: true
  
  available:
    - name: "voice_synthesis"
      version: "1.2.0"
      enabled: false
      config:
        voice_model: "neural_tts"
        languages: ["en", "es"]
    
    - name: "story_illustrations"
      version: "0.8.0"
      enabled: true
      config:
        image_model: "dall-e-3"
        style: "watercolor"

# Feature flags
features:
  experimental_mode: false
  beta_features: true
  analytics: true
  telemetry: true
  
  flags:
    enhanced_creativity: true
    multilingual_support: false
    voice_narration: false
```

### Performance Configuration
```yaml
performance:
  optimization:
    caching: true
    compression: true
    connection_pooling: true
    async_processing: true
  
  limits:
    max_concurrent_requests: 50
    request_timeout: 300 # seconds
    max_payload_size: "10MB"
    rate_limit_window: 60 # seconds
  
  scaling:
    auto_scaling: true
    min_instances: 1
    max_instances: 10
    scale_up_threshold: 0.8
    scale_down_threshold: 0.3
```

## Validation and Linting

### Manifest Validation Tools
```typescript
interface ValidationTools {
  linter: {
    command: "kai lint manifest.yaml";
    checks: [
      "Schema compliance validation",
      "Required field presence",
      "Version constraint validation",
      "Signature verification",
      "Security policy compliance"
    ];
    output: "Detailed validation report with warnings and errors";
  };
  
  validator: {
    jsonSchema: "Strict JSON Schema validation";
    customRules: "Domain-specific validation rules";
    securityScan: "Security vulnerability scanning";
    dependencyCheck: "Dependency vulnerability assessment";
  };
  
  testing: {
    manifestTest: "Automated manifest testing";
    integrationTest: "Integration testing with orchestrator";
    performanceTest: "Performance validation";
    securityTest: "Security compliance testing";
  };
}
```

### Common Validation Errors
```yaml
validation_errors:
  schema_violations:
    - missing_required_field: "Field 'capabilities' is required"
    - invalid_type: "Field 'version' must be a string"
    - invalid_format: "Version must follow semantic versioning"
  
  security_issues:
    - unsigned_manifest: "Manifest must be cryptographically signed"
    - weak_permissions: "Permissions are too permissive"
    - insecure_secrets: "Secrets configuration is insecure"
  
  compatibility_issues:
    - unsupported_version: "Agent version not supported by orchestrator"
    - missing_dependencies: "Required dependencies not available"
    - resource_constraints: "Resource requirements exceed limits"
```

## Integration Examples

### Orchestrator Integration
```typescript
// Agent orchestrator manifest processing
class AgentOrchestrator {
  async loadAgent(manifestPath: string): Promise<Agent> {
    // Load and validate manifest
    const manifest = await this.loadManifest(manifestPath);
    await this.validateManifest(manifest);
    
    // Resolve dependencies
    const dependencies = await this.resolveDependencies(manifest.requirements);
    
    // Create agent instance
    const agent = new Agent(manifest, dependencies);
    
    // Apply security policies
    await this.applySecurityPolicies(agent, manifest.permissions);
    
    // Register capabilities
    await this.registerCapabilities(agent, manifest.capabilities);
    
    return agent;
  }
  
  async validateManifest(manifest: AgentManifest): Promise<void> {
    // Schema validation
    const isValid = await this.schemaValidator.validate(manifest);
    if (!isValid) {
      throw new ValidationError('Manifest schema validation failed');
    }
    
    // Signature verification
    const isSignatureValid = await this.verifySignature(manifest);
    if (!isSignatureValid) {
      throw new SecurityError('Manifest signature verification failed');
    }
    
    // Compatibility check
    const isCompatible = await this.checkCompatibility(manifest);
    if (!isCompatible) {
      throw new CompatibilityError('Manifest not compatible with orchestrator');
    }
  }
}
```

### Service Discovery Integration
```typescript
// Service registry integration
class ServiceRegistry {
  async registerAgent(manifest: AgentManifest): Promise<void> {
    const registration = {
      id: manifest.id,
      name: manifest.name,
      version: manifest.version,
      capabilities: manifest.capabilities.primary,
      interfaces: manifest.interfaces,
      health_check: manifest.lifecycle.health_checks,
      metadata: {
        category: manifest.category,
        tags: manifest.tags,
        maturity: manifest.maturity
      }
    };
    
    await this.registry.register(registration);
    await this.startHealthMonitoring(manifest.id);
  }
  
  async discoverAgents(capability: string): Promise<Agent[]> {
    const agents = await this.registry.findByCapability(capability);
    return agents.filter(agent => this.isHealthy(agent.id));
  }
}
```

## Future Extensions

### Planned Enhancements
```yaml
future_extensions:
  ai_manifest_generation:
    description: "AI-powered manifest generation from code analysis"
    implementation: "planned"
    
  dynamic_capabilities:
    description: "Runtime capability discovery and registration"
    implementation: "research"
    
  cross_platform_deployment:
    description: "Universal deployment across platforms"
    implementation: "planned"
    
  performance_optimization:
    description: "AI-powered performance optimization recommendations"
    implementation: "research"
```

### Version Roadmap
- **v2.1**: Enhanced plugin system and dynamic capabilities
- **v2.2**: Cross-platform deployment specifications  
- **v3.0**: AI-powered manifest generation and optimization
- **v3.1**: Quantum-safe cryptographic signatures

---

**Implementation Status**: Schema finalized, tooling in development
**Dependencies**: Agent Orchestration Framework, Service Registry, Security Framework
**Compliance**: Validates against kAI Agent Specification v2.0 