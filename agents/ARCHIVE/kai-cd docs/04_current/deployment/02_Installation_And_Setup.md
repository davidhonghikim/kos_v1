---
title: "Installation and Setup Guide"
description: "Complete installation and initialization system from current Chrome extension to future kOS deployment"
category: "deployment"
subcategory: "installation"
context: "current_implementation"
implementation_status: "complete"
decision_scope: "medium"
complexity: "medium"
last_updated: "2025-01-20"
code_references:
  - "package.json"
  - "vite.config.ts"
  - "public/manifest.json"
  - "scripts/"
related_documents:
  - "./01_deployment-architecture.md"
  - "../implementation/02_configuration-management.md"
  - "../implementation/03_advanced-configuration.md"
  - "../../bridge/03_decision-framework.md"
dependencies: ["Node.js", "Chrome", "Vite", "TypeScript"]
breaking_changes: false
agent_notes: "Complete installation workflows for current Chrome extension and future kOS environments"
---

# Installation and Setup Guide

## Agent Context
**For AI Agents**: Complete installation and setup guide covering system installation procedures, configuration steps, and setup verification processes. Use this when implementing installation procedures, understanding setup requirements, planning deployment setup, or configuring system installations. Essential reference for all installation and setup work.

**Implementation Notes**: Contains installation procedures, setup configuration steps, system verification processes, and deployment setup strategies. Includes detailed installation workflows and setup verification patterns.
**Quality Requirements**: Keep installation procedures and setup steps synchronized with actual installation process. Maintain accuracy of setup requirements and configuration procedures.
**Integration Points**: Foundation for system deployment, links to deployment architecture, configuration management, and setup verification for comprehensive installation coverage.

## Quick Summary
Complete installation and setup framework covering evolution from current Chrome extension installation to sophisticated kOS deployment workflows with environment detection, dependency management, and configuration initialization.

## Current Implementation: Chrome Extension

### Prerequisites
- Chrome/Chromium browser (version 88+)
- Node.js >= 18.x (for development)
- npm or yarn package manager
- 4GB+ RAM recommended
- 100MB+ available disk space

### Development Setup

#### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/user/kai-cd.git
cd kai-cd

# Install dependencies
npm install

# Copy configuration template
cp src/config/user.env.example.ts src/config/user.env.ts
```

#### 2. Configuration
Current three-tier configuration system:
- `src/config/system.env.ts` - System defaults
- `src/config/user.env.ts` - User overrides (gitignored)
- `src/config/env.ts` - Merged configuration

```typescript
// Example user.env.ts
export const userConfig = {
  networking: {
    localIP: '192.168.1.159',
    remoteIP: '192.168.1.180'
  },
  services: {
    defaultModel: 'llama3.2:latest'
  }
};
```

#### 3. Build Process
```bash
# Development build
npm run dev

# Production build
npm run build

# Type checking
npm run typecheck

# Linting
npm run lint
```

#### 4. Extension Installation
1. Open Chrome Extensions (`chrome://extensions/`)
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `dist/` directory
5. Extension loads with manifest v3 configuration

### Current Build System

#### Vite Configuration
```typescript
// vite.config.ts highlights
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: 'main.html',
        popup: 'popup.html',
        sidepanel: 'sidepanel.html',
        background: 'src/background/main.ts'
      }
    }
  }
});
```

#### Manifest Configuration
```json
{
  "manifest_version": 3,
  "name": "Kai-CD",
  "version": "1.0.0",
  "permissions": ["storage", "sidePanel", "activeTab"],
  "host_permissions": ["http://localhost/*", "http://192.168.*/*"]
}
```

## Future Evolution: kOS Installation System

### Installation Modes

#### 1. Standalone Mode (kAI-CD Enhanced)
- Enhanced browser extension with local services
- Embedded vector database (Chroma/Qdrant)
- Local LLM support (Ollama integration)
- Secure vault with biometric unlock

#### 2. Developer Node
- Full development environment
- Service mesh orchestration
- Plugin development tools
- Verbose logging and debugging

#### 3. Federation Node
- Multi-user access support
- KLP (Kind Link Protocol) enabled
- Public service registry
- JWT/OAuth2 authentication

#### 4. Enterprise Grid
- Kubernetes orchestration
- Auto-scaling capabilities
- LDAP/SAML integration
- Compliance and audit logging

### Installation Workflow Architecture

#### Environment Detection System
```typescript
interface EnvironmentDetector {
  detectOS(): 'linux' | 'macos' | 'windows';
  detectRuntime(): 'browser' | 'node' | 'docker';
  detectGPU(): 'nvidia' | 'amd' | 'none';
  checkDependencies(): DependencyStatus[];
  validateRequirements(): ValidationResult;
}
```

#### Profile-Based Installation
```yaml
# Installation Profile Schema
profile: "developer_node"
services:
  vector_db: "qdrant"
  llm_backend: "ollama"
  vault: true
  pubsub: "redis"
  log_level: "debug"
agent_roles:
  - orchestrator
  - chat_agent
  - file_agent
  - planner
ports:
  api: 8000
  frontend: 9991
  vault: 3000
  qdrant: 6333
```

#### Installation CLI Framework
```bash
# Future kOS installation commands
npx kind init                 # Interactive installer
npx kind install --profile dev    # Profile-based install
npx kind upgrade              # System upgrade
npx kind uninstall           # Clean uninstall
npx kind status              # System health check
```

### Container-Based Deployment

#### Docker Compose Architecture
```yaml
version: '3.8'
services:
  kos-core:
    build: ./kos-core
    environment:
      - NODE_ENV=production
      - VAULT_ENABLED=true
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - qdrant

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: kindai
      POSTGRES_USER: kuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data

  qdrant:
    image: qdrant/qdrant
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
```

### Configuration Management Evolution

#### Centralized Config Service (kConfigD)
```typescript
interface ConfigService {
  validateProfile(profile: InstallProfile): ValidationResult;
  applyConfiguration(config: SystemConfig): Promise<void>;
  publishConfigChanges(changes: ConfigChange[]): void;
  createSnapshot(): ConfigSnapshot;
  rollbackToSnapshot(snapshot: ConfigSnapshot): Promise<void>;
}
```

#### Configuration Directory Structure
```text
/config/
├── profiles/
│   ├── standalone.yaml
│   ├── developer_node.yaml
│   ├── federation_node.yaml
│   └── enterprise.yaml
├── system.env                  # Global environment variables
├── secrets.env                 # Vaulted API keys and tokens
├── klp/
│   ├── peers.list              # Approved federation peers
│   └── klp_settings.yaml       # Kind Link Protocol settings
├── agents/
│   ├── schedulerAgent.yaml     # Role and settings per agent
│   └── translatorAgent.yaml
├── plugins/
│   ├── audit_log.yaml
│   └── logger.yaml
└── themes/
    └── ui_theme_dark.yaml      # UI preferences per node/user
```

### Service Health and Validation

#### Health Check System
```typescript
interface HealthChecker {
  checkCoreServices(): Promise<ServiceHealth[]>;
  validateEndpoints(): Promise<EndpointStatus[]>;
  runDiagnostics(): Promise<DiagnosticReport>;
  generateHealthReport(): HealthReport;
}

interface ServiceHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  lastCheck: Date;
  responseTime: number;
  details: Record<string, any>;
}
```

#### Post-Installation Validation
```bash
# Validation workflow
✅ Core services responding
✅ Database connectivity
✅ Vector store accessible
✅ Vault initialization
✅ Agent registration
✅ KLP handshake (if federation enabled)
✅ UI accessibility
```

### Security and Initialization

#### Secure Initialization Process
1. **Environment Preparation**
   - OS-level security checks
   - Dependency validation
   - Network security assessment

2. **Cryptographic Setup**
   - Key generation (Ed25519)
   - Vault initialization
   - Certificate management

3. **Service Registration**
   - Agent identity creation
   - Service discovery setup
   - Trust relationship establishment

4. **Configuration Finalization**
   - Profile application
   - Secret injection
   - Configuration validation

### Upgrade and Maintenance

#### Upgrade Pathways
```typescript
interface UpgradeManager {
  checkForUpdates(): Promise<UpdateInfo[]>;
  validateUpgrade(version: string): Promise<UpgradeValidation>;
  backupCurrentState(): Promise<BackupResult>;
  applyUpgrade(upgrade: UpgradePackage): Promise<UpgradeResult>;
  rollbackUpgrade(backupId: string): Promise<RollbackResult>;
}
```

#### Maintenance Operations
- Configuration drift detection
- Service health monitoring
- Log rotation and cleanup
- Performance optimization
- Security patch application

### Error Handling and Recovery

#### Installation Error Recovery
```typescript
interface InstallationRecovery {
  detectFailures(): InstallationFailure[];
  suggestFixes(failures: InstallationFailure[]): Fix[];
  applyAutomaticFixes(): Promise<FixResult[]>;
  generateDiagnosticReport(): DiagnosticReport;
  requestUserIntervention(issue: ComplexIssue): Promise<UserResponse>;
}
```

#### Common Issues and Solutions
- Dependency conflicts → Version resolution
- Port conflicts → Dynamic port allocation
- Permission issues → Privilege escalation prompts
- Network connectivity → Proxy configuration
- Resource constraints → Resource optimization

## Implementation Roadmap

### Phase 1: Enhanced Chrome Extension (Current → v1.1)
- ✅ Basic installation working
- 🔄 Improved configuration management
- 📋 Health check system
- 📋 Error recovery mechanisms

### Phase 2: Hybrid Deployment (v1.2)
- 📋 Docker container support
- 📋 Local service orchestration
- 📋 Profile-based installation
- 📋 CLI installer

### Phase 3: Full kOS Integration (v2.0)
- 📋 Federation protocols
- 📋 Multi-node deployment
- 📋 Enterprise features
- 📋 Advanced security

### Phase 4: Advanced Orchestration (v2.1+)
- 📋 Kubernetes support
- 📋 Auto-scaling
- 📋 GitOps integration
- 📋 Zero-downtime updates

## Agent Implementation Guidelines

### For Current Development
1. **Use existing configuration system** via `src/config/env.ts`
2. **Follow build process** with `npm run build`
3. **Test installation** in Chrome developer mode
4. **Validate services** through ServiceManagement UI

### For Future Enhancement
1. **Design profile-aware** installation logic
2. **Implement health checks** for all services
3. **Create upgrade pathways** with rollback support
4. **Build error recovery** mechanisms

### For System Integration
1. **Plan containerization** strategy
2. **Design service mesh** architecture
3. **Implement federation** protocols
4. **Create enterprise** deployment options

## Related Documentation
- [Deployment Architecture](./01_deployment-architecture.md) - Overall deployment strategy
- [Configuration Management](../implementation/02_configuration-management.md) - Configuration system details
- [Service Architecture](../services/01_service-architecture.md) - Service integration patterns
- [Security Framework](../security/01_security-framework.md) - Security implementation

