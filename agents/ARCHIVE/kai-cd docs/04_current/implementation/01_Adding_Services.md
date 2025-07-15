---
title: "Adding New Services - Implementation Guide"
description: "Step-by-step guide for integrating new AI services into Kai-CD"
category: "implementation"
subcategory: "services"
context: "current_implementation"
implementation_status: "complete"
decision_scope: "medium"
complexity: "medium"
last_updated: "2025-01-20"
code_references: 
  - "src/connectors/definitions/"
  - "src/connectors/definitions/all.ts"
  - "src/utils/apiClient.ts"
  - "src/store/serviceStore.ts"
related_documents:
  - "../services/01_service-architecture.md"
  - "../architecture/02_state-management.md"
  - "../../bridge/05_service-migration.md"
agent_notes: "Follow this exact pattern for ALL new service integrations - ensures consistency and kOS compatibility"
---

# Adding New Services - Implementation Guide

## Agent Context
**For AI Agents**: Complete step-by-step implementation guide for integrating new AI services into Kai-CD. Use this when adding any new external service, implementing service connectors, or ensuring consistent integration patterns. Essential reference for all service integration work.

**Implementation Notes**: Contains proven ServiceDefinition pattern used for 20+ successful service integrations. Includes working TypeScript examples, request/response transformations, and integration checklist.
**Quality Requirements**: Keep integration patterns and examples synchronized with actual service connector implementation. Maintain accuracy of ServiceDefinition schema and transformation patterns.
**Integration Points**: Foundation for service integration, links to service architecture, API client system, and state management for consistent service addition workflow.

---

## Quick Summary

This guide walks through integrating a new AI service into Kai-CD using the ServiceDefinition pattern. The process ensures consistency, maintainability, and compatibility with the kOS evolution roadmap.

## Step-by-Step Integration Process

### Step 1: Create Service Definition File

```typescript
// src/connectors/definitions/new-service.ts
import { ServiceDefinition } from '@/types';

export const newServiceDefinition: ServiceDefinition = {
  id: 'new-service',
  name: 'New Service',
  description: 'Description of what this service provides',
  capabilities: ['llm_chat'], // What the service can do
  
  baseUrl: 'https://api.newservice.com',
  defaultModel: 'default-model-name',
  
  authentication: {
    type: 'bearer',
    headerName: 'Authorization',
    valuePrefix: 'Bearer '
  },
  
  endpoints: {
    chat: {
      path: '/v1/chat/completions',
      method: 'POST',
      requestSchema: {
        model: 'string',
        messages: 'array',
        temperature: 'number'
      }
    },
    models: {
      path: '/v1/models',
      method: 'GET'
    }
  },
  
  transformRequest: (endpoint: string, data: any) => {
    if (endpoint === 'chat') {
      return {
        model: data.model || 'default-model',
        messages: data.messages,
        temperature: data.temperature ?? 0.7
      };
    }
    return data;
  },
  
  transformResponse: (endpoint: string, response: any) => {
    if (endpoint === 'chat') {
      return {
        content: response.choices?.[0]?.message?.content || ''
      };
    }
    return response;
  }
};
```

### Step 2: Register Service Definition

```typescript
// src/connectors/definitions/all.ts
import { newServiceDefinition } from './new-service';

export const allServiceDefinitions = [
  // ... existing services
  newServiceDefinition,
];
```

### Step 3: Test Integration

```typescript
// Test the integration
const response = await apiClient.request({
  serviceId: 'new-service',
  endpoint: 'chat',
  data: {
    messages: [{ role: 'user', content: 'Hello' }]
  }
});
```

## For AI Agents

### Key Implementation Points

1. **Always follow ServiceDefinition pattern** - Don't create custom clients
2. **Use standard capability names** - Ensures UI compatibility
3. **Implement proper error handling** - Use established patterns
4. **Add comprehensive tests** - Verify integration works
5. **Document thoroughly** - Include examples and configuration

### Integration Checklist

```typescript
// Implementation checklist
- [ ] ServiceDefinition created
- [ ] Added to all.ts registry  
- [ ] Request/response transformation implemented
- [ ] Error handling configured
- [ ] Tests written and passing
- [ ] Documentation completed
```

---

