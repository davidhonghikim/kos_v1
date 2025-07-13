# KOS v1 New Directory Structure Plan

## Overview
Restructure kos_v1 to align with KOS centralized environment system and unified Docker approach, implementing the modular AI operating system architecture from the PRD manual.

## New Directory Structure

```
kos_v1/
├── src/                          # Main source code
│   ├── core/                     # Core system components
│   │   ├── klf/                  # Kind Link Framework protocol
│   │   │   ├── protocol/         # KLF protocol implementation
│   │   │   ├── client/           # KLF client libraries
│   │   │   ├── server/           # KLF server implementation
│   │   │   └── messaging/        # Message handling and routing
│   │   ├── kitchen/              # Kitchen system (recipe engine)
│   │   │   ├── engine/           # Recipe execution engine
│   │   │   ├── pantry/           # Ingredient management
│   │   │   ├── recipes/          # Recipe definitions
│   │   │   └── plugins/          # Plugin system
│   │   ├── security/             # Zero-trust security framework
│   │   │   ├── auth/             # Authentication system
│   │   │   ├── encryption/       # AES-256 encryption
│   │   │   ├── vault/            # Encrypted identity vaults
│   │   │   └── audit/            # Audit logging
│   │   └── agents/               # Agent framework
│   │       ├── base/             # Base agent classes
│   │       ├── registry/         # Agent registry
│   │       └── runtime/          # Agent runtime environment
│   ├── apps/                     # Application layer
│   │   ├── web/                  # Web application
│   │   │   ├── frontend/         # React/TypeScript frontend
│   │   │   ├── backend/          # FastAPI backend
│   │   │   └── api/              # API endpoints
│   │   ├── mobile/               # Mobile applications
│   │   │   ├── android/          # Android app
│   │   │   └── ios/              # iOS app
│   │   └── cli/                  # Command line interface
│   ├── services/                 # Microservices
│   │   ├── llm/                  # LLM integration service
│   │   ├── data/                 # Data processing service
│   │   ├── marketplace/          # Data marketplace service
│   │   └── monitoring/           # Monitoring and observability
│   └── shared/                   # Shared utilities
│       ├── utils/                # Common utilities
│       ├── types/                # Type definitions
│       └── constants/            # System constants
├── config/                       # Centralized configuration
│   ├── env/                      # Environment configurations
│   │   ├── development.json      # Development environment
│   │   ├── staging.json          # Staging environment
│   │   ├── production.json       # Production environment
│   │   └── local.json            # Local development
│   ├── features/                 # Feature flags
│   │   ├── flags.json            # Feature flag definitions
│   │   └── rules.json            # Feature flag rules
│   ├── security/                 # Security configurations
│   │   ├── encryption.json       # Encryption settings
│   │   ├── auth.json             # Authentication settings
│   │   └── permissions.json      # Permission definitions
│   └── system/                   # System configurations
│       ├── klf.json              # KLF protocol settings
│       ├── kitchen.json          # Kitchen system settings
│       └── agents.json           # Agent configurations
├── docker/                       # Unified Docker system
│   ├── compose/                  # Docker Compose files
│   │   ├── development.yml       # Development environment
│   │   ├── staging.yml           # Staging environment
│   │   ├── production.yml        # Production environment
│   │   └── local.yml             # Local development
│   ├── images/                   # Docker image definitions
│   │   ├── base/                 # Base images
│   │   ├── apps/                 # Application images
│   │   ├── services/             # Service images
│   │   └── tools/                # Tool images
│   ├── scripts/                  # Docker utility scripts
│   └── config/                   # Docker-specific configs
├── infrastructure/               # Infrastructure as Code
│   ├── kubernetes/               # Kubernetes manifests
│   ├── terraform/                # Terraform configurations
│   ├── ansible/                  # Ansible playbooks
│   └── monitoring/               # Monitoring stack
├── data/                         # Data management
│   ├── models/                   # AI models and weights
│   ├── datasets/                 # Training and test datasets
│   ├── recipes/                  # Recipe templates
│   └── marketplace/              # Data marketplace assets
├── docs/                         # Documentation
│   ├── api/                      # API documentation
│   ├── user/                     # User guides
│   ├── developer/                # Developer guides
│   ├── architecture/             # Architecture documentation
│   └── deployment/               # Deployment guides
├── tests/                        # Testing framework
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── e2e/                      # End-to-end tests
│   ├── performance/              # Performance tests
│   └── security/                 # Security tests
├── scripts/                      # Build and deployment scripts
│   ├── build/                    # Build scripts
│   ├── deploy/                   # Deployment scripts
│   ├── migrate/                  # Migration scripts
│   └── maintenance/              # Maintenance scripts
├── tools/                        # Development tools
│   ├── linting/                  # Linting configurations
│   ├── formatting/               # Code formatting
│   ├── testing/                  # Test utilities
│   └── monitoring/               # Development monitoring
├── logs/                         # Log files
├── backups/                      # Backup files
├── .env.example                  # Environment template
├── docker-compose.yml            # Main Docker Compose
├── package.json                  # Node.js dependencies
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Python project config
├── README.md                     # Project documentation
└── .gitignore                    # Git ignore rules
```

## Key Changes and Rationale

### 1. Centralized Configuration System
- **config/env/**: Environment-specific configurations using KOS centralized approach
- **config/features/**: Feature flags for gradual rollouts
- **config/security/**: Centralized security settings
- **config/system/**: System component configurations

### 2. Unified Docker System
- **docker/compose/**: Environment-specific Docker Compose files
- **docker/images/**: Modular Docker image definitions
- **docker/scripts/**: Docker utility scripts for automation

### 3. Modular Source Structure
- **src/core/**: Core system components (KLF, Kitchen, Security, Agents)
- **src/apps/**: Application layer (Web, Mobile, CLI)
- **src/services/**: Microservices architecture
- **src/shared/**: Shared utilities and types

### 4. Infrastructure as Code
- **infrastructure/**: Complete infrastructure management
- **monitoring/**: Comprehensive monitoring stack

### 5. Data Management
- **data/**: Centralized data management
- **marketplace/**: Data marketplace integration

## Migration Strategy

### Phase 1: Foundation (Week 1-2)
1. Create new directory structure
2. Set up centralized configuration system
3. Implement unified Docker system
4. Migrate core components (KLF, Kitchen, Security)

### Phase 2: Applications (Week 3-4)
1. Migrate web application
2. Set up mobile app structure
3. Implement CLI interface
4. Configure microservices

### Phase 3: Infrastructure (Week 5-6)
1. Set up Kubernetes manifests
2. Configure monitoring stack
3. Implement CI/CD pipelines
4. Set up data management

### Phase 4: Testing & Documentation (Week 7-8)
1. Comprehensive testing framework
2. Complete documentation
3. Performance optimization
4. Security audit

## Configuration Management

### Environment Configuration
```json
// config/env/development.json
{
  "environment": "development",
  "debug": true,
  "log_level": "DEBUG",
  "database": {
    "url": "postgresql://localhost/kos_dev",
    "pool_size": 10
  },
  "redis": {
    "url": "redis://localhost:6379"
  },
  "klf": {
    "port": 8080,
    "encryption": true
  },
  "kitchen": {
    "max_concurrent_recipes": 10,
    "timeout": 300
  }
}
```

### Feature Flags
```json
// config/features/flags.json
{
  "data_marketplace": {
    "enabled": true,
    "percentage": 100
  },
  "advanced_analytics": {
    "enabled": false,
    "percentage": 0
  },
  "mobile_app": {
    "enabled": true,
    "percentage": 100
  }
}
```

## Docker Configuration

### Unified Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Core Services
  klf-server:
    build: ./docker/images/klf
    ports:
      - "8080:8080"
    env_file: .env
    depends_on:
      - postgres
      - redis

  kitchen-engine:
    build: ./docker/images/kitchen
    env_file: .env
    depends_on:
      - klf-server
      - postgres

  # Applications
  web-app:
    build: ./docker/images/web
    ports:
      - "3000:3000"
    env_file: .env
    depends_on:
      - klf-server
      - kitchen-engine

  # Infrastructure
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: kos
      POSTGRES_USER: kos_user
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Next Steps

1. **Review and approve** this structure
2. **Create migration script** to move existing files
3. **Set up centralized config** system
4. **Implement unified Docker** system
5. **Begin phased migration** following the strategy above

This structure aligns with KOS principles of modularity, security, and scalability while implementing the centralized environment system and unified Docker approach. 