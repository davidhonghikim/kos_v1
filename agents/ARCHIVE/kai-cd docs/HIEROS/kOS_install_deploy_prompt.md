# kOS Project Reconstruction Blueprint (No Code)

**Instructions for AI Agent:**

You are an AI agent tasked with generating the complete file structure and stub files for a software project named "kOS". You DO NOT have access to existing code files. You must generate the project from scratch based on these specifications.

**General Directives:**

*   **File Structure:** Create the directories and files exactly as specified.
*   **Content Type:** Ensure that each file is of the correct type (e.g., Python, YAML, JSON, Markdown, HTML, CSS).
*   **Headers/Comments:** Include the header/comment blocks at the beginning of each file, as specified.
*   **Dependencies:**  Pay close attention to the dependencies listed in `requirements.txt`. The Python files must correctly import these dependencies. Assume the user will handle .js packages through a package manager.
*   **Configuration:** Understand that configuration is handled via environment variables and is loaded by default into `/configs/defaults.yaml`.
*   **Modularity:** Design the modules to be modular and loosely coupled. Use clear interfaces between components.
*   **Security:** Keep security considerations in mind, especially regarding input validation and secrets management.
*   **Functionality is Necessary** Every single file should have the ability to run some code for basic test. For example, ui\_server.py needs to set up basic routes and be runnable to start a server.

**Project Structure and File Specifications:**

**(Note: Details on code/logic are high-level. You are expected to generate appropriate stub code.)**

## File: agents/agent_example.py

*   **Type:** Python
*   **Header:**

    ```python
    # ==============================================
    # kOS Agent - Example Agent
    # ==============================================
    # A simple example agent for kOS
    # ==============================================
    ```
*   **Dependencies:** `asyncio`, `logging`, `config_loader`, `agent_memory`
*   **Description:** An example agent with:
    *   `__init__`: Initializes the agent, loads configuration using `config_loader`, and connects to memory using `agent_memory`.
    *   `run`: An asynchronous method that runs the agent's main loop. It should log a message every 5 seconds.  Include exception handling for `asyncio.CancelledError` and other exceptions.

## File: configs/defaults.yaml

*   **Type:** YAML
*   **Header:**

    ```yaml
    # ==============================================
    # kOS Default Configuration
    # ==============================================
    # Defines default system profiles
    # ==============================================
    ```
*   **Content:** A YAML file with a `presets` section:
    *   `basic`: Defines agents (`agent_example`) and services (`postgres`, `ollama`) for a basic profile.
    *   `dev`: Defines agents (`agent_dev`, `agent_example`) and services (`postgres`, `ollama`, `a1111`) for a development profile.

## File: docker/Dockerfile

*   **Type:** Dockerfile
*   **Header:**

    ```dockerfile
    # ==============================================
    # kOS Dockerfile
    # ==============================================
    # Defines the Docker image for kOS
    # ==============================================
    ```
*   **Instructions:**
    *   Use a Python 3.11 slim base image.
    *   Set the working directory to `/app`.
    *   Copy `requirements.txt` and install the dependencies using pip.
    *   Copy the entire project into the container.
    *   Set the command to run `ui_server.py`.

## File: docker/docker-compose.yml

*   **Type:** YAML
*   **Header:**

    ```yaml
    # ==============================================
    # kOS Docker Compose
    # ==============================================
    # Defines the services for the kOS stack
    # ==============================================
    ```
*   **Services:**
    *   `ui_server`:
        *   Build from the `docker/Dockerfile`.
        *   Map port `30436:30436`.
        *   Set environment variables (e.g., `SECRET_KEY`, `CORS_ORIGINS`, database credentials) using `${VARIABLE_NAME}` syntax.
        *   Mount the local directory to `/app` inside the container.

## File: docs/dev/00_build_guide.md

*   **Type:** Markdown
*   **Header:** `Build Guide`
*   **Content:** A basic guide with steps to:
    *   Clone the kOS repository.
    *   Build the Docker image using `docker-compose build`.
    *   Launch the kOS stack using `docker-compose up`.
    *   Explain how to modify the code, rebuild the image, and restart the stack during development.

## File: docs/user/01_installation_guide.md

*   **Type:** Markdown
*   **Header:** `Installation Guide`
*   **Content:** A user-friendly guide with steps to:
    *   Clone the kOS repository.
    *   Build and launch the kOS stack using `docker-compose`.
    *   Access the web UI at `http://localhost:30436`.
    *   Explain how to configure the system by modifying the `.env` file.

## File: web/package.json

*   **Type:** JSON
*   **Header:** `Web UI Config File`
*   **Description:** Defines the dependencies and scripts for the React-based web UI.
    *Key Packages*:
      *Install the axios, and all MUI packages.
      *Install packages needed for React.

## File: web/public/index.html

*   **Type:** HTML
*   **Header:** `Basic html config file`
*   **Description:** Basic HTML file with root id.

## File: web/src/App.js

*   **Type:** JavaScript (React)
*   **Header:** `App Definition File`
*   **Description:** Define the main App.js to have the functionality for login, set token, load Agents, etc.

## File: web/src/components/AgentList.js

*   **Type:** JavaScript (React)
*   **Header:** `Agent Listing Component File`
*   **Description:** Displays the available agents to the app from the API.

## File: web/src/components/ConfigDisplay.js

*   **Type:** JavaScript (React)
*   **Header:** `Config Display Component`
*   **Description:** Formats text to be able to set, read and use an editor.

## File: web/src/components/Docs.js

*   **Type:** JavaScript (React)
*   **Header:** `Docs Component File`
*    **Description** Displays the information about the docs and structure.

## File: web/src/components/InstallModal.js

*   **Type:** JavaScript (React)
*   **Header:** `Install Modal Component File`
*   **Description:** List available Agents to install.

## File: web/src/components/LoginForm.js

*   **Type:** JavaScript (React)
*   **Header:** `Login Form Component`
*  **Description** Implements the login prompt with text boxes to load into the website.

## File: web/src/index.css

*   **Type:** CSS
*   **Header:** `CSS File Setup Styling`
*   **Description:**  Basic stylesheet to make things pretty.

## File: web/src/index.js

*   **Type:** JavaScript (React)
*   **Header:** `Index Point Web Entry`
*   **Description:** React DOM file to inject the DOM.

## File: web/src/services/api.js

*   **Type:** JavaScript (React)
*   **Header:** `Web Integration Services File`
*   **Description:**  Used to define all API endpoints to hit.

## File: agent_loader.py

*   **Type:** Python
*   **Header:**

    ```python
    # ==============================================
    # kOS Agent Loader
    # ==============================================
    # Loads and validates agent modules based on the plugin manifest
    # ==============================================
    ```
*   **Dependencies:** `importlib`, `json`, `logging`, `os`, `pathlib`, `config_loader`
*   **Description:**
    *   `load_manifest()`: Loads the `plugin_manifest.json` file.
    *   `is_dependency_met()`: Checks if the dependencies for an agent are met.
    *   `load_agent()`: Dynamically imports and loads an agent module based on the `plugin_manifest.json`.  Includes input validation to prevent module injection.

## File: agent_memory.py

*   **Type:** Python
*   **Header:**

    ```python
    # ==============================================
    # kOS Agent Memory Interface
    # ==============================================
    # Connects agents to vector DBs and structured DBs for RAG2 workflows
    # Supports: ChromaDB, Weaviate, PostgreSQL
    # ==============================================
    ```
*   **Dependencies:** `os`, `chromadb`, `psycopg2`, `weaviate`, `logging`, `config_loader`
*   **Description:**
    *   `__init__`: Initializes the memory interface, loads configuration using `config_loader`, and connects to the specified database backend (`chroma`, `weaviate`, or `postgres`).
    *   `init_connection()`: Establishes a connection to the database backend.  Creates the `memory` table in PostgreSQL if it doesn't exist.
    *   `store()`: Stores text data in the database, organized by namespace.
    *   `query()`: Retrieves data from the database based on a query and namespace.

## File: init_agents.py

*   **Type:** Python
*   **Header:**

    ```python
    # ==============================================
    # kOS Agent Initializer
    # ==============================================
    # Loads default agents from config
    # Spawns subprocesses or threads for each agent module
    # ==============================================
    ```
*   **Dependencies:** `os`, `yaml`, `importlib`, `asyncio`, `logging`, `pathlib`, `config_loader`, `agent_loader`
*   **Description:**
    *   `launch_agent()`: Loads and launches a single agent module using `agent_loader`. Runs the agent's `run()` method as an asyncio task.
    *   `main()`: Loads the system configuration, iterates through the agents listed in the configuration, and launches each agent using `launch_agent()`.

## File: plugin_manifest.json

*   **Type:** JSON
*   **Header:** `JSON File Plugin Manifest`
*   **Content:** A JSON file with a `plugins` array. Each plugin object should have:
    *   `name`: The name of the agent.
    *   `description`: A brief description of the agent.
    *   `entry`: The path to the agent's Python module.
    *   `requires`: An array of service dependencies (e.g., `postgres`, `ollama`).
    *    `class`: The agent Class name.

## File: readme.txt

*   **Type:** Text
*   **Header:** `KOS READ ME File`
*   **Content:** A concise overview of the kOS project.

## File: requirements.txt

*   **Type:** Text
*   **Header:** `Python Req File Setup`
*   **Content:** A list of Python dependencies for the project:

    ```txt
    fastapi
    uvicorn
    python-dotenv
    PyYAML
    jsonschema
    passlib
    python-jose
    starlette
    slowapi
    authlib
    pydantic
    chromadb
    psycopg2
    weaviate-client
    ```

## File: ui_server.py

*   **Type:** Python
*   **Header:** `API Server For ALL`
*   **Dependencies:**
from fastapi import FastAPI, WebSocket, HTTPException, Depends, status, Header
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import json
import asyncio
import logging
from typing import Annotated, Optional
from pydantic import BaseModel, validator
from passlib.context import CryptContext
from jose import JWTError, jwt
from starlette.requests import Request
from slowapi import Limiter, \_rate\_limit\_exceeded\_handler
from slowapi.util import get\_remote\_address
from slowapi.middleware import SlowAPIMiddleware
import os \#To Load Env Var

*   **Description:**
    *   Sets up: Cors, Rate Limiter
    *   Contains the backend routes with login via OAuth2, token handling, and the agents: Start, Stop.
    *   Loads Agent Manager
    *   Has all API calls and the connection to a Websocket to communicate with agents.

## File: .env

*   **Type:** Text
*   **Header:** `ENV SETUP For Config`
*   **Content:** The Following are what you can set
# Environment Variables

\# UI Server
SECRET\_KEY="change\_this\_secret\_key"
CORS\_ORIGINS="http://localhost,http://localhost:8080"

\# PostgreSQL
POSTGRES\_USER="kos"
POSTGRES\_PASSWORD="secret"
POSTGRES\_DB="kosdb"
POSTGRES\_HOST="db"
POSTGRES\_PORT="5432"

\# Agent settings:
AGENT\_DIRECTORY="agents"

\#OAUTH setup
OAUTH\_CLIENT\_ID=""
OAUTH\_CLIENT\_SECRET=""