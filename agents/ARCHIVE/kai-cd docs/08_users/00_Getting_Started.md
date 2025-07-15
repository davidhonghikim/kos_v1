---
title: "Getting Started Guide"
description: "Step-by-step installation and setup guide for new Kai-CD users"
type: "user-guide"
status: "current"
priority: "critical"
last_updated: "2025-01-27"
related_docs: [
  "04_User_Interface_Guide.md",
  "02_Managing_Services.md",
  "../04_current/deployment/02_Installation_And_Setup.md"
]
agent_notes: "Primary onboarding guide for new users - ensure instructions are current and accurate"
---

# Getting Started Guide

## Agent Context
**For AI Agents**: This is the primary onboarding guide for new Kai-CD users. Use this document when helping users with installation, initial setup, and first-time configuration. Ensure all instructions remain current with the latest build process.

**Implementation Notes**: Covers manual installation as unpacked extension since not yet published to Chrome Web Store. Includes build process, browser setup, and initial configuration steps.
**Quality Requirements**: Keep installation instructions synchronized with actual build process. Test all steps regularly to ensure accuracy.
**Integration Points**: Links to user interface guide for next steps and technical deployment documentation for advanced users.

---

Welcome to Kai-CD! This guide will walk you through installing the extension in your browser.

Since Kai-CD is under active development, it is not yet available on the Chrome Web Store. You will need to load it manually as an "unpacked extension."

## Prerequisites

-   A Chromium-based browser (e.g., Google Chrome, Brave, Microsoft Edge).
-   The Kai-CD project files downloaded or cloned to your computer.

## Installation Steps

1.  **Build the Extension:**
    Before you can load the extension, you need to build it from the source code. Open a terminal in the project's root directory and run the following commands:
    ```bash
    # Install all the necessary dependencies
    npm install

    # Build the extension for production
    npm run build
    ```
    This will create a `dist` directory in your project folder. This directory is the extension.

2.  **Open the Extensions Page:**
    In your browser, navigate to the extensions management page. You can usually find this at the URL `chrome://extensions`.

3.  **Enable Developer Mode:**
    Look for a switch labeled "Developer mode" in the top-right corner of the page and turn it **on**. This will reveal a new set of buttons.

    ![Enable Developer Mode](https://developer-chrome-com.imgix.net/image/BrQidfK9jaQyIHwdw91aVpkPiGD2/Z2_H5sUe1V5qdKMaV1hA.png)
    *(Image from developer.chrome.com)*

4.  **Load the `dist` Directory:**
    -   Click the "Load unpacked" button.
    -   A file browser will open. Navigate to where you saved the Kai-CD project.
    -   Select the **`dist`** directory and click "Select" or "Open".

5.  **Installation Complete!**
    The Kai-CD extension should now appear in your list of installed extensions.

    ![Extension Loaded](https://storage.googleapis.com/web-dev-uploads/image/BrQidfK9jaQyIHwdw91aVpkPiGD2/4jOHGg15n932iG2mH5jJ.png)
    *(Image from developer.chrome.com)*

## Next Steps

Now that the extension is installed, you can pin it to your toolbar for easy access. Click the "puzzle piece" icon in your browser's toolbar and then click the pin icon next to "Kai-CD".

