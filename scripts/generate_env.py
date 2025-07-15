#!/usr/bin/env python3
"""
KOS v1 Generic Environment Generator (with service-centric variable mapping)
Generates environment variables from centralized configuration
Outputs both config-structure and service-centric variables
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

class KOSEnvironmentGenerator:
    def __init__(self, config_path: str = "config/centralized_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load centralized configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def generate_environment_variables(self) -> Dict[str, str]:
        """Generate environment variables from configuration"""
        env_vars = {}
        
        # Flatten all configuration sections into environment variables
        for section_name, section_data in self.config.items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            env_key = f"KOS_{section_name.upper()}_{key.upper()}_{sub_key.upper()}"
                            env_vars[env_key] = str(sub_value)
                    else:
                        env_key = f"KOS_{section_name.upper()}_{key.upper()}"
                        env_vars[env_key] = str(value)
            else:
                env_key = f"KOS_{section_name.upper()}"
                env_vars[env_key] = str(section_data)
        
        # --- Service-centric variable mapping ---
        # Map config-structure variables to service-centric variables expected by Compose/templates
        # This mapping is data-driven and can be extended as needed
        mapping = {
            # API
            "KOS_API_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_BACKEND",
            "KOS_API_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_BACKEND",
            "KOS_API_CONTAINER_NAME": "api",
            # REDIS
            "KOS_REDIS_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_REDIS",
            "KOS_REDIS_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_REDIS",
            "KOS_REDIS_CONTAINER_NAME": "redis",
            # POSTGRES
            "KOS_POSTGRES_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_POSTGRES",
            "KOS_POSTGRES_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_POSTGRES",
            "KOS_POSTGRES_CONTAINER_NAME": "postgres",
            # FRONTEND
            "KOS_FRONTEND_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_FRONTEND",
            "KOS_FRONTEND_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_FRONTEND",
            "KOS_FRONTEND_CONTAINER_NAME": "frontend",
            # GITEA
            "KOS_GITEA_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_GITEA",
            "KOS_GITEA_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_GITEA",
            "KOS_GITEA_CONTAINER_NAME": "gitea",
            # MINIO
            "KOS_MINIO_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_MINIO",
            "KOS_MINIO_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_MINIO",
            "KOS_MINIO_CONTAINER_NAME": "minio",
            "KOS_MINIO_CONSOLE_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_MINIO_CONSOLE",
            "KOS_MINIO_CONSOLE_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_MINIO_CONSOLE",
            # OLLAMA
            "KOS_OLLAMA_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_OLLAMA",
            "KOS_OLLAMA_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_OLLAMA",
            "KOS_OLLAMA_CONTAINER_NAME": "ollama",
            # HUGGINGFACE
            "KOS_HUGGINGFACE_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_HUGGINGFACE",
            "KOS_HUGGINGFACE_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_HUGGINGFACE",
            "KOS_HUGGINGFACE_CONTAINER_NAME": "huggingface",
            # AUTOMATIC1111
            "KOS_AUTOMATIC1111_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_AUTOMATIC1111",
            "KOS_AUTOMATIC1111_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_AUTOMATIC1111",
            "KOS_AUTOMATIC1111_CONTAINER_NAME": "automatic1111",
            # COMFYUI
            "KOS_COMFYUI_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_COMFYUI",
            "KOS_COMFYUI_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_COMFYUI",
            "KOS_COMFYUI_CONTAINER_NAME": "comfyui",
            # WEAVIATE
            "KOS_WEAVIATE_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_WEAVIATE",
            "KOS_WEAVIATE_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_WEAVIATE",
            "KOS_WEAVIATE_CONTAINER_NAME": "weaviate",
            # PGADMIN
            "KOS_PGADMIN_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_PGADMIN",
            "KOS_PGADMIN_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_PGADMIN",
            "KOS_PGADMIN_CONTAINER_NAME": "pgadmin",
            # REDIS COMMANDER
            "KOS_REDIS_COMMANDER_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_REDIS_COMMANDER",
            "KOS_REDIS_COMMANDER_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_REDIS_COMMANDER",
            "KOS_REDIS_COMMANDER_CONTAINER_NAME": "redis_commander",
            # MONGO EXPRESS
            "KOS_MONGO_EXPRESS_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_MONGO_EXPRESS",
            "KOS_MONGO_EXPRESS_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_MONGO_EXPRESS",
            "KOS_MONGO_EXPRESS_CONTAINER_NAME": "mongo_express",
            # N8N
            "KOS_N8N_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_N8N",
            "KOS_N8N_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_N8N",
            "KOS_N8N_CONTAINER_NAME": "n8n",
            # PENPOT
            "KOS_PENPOT_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_PENPOT",
            "KOS_PENPOT_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_PENPOT",
            "KOS_PENPOT_CONTAINER_NAME": "penpot",
            # NEXTCLOUD
            "KOS_NEXTCLOUD_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_NEXTCLOUD",
            "KOS_NEXTCLOUD_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_NEXTCLOUD",
            "KOS_NEXTCLOUD_CONTAINER_NAME": "nextcloud",
            # ADMIN PANEL
            "KOS_ADMIN_PANEL_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_ADMIN_PANEL",
            "KOS_ADMIN_PANEL_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_ADMIN_PANEL",
            "KOS_ADMIN_PANEL_CONTAINER_NAME": "admin_panel",
            # REGISTRY
            "KOS_REGISTRY_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_REGISTRY",
            "KOS_REGISTRY_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_REGISTRY",
            "KOS_REGISTRY_CONTAINER_NAME": "registry",
            # PROMETHEUS
            "KOS_PROMETHEUS_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_PROMETHEUS",
            "KOS_PROMETHEUS_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_PROMETHEUS",
            "KOS_PROMETHEUS_CONTAINER_NAME": "prometheus",
            # GRAFANA
            "KOS_GRAFANA_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_GRAFANA",
            "KOS_GRAFANA_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_GRAFANA",
            "KOS_GRAFANA_CONTAINER_NAME": "grafana",
            # CADVISOR
            "KOS_CADVISOR_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_CADVISOR",
            "KOS_CADVISOR_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_CADVISOR",
            "KOS_CADVISOR_CONTAINER_NAME": "cadvisor",
            # ELASTICSEARCH
            "KOS_ELASTICSEARCH_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_ELASTICSEARCH",
            "KOS_ELASTICSEARCH_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_ELASTICSEARCH",
            "KOS_ELASTICSEARCH_CONTAINER_NAME": "elasticsearch",
            # SUPABASE
            "KOS_SUPABASE_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_SUPABASE",
            "KOS_SUPABASE_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_SUPABASE",
            "KOS_SUPABASE_CONTAINER_NAME": "supabase",
            # VSCODIUM
            "KOS_VSCODIUM_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_VSCODIUM",
            "KOS_VSCODIUM_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_VSCODIUM",
            "KOS_VSCODIUM_CONTAINER_NAME": "vscodium",
            # CODE SERVER
            "KOS_CODE_SERVER_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_CODE_SERVER",
            "KOS_CODE_SERVER_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_CODE_SERVER",
            "KOS_CODE_SERVER_CONTAINER_NAME": "code-server",
            # LANGFUSE
            "KOS_LANGFUSE_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_LANGFUSE",
            "KOS_LANGFUSE_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_LANGFUSE",
            "KOS_LANGFUSE_CONTAINER_NAME": "langfuse",
            # PROMPT MANAGER
            "KOS_PROMPT_MANAGER_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_PROMPT_MANAGER",
            "KOS_PROMPT_MANAGER_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_PROMPT_MANAGER",
            "KOS_PROMPT_MANAGER_CONTAINER_NAME": "prompt_manager",
            # ARTIFACT MANAGER
            "KOS_ARTIFACT_MANAGER_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_ARTIFACT_MANAGER",
            "KOS_ARTIFACT_MANAGER_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_ARTIFACT_MANAGER",
            "KOS_ARTIFACT_MANAGER_CONTAINER_NAME": "artifact_manager",
            # VAULT
            "KOS_VAULT_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_VAULT",
            "KOS_VAULT_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_VAULT",
            "KOS_VAULT_CONTAINER_NAME": "vault",
            # NEO4J
            "KOS_NEO4J_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_NEO4J",
            "KOS_NEO4J_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_NEO4J",
            "KOS_NEO4J_CONTAINER_NAME": "neo4j",
            # NEO4J HTTP
            "KOS_NEO4J_HTTP_EXTERNAL_PORT": "KOS_PORT_CONFIGURATION_NEO4J_HTTP",
            "KOS_NEO4J_HTTP_INTERNAL_PORT": "KOS_PORT_CONFIGURATION_NEO4J_HTTP",
        }
        # Add mapped variables to env_vars
        for target_var, source_var in mapping.items():
            if source_var in env_vars:
                env_vars[target_var] = env_vars[source_var]
            elif source_var.lower() == source_var:  # If it's a literal (e.g., 'api')
                env_vars[target_var] = source_var
        
        return env_vars
    
    def save_environment_file(self, env_vars: Dict[str, str], output_path: str = ".env"):
        """Save environment variables to file"""
        with open(output_path, 'w') as f:
            f.write(f"# KOS v1 Environment Variables\n")
            f.write(f"# Generated from centralized configuration\n\n")
            
            for key, value in sorted(env_vars.items()):
                f.write(f"{key}={value}\n")
        
        print(f"Environment file generated: {output_path}")
    
    def run(self):
        """Main execution method"""
        print("KOS v1 Generic Environment Generator (with service-centric mapping)")
        print("=" * 40)
        
        # Generate environment variables
        print("Generating environment variables from configuration...")
        env_vars = self.generate_environment_variables()
        
        # Save environment file
        self.save_environment_file(env_vars, ".env")
        
        print(f"\nGenerated {len(env_vars)} environment variables")
        print("File created: .env")
        
        return env_vars


def main():
    generator = KOSEnvironmentGenerator()
    generator.run()


if __name__ == "__main__":
    main() 