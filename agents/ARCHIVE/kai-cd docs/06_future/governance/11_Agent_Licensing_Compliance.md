---
title: "Agent Licensing & Compliance"
description: "Licensing models, legal identifiers, usage boundaries, and compliance verification protocols for agents"
type: "architecture"
status: "future"
priority: "medium"
last_updated: "2025-01-27"
related_docs: ["governance-framework.md", "governance-protocols-and-interoperability.md"]
implementation_status: "planned"
---

# Agent Licensing & Compliance

This document defines the licensing models, legal identifiers, usage boundaries, and compliance verification protocols for agents operating within the `kAI` and `kOS` environments.

## Agent Context
**For AI Agents:** Include license.meta.yaml file in your root directory, implement runtime license validation, and generate usage.audit.json reports. Follow SPDX standards for OSS licenses and validate license tokens for commercial use.

## Licensing Models

### A. Open Source Licenses (OSL)

- **MIT** — Permissive, allows reuse with attribution
- **Apache 2.0** — Patent-safe and permissive
- **GPLv3** — Copyleft, share-alike requirement
- **MPL 2.0** — File-level copyleft for business compatibility

### B. Commercial Licenses (CL)

- **Single-Use License** — One-time fee, per-user installation
- **Subscription License** — Time-based with renewals
- **Enterprise License** — Multi-agent deployment, unlimited users

### C. Hybrid License (HL)

- OSS core with paid advanced modules
- Example: Core scheduler is GPL, but analytics engine is CL

## License Metadata File

Every agent must contain a `license.meta.yaml` file:

```yaml
id: kind-agent-chatcoach
license: MIT
version: 1.2.0
maintainer: Stone Monk AI Labs
copyright: 2025 Stone Monk AI
compliance:
  logging: required
  telemetry: optional
  audit_ready: true
  expiration: none
```

## TypeScript Implementation

```typescript
interface LicenseMetadata {
  id: string;
  license: string;
  version: string;
  maintainer: string;
  copyright: string;
  compliance: {
    logging: 'required' | 'optional' | 'disabled';
    telemetry: 'required' | 'optional' | 'disabled';
    audit_ready: boolean;
    expiration: string | 'none';
  };
}

interface UsageAudit {
  agent_id: string;
  start_time: string;
  end_time: string;
  host_id_hash: string;
  feature_usage: Record<string, number>;
  interaction_count: number;
}

class LicenseValidator {
  private metadata: LicenseMetadata;
  
  constructor(metadata: LicenseMetadata) {
    this.metadata = metadata;
  }
  
  async validateLicense(): Promise<boolean> {
    // Check expiration
    if (this.metadata.compliance.expiration !== 'none') {
      const expiry = new Date(this.metadata.compliance.expiration);
      if (expiry < new Date()) {
        return false;
      }
    }
    
    // Validate license format
    return this.isValidLicense(this.metadata.license);
  }
  
  async generateAuditReport(): Promise<UsageAudit> {
    return {
      agent_id: this.metadata.id,
      start_time: new Date().toISOString(),
      end_time: new Date().toISOString(),
      host_id_hash: this.generateHostHash(),
      feature_usage: {},
      interaction_count: 0
    };
  }
  
  private isValidLicense(license: string): boolean {
    const validLicenses = ['MIT', 'Apache-2.0', 'GPL-3.0', 'MPL-2.0'];
    return validLicenses.includes(license);
  }
  
  private generateHostHash(): string {
    // Generate anonymized host identifier
    return 'host_' + Math.random().toString(36).substr(2, 9);
  }
}
```

## Usage Boundaries & Quotas

| License Type | Max Instances | Time Limit | Features Gated          |
| ------------ | ------------- | ---------- | ----------------------- |
| OSL (MIT)    | ∞             | ∞          | None                    |
| CL (Single)  | 1             | ∞          | Agent chaining          |
| CL (Sub)     | 5             | 1 year     | UI analytics, telemetry |
| HL           | Variable      | Variable   | Paid modules            |

## Compliance Audit System

### A. Self-Report Mechanism
Agents generate `usage.audit.json` with anonymized usage data.

### B. Audit Collection Endpoint
`POST /compliance/report` with optional opt-out capability.

## Cross-References

- [Governance Framework](governance-framework.md) - Overall governance structure
- [Governance Protocols](governance-protocols-and-interoperability.md) - Protocol governance 