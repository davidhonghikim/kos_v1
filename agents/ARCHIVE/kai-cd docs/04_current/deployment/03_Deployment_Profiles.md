---
title: "Deployment Profiles"
description: "Standardized deployment configurations for different environments and use cases"
category: "deployment"
subcategory: "configuration"
context: "current_implementation"
implementation_status: "complete"
decision_scope: "medium"
complexity: "medium"
last_updated: "2025-01-20"
code_references:
  - "config/profiles/"
  - "public/manifest.json"
  - "background.js"
related_documents:
  - "./01_deployment-architecture.md"
  - "./02_installation-and-setup.md"
  - "../implementation/02_configuration-management.md"
dependencies: ["YAML", "JSON", "Chrome Extension APIs", "Firefox Add-on APIs"]
breaking_changes: false
agent_notes: "Deployment profiles define environment-specific configurations - use for different deployment scenarios"
---

# Deployment Profiles

## Agent Context
**For AI Agents**: Complete deployment profiles documentation covering environment-specific deployment configurations and profile management strategies. Use this when implementing deployment profiles, understanding environment configuration, planning deployment strategies, or configuring environment-specific deployments. Essential reference for all deployment profile work.

**Implementation Notes**: Contains deployment profile patterns, environment configuration strategies, profile management systems, and deployment customization approaches. Includes detailed profile configuration and environment-specific deployment patterns.
**Quality Requirements**: Keep deployment profiles and environment configurations synchronized with actual deployment processes. Maintain accuracy of profile management and environment-specific deployment strategies.
**Integration Points**: Foundation for environment deployment, links to deployment architecture, configuration management, and environment strategies for comprehensive deployment profile coverage.

## Quick Summary
Deployment profiles define standardized configurations for deploying Kai-CD across different environments and use cases, from simple browser extension installation to complex distributed kOS mesh deployments.

## Overview

Deployment profiles define standardized configurations for deploying Kai-CD across different environments and use cases. The system supports multiple deployment modes from simple browser extension installation to complex distributed kOS mesh deployments.

## Current Deployment Profiles

### Development Profile

**Target**: Local development and testing

```yaml
# config/profiles/development.yaml
profile:
  name: "development"
  environment: "dev"
  debug: true
  
services:
  enabled:
    - logger
    - vault
    - ui
  
configuration:
  hot_reload: true
  debug_mode: true
  console_logging: true
  
security:
  strict_mode: false
  allow_unsafe_eval: true
  
storage:
  type: "local"
  persistence: false
```

**Characteristics**:
- Hot reloading enabled
- Debug logging active
- Relaxed security for development
- Local storage only
- No persistence between sessions

### Production Profile

**Target**: End-user browser extension deployment

```yaml
# config/profiles/production.yaml
profile:
  name: "production"
  environment: "prod"
  debug: false
  
services:
  enabled:
    - logger
    - vault
    - ui
    - analytics
  
configuration:
  hot_reload: false
  debug_mode: false
  console_logging: false
  
security:
  strict_mode: true
  allow_unsafe_eval: false
  content_security_policy: "strict"
  
storage:
  type: "encrypted"
  persistence: true
  backup_enabled: true
```

**Characteristics**:
- Optimized for performance
- Security hardened
- Encrypted storage
- Analytics enabled
- Full persistence

### Testing Profile

**Target**: Automated testing and CI/CD

```yaml
# config/profiles/testing.yaml
profile:
  name: "testing"
  environment: "test"
  debug: true
  
services:
  enabled:
    - logger
    - vault
    - ui
    - test_harness
  
configuration:
  hot_reload: false
  debug_mode: true
  console_logging: true
  test_mode: true
  
security:
  strict_mode: false
  allow_test_overrides: true
  
storage:
  type: "memory"
  persistence: false
  
testing:
  mock_services: true
  simulate_errors: true
  performance_monitoring: true
```

**Characteristics**:
- Mock services for isolation
- Error simulation capabilities
- Performance monitoring
- Memory-only storage
- Test-specific overrides

## Browser Extension Deployment

### Chrome Web Store Deployment

```typescript
// manifest.json configuration
{
  "manifest_version": 3,
  "name": "Kai-CD",
  "version": "1.0.0",
  "permissions": [
    "storage",
    "activeTab",
    "scripting"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"]
  }],
  "web_accessible_resources": [{
    "resources": ["assets/*"],
    "matches": ["<all_urls>"]
  }]
}
```

### Firefox Add-on Deployment

```typescript
// manifest.json (Firefox-specific)
{
  "manifest_version": 2,
  "name": "Kai-CD",
  "version": "1.0.0",
  "permissions": [
    "storage",
    "activeTab",
    "<all_urls>"
  ],
  "background": {
    "scripts": ["background.js"],
    "persistent": false
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"]
  }]
}
```

## Enterprise Deployment Profiles

### Corporate Profile

**Target**: Enterprise environments with strict security requirements

```yaml
# config/profiles/corporate.yaml
profile:
  name: "corporate"
  environment: "enterprise"
  compliance: "strict"
  
services:
  enabled:
    - logger
    - vault
    - ui
    - audit
    - compliance
  
configuration:
  audit_logging: true
  compliance_mode: true
  data_retention: 365
  
security:
  strict_mode: true
  encryption: "AES-256"
  certificate_pinning: true
  
storage:
  type: "encrypted"
  backup_frequency: "daily"
  retention_policy: "7_years"
  
compliance:
  gdpr: true
  hipaa: true
  sox: true
```

### Government Profile

**Target**: Government and high-security environments

```yaml
# config/profiles/government.yaml
profile:
  name: "government"
  environment: "gov"
  security_level: "high"
  
services:
  enabled:
    - logger
    - vault
    - ui
    - security_monitor
    - compliance
  
configuration:
  fips_mode: true
  audit_everything: true
  
security:
  encryption: "AES-256-GCM"
  key_derivation: "PBKDF2"
  certificate_validation: "strict"
  
storage:
  type: "encrypted"
  wipe_on_exit: true
  
compliance:
  fedramp: true
  fisma: true
```

## Future kOS Deployment Profiles

### Mesh Node Profile

**Target**: Individual nodes in kOS mesh network

```yaml
# config/profiles/mesh_node.yaml
profile:
  name: "mesh_node"
  environment: "kos"
  node_type: "standard"
  
services:
  enabled:
    - agent_runtime
    - mesh_coordinator
    - trust_manager
    - knowledge_graph
  
mesh:
  discovery: "auto"
  routing: "adaptive"
  redundancy: 3
  
agents:
  max_concurrent: 10
  sandbox_mode: true
  trust_verification: true
  
storage:
  distributed: true
  replication_factor: 3
```

### Orchestrator Profile

**Target**: Central coordination nodes in kOS mesh

```yaml
# config/profiles/orchestrator.yaml
profile:
  name: "orchestrator"
  environment: "kos"
  node_type: "orchestrator"
  
services:
  enabled:
    - agent_runtime
    - mesh_coordinator
    - trust_manager
    - knowledge_graph
    - workflow_engine
    - resource_manager
  
orchestration:
  max_agents: 100
  delegation_depth: 5
  consensus_algorithm: "raft"
  
mesh:
  leadership: true
  coordination: true
  
storage:
  type: "distributed"
  consistency: "strong"
```

### Edge Profile

**Target**: Edge computing and IoT deployments

```yaml
# config/profiles/edge.yaml
profile:
  name: "edge"
  environment: "edge"
  resource_constrained: true
  
services:
  enabled:
    - minimal_agent_runtime
    - edge_coordinator
    - local_storage
  
constraints:
  memory_limit: "512MB"
  cpu_limit: "1_core"
  storage_limit: "2GB"
  
agents:
  max_concurrent: 3
  lightweight_mode: true
  
connectivity:
  offline_capable: true
  sync_on_connect: true
```

## Deployment Automation

### Docker Deployment

```dockerfile
# Dockerfile for kOS deployment
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  kai-cd:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PROFILE=production
    volumes:
      - ./config:/app/config
      - ./data:/app/data
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kai-cd
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kai-cd
  template:
    metadata:
      labels:
        app: kai-cd
    spec:
      containers:
      - name: kai-cd
        image: kai-cd:latest
        ports:
        - containerPort: 3000
        env:
        - name: PROFILE
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Configuration Management

### Profile Selection

```typescript
// src/config/ProfileManager.ts
export class ProfileManager {
  private static instance: ProfileManager;
  private currentProfile: DeploymentProfile;
  
  static getInstance(): ProfileManager {
    if (!ProfileManager.instance) {
      ProfileManager.instance = new ProfileManager();
    }
    return ProfileManager.instance;
  }
  
  loadProfile(profileName: string): DeploymentProfile {
    const profilePath = `config/profiles/${profileName}.yaml`;
    const profile = this.loadYamlConfig(profilePath);
    
    this.validateProfile(profile);
    this.currentProfile = profile;
    
    return profile;
  }
  
  getCurrentProfile(): DeploymentProfile {
    return this.currentProfile;
  }
}
```

### Environment Detection

```typescript
// src/config/EnvironmentDetector.ts
export class EnvironmentDetector {
  static detectEnvironment(): string {
    // Browser extension detection
    if (typeof chrome !== 'undefined' && chrome.runtime) {
      return 'browser_extension';
    }
    
    // Node.js environment
    if (typeof process !== 'undefined' && process.versions?.node) {
      return process.env.NODE_ENV || 'development';
    }
    
    // Web environment
    if (typeof window !== 'undefined') {
      return 'web';
    }
    
    return 'unknown';
  }
  
  static selectDefaultProfile(): string {
    const env = this.detectEnvironment();
    
    switch (env) {
      case 'browser_extension':
        return 'production';
      case 'development':
        return 'development';
      case 'test':
        return 'testing';
      default:
        return 'production';
    }
  }
}
```

## Monitoring and Observability

### Health Checks

```typescript
// src/deployment/HealthCheck.ts
export class DeploymentHealthCheck {
  async checkHealth(): Promise<HealthStatus> {
    const checks = [
      this.checkServices(),
      this.checkStorage(),
      this.checkConfiguration(),
      this.checkSecurity()
    ];
    
    const results = await Promise.all(checks);
    
    return {
      status: results.every(r => r.healthy) ? 'healthy' : 'unhealthy',
      checks: results,
      timestamp: new Date().toISOString()
    };
  }
  
  private async checkServices(): Promise<HealthCheckResult> {
    // Service health verification
    return { name: 'services', healthy: true };
  }
}
```

### Metrics Collection

```typescript
// src/deployment/MetricsCollector.ts
export class DeploymentMetrics {
  collectMetrics(): DeploymentMetrics {
    return {
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      cpu: process.cpuUsage(),
      profile: ProfileManager.getInstance().getCurrentProfile().name,
      environment: EnvironmentDetector.detectEnvironment(),
      timestamp: new Date().toISOString()
    };
  }
}
```

## Security Considerations

### Profile Security

```typescript
// src/security/ProfileSecurity.ts
export class ProfileSecurity {
  validateProfile(profile: DeploymentProfile): void {
    // Validate security settings
    if (profile.environment === 'production' && !profile.security.strict_mode) {
      throw new Error('Production profile must have strict security mode');
    }
    
    // Validate encryption requirements
    if (profile.security.encryption && !this.isValidEncryption(profile.security.encryption)) {
      throw new Error('Invalid encryption configuration');
    }
  }
  
  private isValidEncryption(encryption: string): boolean {
    const validAlgorithms = ['AES-256', 'AES-256-GCM', 'ChaCha20-Poly1305'];
    return validAlgorithms.includes(encryption);
  }
}
```

## Implementation Roadmap

### Phase 1: Enhanced Current Profiles
- Implement dynamic profile switching
- Add profile validation and security checks
- Create deployment automation scripts
- Build monitoring and health checks

### Phase 2: kOS Mesh Profiles
- Develop mesh node deployment profiles
- Implement orchestrator configurations
- Create edge computing profiles
- Build distributed deployment tools

### Phase 3: Advanced Deployment
- Implement zero-downtime deployments
- Create auto-scaling configurations
- Build multi-region deployments
- Develop disaster recovery profiles

## Code References

- Profile management: `src/config/ProfileManager.ts`
- Environment detection: `src/config/EnvironmentDetector.ts`
- Deployment automation: `scripts/deploy/`
- Configuration validation: `src/config/validation/`

## Configuration Examples

```yaml
# Custom profile example
profile:
  name: "custom"
  environment: "staging"
  
services:
  enabled:
    - logger
    - vault
    - ui
    - analytics
  
configuration:
  debug_mode: false
  performance_monitoring: true
  
security:
  strict_mode: true
  audit_logging: true
  
storage:
  type: "encrypted"
  backup_enabled: true
```

---

