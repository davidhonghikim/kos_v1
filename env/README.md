# kOS v1 Centralized Environment, Configuration, and Docker Generation System

---
**CRITICAL ARCHITECTURE: DO NOT DEVIATE**
This system's stability depends on a strict separation of configuration files. Failure to follow these rules *will* break the automated installers and generators.

- **`ports.env`**: **ONLY** for network settings. This includes port assignments, container names, network configs (`KOS_CONTAINER_NETWORK`), admin credentials, and health check/restart policies. **NO enable flags or image tags here.**

- **`settings.env`**: **ONLY** for system-wide flags and secrets. This includes all `KOS_*_ENABLE` flags and secret keys (`JWT_SECRET`, etc.). **NO ports or container names here.**

- **`local.env`**: **ONLY** for service definitions. This includes image tags (`KOS_*_IMAGE`), compose profiles (`..._PROFILE`), dependencies (`..._DEPENDS_ON`), and any special commands.

- **`api-keys.env` & `cloud.env`**: For external service keys. These are loaded with the lowest priority.

**Never duplicate or move variables between these files.** The `env_loader.py` script depends on this structure to assemble the final, unified `.env` file.
---

## 1. Centralized Environment System Overview

All configuration for kOS v1 is managed through modular `.env` files, strictly separated by purpose. This ensures a single source of truth for all settings. All downstream systems (including Docker and backend services) consume **only** the generated unified `.env` file.

## 2. File Structure and Roles
Use code with caution.
Markdown
env/
├── api-keys.env # (Optional) External API keys (e.g., OPENAI_API_KEY)
├── cloud.env # (Optional) Cloud deployment overrides
├── local.env # Service definitions (images, profiles, dependencies)
├── ports.env # Network/Orchestration (ports, names, health checks)
├── settings.env # Feature Flags & Secrets (ENABLE flags, JWT_SECRET)
└── README.md # This file

## Canonical Port Mapping (Validated)
**This table is the single source of truth for port assignments and must be kept in sync with `ports.env`.**

| Service/Variable         | External Port | Internal Port | Notes/Standard         |
|-------------------------|--------------|--------------|-----------------------|
| Gitea SSH               | 22           | 2222         | SSH                   |
| NGINX                   | 80           | 80           | HTTP standard         |
| NGINX SSL               | 443          | 443          | HTTPS standard        |
| Frontend                | 3000         | 3000         | Web UI                |
| OpenWebUI               | 3001         | 8080         | Web UI                |
| Gitea                   | 3002         | 3000         | Web UI                |
| Supabase Studio         | 3003         | 3000         | Web UI                |
| Browseruse              | 3004         | 3000         | Web UI                |
| Context7                | 3005         | 3000         | Web UI                |
| Codium                  | 3006         | 8080         | Web UI                |
| Grafana                 | 3007         | 3000         | Monitoring UI         |
| Prompt Manager          | 3008         | 8000         | Manager UI            |
| Artifact Manager        | 3009         | 8000         | Manager UI            |
| Registry                | 5000         | 5000         | Registry std          |
| Postgres                | 5432         | 5432         | DB standard           |
| PGAdmin                 | 5433         | 80           | DB admin UI           |
| N8N                     | 5678         | 5678         | Workflow std          |
| Redis                   | 6379         | 6379         | DB standard           |
| Redis Commander         | 6380         | 8081         | DB admin UI           |
| Neo4j HTTP              | 7474         | 7474         | DB standard           |
| Neo4j                   | 7687         | 7687         | DB standard           |
| Automatic1111           | 7860         | 7860         | AI/ML std             |
| API                     | 8000         | 8000         | API standard          |
| cAdvisor                | 8081         | 8081         | Monitoring            |
| Weaviate                | 8082         | 8080         | DB standard           |
| Nextcloud               | 8083         | 8083         | Web UI                |
| Huggingface             | 8084         | 8082         | AI/ML std             |
| ComfyUI                 | 8188         | 8188         | AI/ML std             |
| InvokeAI                | 8189         | 8189         | AI/ML std             |
| MinIO                   | 9000         | 9000         | Storage std           |
| MinIO Console           | 9001         | 9001         | Storage UI            |
| Penpot                  | 9002         | 9002         | Web UI                |
| Admin Panel             | 9003         | 9003         | Web UI                |
| Prometheus              | 9090         | 9090         | Monitoring            |
| Elasticsearch           | 9200         | 9200         | DB standard           |
| Elasticsearch Cluster   | 9300         | 9300         | DB standard           |
| Ollama                  | 11434        | 11434        | AI/ML std             |
| MongoDB                 | 27017        | 27017        | DB standard           |
| Mongo Express           | 27018        | 8081         | DB admin UI           |
| Supabase                | 54321        | 5432         | DB                    |

## 3. Workflow

1.  Edit the appropriate `env/*.env` files according to the rules.
2.  Run the install script (`kos-install.sh` or `.bat`). This will:
    *   Audit the environment for correctness (`env_audit.py`).
    *   Load and merge all `.env` files into a single, unified `.env` file (`env_loader.py`).
    *   Generate all `docker-compose-*.yml` files from the unified `.env` file (`generate_docker_compose.py`).
3.  Deploy the stack: `docker-compose -f docker/docker-compose.full.yml up -d`.
4.  Review logs in the `logs/` directory to troubleshoot.
5.  **After archiving any handoff or critical file, immediately verify the archive exists at the expected path and (optionally) matches the source before proceeding. Log or document the result. If verification fails, halt and resolve before continuing.**

--- END OF FILE README.md ---

## 4. Script Locations and Troubleshooting

**All installer and build scripts are now located in `scripts/installer/`.**
- The only entry points are `kos-install.sh` (Linux/macOS) and `kos-install.bat` (Windows) in the project root.
- If you encounter a 'file not found' or 'script missing' error, verify that all scripts (`gpu_autodetect.py`, `env_loader.py`, `env_audit.py`, `generate_docker_compose.py`) exist in `scripts/installer/`.
- Never run scripts directly from the old `installer/` directory.

**Troubleshooting Common Install Errors:**
- If the installer fails at any step, check the logs printed to the terminal and in the `logs/` directory.
- Ensure your Python environment is set up correctly and all dependencies are installed.
- If Docker Compose fails to start, verify that the unified `.env` file was generated and all required images are available.
- Never edit generated Docker Compose files by hand. All changes must be made in the env files and applied via the loader pipeline.

# Hardware Detection and GPU Environment Variables

All hardware-specific variables (e.g., KOS_GPU_ENABLE, KOS_GPU_COUNT, KOS_GPU_NAMES, CUDA_VISIBLE_DEVICES, etc.) are set by the GPU autodetector and written to env/gpu.env. Do not hardcode any hardware values in ports.env. The env_loader.py script merges gpu.env into the unified .env and config, which are then used by all downstream services and compose files.

Workflow:
1. Run the GPU autodetector (installer/gpu_autodetect.py or .bat) to generate env/gpu.env.
2. Run env_loader.py to merge ports.env and gpu.env into the unified .env and config.
3. All downstream services use the unified .env for hardware configuration.