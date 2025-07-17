#!/usr/bin/env python3
"""
KOS v1 Generic Docker Compose Generator
Generates docker-compose.yml dynamically from environment variables only
No hardcoded service templates or configurations
"""

import os
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from scripts.utils.logger import get_logger
logger = get_logger('docker_generator')

# --- Logging ---
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'docker_generator.log')

# Remove dlog and replace all dlog(msg, level) with logger.log(msg, level)

# NOTE: For AI/ML services (A1111, InvokeAI, ComfyUI, etc.), the generator should set CPU/GPU mode based on system autodetection.
# On Intel Macs and non-GPU systems, CPU-only mode is required and should be set automatically.

class KOSDockerComposeGenerator:
    def __init__(self, env_file: str = ".env"):
        # Always use the root .env file as the single source of truth
        self.env_file = env_file
        self.env_vars = self.load_env_vars()
        
    def load_env_vars(self) -> Dict[str, str]:
        """Load environment variables from the generated .env file"""
        env_vars = {}
        
        # Load from the generated .env file (single source of truth)
        if os.path.exists(self.env_file):
            logger.log(f"Loading environment from: {self.env_file}", 'INFO')
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        else:
            logger.log(f"Environment file {self.env_file} not found!", 'ERROR')
            logger.log("Please run installer/env_loader.py first to generate the .env file.", 'ERROR')
            return {}
        
        # Resolve variable substitutions
        resolved_vars = {}
        for key, value in env_vars.items():
            resolved_vars[key] = self.resolve_variable(value, env_vars)
        
        return resolved_vars
    
    def resolve_variable(self, value: str, env_vars: Dict[str, str], depth=0) -> str:
        """Recursively resolve variable substitutions in a value"""
        if depth > 10:
            return value
        pattern = r'\$\{([^}]+)\}'
        matches = re.findall(pattern, value)
        if not matches:
            return value
        for var_name in matches:
            var_value = env_vars.get(var_name, '')
            if pattern in var_value:
                var_value = self.resolve_variable(var_value, env_vars, depth+1)
            value = value.replace(f'${{{var_name}}}', var_value)
        return value

    # Use this resolve_variable everywhere an env value is set in the compose output, including health checks and all environment variables.
    
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
        """Categorize services into logical groups using env variables"""
        enabled_services = self.get_enabled_services()
        categories = {}
        compose_groups = {}
        for service in enabled_services:
            upper = service.upper()
            cat_key = f'KOS_{upper}_CATEGORY'
            group_key = f'KOS_{upper}_COMPOSE_GROUP'
            category = self.env_vars.get(cat_key, 'uncategorized')
            group = self.env_vars.get(group_key, 'uncategorized')
            categories.setdefault(category, []).append(service)
            compose_groups.setdefault(group, []).append(service)
        return compose_groups
    
    def check_service_endpoint_exposure(self, service_name: str, service_def: Dict[str, Any]) -> bool:
        """
        Check if a service exposes at least one endpoint (UI, healthcheck, or addon).
        Returns True if service has endpoint exposure, False if headless.
        """
        # Check if service has ports exposed
        if 'ports' in service_def and service_def['ports']:
            return True
        
        # Check if service has healthcheck defined
        if 'healthcheck' in service_def and service_def['healthcheck']:
            return True
        
        # Check if service has environment variables that indicate UI/addon exposure
        env_vars = service_def.get('environment', [])
        for env_var in env_vars:
            if any(keyword in env_var.upper() for keyword in ['UI', 'WEB', 'DASHBOARD', 'CONSOLE', 'ADMIN']):
                return True
        
        # Check for specific service patterns that indicate endpoint exposure
        service_endpoint_indicators = {
            'api': True,  # API always has endpoints
            'frontend': True,  # Frontend always has UI
            'nginx': True,  # Nginx is a web server
            'grafana': True,  # Grafana has web UI
            'prometheus': True,  # Prometheus has web UI
            'cadvisor': True,  # cAdvisor has web UI
            'pgadmin': True,  # pgAdmin has web UI
            'mongo_express': True,  # Mongo Express has web UI
            'redis_commander': True,  # Redis Commander has web UI
            'nextcloud': True,  # Nextcloud has web UI
            'openwebui': True,  # OpenWebUI has web interface
            'automatic1111': True,  # A1111 has web UI
            'comfyui': True,  # ComfyUI has web UI
            'invokeai': True,  # InvokeAI has web UI
            'n8n': True,  # n8n has web UI
            'penpot': True,  # Penpot has web UI
            'admin_panel': True,  # Admin panel has web UI
            'gitea': True,  # Gitea has web UI
            'supabase': True,  # Supabase has studio
            'browseruse': True,  # Browseruse has web interface
            'context7': True,  # Context7 has web interface
            'codium': True,  # Codium has web interface
            'registry': True,  # Registry has web interface
            'vault': True,  # Vault has web UI
            'prompt_manager': True,  # Prompt manager has web interface
            'artifact_manager': True,  # Artifact manager has web interface
            'neo4j': True,  # Neo4j has web UI (browser)
        }
        
        return service_endpoint_indicators.get(service_name, False)

    def generate_service_definition(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service definition for Docker Compose"""
        service_def = {}
        
        # Image - use standardized KOS_*_IMAGE variable - NO FALLBACKS
        image_key = f"KOS_{service_name.upper()}_IMAGE"
        image = self.env_vars.get(image_key)
        if not image:
            logger.log(f"Missing image configuration for {service_name} ({image_key})", 'ERROR')
            return {}
            
        if image.startswith('kos-v1-'):
            service_def['build'] = {
                'context': '..',
                'dockerfile': 'docker/Dockerfile.unified'
            }
        elif image == 'context7-mcp:latest':
            # Custom build for Context7 MCP server
            service_def['build'] = {
                'context': '..',
                'dockerfile': 'docker/context7.Dockerfile'
            }
        else:
            service_def['image'] = image
        
        # Container name - use standardized KOS_*_CONTAINER_NAME variable - NO FALLBACKS
        container_name_key = f"KOS_{service_name.upper()}_CONTAINER_NAME"
        container_name = self.env_vars.get(container_name_key)
        if not container_name:
            logger.log(f"Missing container name for {service_name} ({container_name_key})", 'ERROR')
            return {}
            
        # Resolve any variable substitutions in container name
        container_name = self.resolve_variable(container_name, self.env_vars)
        service_def['container_name'] = container_name
        
        # Ports - use standardized EXTERNAL_PORT and INTERNAL_PORT variables - NO FALLBACKS
        ports = []
        external_port_key = f"KOS_{service_name.upper()}_EXTERNAL_PORT"
        internal_port_key = f"KOS_{service_name.upper()}_INTERNAL_PORT"
        
        external_port = self.env_vars.get(external_port_key)
        internal_port = self.env_vars.get(internal_port_key)
        
        if external_port and internal_port:
            ports.append(f"{self.resolve_variable(external_port, self.env_vars)}:{self.resolve_variable(internal_port, self.env_vars)}")
        else:
            logger.log(f"Missing port configuration for {service_name} ({external_port_key}, {internal_port_key})", 'ERROR')
            return {}
        
        # Handle special cases for services with multiple ports - ALL FROM ENV
        if service_name == 'neo4j':
            # Neo4j has both HTTP and Bolt ports
            neo4j_http_ext = self.env_vars.get('KOS_NEO4J_HTTP_EXTERNAL_PORT')
            neo4j_http_int = self.env_vars.get('KOS_NEO4J_HTTP_INTERNAL_PORT')
            if neo4j_http_ext and neo4j_http_int:
                ports.append(f"{self.resolve_variable(neo4j_http_ext, self.env_vars)}:{self.resolve_variable(neo4j_http_int, self.env_vars)}")
        
        elif service_name == 'elasticsearch':
            # Elasticsearch has cluster port
            es_cluster_ext = self.env_vars.get('KOS_ELASTICSEARCH_CLUSTER_EXTERNAL_PORT')
            es_cluster_int = self.env_vars.get('KOS_ELASTICSEARCH_CLUSTER_INTERNAL_PORT')
            if es_cluster_ext and es_cluster_int:
                ports.append(f"{self.resolve_variable(es_cluster_ext, self.env_vars)}:{self.resolve_variable(es_cluster_int, self.env_vars)}")
        
        elif service_name == 'minio':
            # MinIO has console port
            minio_console_ext = self.env_vars.get('KOS_MINIO_CONSOLE_EXTERNAL_PORT')
            minio_console_int = self.env_vars.get('KOS_MINIO_CONSOLE_INTERNAL_PORT')
            if minio_console_ext and minio_console_int:
                ports.append(f"{self.resolve_variable(minio_console_ext, self.env_vars)}:{self.resolve_variable(minio_console_int, self.env_vars)}")
        
        elif service_name == 'gitea':
            # Gitea has SSH port
            gitea_ssh_ext = self.env_vars.get('KOS_GITEA_SSH_EXTERNAL_PORT')
            gitea_ssh_int = self.env_vars.get('KOS_GITEA_SSH_INTERNAL_PORT')
            if gitea_ssh_ext and gitea_ssh_int:
                ports.append(f"{self.resolve_variable(gitea_ssh_ext, self.env_vars)}:{self.resolve_variable(gitea_ssh_int, self.env_vars)}")
        
        elif service_name == 'supabase':
            # Supabase has studio port
            supabase_studio_ext = self.env_vars.get('KOS_SUPABASE_STUDIO_EXTERNAL_PORT')
            supabase_studio_int = self.env_vars.get('KOS_SUPABASE_STUDIO_INTERNAL_PORT')
            if supabase_studio_ext and supabase_studio_int:
                ports.append(f"{self.resolve_variable(supabase_studio_ext, self.env_vars)}:{self.resolve_variable(supabase_studio_int, self.env_vars)}")
        
        if ports:
            service_def['ports'] = ports
        
        # Environment variables - include all KOS_* variables for this service
        env_vars = []
        # Whitelist for third-party services
        third_party_env_whitelists = {
            'registry': ['REGISTRY_HTTP_SECRET'],
            'pgadmin': ['PGADMIN_DEFAULT_EMAIL', 'PGADMIN_DEFAULT_PASSWORD'],
            'mongo_express': ['ME_CONFIG_MONGODB_SERVER', 'ME_CONFIG_MONGODB_ADMINUSERNAME', 'ME_CONFIG_MONGODB_ADMINPASSWORD'],
            'redis_commander': ['REDIS_HOSTS', 'REDIS_COMMANDER_USER', 'REDIS_COMMANDER_PASSWORD'],
            # Add more as needed
        }
        if service_name in third_party_env_whitelists:
            for key, value in self.env_vars.items():
                for allowed in third_party_env_whitelists[service_name]:
                    if key == allowed or key.endswith('_' + allowed):
                        env_key = key[4:] if key.startswith('KOS_') else key
                        resolved_value = self.resolve_variable(value, self.env_vars)
                        env_vars.append(f"{env_key}={resolved_value}")
        else:
            for key, value in self.env_vars.items():
                if key.startswith(f"KOS_{service_name.upper()}_"):
                    env_key = key[4:]
                    resolved_value = self.resolve_variable(value, self.env_vars)
                    env_vars.append(f"{env_key}={resolved_value}")
        
        # Add global admin user/password variables (only if not already added)
        if 'KOS_ADMIN_USER' in self.env_vars and 'ADMIN_USER' not in [env.split('=')[0] for env in env_vars]:
            admin_user = self.resolve_variable(self.env_vars['KOS_ADMIN_USER'], self.env_vars)
            env_vars.append(f"ADMIN_USER={admin_user}")
        if 'KOS_ADMIN_PASSWORD' in self.env_vars and 'ADMIN_PASSWORD' not in [env.split('=')[0] for env in env_vars]:
            admin_password = self.resolve_variable(self.env_vars['KOS_ADMIN_PASSWORD'], self.env_vars)
            env_vars.append(f"ADMIN_PASSWORD={admin_password}")
        
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
        
        # --- Centralized Model Volume Logic for Media Gen Services ---
        media_gen_services = ['automatic1111', 'comfyui', 'invokeai']
        if service_name in media_gen_services:
            model_root = self.env_vars.get('KOS_MODEL_ROOT')
            model_volume = self.env_vars.get('KOS_MODEL_VOLUME', 'kos-models-data')
            if model_root:
                # User override: bind mount
                service_def['volumes'] = [f'{model_root}:/models']
            else:
                # Default: shared Docker volume
                service_def['volumes'] = [f'{model_volume}:/models']
        else:
            # Volumes - look for KOS_*_VOLUME variables - NO FALLBACKS
            volumes = []
            for key, value in self.env_vars.items():
                if key.startswith(f"KOS_{service_name.upper()}_") and key.endswith('_VOLUME'):
                    # Split value at the first colon for Docker named volume syntax
                    if ':' in value:
                        vol_name, cont_path = value.split(':', 1)
                        volumes.append({'type': 'volume', 'source': vol_name, 'target': cont_path, 'volume': {}})
                    else:
                        volumes.append(value)
            default_volume = self.env_vars.get(f'KOS_{service_name.upper()}_DEFAULT_VOLUME')
            if not volumes and default_volume:
                if ':' in default_volume:
                    vol_name, cont_path = default_volume.split(':', 1)
                    volumes.append({'type': 'volume', 'source': vol_name, 'target': cont_path, 'volume': {}})
                else:
                    volumes.append(default_volume)
            if volumes:
                service_def['volumes'] = volumes
        
        # --- GPU Runtime Logic for AI/ML Services ---
        ai_ml_services = ['automatic1111', 'comfyui', 'invokeai', 'huggingface']
        if service_name in ai_ml_services:
            # Check for GPU support (env or detection)
            gpu_enable = self.env_vars.get('KOS_GPU_ENABLE', '').lower() == 'true'
            # Compose v3.8+ (preferred)
            if gpu_enable:
                service_def['deploy'] = {
                    'resources': {
                        'reservations': {
                            'devices': [
                                {
                                    'driver': 'nvidia',
                                    'count': 'all',
                                    'capabilities': ['gpu']
                                }
                            ]
                        }
                    }
                }
            # For legacy Compose, add runtime: nvidia (if needed)
            # else: fallback to CPU (no runtime stanza)
        # Networks - get from environment - NO FALLBACKS
        network_key = f'KOS_{service_name.upper()}_NETWORK'
        network = self.env_vars.get(network_key)
        if not network:
            logger.log(f"ERROR: Missing network configuration for {service_name} ({network_key})", 'ERROR')
            return {}
        service_def['networks'] = [network]
        
        # Restart policy - get from environment - NO FALLBACKS
        restart_key = f'KOS_{service_name.upper()}_RESTART_POLICY'
        restart_policy = self.env_vars.get(restart_key)
        if not restart_policy:
            logger.log(f"ERROR: Missing restart policy for {service_name} ({restart_key})", 'ERROR')
            return {}
        service_def['restart'] = restart_policy
        
        # Health checks for critical services
        healthcheck = self.get_health_check(service_name)
        if healthcheck:
            # Recursively resolve all values in healthcheck dict
            for k, v in healthcheck.items():
                if isinstance(v, list):
                    healthcheck[k] = [self.resolve_variable(str(item), self.env_vars) for item in v]
                else:
                    healthcheck[k] = self.resolve_variable(str(v), self.env_vars)
            service_def['healthcheck'] = healthcheck
        
        # Dependencies from env
        depends_key = f'KOS_{service_name.upper()}_DEPENDS_ON'
        depends_val = self.env_vars.get(depends_key, '')
        dependencies = [dep.strip() for dep in depends_val.split(',') if dep.strip()]
        if dependencies:
            service_def['depends_on'] = dependencies
        
        # Command - use KOS_*_COMMAND variable
        command_key = f"KOS_{service_name.upper()}_COMMAND"
        if command_key in self.env_vars:
            service_def['command'] = self.env_vars[command_key]
        
        # Check endpoint exposure and warn if headless
        if not self.check_service_endpoint_exposure(service_name, service_def):
            logger.log(f"  ⚠️  WARNING: {service_name} appears to be headless (no UI, healthcheck, or addon endpoint)", 'WARNING')
        
        return service_def
    
    def get_health_check(self, service_name: str) -> dict:
        """Get health check configuration for a service"""
        # Get health check configuration from environment variables - NO FALLBACKS
        health_check_enabled = self.env_vars.get(f'KOS_{service_name.upper()}_HEALTH_CHECK_ENABLED')
        if not health_check_enabled or health_check_enabled.lower() != 'true':
            return {}
            
        # Get health check configuration from environment variables - NO FALLBACKS
        interval = self.env_vars.get(f'KOS_{service_name.upper()}_HEALTH_CHECK_INTERVAL')
        timeout = self.env_vars.get(f'KOS_{service_name.upper()}_HEALTH_CHECK_TIMEOUT')
        retries = self.env_vars.get(f'KOS_{service_name.upper()}_HEALTH_CHECK_RETRIES')
        
        # Get service port from environment variables - NO FALLBACKS
        internal_port = self.env_vars.get(f'KOS_{service_name.upper()}_INTERNAL_PORT')
        
        # Validate required values exist
        if not interval or not timeout or not retries or not internal_port:
            logger.log(f"ERROR: Missing required health check configuration for {service_name}", 'ERROR')
            return {}
        
        # Get health check command from environment - NO FALLBACKS
        health_command = self.env_vars.get(f'KOS_{service_name.upper()}_HEALTH_CHECK_COMMAND')
        if not health_command:
            logger.log(f"ERROR: Missing health check command for {service_name}", 'ERROR')
            return {}
        
        # Resolve any variable substitutions in the health command
        resolved_health_command = self.resolve_variable(health_command, self.env_vars)
        
        return {
            'test': ['CMD-SHELL', resolved_health_command],
            'interval': interval,
            'timeout': timeout,
            'retries': int(retries)
        }
    
    def generate_compose_file(self, services: List[str], filename: str, description: str = "") -> None:
        """Generate a Docker Compose file for the specified services"""
        # Ensure docker directory exists
        docker_dir = Path("docker")
        docker_dir.mkdir(exist_ok=True)
        
        # Create full path in docker directory
        file_path = docker_dir / filename
        
        # Get network configuration from environment - NO FALLBACKS
        network_name = self.env_vars.get('KOS_CONTAINER_NETWORK')
        network_driver = self.env_vars.get('KOS_NETWORK_DRIVER')
        network_subnet = self.env_vars.get('KOS_NETWORK_SUBNET')
        
        if not network_name or not network_driver or not network_subnet:
            logger.log(f"ERROR: Missing network configuration (KOS_CONTAINER_NETWORK, KOS_NETWORK_DRIVER, KOS_NETWORK_SUBNET)", 'ERROR')
            return
        
        compose_data = {
            'name': self.env_vars.get('KOS_PROJECT_NAME', 'kos-v1'),
            'services': {},
            'networks': {
                network_name: {
                    'driver': network_driver,
                    'ipam': {
                        'config': [{'subnet': network_subnet}]
                    }
                }
            },
            'volumes': {}
        }
        
        logger.log(f"\nGenerating {file_path} ({description})", 'INFO')
        logger.log(f"Services: {', '.join(services)}", 'INFO')
        
        # Collect all volumes used by services
        all_volumes = set()
        
        for service_name in services:
            config = self.get_service_config(service_name)
            if config:
                service_def = self.generate_service_definition(service_name, config)
                if not service_def:  # Service definition failed due to missing env vars
                    logger.log(f"  {service_name}: ❌ CONFIGURATION ERROR", 'ERROR')
                    continue
                    
                # Filter depends_on to only include services in this compose file
                if 'depends_on' in service_def:
                    filtered_deps = [dep for dep in service_def['depends_on'] if dep in services]
                    if filtered_deps:
                        service_def['depends_on'] = filtered_deps
                    else:
                        service_def.pop('depends_on')
                compose_data['services'][service_name] = service_def
                logger.log(f"  {service_name}: ✅ ENABLED", 'INFO')
                
                # Add service volumes to the volumes section
                if 'volumes' in service_def:
                    for volume in service_def['volumes']:
                        if isinstance(volume, dict): # Check if it's a dict for named volume
                            vol_name = volume['source']
                            all_volumes.add(vol_name)
                        elif ':' in volume:  # Format: volume_name:container_path
                            volume_name = volume.split(':')[0]
                            all_volumes.add(volume_name)
            else:
                logger.log(f"  {service_name}: ❌ NO CONFIG", 'ERROR')
        
        # Add all collected volumes to the volumes section
        for volume_name in all_volumes:
            compose_data['volumes'][volume_name] = {
                'driver': 'local'
            }
        
        # Write the compose file
        with open(file_path, 'w') as f:
            yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
        
        logger.log(f"Generated: {file_path}", 'INFO')
    
    def generate_all_files(self):
        """Generate all Docker Compose files with logical organization"""
        categories = self.categorize_services()
        
        # Generate infrastructure compose file (core database and storage)
        infrastructure_services = categories.get('infrastructure', [])
        if infrastructure_services:
            self.generate_compose_file(infrastructure_services, 'docker-compose.infrastructure.yml', 'Infrastructure Services (Database + Storage)')
        
        # Generate core compose file (main application components)
        core_services = categories.get('core', [])
        if core_services:
            self.generate_compose_file(core_services, 'docker-compose.core.yml', 'Core Application Services (API + Frontend + Nginx)')
        
        # Generate AI compose file (AI/ML services)
        ai_services = categories.get('ai', [])
        if ai_services:
            self.generate_compose_file(ai_services, 'docker-compose.ai.yml', 'AI Services (Ollama + OpenWebUI + Image Generation)')
        
        # Generate workflow compose file (automation and workflow tools)
        workflow_services = categories.get('workflow', [])
        if workflow_services:
            self.generate_compose_file(workflow_services, 'docker-compose.workflow.yml', 'Workflow Services (n8n + Penpot + Nextcloud)')
        
        # Generate monitoring compose file (optional monitoring stack)
        monitoring_services = categories.get('monitoring', [])
        if monitoring_services:
            self.generate_compose_file(monitoring_services, 'docker-compose.monitoring.yml', 'Monitoring Services (Optional)')
        
        # Generate admin compose file (database management UIs)
        admin_services = categories.get('admin', [])
        if admin_services:
            self.generate_compose_file(admin_services, 'docker-compose.admin.yml', 'Admin Tools (Database Management UIs)')
        
        # Generate development compose file (optional development environment)
        dev_services = categories.get('dev', [])
        if dev_services:
            self.generate_compose_file(dev_services, 'docker-compose.dev.yml', 'Development Tools (Optional)')
        
        # Generate heavy AI compose file (resource-intensive AI services)
        heavy_ai_services = categories.get('heavy_ai', [])
        if heavy_ai_services:
            self.generate_compose_file(heavy_ai_services, 'docker-compose.heavy-ai.yml', 'Heavy AI Services (Resource Intensive)')
        
        # Generate unified compose file (all services)
        all_services = []
        for category_services in categories.values():
            all_services.extend(category_services)
        
        if all_services:
            self.generate_compose_file(all_services, 'docker-compose.full.yml', 'All Services (Complete Stack)')
        
        # Count files in docker directory
        docker_dir = Path("docker")
        compose_files = list(docker_dir.glob("docker-compose*.yml"))
        
        logger.log(f"\n🎉 Generated {len(compose_files)} Docker Compose files in docker/ directory!", 'INFO')
        logger.log("\n📋 Usage:", 'INFO')
        logger.log("  docker-compose -f docker/docker-compose.infrastructure.yml up -d      # Start infrastructure (databases)", 'INFO')
        logger.log("  docker-compose -f docker/docker-compose.core.yml up -d               # Start core application", 'INFO')
        logger.log("  docker-compose -f docker/docker-compose.ai.yml up -d                 # Start AI services", 'INFO')
        logger.log("  docker-compose -f docker/docker-compose.workflow.yml up -d           # Start workflow tools", 'INFO')
        logger.log("  docker-compose -f docker/docker-compose.monitoring.yml up -d         # Start monitoring", 'INFO')
        logger.log("  docker-compose -f docker/docker-compose.admin.yml up -d              # Start admin tools", 'INFO')
        logger.log("  docker-compose -f docker/docker-compose.dev.yml up -d                # Start development tools", 'INFO')
        logger.log("  docker-compose -f docker/docker-compose.heavy-ai.yml up -d           # Start heavy AI services", 'INFO')
        logger.log("  docker-compose -f docker/docker-compose.full.yml up -d               # Start all services", 'INFO')
        logger.log("\n🔧 Logical Organization:", 'INFO')
        logger.log("  Infrastructure: PostgreSQL, Redis, MinIO, Neo4j, Elasticsearch, Weaviate", 'INFO')
        logger.log("  Core: API, Frontend, Nginx", 'INFO')
        logger.log("  AI: Ollama, OpenWebUI, Automatic1111, ComfyUI, InvokeAI", 'INFO')
        logger.log("  Workflow: n8n, Penpot, Nextcloud", 'INFO')
        logger.log("  Admin: Database management UIs (pgAdmin, mongo_express, redis_commander)", 'INFO')
        logger.log("  Monitoring: Prometheus, Grafana, cAdvisor", 'INFO')
        logger.log("  Development: Browser tools, code editors", 'INFO')
        logger.log("  Heavy AI: Resource-intensive AI services (HuggingFace)", 'INFO')

def main():
    generator = KOSDockerComposeGenerator()
    generator.generate_all_files()

if __name__ == "__main__":
    logger.log('Starting Docker Compose generation', 'INFO')
    try:
        main()
        logger.log('Docker Compose generation completed successfully', 'INFO')
    except Exception as e:
        logger.log(f'Fatal error: {e}', 'ERROR')
        raise 