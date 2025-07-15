---
title: "Adding A New Service"
description: "Technical specification for adding a new service"
type: "developer-guide"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing adding a new service"
---

# 6. Adding a New Service

## Agent Context
**For AI Agents**: Complete guide for adding new services to the Kai-CD platform covering step-by-step integration procedures and service implementation patterns. Use this when implementing new service integrations, understanding service addition workflows, planning service extensions, or building service connectors. Essential reference for all new service development work.

**Implementation Notes**: Contains step-by-step service integration procedures, service implementation patterns, integration workflows, and development best practices. Includes detailed service addition methodology and implementation frameworks.
**Quality Requirements**: Keep service addition procedures and implementation patterns synchronized with actual integration process. Maintain accuracy of service integration workflows and development best practices.
**Integration Points**: Foundation for service expansion, links to service architecture, integration frameworks, and development guidelines for comprehensive service addition coverage.

This guide provides a step-by-step tutorial for adding support for a new service to Kai-CD. The process mostly involves creating a single new file: a service definition.

Let's imagine we want to add support for a fictional new LLM service called "MegaChat."

### Step 1: Create the Definition File

Create a new file in `src/connectors/definitions/megachat.ts`. This file will contain the entire definition for our new service.

### Step 2: Define the Basic Service Info

Start with the basic properties for the `ServiceDefinition` object.

```typescript
// src/connectors/definitions/megachat.ts

import { ServiceDefinition, LlmChatCapability } from '@/types';

export const megaChatDefinition: ServiceDefinition = {
  id: 'megachat',
  name: 'MegaChat',
  description: 'A fictional new LLM service.',
  logo: 'data:image/svg+xml;...', // (Optional) Add an SVG logo
  baseUrl: 'http://localhost:1234/v1', // The default base URL
  auth: {
    type: 'bearer_token',
    token: '', // The user will provide this
  },
  capabilities: [], // We will add this next
};
```

-   **`id`**: Must be a unique, lowercase string.
-   **`baseUrl`**: The default URL for the service. The user can override this.
-   **`auth`**: Define the authentication method. `'bearer_token'` will cause the UI to render a text input for a token. Other options include `'none'` and `'api_key'`.

### Step 3: Define the Capability

Our service is for chat, so we need to create an `LlmChatCapability`. This object will define the endpoints and parameters for the chat functionality.

```typescript
// src/connectors/definitions/megachat.ts

const llmChatCapability: LlmChatCapability = {
  name: 'llm_chat',
  endpoints: [
    // Define endpoints here
  ],
  parameters: [
    // Define parameters here
  ],
};

// ... update the main definition:
export const megaChatDefinition: ServiceDefinition = {
  // ...
  capabilities: [llmChatCapability],
};
```

### Step 4: Define the Endpoints

Now, we fill in the `endpoints` array inside the capability. Let's assume MegaChat has two endpoints we care about: one to get a list of models and one to handle the chat stream.

```typescript
// Inside llmChatCapability
endpoints: [
  {
    id: 'getModels',
    path: '/models',
    method: 'GET',
    parser: {
      type: 'json',
      path: 'data', // Where the array of models is in the response
      id: 'id',     // The property to use as the model ID
      name: 'id',   // The property to use for the display name
    },
  },
  {
    id: 'chat',
    path: '/chat/completions',
    method: 'POST',
    body: { // How to structure the request body
      model: '{{model}}', // Use template variables for parameters
      messages: '{{messages}}',
      temperature: '{{temperature}}',
      stream: true,
    },
    isStreaming: true,
  },
],
```

-   The `parser` object in `getModels` tells the application how to parse the JSON response to get a list of models.
-   The `body` object in `chat` is a template. The `apiClient` will replace variables like `{{model}}` with the actual values from the UI.

### Step 5: Define the Parameters

Finally, define the `parameters` array. This schema will be used to automatically generate the UI form.

```typescript
// Inside llmChatCapability
parameters: [
  {
    id: 'model',
    type: 'select',
    label: 'Model',
    defaultValue: 'megachat-pro',
    optionsEndpoint: 'getModels', // Tells the UI to call the 'getModels' endpoint to populate this dropdown
  },
  {
    id: 'temperature',
    type: 'number',
    label: 'Temperature',
    defaultValue: 0.7,
    min: 0,
    max: 2,
    step: 0.1,
  },
  {
    id: 'system_prompt',
    type: 'string',
    label: 'System Prompt',
    defaultValue: 'You are a helpful assistant.',
    isSystem: true, // Marks this as the system prompt
  },
],
```

-   The `'select'` parameter with `optionsEndpoint` is the key to creating a dynamic model selector.

### Step 6: Add to the Global List

The final step is to make the application aware of your new definition. Open `src/connectors/definitions/all.ts` and add your new definition to the imported list and the exported array.

```typescript
// src/connectors/definitions/all.ts

import { megaChatDefinition } from './megachat'; // 1. Import it
// ... other imports

export const allServiceDefinitions = [
  // ... other definitions
  megaChatDefinition, // 2. Add it to the array
];
```

### Step 7: Test

