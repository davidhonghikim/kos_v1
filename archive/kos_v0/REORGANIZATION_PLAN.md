# kOS Directory Reorganization Plan

## Current Issues
1. Mixed responsibilities in root directory
2. Inconsistent naming conventions
3. Missing clear separation of concerns
4. Documentation scattered across multiple formats
5. No clear distinction between core system and applications

## Proposed New Structure

```
kos_v1/
├── src/                          # Source code root
│   ├── core/                     # Core system components
│   │   ├── agents/               # Base agent implementations
│   │   ├── nodes/                # Node implementations
│   │   ├── services/             # Core services
│   │   ├── gateway/              # Gateway components
│   │   ├── orchestrator/         # Orchestration logic
│   │   ├── klf/                  # KindLink Framework
│   │   └── mcp/                  # Model Context Protocol
│   ├── apps/                     # Application layer
│   │   ├── frontend/             # Web frontend
│   │   ├── extension/            # Browser extension
│   │   └── cli/                  # Command line interface
│   ├── runtime/                  # Runtime environments
│   └── shared/                   # Shared utilities and types
├── config/                       # Configuration files
│   ├── system/                   # System configuration
│   ├── features/                 # Feature flags
│   └── environments/             # Environment-specific configs
├── docs/                         # Documentation
│   ├── architecture/             # System architecture docs
│   ├── api/                      # API documentation
│   ├── guides/                   # User and developer guides
│   └── reference/                # Reference documentation
├── tests/                        # Test suites
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
├── scripts/                      # Build and utility scripts
│   ├── build/                    # Build scripts
│   ├── deploy/                   # Deployment scripts
│   └── tools/                    # Development tools
├── docker/                       # Docker configuration
│   ├── images/                   # Docker images
│   └── compose/                  # Docker compose files
├── infrastructure/               # Infrastructure configuration
│   ├── nginx/                    # Nginx configuration
│   ├── monitoring/               # Monitoring setup
│   └── security/                 # Security configurations
├── data/                         # Data files
│   ├── models/                   # AI models
│   ├── datasets/                 # Training datasets
│   └── artifacts/                # Generated artifacts
├── logs/                         # Log files
├── .github/                      # GitHub workflows
├── package.json                  # Node.js dependencies
├── requirements.txt              # Python dependencies
├── README.md                     # Project overview
└── CHANGELOG.md                  # Version history
```

## Migration Strategy

### Phase 1: Core Restructuring
1. Create new directory structure
2. Move core components to `src/core/`
3. Move applications to `src/apps/`
4. Consolidate configuration files

### Phase 2: Documentation Cleanup
1. Convert all documentation to JSON format (per user preferences)
2. Organize docs by category
3. Remove .md files after JSON conversion

### Phase 3: Reference Updates
1. Update all import statements
2. Update configuration file paths
3. Update documentation references
4. Update build scripts

### Phase 4: Testing and Validation
1. Run all tests to ensure functionality
2. Verify all imports work correctly
3. Test build process
4. Validate deployment

## Benefits of New Structure

1. **Clear Separation of Concerns**: Core system vs applications
2. **Industry Standard**: Follows common patterns for large projects
3. **Scalability**: Easy to add new components and services
4. **Maintainability**: Logical grouping makes code easier to find
5. **Documentation**: Centralized and organized documentation
6. **Testing**: Clear test organization
7. **Deployment**: Separated infrastructure concerns

## File Naming Conventions

- Use kebab-case for directories: `feature-flags/`
- Use snake_case for Python files: `base_agent.py`
- Use camelCase for JavaScript/TypeScript files: `agentLoader.ts`
- Use UPPER_CASE for environment variables: `API_KEY`
- Use PascalCase for classes: `BaseAgent`

## Configuration Management

- System config: `config/system/`
- Feature flags: `config/features/`
- Environment configs: `config/environments/`
- All configs in YAML format (per user preferences) 