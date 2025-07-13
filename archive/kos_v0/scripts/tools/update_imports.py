#!/usr/bin/env python3
"""
Script to update import references after directory reorganization.
This script updates all Python import statements to reflect the new directory structure.
"""

import os
import re
import glob
from pathlib import Path

# Mapping of old imports to new imports
IMPORT_MAPPINGS = {
    # Core components
    'from src.core.agents.': 'from src.core.agents.',
    'from src.core.nodes.': 'from src.core.nodes.',
    'from src.core.services.': 'from src.core.services.',
    'from src.core.gateway.': 'from src.core.gateway.',
    'from src.core.orchestrator.': 'from src.core.orchestrator.',
    'from src.core.klf.': 'from src.core.klf.',
    'from src.core.mcp.': 'from src.core.mcp.',
    
    # Applications
    'from src.apps.frontend.': 'from src.apps.frontend.',
    'from src.apps.extension.': 'from src.apps.extension.',
    
    # Runtime
    'from src.runtime.': 'from src.runtime.',
    
    # Shared
    'from src.shared.': 'from src.shared.',
}

def update_file_imports(file_path):
    """Update import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update import statements
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Update relative imports that might be affected
        # This is a more complex pattern that might need manual review
        content = re.sub(
            r'from \.\.(\w+)',
            r'from src.core.\1',
            content
        )
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated imports in {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def update_config_references(file_path):
    """Update configuration file references."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update config file paths
        config_updates = {
            'config/system.yaml': 'config/system/system.yaml',
            'config/features.yaml': 'config/features/features.yaml',
            'config/vault.schema.json': 'config/system/vault.schema.json',
        }
        
        for old_path, new_path in config_updates.items():
            content = content.replace(old_path, new_path)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated config references in {file_path}")
            return True
        else:
            print(f"⏭️  No config changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating config references in {file_path}: {e}")
        return False

def main():
    """Main function to update all files."""
    print("🔄 Starting import reference updates...")
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"📁 Found {len(python_files)} Python files to process")
    
    # Update imports
    updated_count = 0
    for file_path in python_files:
        if update_file_imports(file_path):
            updated_count += 1
    
    # Find all configuration files (YAML, JSON, etc.)
    config_files = []
    for ext in ['*.yaml', '*.yml', '*.json', '*.toml', '*.ini']:
        config_files.extend(glob.glob(f'**/{ext}', recursive=True))
    
    print(f"📁 Found {len(config_files)} configuration files to process")
    
    # Update config references
    config_updated_count = 0
    for file_path in config_files:
        if update_config_references(file_path):
            config_updated_count += 1
    
    print(f"\n✅ Import updates completed!")
    print(f"   - Updated {updated_count} Python files")
    print(f"   - Updated {config_updated_count} configuration files")
    print(f"   - Total files processed: {len(python_files) + len(config_files)}")

if __name__ == '__main__':
    main() 