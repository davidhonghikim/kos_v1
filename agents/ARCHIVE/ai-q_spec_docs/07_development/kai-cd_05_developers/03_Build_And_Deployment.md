---
title: "Build And Deployment"
description: "Technical specification for build and deployment"
type: "developer-guide"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing build and deployment"
---

# 7. Build and Deployment

## Agent Context
**For AI Agents**: Complete build and deployment documentation covering build processes, deployment strategies, and production workflows. Use this when implementing build systems, understanding deployment procedures, planning production releases, or configuring build pipelines. Essential foundation for all build and deployment work.

**Implementation Notes**: Contains build system configuration, deployment procedures, production workflow strategies, and release management processes. Includes detailed build pipeline and deployment automation patterns.
**Quality Requirements**: Keep build and deployment documentation synchronized with actual build processes and deployment procedures. Maintain accuracy of build configurations and deployment workflows.
**Integration Points**: Foundation for production deployment, links to development workflows, configuration management, and release strategies for comprehensive build and deployment coverage.

This document explains the build process for Kai-CD and how to load it for development and testing.

## Technology Stack

-   **Build Tool:** [Vite](https://vitejs.dev/)
-   **Framework:** [React](https://react.dev/)
-   **Language:** [TypeScript](https://www.typescriptlang.org/)
-   **Styling:** [Tailwind CSS](https://tailwindcss.com/)
-   **State Management:** [Zustand](https://github.com/pmndrs/zustand)

## Development Workflow

The recommended workflow is to use the Vite development server, which provides Hot Module Replacement (HMR) for rapid development.

1.  **Install Dependencies:**
    If you haven't already, install the required Node.js packages.
    ```bash
    npm install
    ```

2.  **Run the Development Server:**
    ```bash
    npm run dev
    ```
    This command does two things:
    -   It runs the Vite compiler in watch mode. When you save a change to a source file, Vite will instantly re-bundle the necessary parts of the extension.
    -   It generates the initial output in the `dist/` directory.

## Loading the Extension in Chrome

To test the extension, you must load the generated `dist/` directory into a Chromium-based browser.

1.  **Open the Extensions Page:**
    Navigate to `chrome://extensions` in your browser.

2.  **Enable Developer Mode:**
    In the top-right corner of the Extensions page, toggle the "Developer mode" switch to **On**.

3.  **Load the Unpacked Extension:**
    -   Click the "Load unpacked" button that appears on the top-left.
    -   In the file selection dialog, navigate to the root of the Kai-CD project folder.
    -   Select the `dist` directory and click "Select".

    ![Load Unpacked Extension](https://developer-chrome-com.imgix.net/image/BrQidfK9jaQyIHwdw91aVpkPiGD2/LgwsO231V41S9Glqg6sY.png)
    *(Image from developer.chrome.com)*

4.  **Pin the Extension (Optional):**
    Click the "puzzle piece" icon in the Chrome toolbar and then click the "pin" icon next to Kai-CD to make it visible for easy access to the popup.

## The `dist/` Directory

The `dist/` directory is the **build output**. It is the actual extension that the browser runs. You should **never** edit files in this directory manually, as they will be overwritten by the Vite compiler every time you make a change to the source files in `src/`.

