#!/usr/bin/env python3
"""
KOS v1 Generic Docker Compose Generator
Generates docker-compose.yml dynamically from environment variables only
No hardcoded service templates or configurations
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List

class KOSDockerComposeGenerator:
    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self.env_vars = self.load_env_vars()
        
    def load_env_vars(self) -> Dict[str, str]:
        """Load environment variables from .env file"""
        env_vars = {}
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        # Resolve variable substitutions
        resolved_vars = {}
        for key, value in env_vars.items():
            resolved_vars[key] = self.resolve_variable(value, env_vars)
        
        return resolved_vars
    
    def resolve_variable(self, value: str, env_vars: Dict[str, str]) -> str:
        """Resolve variable substitutions in a value"""
        if not value.startswith('${') or not value.endswith('}'):
            return value
        
        var_name = value[2:-1]  # Remove ${ and }
        if var_name in env_vars:
            return env_vars[var_name]
        return value
    
    def get_enabled_services(self) -> List[str]:
        """Get list of enabled services"""
        enabled_services = []
        for key, value in self.env_vars.items():
            if key.endswith('_ENABLE') and key.startswith('KOS_') and value.lower() == 'true':
                service_name = key[4:-7].lower()  # Remove KOS_ prefix and _ENABLE suffix
                enabled_services.append(service_name)
        return enabled_services
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for a specific service"""
        config = {}
        prefix = f"KOS_{service_name.upper()}"
        
        # Extract all variables for this service
        for key, value in self.env_vars.items():
            if key.startswith(prefix):
                config_key = key[len(prefix)+1:].lower()  # Remove prefix and convert to lowercase
                config[config_key] = value
        
        return config
    
    def get_service_build_config(self, service_name: str) -> dict:
        """Get build configuration for a specific service"""
        # Always set build context to project root
        build_config = {
            'context': '..',
            'dockerfile': f'docker/Dockerfile.unified'
        }
        return build_config
    
    def categorize_services(self) -> Dict[str, List[str]]:
        """Categorize services into different stages"""
        enabled_services = self.get_enabled_services()
        
        # Define service categories - CORE includes all essential services
        core_services = [
            'api', 'postgres', 'redis', 'nginx', 'frontend',  # Basic infrastructure
            'minio', 'neo4j', 'elasticsearch', 'weaviate',    # Storage services
            'prometheus', 'grafana', 'cadvisor',              # Monitoring (essential)
            'vault', 'nextcloud'                              # Security & file storage
        ]
        dev_services = ['gitea', 'supabase', 'browseruse', 'context7', 'vscodium', 'code_server']
        ai_services = ['ollama', 'openwebui', 'huggingface', 'automatic1111', 'comfyui']
        workflow_services = ['n8n', 'penpot']
        manager_services = ['prompt_manager', 'artifact_manager']
        admin_services = ['admin_panel', 'registry', 'pgadmin', 'redis_commander', 'mongo_express']
        
        # Categorize enabled services
        categories = {
            'core': [s for s in enabled_services if s in core_services],
            'dev': [s for s in enabled_services if s in dev_services],
            'ai': [s for s in enabled_services if s in ai_services],
            'workflow': [s for s in enabled_services if s in workflow_services],
            'manager': [s for s in enabled_services if s in manager_services],
            'admin': [s for s in enabled_services if s in admin_services]
        }
        
        return categories
    
    def generate_service_definition(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service definition for Docker Compose"""
        service_def = {}
        
        # Image - use standardized KOS_*_IMAGE variable
        image_key = f"KOS_{service_name.upper()}_IMAGE"
        image = self.env_vars.get(image_key, f'{service_name}:latest')
        if image.startswith('kos-v1-'):
            service_def['build'] = {
                'context': '..',
                'dockerfile': 'docker/Dockerfile.unified'
            }
        else:
            service_def['image'] = image
        
        # Container name - use standardized KOS_*_CONTAINER_NAME variable
        container_name_key = f"KOS_{service_name.upper()}_CONTAINER_NAME"
        container_name = self.env_vars.get(container_name_key, f'kos-{service_name}')
        service_def['container_name'] = container_name
        
        # Ports - use standardized EXTERNAL_PORT and INTERNAL_PORT variables
        ports = []
        external_port_key = f"KOS_{service_name.upper()}_EXTERNAL_PORT"
        internal_port_key = f"KOS_{service_name.upper()}_INTERNAL_PORT"
        
        if external_port_key in self.env_vars and internal_port_key in self.env_vars:
            external_port = self.env_vars[external_port_key]
            internal_port = self.env_vars[internal_port_key]
            ports.append(f"{external_port}:{internal_port}")
        
        # Handle special cases for services with multiple ports
        if service_name == 'neo4j':
            # Neo4j has both HTTP and Bolt ports
            neo4j_http_ext = self.env_vars.get('KOS_NEO4J_HTTP_EXTERNAL_PORT')
            neo4j_http_int = self.env_vars.get('KOS_NEO4J_HTTP_INTERNAL_PORT')
            if neo4j_http_ext and neo4j_http_int:
                ports.append(f"{neo4j_http_ext}:{neo4j_http_int}")
        
        elif service_name == 'elasticsearch':
            # Elasticsearch has cluster port
            es_cluster_ext = self.env_vars.get('KOS_ELASTICSEARCH_CLUSTER_EXTERNAL_PORT')
            es_cluster_int = self.env_vars.get('KOS_ELASTICSEARCH_CLUSTER_INTERNAL_PORT')
            if es_cluster_ext and es_cluster_int:
                ports.append(f"{es_cluster_ext}:{es_cluster_int}")
        
        elif service_name == 'minio':
            # MinIO has console port
            minio_console_ext = self.env_vars.get('KOS_MINIO_CONSOLE_EXTERNAL_PORT')
            minio_console_int = self.env_vars.get('KOS_MINIO_CONSOLE_INTERNAL_PORT')
            if minio_console_ext and minio_console_int:
                ports.append(f"{minio_console_ext}:{minio_console_int}")
        
        elif service_name == 'gitea':
            # Gitea has SSH port
            gitea_ssh_ext = self.env_vars.get('KOS_GITEA_SSH_EXTERNAL_PORT')
            gitea_ssh_int = self.env_vars.get('KOS_GITEA_SSH_INTERNAL_PORT')
            if gitea_ssh_ext and gitea_ssh_int:
                ports.append(f"{gitea_ssh_ext}:{gitea_ssh_int}")
        
        elif service_name == 'supabase':
            # Supabase has studio port
            supabase_studio_ext = self.env_vars.get('KOS_SUPABASE_STUDIO_EXTERNAL_PORT')
            supabase_studio_int = self.env_vars.get('KOS_SUPABASE_STUDIO_INTERNAL_PORT')
            if supabase_studio_ext and supabase_studio_int:
                ports.append(f"{supabase_studio_ext}:{supabase_studio_int}")
        
        if ports:
            service_def['ports'] = ports
        
        # Environment variables - include all KOS_* variables for this service
        env_vars = []
        for key, value in self.env_vars.items():
            if key.startswith(f"KOS_{service_name.upper()}_"):
                # Convert KOS_SERVICE_VAR to SERVICE_VAR for Docker
                env_key = key[4:]  # Remove KOS_ prefix
                env_vars.append(f"{env_key}={value}")
        
        # Add global admin user/password variables
        if 'KOS_ADMIN_USER' in self.env_vars:
            env_vars.append(f"ADMIN_USER={self.env_vars['KOS_ADMIN_USER']}")
        if 'KOS_ADMIN_PASSWORD' in self.env_vars:
            env_vars.append(f"ADMIN_PASSWORD={self.env_vars['KOS_ADMIN_PASSWORD']}")
        
        # Add service-specific user/password mappings
        user_password_mappings = {
            'postgres': ('POSTGRES_USER', 'POSTGRES_PASSWORD'),
            'redis': (None, 'REDIS_PASSWORD'),
            'neo4j': ('NEO4J_USER', 'NEO4J_PASSWORD'),
            'minio': ('MINIO_ROOT_USER', 'MINIO_ROOT_PASSWORD'),
            'elasticsearch': ('ELASTICSEARCH_USERNAME', 'ELASTICSEARCH_PASSWORD'),
            'grafana': ('GRAFANA_ADMIN_USER', 'GRAFANA_ADMIN_PASSWORD'),
            'openwebui': ('OPENWEBUI_ADMIN_USER', 'OPENWEBUI_ADMIN_PASSWORD'),
            'n8n': ('N8N_BASIC_AUTH_USER', 'N8N_BASIC_AUTH_PASSWORD'),
            'penpot': ('PENPOT_ADMIN_USER', 'PENPOT_ADMIN_PASSWORD'),
            'nextcloud': ('NEXTCLOUD_ADMIN_USER', 'NEXTCLOUD_ADMIN_PASSWORD'),
            'pgadmin': (None, None),  # handled below
            'redis_commander': ('REDIS_COMMANDER_USER', 'REDIS_COMMANDER_PASSWORD'),
            'mongo_express': ('MONGO_EXPRESS_USER', 'MONGO_EXPRESS_PASSWORD'),
        }

        if service_name == 'pgadmin':
            # Always use the resolved KOS_PGADMIN_EMAIL for PGADMIN_DEFAULT_EMAIL
            if 'KOS_PGADMIN_EMAIL' in self.env_vars:
                email_value = self.resolve_variable(self.env_vars['KOS_PGADMIN_EMAIL'], self.env_vars)
                env_vars.append(f"PGADMIN_DEFAULT_EMAIL={email_value}")
            if 'KOS_PGADMIN_PASSWORD' in self.env_vars:
                password_value = self.resolve_variable(self.env_vars['KOS_PGADMIN_PASSWORD'], self.env_vars)
                env_vars.append(f"PGADMIN_DEFAULT_PASSWORD={password_value}")
        elif service_name in user_password_mappings:
            user_key, password_key = user_password_mappings[service_name]
            if user_key and f"KOS_{service_name.upper()}_USER" in self.env_vars:
                user_value = self.resolve_variable(self.env_vars[f'KOS_{service_name.upper()}_USER'], self.env_vars)
                env_vars.append(f"{user_key}={user_value}")
            elif user_key and f"KOS_{service_name.upper()}_EMAIL" in self.env_vars:
                email_value = self.resolve_variable(self.env_vars[f'KOS_{service_name.upper()}_EMAIL'], self.env_vars)
                env_vars.append(f"{user_key}={email_value}")
            if password_key and f"KOS_{service_name.upper()}_PASSWORD" in self.env_vars:
                password_value = self.resolve_variable(self.env_vars[f'KOS_{service_name.upper()}_PASSWORD'], self.env_vars)
                env_vars.append(f"{password_key}={password_value}")
        
        # Add ENV_ prefixed variables for supervisor compatibility
        env_with_env_prefix = {}
        for k, v in config.items():
            env_with_env_prefix[k] = v
            env_key = f'ENV_{k}'
            if not config.get(env_key):
                env_with_env_prefix[env_key] = v
        config['environment'] = env_with_env_prefix
        
        if env_vars:
            service_def['environment'] = env_vars
        
        # Volumes - look for KOS_*_VOLUME variables
        volumes = []
        for key, value in self.env_vars.items():
            if key.startswith(f"KOS_{service_name.upper()}_") and key.endswith('_VOLUME'):
                volumes.append(value)
        
        # Add default data volume if no specific volumes defined
        if not volumes:
            volumes.append(f"kos-{service_name}-data:/data")
        
        if volumes:
            service_def['volumes'] = volumes
        
        # Networks
        service_def['networks'] = ['kos-network']
        
        # Restart policy
        service_def['restart'] = 'unless-stopped'
        
        # Health checks for critical services
        service_def['healthcheck'] = self.get_health_check(service_name)
        
        # Dependencies
        dependencies = []
        if service_name == 'api':
            dependencies.extend(['postgres', 'redis'])
        elif service_name == 'frontend':
            dependencies.append('api')
        elif service_name in ['grafana', 'prometheus']:
            dependencies.append('elasticsearch')
        elif service_name == 'weaviate':
            dependencies.append('huggingface')  # Weaviate needs Huggingface for transformers
        
        if dependencies:
            service_def['depends_on'] = dependencies
        
        # Command - use KOS_*_COMMAND variable
        command_key = f"KOS_{service_name.upper()}_COMMAND"
        if command_key in self.env_vars:
            service_def['command'] = self.env_vars[command_key]
        
        return service_def
    
    def get_health_check(self, service_name: str) -> dict:
        """Get health check configuration for a service"""
        if service_name == 'redis':
            return {
                'test': ['CMD-SHELL', 'redis-cli ping | grep PONG'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'postgres':
            return {
                'test': ['CMD-SHELL', 'pg_isready -U kos-admin -d kos'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'elasticsearch':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:9200/_cluster/health || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'neo4j':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:7474/browser/ || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'weaviate':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:8080/v1/.well-known/ready || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'minio':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:9000/minio/health/live || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'vault':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:8200/v1/sys/health || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'grafana':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:3000/api/health || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'prometheus':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:9090/-/healthy || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'cadvisor':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:8081/healthz || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'nextcloud':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:8083/status.php || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'pgadmin':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:80/misc/ping || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'redis_commander':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:8081 || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'admin_panel':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:9003/api/status || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'mongo_express':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:8081 || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'api':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:8000/health || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        elif service_name == 'frontend':
            return {
                'test': ['CMD-SHELL', 'curl -f http://localhost:3000 || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        else:
            # Default health check for HTTP services
            port = self.env_vars.get(f'KOS_{service_name.upper()}_INTERNAL_PORT', '8000')
            return {
                'test': ['CMD-SHELL', f'curl -f http://localhost:{port}/health || exit 1'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
    
    def generate_compose_file(self, services: List[str], filename: str, description: str = "") -> None:
        """Generate a Docker Compose file for the specified services"""
        # Ensure docker directory exists
        docker_dir = Path("docker")
        docker_dir.mkdir(exist_ok=True)
        
        # Create full path in docker directory
        file_path = docker_dir / filename
        
        compose_data = {
            'name': 'kos-v1',
            'services': {},
            'networks': {
                'kos-network': {
                    'driver': 'bridge',
                    'ipam': {
                        'config': [{'subnet': '172.20.0.0/16'}]
                    }
                }
            },
            'volumes': {}
        }
        
        print(f"\nGenerating {file_path} ({description})")
        print(f"Services: {', '.join(services)}")
        
        # Collect all volumes used by services
        all_volumes = set()
        
        for service_name in services:
            config = self.get_service_config(service_name)
            if config:
                service_def = self.generate_service_definition(service_name, config)
                # Filter depends_on to only include services in this compose file
                if 'depends_on' in service_def:
                    filtered_deps = [dep for dep in service_def['depends_on'] if dep in services]
                    if filtered_deps:
                        service_def['depends_on'] = filtered_deps
                    else:
                        service_def.pop('depends_on')
                compose_data['services'][service_name] = service_def
                print(f"  {service_name}: ✅ ENABLED")
                
                # Add service volumes to the volumes section
                if 'volumes' in service_def:
                    for volume in service_def['volumes']:
                        if ':' in volume:  # Format: volume_name:container_path
                            volume_name = volume.split(':')[0]
                            all_volumes.add(volume_name)
            else:
                print(f"  {service_name}: ❌ NO CONFIG")
        
        # Add all collected volumes to the volumes section
        for volume_name in all_volumes:
            compose_data['volumes'][volume_name] = {
                'driver': 'local'
            }
        
        # Write the compose file
        with open(file_path, 'w') as f:
            yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"Generated: {file_path}")
    
    def generate_all_files(self):
        """Generate all Docker Compose files"""
        categories = self.categorize_services()
        
        # Generate core compose file (essential services)
        core_services = categories.get('core', [])
        if core_services:
            self.generate_compose_file(core_services, 'docker-compose.core.yml', 'Core Services (Essential Infrastructure)')
        
        # Generate dev compose file
        dev_services = categories.get('dev', [])
        if dev_services:
            self.generate_compose_file(dev_services, 'docker-compose.dev.yml', 'Development Services')
        
        # Generate AI compose file
        ai_services = categories.get('ai', [])
        if ai_services:
            self.generate_compose_file(ai_services, 'docker-compose.ai.yml', 'AI/ML Services')
        
        # Generate workflow compose file
        workflow_services = categories.get('workflow', [])
        if workflow_services:
            self.generate_compose_file(workflow_services, 'docker-compose.workflow.yml', 'Workflow Services')
        
        # Generate manager compose file
        manager_services = categories.get('manager', [])
        if manager_services:
            self.generate_compose_file(manager_services, 'docker-compose.manager.yml', 'Manager Services')
        
        # Generate admin compose file
        admin_services = categories.get('admin', [])
        if admin_services:
            self.generate_compose_file(admin_services, 'docker-compose.admin.yml', 'Admin Services')
        
        # Generate full compose file (all services)
        all_services = []
        for category_services in categories.values():
            all_services.extend(category_services)
        
        if all_services:
            self.generate_compose_file(all_services, 'docker-compose.full.yml', 'All Services Combined')
        
        # Generate main docker-compose.yml (defaults to core)
        if core_services:
            self.generate_compose_file(core_services, 'docker-compose.yml', 'Default (Core Services)')
        
        # Count files in docker directory
        docker_dir = Path("docker")
        compose_files = list(docker_dir.glob("docker-compose*.yml"))
        
        print(f"\n🎉 Generated {len(compose_files)} Docker Compose files in docker/ directory!")
        print("\n📋 Usage:")
        print("  docker-compose -f docker/docker-compose.yml up -d                    # Start core services (default)")
        print("  docker-compose -f docker/docker-compose.dev.yml up -d")
        print("  docker-compose -f docker/docker-compose.ai.yml up -d")
        print("  docker-compose -f docker/docker-compose.workflow.yml up -d")
        print("  docker-compose -f docker/docker-compose.full.yml up -d  # Start all services")
        print("\n🔧 Core Services include: API, Database, Storage, Monitoring, Security")
        print("🔧 Optional Services: Development, AI/ML, Workflow, Management")

def main():
    generator = KOSDockerComposeGenerator()
    generator.generate_all_files()

if __name__ == "__main__":
    main() 