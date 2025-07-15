---
title: "Managing Services User Guide"
description: "User guide for configuring and managing AI service connections in Kai-CD"
type: "user-guide"
status: "current"
priority: "high"
last_updated: "2025-01-27"
related_docs: [
  "00_Getting_Started.md",
  "04_User_Interface_Guide.md",
  "../04_current/services/01_Service_Architecture.md"
]
agent_notes: "User-facing service management guide - focus on clear step-by-step instructions for service configuration"
---

# Managing Services User Guide

## Agent Context
**For AI Agents**: This guide provides user-facing instructions for managing AI service connections in Kai-CD. Use this when helping users configure services, troubleshoot connections, or understand service management workflows.

**Implementation Notes**: Covers adding new services, testing connections, authentication setup, and service management operations. All procedures described here reflect current UI implementation.
**Quality Requirements**: Keep instructions synchronized with actual UI elements and service configuration process. Test all steps to ensure accuracy.
**Integration Points**: Links to getting started guide, UI documentation, and technical service architecture for advanced users.

---

The Service Management view is where you configure the connections to your local or remote AI services. To access it, open the Main Tab and click the "plug" icon in the navigation rail.

*(Screenshot of the Service Management view to be added here)*

## Adding a New Service

1.  Click the "**+ Add New Service**" button. This will open the Service Form.
2.  **Select Service Type:** Choose the type of service you want to add from the "Service Definition" dropdown (e.g., "Ollama", "OpenAI-Compatible").
3.  **Name:** Give your service a custom name that will appear in the UI (e.g., "My Local Llama3").
4.  **Base URL:** Enter the base URL for the service's API. For local services, this is often `http://localhost:11434`. The form will show you examples of what the final API endpoint URLs will look like as you type.
5.  **Authentication:** If the service requires authentication, the necessary fields will appear.
    -   For a `Bearer Token` or `API Key`, paste your key into the text field.
6.  **Save:** Click the "Save" button.

The new service will now appear in your list.

## Testing a Service

After adding a service, it's a good idea to test the connection.

-   The **Status Indicator** dot next to the service name shows its health.
    -   **Gray:** The status is unknown (it hasn't been checked yet).
    -   **Green:** The health check was successful, and the service is reachable.
    -   **Red:** The health check failed. The service is likely unreachable or misconfigured.
-   Click the "**Test**" button to manually trigger a health check. If the check fails, you will see a detailed error message.

## Editing or Deleting a Service

-   To **edit** an existing service, click the "Edit" (pencil) button. This will open the same Service Form with the existing details filled in.
