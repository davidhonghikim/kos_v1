# kOS Implementation Plan

## Phase 1: Foundation Setup

### Step 1.1: Create Integration Branch
```bash
cd ../kos_v1
git checkout -b integration-phase1
git push -u origin integration-phase1
```

### Step 1.2: Set Up Monorepo Structure
```bash
# Create new directory structure
mkdir -p src/{bootloader,agent_orchestrator,KLF_api,vault_manager,kitchen_engine,backend_kernel,RAG_stack,frontend_router,plugin_manager,plugin_marketplace,monitoring}
mkdir -p src/kitchen_engine/{pantry,recipes}
mkdir -p src/backend_kernel/database
mkdir -p src/frontend_router/{components,store}
```

### Step 1.3: Port Bootloader from ai-Q
```bash
# Copy ai-Q's main_dynamic.py
cp ../ai-Q/src/core/main_dynamic.py src/bootloader/entrypoint.py

# Create bootloader module structure
cat > src/bootloader/__init__.py << 'EOF'
"""
kOS Bootloader Module
Handles system initialization and environment validation
"""
from .entrypoint import main

__all__ = ['main']
EOF

# Create environment validator
cat > src/bootloader/env_validator.py << 'EOF'
"""
Environment validation for kOS system
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

def validate_environment() -> Dict[str, Any]:
    """Validate system environment and dependencies"""
    issues = []
    warnings = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    
    # Check required directories
    required_dirs = ['src', 'config', 'logs']
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            warnings.append(f"Directory {dir_name} not found")
    
    # Check environment variables
    required_env = ['KOS_ENV', 'KOS_BACKEND_HOST', 'KOS_BACKEND_PORT']
    for env_var in required_env:
        if not os.getenv(env_var):
            warnings.append(f"Environment variable {env_var} not set")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings
    }
EOF
```

### Step 1.4: Port Agent Orchestrator from Griot + ai-Q
```bash
# Copy Griot's core manager
cp -r ../griot/packages/core/src/core/manager/* src/agent_orchestrator/

# Copy ai-Q's component loader
cp ../ai-Q/src/core/component_loader.py src/agent_orchestrator/component_loader.py
cp ../ai-Q/src/core/feature_manager.py src/agent_orchestrator/feature_manager.py

# Create agent orchestrator main file
cat > src/agent_orchestrator/main.py << 'EOF'
"""
kOS Agent Orchestrator
Manages agent lifecycle and coordination
"""
from .component_loader import ComponentLoader
from .feature_manager import FeatureManager
from .manager import AgentManager

class AgentOrchestrator:
    def __init__(self):
        self.component_loader = ComponentLoader()
        self.feature_manager = FeatureManager()
        self.agent_manager = AgentManager()
    
    def start(self):
        """Start the agent orchestrator"""
        self.component_loader.load_components()
        self.feature_manager.initialize()
        self.agent_manager.start()
    
    def stop(self):
        """Stop the agent orchestrator"""
        self.agent_manager.stop()
EOF
```

### Step 1.5: Port KLF Protocol from Griot
```bash
# Copy Griot's KLF client
cp -r ../griot/packages/klf-client/* src/KLF_api/

# Copy Griot's protocol implementation
cp -r ../griot/packages/core/src/core/protocol/* src/KLF_api/protocol/

# Copy kOS's frontend KLF files
cp ../kos/src/frontend/klf-*.ts src/KLF_api/frontend/

# Create KLF API main file
cat > src/KLF_api/main.py << 'EOF'
"""
kOS KLF API
KindLink Framework protocol implementation
"""
from .protocol import KLFProtocol
from .client import KLFClient

class KLFAPI:
    def __init__(self):
        self.protocol = KLFProtocol()
        self.client = KLFClient()
    
    def start(self):
        """Start KLF API"""
        self.protocol.initialize()
        self.client.connect()
    
    def stop(self):
        """Stop KLF API"""
        self.client.disconnect()
EOF
```

### Step 1.6: Port Vault Manager from kai-cd + Griot
```bash
# Copy kai-cd's vault UI components
cp ../kai-cd/src/components/VaultManager.tsx src/vault_manager/frontend/
cp ../kai-cd/src/store/vaultStore.ts src/vault_manager/frontend/

# Copy Griot's personal library backend
cp -r ../griot/services/personal-library/* src/vault_manager/backend/

# Create vault manager main file
cat > src/vault_manager/main.py << 'EOF'
"""
kOS Vault Manager
Secure credential and key management
"""
from .backend.storage import SecureStorage
from .backend.encryption import EncryptionManager

class VaultManager:
    def __init__(self):
        self.storage = SecureStorage()
        self.encryption = EncryptionManager()
    
    def initialize(self, master_password: str):
        """Initialize vault with master password"""
        self.encryption.setup(master_password)
        self.storage.initialize()
    
    def store_credential(self, key: str, value: str):
        """Store encrypted credential"""
        encrypted_value = self.encryption.encrypt(value)
        self.storage.store(key, encrypted_value)
    
    def get_credential(self, key: str) -> str:
        """Retrieve and decrypt credential"""
        encrypted_value = self.storage.retrieve(key)
        return self.encryption.decrypt(encrypted_value)
EOF
```

## Phase 2: Kitchen System Integration

### Step 2.1: Port Kitchen Engine from ai-Q
```bash
# Copy ai-Q's kitchen engine
cp ../ai-Q/kitchen/core/kitchen_engine.py src/kitchen_engine/engine.py

# Split large file into smaller modules
# Create kitchen engine main file
cat > src/kitchen_engine/main.py << 'EOF'
"""
kOS Kitchen Engine
Recipe execution and workflow orchestration
"""
from .engine import KitchenEngine

class KitchenSystem:
    def __init__(self):
        self.engine = KitchenEngine()
    
    def start(self):
        """Start kitchen system"""
        return self.engine.start()
    
    def execute_recipe(self, recipe_id: str, parameters: dict = None):
        """Execute a recipe"""
        return self.engine.execute_recipe(recipe_id, parameters)
    
    def stop(self):
        """Stop kitchen system"""
        return self.engine.stop()
EOF
```

### Step 2.2: Port Pantry System from ai-Q
```bash
# Copy ai-Q's pantry system
cp -r ../ai-Q/kitchen/pantry/* src/kitchen_engine/pantry/

# Create pantry main file
cat > src/kitchen_engine/pantry/main.py << 'EOF'
"""
kOS Pantry System
Ingredient management and availability tracking
"""
from .core import PantryCore
from .ingredients import IngredientManager
from .operations import OperationRegistry

class PantrySystem:
    def __init__(self):
        self.core = PantryCore()
        self.ingredients = IngredientManager()
        self.operations = OperationRegistry()
    
    def initialize(self):
        """Initialize pantry system"""
        self.core.initialize()
        self.ingredients.load_ingredients()
        self.operations.discover_operations()
    
    def get_ingredient(self, name: str):
        """Get ingredient by name"""
        return self.ingredients.get(name)
    
    def list_ingredients(self):
        """List all available ingredients"""
        return self.ingredients.list_all()
EOF
```

### Step 2.3: Port Recipe Management from ai-Q + Griot
```bash
# Copy ai-Q's recipes
cp -r ../ai-Q/kitchen/pantry/recipes/* src/kitchen_engine/recipes/
cp -r ../ai-Q/kitchen/griot_node_recipes/* src/kitchen_engine/recipes/griot/

# Copy Griot's kitchen app recipes
cp -r ../griot/apps/griot-kitchen/recipes/* src/kitchen_engine/recipes/griot/

# Create recipe management main file
cat > src/kitchen_engine/recipes/main.py << 'EOF'
"""
kOS Recipe Management
Recipe creation, validation, and execution
"""
from .validator import RecipeValidator
from .executor import RecipeExecutor
from .registry import RecipeRegistry

class RecipeManager:
    def __init__(self):
        self.validator = RecipeValidator()
        self.executor = RecipeExecutor()
        self.registry = RecipeRegistry()
    
    def create_recipe(self, recipe_data: dict):
        """Create and validate a new recipe"""
        if self.validator.validate(recipe_data):
            return self.registry.register(recipe_data)
        else:
            raise ValueError("Invalid recipe data")
    
    def execute_recipe(self, recipe_id: str, parameters: dict = None):
        """Execute a recipe"""
        recipe = self.registry.get(recipe_id)
        return self.executor.execute(recipe, parameters)
EOF
```

## Phase 3: Backend Services Integration

### Step 3.1: Port FastAPI Backend from kOS + Griot
```bash
# Copy kOS's FastAPI backend
cp ../kos/src/backend/main.py src/backend_kernel/api_server.py

# Copy Griot's backend services
cp -r ../griot/apps/backend-v2/* src/backend_kernel/services/
cp -r ../griot/apps/backend-react-v1/* src/backend_kernel/services/

# Create backend kernel main file
cat > src/backend_kernel/main.py << 'EOF'
"""
kOS Backend Kernel
FastAPI backend server and API management
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api_server import app
from .routes import register_routes

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    register_routes(app)
    
    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(create_app(), host="0.0.0.0", port=8000)
EOF
```

### Step 3.2: Port Database Services from ai-Q + Griot
```bash
# Copy ai-Q's database services
cp ../ai-Q/src/services/database.py src/backend_kernel/database/main.py
cp -r ../ai-Q/src/databases/* src/backend_kernel/database/

# Copy Griot's database dependencies
cp ../griot/packages/core/package.json src/backend_kernel/database/package.json

# Create database manager
cat > src/backend_kernel/database/manager.py << 'EOF'
"""
kOS Database Manager
Multi-database support and connection management
"""
import asyncio
from typing import Dict, Any
from .main import DatabaseService

class DatabaseManager:
    def __init__(self):
        self.services: Dict[str, DatabaseService] = {}
    
    async def initialize(self, config: Dict[str, Any]):
        """Initialize database connections"""
        for db_name, db_config in config.items():
            service = DatabaseService(db_config)
            await service.connect()
            self.services[db_name] = service
    
    async def get_service(self, name: str) -> DatabaseService:
        """Get database service by name"""
        return self.services.get(name)
    
    async def close_all(self):
        """Close all database connections"""
        for service in self.services.values():
            await service.disconnect()
EOF
```

### Step 3.3: Port Vector/RAG Services from ai-Q + Griot
```bash
# Copy ai-Q's vector and search services
cp ../ai-Q/src/services/vector.py src/RAG_stack/weaviate_client.py
cp ../ai-Q/src/services/search.py src/RAG_stack/search.py

# Copy Griot's Weaviate integration
cp ../griot/packages/core/src/core/weaviate/* src/RAG_stack/weaviate/

# Create RAG stack main file
cat > src/RAG_stack/main.py << 'EOF'
"""
kOS RAG Stack
Retrieval-Augmented Generation system
"""
from .weaviate_client import WeaviateClient
from .search import SearchService
from .indexer import ContentIndexer

class RAGStack:
    def __init__(self):
        self.weaviate = WeaviateClient()
        self.search = SearchService()
        self.indexer = ContentIndexer()
    
    async def initialize(self):
        """Initialize RAG stack"""
        await self.weaviate.connect()
        await self.search.initialize()
        await self.indexer.initialize()
    
    async def index_content(self, content: str, metadata: dict):
        """Index content for retrieval"""
        return await self.indexer.index(content, metadata)
    
    async def search_content(self, query: str, limit: int = 10):
        """Search indexed content"""
        return await self.search.search(query, limit)
EOF
```

### Step 3.4: Port ELK Monitoring from Griot
```bash
# Copy Griot's ELK stack
cp -r ../griot/elk/* src/monitoring/

# Create monitoring main file
cat > src/monitoring/main.py << 'EOF'
"""
kOS Monitoring System
ELK stack integration and system monitoring
"""
from .elasticsearch import ElasticsearchClient
from .logstash import LogstashClient
from .kibana import KibanaClient

class MonitoringSystem:
    def __init__(self):
        self.elasticsearch = ElasticsearchClient()
        self.logstash = LogstashClient()
        self.kibana = KibanaClient()
    
    async def initialize(self):
        """Initialize monitoring system"""
        await self.elasticsearch.connect()
        await self.logstash.start()
        await self.kibana.start()
    
    async def log_event(self, event: dict):
        """Log an event to ELK stack"""
        await self.logstash.send_event(event)
    
    async def get_metrics(self):
        """Get system metrics"""
        return await self.elasticsearch.get_metrics()
EOF
```

## Phase 4: Frontend Unification

### Step 4.1: Port UI Components from kai-cd
```bash
# Copy kai-cd's comprehensive component library
cp -r ../kai-cd/src/components/* src/frontend_router/components/
cp -r ../kai-cd/src/store/* src/frontend_router/store/
cp -r ../kai-cd/src/styles/* src/frontend_router/styles/

# Copy kOS's KLF integration files
cp ../kos/src/frontend/klf-*.ts src/frontend_router/klf/

# Create frontend router main file
cat > src/frontend_router/main.tsx << 'EOF'
"""
kOS Frontend Router
Dynamic frontend module loading and routing
"""
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useKLF } from './klf/klf-hooks';
import { VaultManager } from './components/VaultManager';
import { ServiceManagement } from './components/ServiceManagement';

const FrontendRouter: React.FC = () => {
  const { isConnected } = useKLF();

  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/vault" element={<VaultManager />} />
          <Route path="/services" element={<ServiceManagement />} />
          {/* Add more routes as components are integrated */}
        </Routes>
      </div>
    </Router>
  );
};

export default FrontendRouter;
EOF
```

## Phase 5: Advanced Features

### Step 5.1: Port Agent System from Griot + ai-Q
```bash
# Copy Griot's agent system
cp -r ../griot/packages/core/src/nodes/* src/agent_orchestrator/agents/
cp -r ../griot/apps/persona-rag-bridge/* src/agent_orchestrator/persona/

# Copy ai-Q's AI services
cp -r ../ai-Q/src/ai/* src/agent_orchestrator/ai/
cp -r ../ai-Q/agents/* src/agent_orchestrator/agents/

# Create agent system main file
cat > src/agent_orchestrator/agents/main.py << 'EOF'
"""
kOS Agent System
Agent coordination and persona management
"""
from .manager import AgentManager
from .persona import PersonaManager
from .ai import AIService

class AgentSystem:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.persona_manager = PersonaManager()
        self.ai_service = AIService()
    
    async def initialize(self):
        """Initialize agent system"""
        await self.agent_manager.initialize()
        await self.persona_manager.initialize()
        await self.ai_service.initialize()
    
    async def create_agent(self, agent_type: str, config: dict):
        """Create a new agent"""
        return await self.agent_manager.create_agent(agent_type, config)
    
    async def create_persona(self, persona_data: dict):
        """Create a new persona"""
        return await self.persona_manager.create_persona(persona_data)
EOF
```

### Step 5.2: Port Plugin System from Griot
```bash
# Copy Griot's service connectors
cp -r ../griot/packages/service-connectors/* src/plugin_manager/

# Create plugin manager main file
cat > src/plugin_manager/main.py << 'EOF'
"""
kOS Plugin Manager
Plugin discovery, installation, and sandboxing
"""
from .discovery import PluginDiscovery
from .installer import PluginInstaller
from .sandbox import PluginSandbox

class PluginManager:
    def __init__(self):
        self.discovery = PluginDiscovery()
        self.installer = PluginInstaller()
        self.sandbox = PluginSandbox()
    
    async def discover_plugins(self):
        """Discover available plugins"""
        return await self.discovery.scan()
    
    async def install_plugin(self, plugin_id: str):
        """Install a plugin"""
        plugin_data = await self.discovery.get_plugin(plugin_id)
        return await self.installer.install(plugin_data)
    
    async def execute_plugin(self, plugin_id: str, parameters: dict):
        """Execute a plugin in sandbox"""
        return await self.sandbox.execute(plugin_id, parameters)
EOF
```

### Step 5.3: Build Plugin Marketplace
```bash
# Create plugin marketplace structure
mkdir -p src/plugin_marketplace/{registry,discovery,distribution}

# Create plugin marketplace main file
cat > src/plugin_marketplace/main.py << 'EOF'
"""
kOS Plugin Marketplace
Plugin discovery and distribution
"""
from .registry import PluginRegistry
from .discovery import PluginDiscovery
from .distribution import PluginDistribution

class PluginMarketplace:
    def __init__(self):
        self.registry = PluginRegistry()
        self.discovery = PluginDiscovery()
        self.distribution = PluginDistribution()
    
    async def initialize(self):
        """Initialize plugin marketplace"""
        await self.registry.initialize()
        await self.discovery.initialize()
        await self.distribution.initialize()
    
    async def list_plugins(self, category: str = None):
        """List available plugins"""
        return await self.registry.list_plugins(category)
    
    async def get_plugin_details(self, plugin_id: str):
        """Get plugin details"""
        return await self.registry.get_plugin(plugin_id)
    
    async def download_plugin(self, plugin_id: str):
        """Download a plugin"""
        return await self.distribution.download(plugin_id)
EOF
```

## Phase 6: Integration & Polish

### Step 6.1: Configuration Unification
```bash
# Create unified configuration structure
mkdir -p config/{environments,modules,security}

# Create main configuration file
cat > config/system.json << 'EOF'
{
  "os_name": "kOS",
  "version": "1.0.0",
  "debug": true,
  "services": [
    "vault",
    "agent_orchestrator",
    "kitchen_engine",
    "backend_kernel",
    "RAG_stack",
    "plugin_manager",
    "monitoring"
  ],
  "modules": {
    "bootloader": {
      "enabled": true,
      "config": "config/modules/bootloader.json"
    },
    "agent_orchestrator": {
      "enabled": true,
      "config": "config/modules/agent_orchestrator.json"
    }
  }
}
EOF
```

### Step 6.2: Testing Integration
```bash
# Create comprehensive test structure
mkdir -p tests/{unit,integration,e2e}

# Create test configuration
cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=95
EOF

# Create test runner
cat > run_tests.sh << 'EOF'
#!/bin/bash
echo "Running kOS test suite..."

# Run unit tests
echo "Running unit tests..."
pytest tests/unit/ -v

# Run integration tests
echo "Running integration tests..."
pytest tests/integration/ -v

# Run end-to-end tests
echo "Running end-to-end tests..."
pytest tests/e2e/ -v

echo "Test suite completed!"
EOF

chmod +x run_tests.sh
```

### Step 6.3: Documentation Completion
```bash
# Create documentation structure
mkdir -p docs/{api,user,developer,deployment}

# Create API documentation
cat > docs/api/README.md << 'EOF'
# kOS API Documentation

## Overview
kOS provides a comprehensive API for agent orchestration, kitchen management, and system administration.

## Endpoints

### Agent Management
- `POST /api/agents` - Create agent
- `GET /api/agents` - List agents
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Kitchen Management
- `POST /api/kitchen/recipes` - Create recipe
- `GET /api/kitchen/recipes` - List recipes
- `POST /api/kitchen/execute` - Execute recipe

### Vault Management
- `POST /api/vault/credentials` - Store credential
- `GET /api/vault/credentials/{key}` - Retrieve credential
- `DELETE /api/vault/credentials/{key}` - Delete credential
EOF

# Create user documentation
cat > docs/user/README.md << 'EOF'
# kOS User Guide

## Getting Started

### Installation
1. Clone the repository
2. Run `./bootstrap.sh`
3. Configure your environment
4. Start the system

### Basic Usage
1. Unlock your vault
2. Create your first agent
3. Execute your first recipe
4. Monitor system status

## Features
- Agent orchestration
- Kitchen system
- Secure vault
- Plugin marketplace
EOF
```

### Step 6.4: Security Hardening
```bash
# Create security configuration
cat > config/security/security.json << 'EOF'
{
  "encryption": {
    "algorithm": "AES-256-GCM",
    "key_derivation": "PBKDF2",
    "iterations": 100000
  },
  "authentication": {
    "methods": ["passphrase", "device_fingerprint", "biometrics"],
    "session_timeout": 86400
  },
  "audit": {
    "enabled": true,
    "log_all_operations": true,
    "retention_days": 365
  },
  "zero_trust": {
    "enabled": true,
    "verify_all_connections": true,
    "encrypt_all_data": true
  }
}
EOF

# Create security scanner
cat > src/pentest_toolkit/scanner.py << 'EOF'
"""
kOS Security Scanner
Comprehensive security validation
"""
import asyncio
from typing import List, Dict

class SecurityScanner:
    def __init__(self):
        self.scans = []
    
    async def scan_system(self) -> Dict[str, any]:
        """Perform comprehensive security scan"""
        results = {
            "vault_access": await self.scan_vault_access(),
            "external_calls": await self.scan_external_calls(),
            "plugin_validation": await self.scan_plugins(),
            "model_integrity": await self.scan_models()
        }
        return results
    
    async def scan_vault_access(self):
        """Scan vault access patterns"""
        # Implementation here
        pass
    
    async def scan_external_calls(self):
        """Scan external API calls"""
        # Implementation here
        pass
    
    async def scan_plugins(self):
        """Scan plugin security"""
        # Implementation here
        pass
    
    async def scan_models(self):
        """Scan model integrity"""
        # Implementation here
        pass
EOF
```

## Final Integration Steps

### Step 7.1: Create Main Entry Point
```bash
# Create main entry point
cat > main.py << 'EOF'
"""
kOS Main Entry Point
System initialization and orchestration
"""
import asyncio
import logging
from src.bootloader import main as bootloader_main
from src.agent_orchestrator import AgentOrchestrator
from src.KLF_api import KLFAPI
from src.vault_manager import VaultManager
from src.kitchen_engine import KitchenSystem
from src.backend_kernel import create_app
from src.RAG_stack import RAGStack
from src.monitoring import MonitoringSystem

async def main():
    """Main kOS system entry point"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize bootloader
        logger.info("Initializing kOS bootloader...")
        bootloader_main()
        
        # Initialize core systems
        logger.info("Initializing core systems...")
        vault = VaultManager()
        klf = KLFAPI()
        agents = AgentOrchestrator()
        kitchen = KitchenSystem()
        rag = RAGStack()
        monitoring = MonitoringSystem()
        
        # Start systems
        logger.info("Starting kOS systems...")
        await asyncio.gather(
            monitoring.initialize(),
            rag.initialize(),
            kitchen.start()
        )
        
        klf.start()
        agents.start()
        
        # Start FastAPI backend
        app = create_app()
        logger.info("kOS system started successfully!")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to start kOS: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
EOF
```

### Step 7.2: Create Bootstrap Script
```bash
# Create bootstrap script
cat > bootstrap.sh << 'EOF'
#!/bin/bash

echo "🚀 Bootstrapping kOS System..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.8+ required, found $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
npm install

# Initialize configuration
echo "⚙️  Initializing configuration..."
cp .env.template .env
echo "Please edit .env with your configuration"

# Create required directories
echo "📁 Creating required directories..."
mkdir -p logs data cache

# Run tests
echo "🧪 Running tests..."
./run_tests.sh

echo "✅ kOS bootstrap completed!"
echo "Run 'python main.py' to start the system"
EOF

chmod +x bootstrap.sh
```

### Step 7.3: Create Docker Configuration
```bash
# Create Docker Compose file
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  kos-backend:
    build:
      context: .
      dockerfile: docker/backend.dockerfile
    ports:
      - "8000:8000"
    environment:
      - KOS_ENV=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
      - weaviate

  kos-frontend:
    build:
      context: .
      dockerfile: docker/frontend.dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - kos-backend

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: kos
      POSTGRES_USER: kos
      POSTGRES_PASSWORD: kos_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  weaviate:
    image: semitechnologies/weaviate:1.22.0
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'none'
      ENABLE_MODULES: 'text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai'
      CLUSTER_HOSTNAME: 'node1'

volumes:
  postgres_data:
  redis_data:
EOF
```

This implementation plan provides detailed, step-by-step instructions for integrating all repositories into a unified kOS system. Each step includes specific file operations, commands, and code examples to ensure successful integration. 