---
title: "Agent System Protocols and Directory Structure"
description: "Complete breakdown of system architecture, directory structure, and configuration protocols for all agent modules in kAI and kOS ecosystems"
category: "protocols"
subcategory: "agent-system"
context: "future/kos-vision"
implementation_status: "planned"
decision_scope: "system-wide"
complexity: "high"
last_updated: "2024-01-20"
code_references: [
  "kai/agents/",
  "kai/comms/klp/",
  "kai/config/",
  "kai/core/"
]
related_documents: [
  "future/agents/03_agent-protocols-and-hierarchy.md",
  "future/protocols/01_klp-specification.md",
  "future/architecture/04_kos-core-architecture.md"
]
dependencies: [
  "KLP Protocol",
  "Agent Directory Structure",
  "Configuration System",
  "Authentication Framework"
]
breaking_changes: [
  "New directory structure standard",
  "Enhanced KLP message schema",
  "Unified configuration system"
]
agent_notes: [
  "Defines complete agent system directory structure",
  "Contains full KLP message schema specifications",
  "Critical reference for agent module implementation",
  "Includes configuration conventions and runtime mappings"
]
---

# Agent System Protocols and Directory Structure

> **Agent Context**: This document provides the complete breakdown of system architecture, directory structure, and configuration protocols for all agent modules in kAI and kOS ecosystems. Use this when implementing agent modules, configuring system architecture, or understanding protocol specifications. All implementation details follow strict conventions for consistency across development teams.

## Quick Summary
Comprehensive system architecture specification defining master directory layout, KLP message contracts, configuration conventions, role-to-file mappings, and runtime settings for all agent modules in the kAI and kOS ecosystem.

## Master Directory Layout

```text
kai/
├── agents/
│   ├── kCore/
│   │   ├── controller.py
│   │   ├── config/
│   │   │   ├── system.json
│   │   │   └── defaults.yml
│   │   ├── tasks/
│   │   │   └── startup.py
│   │   └── logs/
│   │       └── controller.log
│   ├── kPlanner/
│   │   ├── planner.py
│   │   ├── prompts/
│   │   └── config/planner.json
│   ├── kExecutor/
│   │   ├── executor.py
│   │   ├── plugins/
│   │   └── config/executor.json
│   ├── kReviewer/
│   ├── kMemory/
│   ├── kPersona/
│   ├── kBridge/
│   └── kSentinel/
├── comms/
│   ├── klp/
│   │   ├── schema.json
│   │   ├── transport_grpc.py
│   │   ├── transport_ws.py
│   │   ├── auth/
│   │   │   ├── signer.py
│   │   │   └── verifier.py
│   │   └── protocol_handler.py
│   └── mesh/
│       ├── local_mesh.py
│       └── remote_mesh.py
├── config/
│   ├── agents/
│   │   ├── manifest.json
│   │   ├── kExecutor:webscraper.json
│   │   └── kPlanner:research.json
│   ├── services.yml
│   └── global_settings.json
├── core/
│   ├── orchestrator.py
│   ├── scheduler.py
│   ├── dispatcher.py
│   └── logger.py
├── data/
│   ├── embeddings/
│   ├── memory/
│   └── vault/
├── logs/
│   ├── kCore/
│   ├── kPlanner/
│   └── global.log
├── plugins/
│   ├── generator_tools/
│   ├── validators/
│   └── external_apis/
├── security/
│   ├── keys/
│   ├── audit/
│   └── policies/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── simulation/
└── ui/
    ├── webapp/
    │   ├── components/
    │   ├── store/
    │   ├── pages/
    │   └── index.tsx
    └── themes/
        └── default.css
```

## Configuration Conventions

### File Format Standards
- **JSON**: Runtime settings, identities, manifests
- **YAML**: User-editable service descriptions
- **Environment Variables**: Deployment-specific overrides

### Global Settings Example
```json
// /config/global_settings.json
{
  "debug_mode": true,
  "default_language": "en",
  "max_parallel_tasks": 5,
  "enable_mesh": true,
  "security": {
    "require_signatures": true,
    "audit_all_operations": true,
    "max_trust_level": 85
  }
}
```

## KLP Message Contract (Full Schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "KLPMessage",
  "type": "object",
  "required": ["type", "from", "to", "task_id", "payload"],
  "properties": {
    "type": { 
      "type": "string", 
      "enum": [
        "TASK_REQUEST", 
        "TASK_RESULT", 
        "TASK_ERROR",
        "STATUS_UPDATE",
        "INTENTION_DECLARATION",
        "MEMORY_READ",
        "MEMORY_WRITE",
        "PLAN_GRAPH",
        "SECURITY_ALERT",
        "CONFIG_UPDATE"
      ]
    },
    "from": { "type": "string" },
    "to": { "type": "string" },
    "task_id": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "payload": { "type": "object" },
    "auth": {
      "type": "object",
      "properties": {
        "signature": { "type": "string" },
        "token": { "type": "string" }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "priority": { "enum": ["low", "medium", "high", "critical"] },
        "ttl": { "type": "number" },
        "retryCount": { "type": "number" }
      }
    }
  }
}
```

## Role-to-File Mapping Table

| Role      | Main File                      | Config Path                      | Notes                         |
| --------- | ------------------------------ | -------------------------------- | ----------------------------- |
| kCore     | `agents/kCore/controller.py`   | `config/global_settings.json`    | Primary runtime orchestrator  |
| kPlanner  | `agents/kPlanner/planner.py`   | `config/agents/kPlanner:*.json`  | Supports dynamic subroles     |
| kExecutor | `agents/kExecutor/executor.py` | `config/agents/kExecutor:*.json` | Pluggable execution handlers  |
| kBridge   | `agents/kBridge/bridge.py`     | `config/services.yml`            | Handles external API bindings |
| kSentinel | `agents/kSentinel/security.py` | `security/policies/*.yml`        | RBAC + anomaly detection      |
| kMemory   | `agents/kMemory/memory.py`     | `config/agents/kMemory.json`     | Vector + graph memory         |
| kPersona  | `agents/kPersona/persona.py`   | `agents/kPersona/personas/*.yml` | Personality overlays          |
| kReviewer | `agents/kReviewer/reviewer.py` | `config/agents/kReviewer.json`   | Quality assurance checks      |

## Environment and Runtime Settings

### Environment Configuration
```bash
# .env.example
POSTGRES_URL=postgresql://user:pass@localhost:5432/kai
REDIS_URL=redis://localhost:6379
VECTORDB=qdrant
DEBUG=true
ENABLE_KLP=true
AGENT_KEY_DIR=./security/keys
LOG_LEVEL=INFO
MAX_AGENT_MEMORY=2GB
MESH_PORT=8080
```

### Runtime Entrypoint
```python
# main.py
from core.orchestrator import start_system
from core.logger import setup_logging

def main():
    setup_logging()
    start_system()

if __name__ == "__main__":
    main()
```

## Agent Configuration Examples

### Agent Manifest
```json
// config/agents/manifest.json
{
  "version": "1.0.0",
  "lastModified": "2025-01-20T10:00:00Z",
  "agents": [
    {
      "id": "kCore:main",
      "type": "controller",
      "class": "kCore",
      "active": true,
      "version": "1.0.0",
      "lastUpdate": "2025-01-20T10:00:00Z"
    },
    {
      "id": "kPlanner:research",
      "type": "planner",
      "class": "kPlanner",
      "active": true,
      "version": "1.0.0",
      "lastUpdate": "2025-01-20T10:00:00Z"
    }
  ]
}
```

### Individual Agent Configuration
```json
// config/agents/kExecutor:webscraper.json
{
  "name": "Web Scraper Executor",
  "allowed_domains": ["web", "research"],
  "max_tasks": 3,
  "persona": "Efficient, Thorough",
  "autonomy_level": "medium",
  "enabled": true,
  "resources": {
    "max_memory": "512MB",
    "max_cpu_percent": 50,
    "timeout_seconds": 300
  },
  "security": {
    "sandbox_mode": true,
    "allowed_operations": ["http_get", "http_post", "file_write"],
    "restricted_domains": ["internal.company.com"]
  }
}
```

## Protocol Implementation Details

### Transport Layer Configuration
```python
# comms/klp/transport_config.py
TRANSPORT_CONFIG = {
    'websocket': {
        'port': 8080,
        'max_connections': 100,
        'heartbeat_interval': 30
    },
    'grpc': {
        'port': 50051,
        'max_workers': 10,
        'compression': 'gzip'
    },
    'mqtt': {
        'broker': 'localhost',
        'port': 1883,
        'qos': 1
    }
}
```

### Authentication Implementation
```python
# comms/klp/auth/signer.py
import ed25519
import json
from datetime import datetime

class MessageSigner:
    def __init__(self, private_key_path: str):
        with open(private_key_path, 'rb') as f:
            self.private_key = ed25519.SigningKey(f.read())
    
    def sign_message(self, message: dict) -> str:
        """Sign a KLP message with Ed25519"""
        message_bytes = json.dumps(message, sort_keys=True).encode()
        signature = self.private_key.sign(message_bytes)
        return f"ed25519:{signature.hex()}"
```

## Future Expansion Notes

### Planned Enhancements
- **Agent Containerization**: Isolated runtime with audit hooks
- **Persona Overlays**: Real-time personality modulation in `/agents/kPersona/personas/*.yml`
- **Vault Tiers**: In-memory + encrypted-disk storage layers
- **ZK Token Signing**: Zero-knowledge proof integration for KLP protocol

### Scalability Considerations
- Each agent module designed for horizontal scaling
- Configuration hot-reloading for dynamic updates
- Distributed logging and monitoring integration
- Plugin architecture for extensible functionality

### Security Architecture
- All agent communications cryptographically signed
- Role-based access control enforced by kSentinel
- Audit trail for all critical operations
- Sandboxed execution environments for untrusted code

---

