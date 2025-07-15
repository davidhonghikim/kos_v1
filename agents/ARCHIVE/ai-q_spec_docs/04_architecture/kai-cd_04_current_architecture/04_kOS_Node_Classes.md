---
title: "kOS Node Classes"
description: "Canonical definition of the specialized, interoperable server nodes that form the kOS ecosystem, outlining their roles and responsibilities."
type: "architecture_definition"
status: "current"
priority: "high"
last_updated: "{{CURRENT_TIMESTAMP}}"
related_docs: [
  "documentation/01_agents/02_planning/Execution_Plan_kOS_Bootstrap.md"
]
agent_notes: "This is the canonical source of truth for the roles of all 13 node classes. It was synthesized from the files in brainstorm/deploy/roles."
---

# 04: kOS Node Classes

**Version**: 1.0.0
**Status**: Current
**Contact**: System Architect

## 1. Overview

The `kOS` ecosystem is composed of specialized, interoperable server nodes, each with a distinct role inspired by archetypes of community and knowledge. This document provides the canonical definition for each node class, outlining their core essence and key responsibilities. This serves as the master guide for understanding the architecture's separation of concerns.

---

## 2. Core Infrastructure & Deployment

### 2.1. Griot: The Seed & Librarian
- **Essence**: Preserves, packages, and distributes the `ai-q` knowledge library, enabling new `kOS` nodes to be created and maintained.
- **Key Responsibilities**:
  - Building and distributing OS releases (ISO, images).
  - Providing an interactive installer.
  - Synchronizing updates and verifying package signatures.
  - Repairing broken or missing components.
  - Acting as a steward for the foundational HIEROS ethics.

### 2.2. Ronin: The Pathfinder & Interlinker
- **Essence**: Discovers new peers, bridges disconnected network clusters, and enables resource exchange without central authority.
- **Key Responsibilities**:
  - Network discovery across various mediums (LAN, BLE, LoRa).
  - Automated mesh network formation (e.g., Yggdrasil, cjdns).
  - Providing relay services and NAT traversal for isolated peers.
  - Enforcing ethical compliance of discovered peers.

---

## 3. Knowledge & Data Management

### 3.1. Tohunga: The Research & Lore Curator
- **Essence**: Acts as a research librarian, collecting raw external knowledge, transforming it into usable artifacts, and guaranteeing its provenance.
- **Key Responsibilities**:
  - Acquiring public datasets, models, and documentation.
  - Verifying licenses (SPDX) and tracking provenance.
  - Pre-processing data (e.g., generating embeddings).
  - Publishing curated knowledge via APIs.

### 3.2. Yachay: The Knowledge Warehouse
- **Essence**: Serves as a heavyweight storage and compute hub for large datasets and models.
- **Key Responsibilities**:
  - Hosting S3-compatible storage for datasets and model checkpoints.
  - Providing a versioned Model Registry API.
  - Orchestrating distributed training jobs (e.g., Kubeflow, Ray).
  - Scheduling and exposing GPU/CPU resources.

---

## 4. Governance & Ethics

### 4.1. Archon: The Federation Steward
- **Essence**: Acts as a chief magistrate, coordinating multi-node governance, resource quotas, and consensus.
- **Key Responsibilities**:
  - Maintaining the authoritative registry of nodes and their public keys.
  - Running a consensus engine (e.g., Tendermint) for governance votes.
  - Managing and enforcing resource quotas.
  - Publishing signed network policies.

### 4.2. Junzi: The Integrity & Compliance Steward
- **Essence**: Embodies impartial integrity, auditing operations, and verifying adherence to policies and Sacred Intentions.
- **Key Responsibilities**:
  - Hosting a policy engine (e.g., OPA) for access control.
  - Auditing system logs for compliance.
  - Vetoing actions that breach critical policies.
  - Overseeing cultural content for misrepresentation.

### 4.3. Sachem: The Consensus Mediator
- **Essence**: Facilitates community dialogue, mediates disputes, and helps build consensus in alignment with the Sacred Intentions.
- **Key Responsibilities**:
  - Hosting forums for debate and structured proposals.
  - Automating and recording community ceremonies.
  - Possessing the ability to override a `Junzi` veto with a supermajority vote.

---

## 5. Security & Health

### 5.1. Musa: The Sentinel & Cyber-Guardian
- **Essence**: Serves as a security sentinel, providing active defense, monitoring, and incident response.
- **Key Responsibilities**:
  - Running Intrusion Detection Systems (IDS).
  - Managing automated CVE patching and container image rebuilding.
  - Sandboxing untrusted workloads.
  - Providing forensic tools for incident response.

### 5.2. Hakim: The Healer & Diagnostician
- **Essence**: Acts as a wise physician, continuously monitoring system health, diagnosing anomalies, and recommending corrective actions.
- **Key Responsibilities**:
  - Aggregating and visualizing system metrics (e.g., Grafana).
  - Performing root-cause analysis on failures, often using ML models.
  - Generating and proposing remediation playbooks.
  - Publishing regular system wellness reports.

---

## 6. Content & Culture

### 6.1. Skald: The Creative Media Artisan
- **Essence**: Acts as a creative artisan, transforming curated knowledge into accessible articles, tutorials, visuals, and multimedia.
- **Key Responsibilities**:
  - Generating content using LLMs and other generative models.
  - Ensuring proper attribution and licensing of all generated media.
  - Hosting and serving media via CDN-like services.
  - Checking generated content for toxicity and bias.

### 6.2. Amauta: The Cultural Mentor & Educator
- **Essence**: Serves as a cultural mentor, curating learning materials and advising on respectful representation to maintain diversity.
- **Key Responsibilities**:
  - Hosting an educational "academy" portal.
  - Providing a review service to evaluate content for cultural respect.
  - Matching new nodes with mentors to guide their integration.

---

## 7. Strategy & Legacy

### 7.1. Oracle: The Insight & Predictive Analyst
- **Essence**: Interprets data to provide predictive analytics and strategic foresight for the network.
- **Key Responsibilities**:
  - Ingesting and warehousing telemetry data.
  - Running forecasting models (e.g., for resource usage, model drift).
  - Simulating "what-if" scenarios for network changes.
  - Providing recommendations with confidence intervals.

### 7.2. Mzee: The Elder Advisor & Legacy Archivist
- **Essence**: Serves as a wise advisor and archivist, preserving historical data to ensure long-term continuity and institutional memory.
- **Key Responsibilities**:
  - Creating and storing immutable historical snapshots of manifests and policies.
  - Maintaining long-term metrics archives (e.g., via Thanos).
  - Providing trend analysis to advise on sustainability.
  - Preserving narrative logs from `Skald` and `Griot` nodes. 