# kOS v1 Environment Configuration System

This directory contains the modular environment configuration system for kOS v1, using a sophisticated variable resolution system.

## Overview

The environment system uses multiple separate `.env` files that are loaded in a specific order and combined into a unified configuration. This allows for:

- **Centralized Management**: Admin credentials and ports in one place
- **Variable Resolution**: Cross-references between files with cycle detection
- **Modularity**: Different aspects of configuration are separated
- **Flexibility**: Easy to modify specific parts without affecting others
- **Clarity**: Clear organization of settings by purpose

## File Structure

```
env/
├── ports.env                  # Centralized ports, container names, admin credentials
├── local.env                  # Local development service configurations
├── cloud.env                  # Cloud deployment settings
├── api-keys.env               # API keys and secrets (not committed)
├── settings/                  # Service-specific settings
│   ├── api.settings.env
│   ├── ollama.settings.env
│   └── openwebui.settings.env
└── README.md                  # This file
```

## Environment Loader System (`scripts/env_loader.py`)

### Load Order
The environment loader loads files in this specific order:

1. **`ports.env`** - Centralized ports, container names, admin credentials
2. **`local.env`** - Local development settings
3. **`cloud.env`** - Cloud deployment settings
4. **Additional environment-specific files**

### Variable Resolution Features

- **Recursive Resolution**: Variables can reference other variables (e.g., `${KOS_ADMIN_EMAIL}`)
- **Cycle Detection**: Prevents infinite loops in variable references
- **Recursion Depth Limit**: Maximum 10 levels to prevent stack overflow
- **Fallback Values**: Graceful handling of missing variables
- **Cross-Reference Support**: Variables from any loaded file can reference others

### Example Variable Resolution

```bash
# ports.env (loaded first)
KOS_ADMIN_EMAIL=admin@kos.local
KOS_ADMIN_USER=kos-admin
KOS_ADMIN_PASSWORD=kos-30437

# local.env (loaded second)
KOS_PGADMIN_EMAIL=${KOS_ADMIN_EMAIL}        # Resolves to: admin@kos.local
KOS_PGADMIN_USER=${KOS_ADMIN_USER}          # Resolves to: kos-admin
KOS_PGADMIN_PASSWORD=${KOS_ADMIN_PASSWORD}  # Resolves to: kos-30437
```

### Usage

```bash
python scripts/env_loader.py
```

This generates a unified `.env` file with all variables resolved and displays the source of each variable.

## Configuration Files

### ports.env (Centralized Configuration)
**This is the single source of truth for:**
- Admin credentials (user, password, email)
- All port assignments (external and internal)
- Container names
- Network configuration

**Key Variables:**
```bash
# Admin credentials (EDIT THESE ONCE FOR ALL SERVICES)
KOS_ADMIN_USER=kos-admin
KOS_ADMIN_PASSWORD=kos-30437
KOS_ADMIN_EMAIL=admin@kos.local

# Port assignments
KOS_POSTGRES_EXTERNAL_PORT=5432
KOS_REDIS_EXTERNAL_PORT=6379
KOS_API_EXTERNAL_PORT=8000
# ... etc
```

### local.env (Service Configuration)
Contains service-specific configurations organized by category:
- Core Services (API, Frontend, Databases)
- AI/ML Services (Ollama, OpenWebUI, Automatic1111, ComfyUI, InvokeAI)
- Storage Services (Weaviate, MinIO, Elasticsearch, Neo4j)
- Development Services (Gitea, Supabase, BrowserUse, Context7, Codium)
- Monitoring Services (Prometheus, Grafana, cAdvisor)
- Workflow Services (N8N, Penpot)
- Self-hosted Services (Nextcloud, Admin Panel, etc.)

### cloud.env (Cloud Deployment)
Contains cloud-specific settings for production deployments.

### api-keys.env (Sensitive Data)
Contains all API keys, secrets, and sensitive configuration. **Never commit this file with real keys.**

### settings/ (Service-Specific Settings)
Contains service-specific advanced settings that can be customized per service.

## Usage

### 1. Initial Setup

1. Copy the example files to create your actual configuration:
   ```bash
   cp env/ports.env.example env/ports.env
   cp env/local.env.example env/local.env
   cp env/api-keys.env.example env/api-keys.env
   cp env/cloud.env.example env/cloud.env
   ```

2. Copy settings files as needed:
   ```bash
   cp env/settings/api.settings.env.example env/settings/api.settings.env
   cp env/settings/ollama.settings.env.example env/settings/ollama.settings.env
   cp env/settings/openwebui.settings.env.example env/settings/openwebui.settings.env
   ```

### 2. Generate Unified Environment

Run the environment loader to combine all files:

```bash
python scripts/env_loader.py
```

This creates a `.env` file in the project root with all variables resolved and combined.

### 3. Customize Configuration

Edit the individual `.env` files to customize your setup:

- **ports.env**: Change admin credentials and port assignments
- **local.env**: Modify service configurations
- **api-keys.env**: Add your actual API keys and secrets
- **cloud.env**: Configure for your cloud provider
- **settings/*.env**: Customize service-specific settings

### 4. Regenerate After Changes

After making changes to any `.env` file, regenerate the unified environment:

```bash
python scripts/env_loader.py
```

## Environment Variables

### Centralized Admin Credentials (ports.env)

```bash
# Single source of truth for all admin credentials
KOS_ADMIN_USER=kos-admin
KOS_ADMIN_PASSWORD=kos-30437
KOS_ADMIN_EMAIL=admin@kos.local
```

**Benefits:**
- Update once, applies everywhere
- No duplication across files
- Consistent credentials across all services
- Easy to change for different environments

### Service Enablement

Each service has an enable flag:
```bash
KOS_API_ENABLE=true
KOS_POSTGRES_ENABLE=true
KOS_OLLAMA_ENABLE=true
KOS_INVOKEAI_ENABLE=true
# etc.
```

### Port Configuration

Services use both external and internal ports:
```bash
KOS_API_EXTERNAL_PORT=8000    # Host port
KOS_API_INTERNAL_PORT=8000    # Container port
```

## Best Practices

1. **Never commit real API keys**: Only commit `.example` files
2. **Use centralized admin credentials**: Edit only `ports.env` for admin settings
3. **Use consistent naming**: All variables prefixed with `KOS_`
4. **Reference centralized variables**: Use `${KOS_ADMIN_EMAIL}` in configurations
5. **Group related settings**: Keep related variables together
6. **Document changes**: Update this README when adding new services

## Troubleshooting

### Port Conflicts
If you get port conflicts, modify `ports.env` to use different external ports.

### Missing Variables
If a service complains about missing variables, check that the corresponding `.env` file exists and contains the required variables.

### Variable Resolution Errors
If variable resolution fails:
1. Check for circular references
2. Verify all referenced variables exist
3. Run `python scripts/env_loader.py` to see resolution details

### Generation Errors
If the generator fails, check that all referenced `.env` files exist and have valid syntax.

## Integration with Docker

The generated `.env` file is used by Docker Compose files. The system supports both legacy Docker format and modern format:

- Legacy: `KOS_API_PORT=8000`
- Modern: `KOS_API_EXTERNAL_PORT=8000`, `KOS_API_INTERNAL_PORT=8000`

Both formats are included for compatibility.

## Canonical Port Mapping (Validated)

| Service/Variable                | External Port | Notes/Standard         |
|---------------------------------|--------------|-----------------------|
| **Core Services**               |              |                       |
| API                             | 8000         | API standard          |
| Frontend                        | 3000         | Web UI                |
| NGINX                           | 80           | HTTP standard         |
| NGINX SSL                       | 443          | HTTPS standard        |
| Postgres                        | 5432         | DB standard           |
| Redis                           | 6379         | DB standard           |
| MongoDB                         | 27017        | DB standard           |
| Neo4j                           | 7687         | DB standard           |
| Neo4j HTTP                      | 7474         | DB standard           |
| Elasticsearch                   | 9200         | DB standard           |
| Elasticsearch Cluster           | 9300         | DB standard           |
| Weaviate                        | 8082         | DB standard           |
| MinIO                           | 9000         | Storage std           |
| Nextcloud                       | 8083         | Web UI                |

| **Admin Tools**                 |              |                       |
| pgAdmin                         | 5433         | DB admin UI           |
| Redis Commander                 | 6380         | DB admin UI           |
| Mongo Express                   | 27018        | DB admin UI           |
| Registry                        | 5000         | Registry std          |
| MinIO Console                   | 9001         | Storage UI            |

| **Monitoring**                  |              |                       |
| Prometheus                      | 9090         | Monitoring            |
| Grafana                         | 3007         | Monitoring UI         |
| cAdvisor                        | 8081         | Monitoring            |

| **Development**                 |              |                       |
| Gitea                           | 3002         | Web UI                |
| Gitea SSH                       | 2222         | SSH                   |
| Supabase                        | 54321        | DB                    |
| Supabase Studio                 | 3003         | Web UI                |
| Browseruse                      | 3004         | Web UI                |
| Context7                        | 3005         | Web UI                |
| Codium                          | 3006         | Web UI                |

| **Workflow**                    |              |                       |
| n8n                             | 5678         | Workflow std          |
| Penpot                          | 9002         | Web UI                |
| Admin Panel                     | 9003         | Web UI                |
| Prompt Manager                  | 3008         | Manager UI            |
| Artifact Manager                | 3009         | Manager UI            |

| **AI/ML**                       |              |                       |
| Ollama                          | 11434        | AI/ML std             |
| Huggingface                     | 8084         | AI/ML std             |
| Automatic1111                   | 7860         | AI/ML std             |
| ComfyUI                         | 8188         | AI/ML std             |

| **Security**                    |              |                       |
| Vault                           | 8200         | Security std          |

**This table is generated from the current ports.env and validated to have no conflicts.** 