# KOS v1 Cleanup and Reorganization Plan

## Current Problem
- Multiple duplicate directories from previous reorganization attempts
- Old structure mixed with new structure
- Backup directories taking up space
- No clear migration path

## Current Duplicates Identified

### Source Code Duplicates:
- `kos_v1/src/` (new structure) 
- `kos_v1/agents/` (old structure)
- `kos_v1/kitchen/` (old structure) 
- `kos_v1/klf/` (old structure)
- `kos_v1/services/` (old structure)
- `kos_v1/gateway/` (old structure)
- `kos_v1/orchestrator/` (old structure)

### Configuration Duplicates:
- `kos_v1/config/env/` (new)
- `kos_v1/config/environments/` (old)

### Backup Directories:
- `kos_v1/src/backup/`
- `kos_v1/backups/`

## Cleanup Strategy

### Phase 1: Assessment and Backup (SAFE)
1. Create a single comprehensive backup of current state
2. Document what's in each directory
3. Identify which files are actually needed

### Phase 2: Consolidation (CAREFUL)
1. Move unique files from old directories to new structure
2. Merge configuration files
3. Remove empty directories

### Phase 3: Verification (THOROUGH)
1. Test that all functionality still works
2. Update any import paths
3. Verify no data loss

## Immediate Action Plan

### Step 1: Create Single Backup
```bash
# Create timestamped backup of entire project
tar -czf kos_v1_backup_$(date +%Y%m%d_%H%M%S).tar.gz kos_v1/
```

### Step 2: Document Current State
- List all files in each directory
- Identify which are unique vs duplicates
- Map old paths to new paths

### Step 3: Consolidate Configuration
- Merge `config/environments/` into `config/env/`
- Keep only the centralized configuration system

### Step 4: Consolidate Source Code
- Move unique files from old directories to new `src/` structure
- Preserve any unique functionality
- Remove empty directories

## Questions for User
1. Should I proceed with this cleanup plan?
2. Do you want me to create the comprehensive backup first?
3. Are there any specific files/directories you want to preserve from the old structure?
4. Should I document the current state before making any changes?

## Recommendation
**STOP creating new directories** and instead:
1. Assess what we have
2. Create proper backup
3. Consolidate systematically
4. Test thoroughly

This approach prevents further duplication and ensures no data loss. 