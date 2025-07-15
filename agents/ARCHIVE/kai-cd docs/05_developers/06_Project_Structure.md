---
title: "Project Structure"
description: "Technical specification for project structure"
type: "developer-guide"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing project structure"
---

# 2. Project Structure

## Agent Context
**For AI Agents**: Complete project structure documentation covering directory organization, file conventions, and architectural organization patterns. Use this when understanding project layout, navigating codebase structure, planning file organization, or implementing architectural patterns. Essential foundation for all project structure work.

**Implementation Notes**: Contains project organization patterns, directory structure guidelines, file naming conventions, and architectural organization principles. Includes detailed project layout and organization strategies.
**Quality Requirements**: Keep project structure documentation and organization patterns synchronized with actual codebase layout. Maintain accuracy of directory structure and file organization principles.
**Integration Points**: Foundation for codebase navigation, links to architectural patterns, development guidelines, and project organization for comprehensive structure understanding.

This document provides a map of the Kai-CD repository, explaining the purpose of each key file and directory.

```
kai-cd/
├── public/
│   ├── icons/
│   └── manifest.json
├── src/
│   ├── background/
│   ├── components/
│   │   └── capabilities/
│   ├── config/
│   ├── connectors/
│   │   └── definitions/
│   ├── hooks/
│   ├── popup/
│   ├── sidepanel/
│   ├── store/
│   ├── styles/
│   ├── tab/
│   ├── types/
│   └── utils/
├── vite.config.ts
├── package.json
└── tsconfig.json
```

---

### Root Directory

-   **`vite.config.ts`**: The configuration file for Vite, the build tool. It defines the multiple entry points (`popup`, `sidepanel`, `tab`, `background`) for the Chrome Extension and handles the build process.
-   **`package.json`**: Defines the project's dependencies, scripts (`dev`, `build`), and metadata.
-   **`tsconfig.json`**: The base TypeScript configuration for the project.
-   **`tailwind.config.js`**: Configuration for the Tailwind CSS utility-first framework.
-   **`postcss.config.js`**: Configuration for PostCSS, which processes the CSS.
-   **`eslint.config.js`**: Configuration for ESLint, the code linter.

### `public/`

This directory contains static assets that are copied directly to the final `dist` directory without being processed by Vite.

-   **`manifest.json`**: The core configuration file for the Chrome Extension. It defines permissions, background scripts, UI entry points, and other essential metadata.
-   **`icons/`**: Contains the `.png` icons for the extension used in the browser toolbar, extensions page, etc.

### `src/`

This is the main application source code directory.

-   **`main.tsx`**: The primary entry point for the main tab view (`tab.html`).
-   **`index.css`**: Global CSS styles and Tailwind CSS imports.

#### `src/background/`

-   **`main.ts`**: The extension's service worker. This script runs in the background and manages communication between different parts of the extension, primarily handling the logic to open the main tab from the popup.

#### `src/components/`

The central library of shared React components.

-   **`CapabilityUI.tsx`**: The dynamic "router" component that renders the correct UI for a given service based on its capabilities.
-   **`ServiceManagement.tsx`**: The main view for adding, editing, and removing services.
-   **`capabilities/`**: Contains the high-level components for each specific AI task.
    -   **`LlmChatView.tsx`**: The complete UI for the chat capability.
    -   **`ImageGenerationView.tsx`**: The UI for the image generation capability.
    -   **`registry.tsx`**: The mapping from a capability name (e.g., `'llm_chat'`) to the component that renders it.

#### `src/config/`

Contains application-wide, static configuration data.

-   **`system.env.ts`**: The default configuration for the application.
-   **`user.env.example.ts`**: An example file for users to create their own `user.env.ts` to override system defaults.
-   **`env.ts`**: Merges the system and user configurations into a single exported `config` object.
-   **`errorCodes.ts`**: A registry of user-friendly error messages mapped to internal error codes.

#### `src/connectors/`

The core of the service-oriented architecture.

-   **`definitions/`**: Contains the "Rich Service Definitions". Each file in this directory (e.g., `ollama.ts`, `a1111.ts`) defines a single service, its API endpoints, and its parameters.
    -   **`all.ts`**: Imports all individual service definitions and exports them as a single array, which the application uses to populate the "Add Service" menu.

#### `src/hooks/`

Contains custom React hooks for shared logic.

-   **`useModelList.ts`**: A key hook that dynamically fetches the list of available models for a service from its API.

#### `src/popup/` & `src/sidepanel/` & `src/tab/`

Each of these directories contains the entry point (`main.tsx`) and root component (`Popup.tsx`, `Sidepanel.tsx`, `Tab.tsx`) for one of the three UI surfaces of the extension.

#### `src/store/`

Contains the Zustand stores for global state management.

-   **`serviceStore.ts`**: Manages the list of all configured services. Persisted to `chrome.storage.local`.
-   **`viewStateStore.ts`**: Manages the current UI state (e.g., active service/model). Not persisted.
-   **`settingsStore.ts`**: Manages user settings (e.g., theme). Persisted.
-   **`logStore.ts`**: Manages the in-app console logs. Not persisted.
-   **`chromeStorage.ts`**: The custom storage adapter for the `persist` middleware, allowing Zustand to save to the Chrome Extension storage API.

#### `src/types/`

-   **`index.ts`**: Contains the core TypeScript type definitions used throughout the application, such as `Service`, `ServiceDefinition`, `ParameterDefinition`, and `Capability`.

#### `src/utils/`

Contains shared utility functions and classes.

-   **`apiClient.ts`**: The centralized class for making all API requests to external services.
-   **`logger.ts`**: The application-wide logging system that overrides the global console and pushes logs to the `logStore`.
