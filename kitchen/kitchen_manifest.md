Kitchen Engine File Manifest
This document provides a centralized index of all the core files for the Kitchen Orchestration System. Click on any link to view the corresponding file's code.

Core Engine (kitchen/core/)

kitchen/core/kitchen_engine.py - The main engine orchestrator.

kitchen/core/config.py - Handles loading kitchen_config.json.

kitchen/core/logging.py - Standardized logging setup.

kitchen/core/recipe_parser.py - Parses and validates recipe files.

kitchen/core/step_executor.py - Executes individual recipe steps.

Recipes (recipes/system/)

recipes/system/bootstrap_system.json - The master recipe for system initialization.

Pantry Ingredients (kitchen/pantry/operations/system/)

kitchen/pantry/operations/system/env_audit.py - Validates the host environment.

kitchen/pantry/operations/system/generate_env.py - Creates .env files from templates.

kitchen/pantry/operations/system/generate_docker_compose.py - Builds the docker-compose.yml file.

kitchen/pantry/operations/system/execute_docker_compose.py - Runs docker-compose commands.

kitchen/pantry/operations/system/post_install_diagnostic.py - Runs health checks on services.

Documentation

kitchen/README.md - The main documentation for the Kitchen system.