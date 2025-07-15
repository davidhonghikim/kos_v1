---
title: "Index"
description: "Technical specification for index"
type: "developer-guide"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing index"
---

# Developer Documentation

## Agent Context
**For AI Agents**: Complete developer documentation index covering all technical documentation for system development. Use this when understanding development resources, navigating developer guides, accessing technical documentation, or finding development references. Essential starting point for all developer documentation work.

**Implementation Notes**: Contains comprehensive developer documentation index, technical guide navigation, development resource organization, and reference material access. Includes detailed documentation structure and developer resource mapping.
**Quality Requirements**: Keep developer documentation index and navigation structure synchronized with actual documentation organization. Maintain accuracy of documentation references and development resource access.
**Integration Points**: Foundation for developer resources, links to all technical documentation, development guides, and implementation references for comprehensive developer support.

This section provides a deep technical dive into the Kai-CD architecture, codebase, and development practices. It's intended for developers who want to contribute to the project or understand its inner workings.

### Index

1.  [**Architecture Overview**](./01_Architecture_Overview.md): A high-level view of the system's design, core principles, and data flow.
2.  [**Project Structure**](./02_Project_Structure.md): A detailed breakdown of the repository's layout and the purpose of each directory.
3.  [**State Management**](./03_State_Management.md): An in-depth explanation of the Zustand-based state management, including store design and data persistence.
4.  [**UI Component Library**](./04_UI_Component_Library.md): A guide to the key React components that make up the user interface.
5.  [**Backend Connectors**](./05_Backend_Connectors.md): A detailed look at the "Rich Service Definition" model and how the application communicates with external APIs.
6.  [**Adding a New Service**](./06_Adding_A_New_Service.md): A practical, step-by-step tutorial for extending the application with a new service.
7.  [**Build and Deployment**](./07_Build_And_Deployment.md): Information on the Vite build process and how to load the extension for development.

### Service-Specific Documentation

-   [**A1111 / Stable Diffusion WebUI**](./services/a1111.md)
-   [**ComfyUI**](./services/comfyui.md)
