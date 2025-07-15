---
title: "State Management"
description: "Technical specification for state management"
type: "developer-guide"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing state management"
---

# 3. State Management

## Agent Context
**For AI Agents**: Complete state management documentation covering Zustand implementation, persistent storage, and state coordination patterns. Use this when implementing state management, understanding data flow, planning state architecture, or building state coordination systems. Essential foundation for all state management work.

**Implementation Notes**: Contains state management patterns, Zustand store implementations, persistence strategies, and state coordination mechanisms. Includes detailed state architecture and data flow patterns.
**Quality Requirements**: Keep state management patterns and data flow documentation synchronized with actual implementation. Maintain accuracy of state coordination and persistence mechanisms.
**Integration Points**: Foundation for data management, links to storage systems, component state, and persistence layers for comprehensive state management coverage.

Kai-CD uses [Zustand](https://github.com/pmndrs/zustand) for global state management. It provides a simple, unopinionated, and performant way to manage state across the entire application. The state is divided into several "stores," each with a specific domain of responsibility.

A key feature of the state management is its persistence layer, which uses a custom middleware to save and retrieve data from the `chrome.storage.local` API. This ensures that user-configured services and settings are preserved between browser sessions.

## State Management Diagram

This diagram shows the different stores, what they manage, and how they interact with the UI and the persistence layer.

```mermaid
graph TD
    subgraph "React UI Components"
        direction LR
        A[ServiceManagement.tsx]
        B[LlmChatView.tsx]
        C[SettingsView.tsx]
        D[Tab.tsx]
    end

    subgraph "Zustand Stores"
        direction TB
        ServiceStore[serviceStore.ts<br/>- Services[]<br/>- selectedServiceId<br/>- customUrls{}]
        ViewStateStore[viewStateStore.ts<br/>- activeServiceId<br/>- activeModel<br/>- chatParameters{}]
        SettingsStore[settingsStore.ts<br/>- theme<br/>- logLevel]
        LogStore[logStore.ts<br/>- logs[]]
    end

    subgraph "Persistence Layer"
        direction TB
        PersistMiddleware[Zustand Persist Middleware]
        ChromeStorage[chromeStorage.ts Adapter]
        BrowserStorage[chrome.storage.local]
    end

    A -- "Reads/Writes" --> ServiceStore
    B -- "Reads/Writes" --> ViewStateStore
    B -- "Reads/Writes" --> ServiceStore
    C -- "Reads/Writes" --> SettingsStore
    D -- "Reads" --> ServiceStore
    D -- "Reads" --> SettingsStore
    D -- "Reads" --> LogStore

    ServiceStore -- "Uses" --> PersistMiddleware
    SettingsStore -- "Uses" --> PersistMiddleware

    PersistMiddleware -- "Uses" --> ChromeStorage
    ChromeStorage -- "Writes/Reads" --> BrowserStorage
```

---

## Core Stores

### 1. `serviceStore.ts`

This is the most important and complex store in the application.

-   **Purpose:** Manages the array of all services the user has configured. This includes their full definition, credentials, chat/generation history, and current status.
-   **State:**
    -   `services: Service[]`: The master list of service objects.
    -   `selectedServiceId: string | null`: The ID of the service currently being edited in the `ServiceManagement` view.
    -   `customUrls: Record<string, string>`: A temporary holding area for the base URL a user is typing into the `ServiceForm`, used for dynamic URL generation.
-   **Persistence:** This store is **persisted**.
-   **Hydration & Race Conditions:**
    -   The rehydration of this store from `chrome.storage.local` is **asynchronous**. Historically, this was a major source of bugs, where the UI would try to read the service list before it was loaded.
    -   To solve this, the store contains a `_hasHydrated` flag. UI components that depend on the `services` array **must** check if `_hasHydrated` is true before attempting to render. The `useServiceStore.persist.onFinishHydration` method is used to set this flag once the data is loaded.
    -   The `merge` function in the `persist` middleware is custom and critical. It ensures that when state is loaded from storage, it is intelligently merged with the initial default state from the service definitions. This allows for default services to be updated in the code without overwriting a user's existing, configured services.

### 2. `viewStateStore.ts`

-   **Purpose:** Manages the "view" or "session" state. This is ephemeral data that describes what the user is currently doing.
-   **State:**
    -   `activeServiceId: string | null`: The ID of the service currently being used in `CapabilityUI`.
    -   `activeModel: string | null`: The name of the specific model selected (e.g., `'gemma2'`).
    -   `chatParameters: Record<string, any>`: An object holding the current values for the active service's parameters (e.g., `temperature`, `top_p`).
-   **Persistence:** This store is **not persisted**. Its state is derived and reset based on user actions within a session. When the user selects a new service, the `setActiveServiceId` action in this store is responsible for populating the `chatParameters` from the new service's definition.

### 3. `settingsStore.ts`

-   **Purpose:** Manages user-configurable settings that are not specific to any one service.
-   **State:**
    -   `theme: 'light' | 'dark' | 'system'`: The current UI theme.
    -   `logLevel: 'debug' | 'info' | 'warn' | 'error'`: The verbosity of the application logger.
-   **Persistence:** This store is **persisted**.

### 4. `logStore.ts`

-   **Purpose:** Acts as a centralized, in-memory buffer for all application logs.
-   **State:**
    -   `logs: LogEntry[]`: An array of all log objects generated by the application.
