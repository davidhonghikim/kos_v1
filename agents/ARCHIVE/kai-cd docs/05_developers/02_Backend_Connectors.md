---
title: "Backend Connectors"
description: "Technical specification for backend connectors"
type: "developer-guide"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing backend connectors"
---

# 5. Backend Connectors

The backend connector system is the most powerful and innovative part of the Kai-CD architecture. It's what makes the application extensible and future-proof. The entire system is built around the concept of the **"Rich Service Definition."**

A Rich Service Definition is a single TypeScript object that contains all the information the application needs to:
1.  Render a dynamic UI for the service.
2.  Construct and send valid API requests to the service.
3.  Handle authentication and errors for the service.

All service definitions are located in `src/connectors/definitions/`.

## The Anatomy of a Service Definition

A `ServiceDefinition` object is composed of several key parts, defined in `src/types/index.ts`. Let's use a simplified version of `ollama.ts` as an example.

```typescript
// Simplified from src/connectors/definitions/ollama.ts
export const ollamaDefinition: ServiceDefinition = {
  id: 'ollama',
  name: 'Ollama',
  // ...
  capabilities: [llmChatCapability],
  // ...
};

const llmChatCapability: LlmChatCapability = {
  name: 'llm_chat',
  endpoints: [
    {
      id: 'getModels',
      path: '/api/tags',
      // ...
    },
    {
      id: 'chat',
      path: '/api/chat',
      // ...
    },
  ],
  parameters: [
    {
      id: 'model',
      type: 'select',
      optionsEndpoint: 'getModels', // <-- Dynamic Options!
      // ...
    },
    {
      id: 'temperature',
      type: 'number',
      defaultValue: 0.8,
      // ...
    },
    // ... more parameters
  ],
};
```

### Key Properties:

-   **`id`**: A unique machine-readable identifier (e.g., `'ollama'`).
-   **`name`**: A human-readable name for display in the UI.
-   **`capabilities`**: An array of `Capability` objects. A capability defines a specific function the service can perform (e.g., `llm_chat`, `image_generation`).
    -   **`endpoints`**: An array of `Endpoint` objects within a capability. Each endpoint defines a single API call, including its `id`, HTTP `method`, and `path`.
    -   **`parameters`**: An array of `ParameterDefinition` objects. This is the **schema** for the UI. It defines every user-configurable parameter, its `type` (for rendering the correct input), its `defaultValue`, and an optional `optionsEndpoint` to dynamically populate a `'select'` input.

## Data Flow Diagram

This diagram shows how a single service definition file is the central source of truth for both the UI and the API client.

```mermaid
graph TD
    subgraph "Design Time"
        ServiceDefinition[Service Definition<br/>(e.g., ollama.ts)]
    end

    subgraph "UI Rendering"
        direction TB
        CapabilityUI[CapabilityUI.tsx]
        ParameterControl[ParameterControl.tsx]
        ModelSelector[ModelSelector.tsx]
    end

    subgraph "API Communication"
        direction TB
        LlmChatView[LlmChatView.tsx]
        ApiClient[apiClient.ts]
        OllamaAPI[Ollama API Server]
    end

    ServiceDefinition -- "Provides Parameter Schema" --> CapabilityUI
    CapabilityUI -- "Renders" --> ParameterControl
    
    ServiceDefinition -- "Provides `optionsEndpoint` ID" --> ModelSelector
    ModelSelector -- "Triggers API Call" --> ApiClient

    LlmChatView -- "Triggers API Call with parameters" --> ApiClient
    ServiceDefinition -- "Provides Endpoint Path & Method" --> ApiClient

    ApiClient -- "Constructs & Sends Request" --> OllamaAPI
```

## The Universal `apiClient.ts`

The `apiClient` is a singleton class that handles all outgoing `fetch` requests. It is designed to be completely generic.

When a component needs to make an API call (e.g., `LlmChatView` submitting a prompt), it calls a method on the `apiClient` like `apiClient.chat(service, parameters)`.

The `apiClient` then performs the following steps:
1.  Takes the `service` object.
2.  Finds the correct `Capability` (e.g., `llm_chat`) within the service's definition.
3.  Finds the correct `Endpoint` (e.g., `chat`) within the capability.
4.  Uses the `path` from the endpoint definition to construct the final URL (e.g., `http://localhost:11434/api/chat`).
5.  Uses the `method` from the endpoint definition.
6.  Transforms the `parameters` from the UI into the correct request body format, as specified by the endpoint's `body` schema.
7.  Adds any required authentication headers based on the service's `auth` definition.
8.  Executes the request, handling streaming responses and errors centrally.

