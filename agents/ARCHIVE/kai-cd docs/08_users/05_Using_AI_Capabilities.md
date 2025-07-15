---
title: "Using AI Capabilities"
description: "Technical specification for using ai capabilities"
type: "user-guide"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing using ai capabilities"
---

# 4. Using AI Capabilities

## Agent Context
**For AI Agents**: Complete user guide for AI capabilities within Kai-CD covering LLM chat, image generation, and service interactions. Use this when understanding user workflows, implementing user-facing AI features, planning capability interfaces, or building user experience patterns. Essential reference for all user-facing AI capability development work.

**Implementation Notes**: Contains user interaction patterns, capability usage workflows, service selection guidance, and practical examples of AI feature usage. Includes user-focused documentation for all implemented AI capabilities.
**Quality Requirements**: Keep user workflows and capability descriptions synchronized with actual implementation. Maintain accuracy of user interface patterns and AI capability usage instructions.
**Integration Points**: Foundation for user-facing AI features, links to capability UI components, service architecture, and user interface design for comprehensive AI capability coverage.

The main purpose of Kai-CD is to provide a consistent interface for interacting with different AI models. These interfaces are called "Capability Views."

## Selecting a Service

To begin, open the Main Tab. The default view is the Capability View. Use the dropdown menu in the header to select which of your configured services you want to use.

*(Screenshot of the service selector dropdown in the header to be added here)*

Once you select a service, the appropriate UI will appear.

## The Chat Interface

If you select a service with the `llm_chat` capability (like Ollama), you will see the chat interface.

*(Screenshot of the LlmChatView to be added here)*

-   **Model Selector:** Below the main header, a second dropdown allows you to choose the specific model you want to chat with (e.g., `gemma2`, `llama3`). This list is fetched directly from the service.
-   **Chat History:** The main panel displays the conversation history. User messages are on the right, and assistant messages are on the left.
-   **Input Form:** At the bottom is the text area where you can type your prompts.
    -   Press `Enter` to send your message.
    -   Press `Shift + Enter` to add a new line.
-   **Parameters Panel:** On the right side of the screen, there is a panel for adjusting the API parameters for the selected model.
    -   Changes you make here (e.g., to the `Temperature`) will be applied to your next chat request.
    -   These settings are saved locally, so you don't have to set them again every time you switch models.

## The Image Generation Interface

If you select a service with the `image_generation` capability (like a Stable Diffusion service), you will see the image generation interface.

*(Screenshot of the ImageGenerationView to be added here)*

-   **Prompt Input:** A large text area at the top allows you to enter your image prompt.
-   **Parameters Panel:** Similar to the chat view, a panel on the right allows you to adjust parameters like `Steps`, `CFG Scale`, `Seed`, etc.
-   **Generate Button:** Click the "Generate" button to send the request to the service.
