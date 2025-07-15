---
title: "Agent Development Rules & Workflow"
description: "Mandatory rules and workflow for AI agents - ensures stability, prevents regressions, and maintains code quality"
type: "rules"
status: "current"
priority: "critical"
last_updated: "2025-01-27"
version: "2.1.0"
related_docs: [
  "00_Index.md",
  "02_Agent_System_Prompt.md", 
  "15_Documentation_Protocol.md",
  "17_Recursive_Verification_System.md",
  "21_Quick_Start_Guide.md"
]
agent_notes: "MANDATORY compliance required - these rules are non-negotiable for all agents. Updated to reference correct documentation system."
---

# Agent Development Rules & Workflow

This document contains the mandatory rules and workflow for any AI agent working on this project. Non-compliance is not an option. This workflow is designed to ensure stability, prevent regressions, and create a high-quality, maintainable codebase.

## Agent Context
**For AI Agents**: These rules are MANDATORY and non-negotiable. Every agent must follow this workflow exactly. The two-edit rule and mid-progress reviews are critical for preventing errors. Always reference the Documentation System Master for current standards.

**Implementation Notes**: Use the test-driven debugging workflow when fixes fail. Create execution plans in `documentation/agents/` directory. Never commit code without explicit user permission.
**Quality Requirements**: 100% compliance with all workflow steps. No shortcuts allowed.
**Integration Points**: Links to System Prompt additions and Documentation Standards. Must coordinate with other agents through execution plans.

## The Core Principle: Proactive Verification

The primary goal is not just to produce a successful build, but to holistically improve the project. The agent must not wait for the user to find errors. The agent must proactively find and fix errors as it works.

## The Mandatory Workflow

1.  **Understand the Request:** Before writing any code, fully understand the user's request. Review all relevant existing documentation, especially the `00_DOCUMENTATION_SYSTEM_MASTER.md` standards document.

2.  **Formulate a Plan:** Create a clear, step-by-step plan to implement the solution.

3.  **Create and Maintain an Execution Plan:**
    -   For any given task, create a detailed `Execution_Plan.md` in the `documentation/agents/` directory.
    -   This document is your **single source of truth**. Do not improvise or deviate from it.
    -   As you complete each step, you **must** update the plan with a comprehensive log of your actions. This includes:
        -   Timestamps for major actions.
        -   Specific filenames, functions, and line numbers you analyzed or modified.
        -   Detailed findings from your analysis.
        -   Any errors encountered and the exact steps taken to fix them.
        -   The log must be detailed enough for another agent to replicate your work and achieve the same outcome.
    -   This living document is your primary work log.

4.  **The "Two-Edit" Rule (Iterative Review):**
    -   After making one or two significant edits (e.g., refactoring a component, modifying a state store), you **must stop**.
    -   You will then perform a **Mid-Progress Review**. This is not optional.
    -   **Mid-Progress Review Steps:**
        1.  **Read Entire Files:** Read the complete source code of the files you have just edited. Do not rely on your memory or a partial view.
        2.  **Trace the Logic:** Mentally (or by writing it down in your thought process) trace the logic flow. Consider edge cases. Ask yourself: "How could this break? What dependencies have I affected?"
        3.  **Check for Common Errors:** Explicitly look for missing imports, incorrect module paths, type mismatches, and other common integration errors.
        4.  **Fix and Document:** If you find a problem, fix it immediately. Document the finding and the fix in your agent log.
        5.  **Re-read Core Docs:** After fixing any self-identified issues, re-read this document and other core architecture docs to ensure your plan is still aligned with the project's requirements.

5.  **Final Verification:**
    -   Once you believe your entire plan is implemented, perform a final, full verification.
    -   **Run the Build:** Execute `npm run build` and check for any compilation or type errors.
    -   **Fix Holistically:** If there are build errors, do not fix them one-by-one. Analyze the root cause and apply a holistic fix. If you are stuck, say so. Do not guess.

6.  **Handling Tool Failures:**
    -   If a tool (e.g., `edit_file`) repeatedly fails to apply a change correctly after 2-3 attempts, do not continue trying.
    -   **Fallback to Temp File Swap:** Use this procedure to forcefully overwrite the target file:
        1.  Read the full content of the target file.
        2.  Make your intended changes to the content in memory.
        3.  Create a temporary file (e.g., `target_file.tmp.ts`) and write the complete, corrected content into it.
        4.  Use `run_terminal_cmd` to rename/move the temporary file to replace the original file (e.g., `mv target_file.tmp.ts target_file.ts`).
    -   This fallback avoids wasting time on inexplicable tool errors.

7.  **Recursive Verification:**
    -   **MANDATORY**: Use the Recursive Verification System for all work
    -   Run verification cycles until 100% compliance achieved
    -   Document each verification cycle with errors found and fixes applied
    -   Never proceed with known errors or incomplete verification

8.  **Documentation Update:**
    -   Update any and all relevant documentation after your code changes are complete and verified.

9.  **Commits and Version Control:**
    -   **Do not commit code unless explicitly asked to do so by the user.** The user manages the version history.

10. **User Verification is Final:**
    -   **Do not mark any task, fix, or plan as "complete" or "done" until the user explicitly confirms it is working as they expect.** Your own verification (e.g., a successful build) is not sufficient. The user is the final arbiter of success.

## The Debugging Workflow: Evidence-Based and Test-Driven

When a user reports that a fix has failed or a regression has occurred, the standard workflow is insufficient. You must immediately switch to this more rigorous debugging workflow.

1.  **Stop and Analyze:** Do not attempt another fix immediately. Acknowledge the failure and begin a holistic analysis of the problem.
2.  **Form a Testable Hypothesis:** Based on the failure, form a specific, testable hypothesis about the root cause.
3.  **Create an Inline Test:**
    *   If a formal testing framework is not available, create a temporary, inline test within the application (e.g., in a `main.tsx` or popup entry point).
    *   This test's purpose is to provide **objective, undeniable proof** of the bug. It must fail in a way that clearly demonstrates the problem.
    *   The test should use `console.log` and `console.assert` to check the actual output of functions against the expected output.
4.  **Implement the Fix:** With the failing test in place, implement the code changes to fix the bug.
5.  **Verify with the Test:** Re-run the test. It must now pass. This is your primary verification, not just a successful build.
6.  **Clean Up and Proceed:** Once the test passes and the build is successful, remove the temporary test code and present your evidence-based fix to the user. 