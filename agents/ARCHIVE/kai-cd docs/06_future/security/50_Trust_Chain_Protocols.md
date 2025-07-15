---
title: "Trust Chain Protocols & Agent Validation"
description: "Protocols for establishing trust, verifying identities, and ensuring secure agent interaction in the kAI/kOS ecosystem"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["agent-trust-protocols.md", "agent-attestation-and-verification.md"]
implementation_status: "planned"
---

# Trust Chain Protocols & Agent Validation

This document outlines the protocols, schemas, and systems used to establish trust, verify identities, and ensure secure agent interaction in the `kAI` / `kOS` ecosystem.

## Agent Context
**For AI Agents:** All communication must be signed and include a valid trust chain. Use the agent.id format exactly, maintain PKI compliance, and implement Chain-of-Trust protocol for all messages. Trust scores affect your system permissions and capabilities.

## Purpose & Philosophy

Trust in a modular, distributed AI ecosystem must be:

- **Verifiable**: Proven cryptographically or via protocol
- **Transparent**: Chain-of-trust auditable at any point
- **Flexible**: Adaptable to different authorities and sandboxing
- **Private**: Compliant with user-controlled disclosure

## Core Concepts

### 1. Agent Identity (`agent.id`)

Every agent must possess a globally unique ID that includes:

```typescript
k:aid:domain:role:hash
// Example: k:aid:education:tutor:f83da92b
```

- `domain`: Domain specialization (e.g., finance, legal)
- `role`: Agent class (e.g., user.personal, system.core)
- `hash`: Public key hash or fingerprint

### 2. Public Key Infrastructure (PKI)

Each agent owns a public/private keypair.

- All communication must be signed.
- Fingerprints are used in `agent.id`.
- Trusted agents are stored in a local `trustring.json` file.

```json
{
  "k:aid:health:coach:abc123": {
    "public_key": "...",
    "trust_level": "linked.trust",
    "source": "qr-import",
    "verified": true
  }
}
```

### 3. Chain-of-Trust Protocol (CoT)

Each agent message must include a signed trust chain:

```json
{
  "agent": "k:aid:edu:planner:xy123",
  "signature": "...",
  "parent": "k:aid:orchestrator:kernel:ab99",
  "chain": [
    {
      "agent": "k:aid:orchestrator:kernel:ab99",
      "signature": "..."
    },
    {
      "agent": "k:aid:system:core:root000",
      "signature": "..."
    }
  ]
}
```

## TypeScript Implementation

```typescript
interface AgentIdentity {
  id: string; // Format: k:aid:domain:role:hash
  publicKey: string;
  trustLevel: 'root.kernel' | 'trusted.user' | 'linked.trust' | 'restricted' | 'external';
  source: string;
  verified: boolean;
  created_at: string;
  expires_at?: string;
}

interface TrustChain {
  agent: string;
  signature: string;
  parent?: string;
  chain: TrustLink[];
  timestamp: string;
}

interface TrustLink {
  agent: string;
  signature: string;
  timestamp: string;
}

class TrustValidator {
  private trustedAgents: Map<string, AgentIdentity> = new Map();
  
  async verifyTrustChain(chain: TrustChain): Promise<boolean> {
    // Verify each link in the chain
    for (const link of chain.chain) {
      if (!await this.verifySignature(link)) {
        return false;
      }
    }
    
    // Verify root trust
    return this.verifyRootTrust(chain.chain[chain.chain.length - 1]);
  }
  
  async calculateTrustScore(agentId: string): Promise<number> {
    const identity = this.trustedAgents.get(agentId);
    if (!identity) return 0;
    
    let score = 0;
    
    // Base score from trust level
    const trustLevelScores = {
      'root.kernel': 100,
      'trusted.user': 80,
      'linked.trust': 60,
      'restricted': 30,
      'external': 10
    };
    
    score += trustLevelScores[identity.trustLevel] || 0;
    
    // Verification bonus
    if (identity.verified) score += 10;
    
    // Age penalty (newer agents have lower initial trust)
    const age = Date.now() - new Date(identity.created_at).getTime();
    const ageDays = age / (1000 * 60 * 60 * 24);
    if (ageDays > 30) score += 5; // Established agent bonus
    
    return Math.min(100, score);
  }
  
  private async verifySignature(link: TrustLink): Promise<boolean> {
    // Implement cryptographic signature verification
    return true; // Placeholder
  }
  
  private verifyRootTrust(rootLink: TrustLink): boolean {
    // Verify against known root certificates
    return this.trustedAgents.has(rootLink.agent);
  }
}
```

## Trust Authority Modes

| Mode         | Description                                 |
| ------------ | ------------------------------------------- |
| `local`      | Only local trustring.json is consulted      |
| `federated`  | Uses signed trust maps from linked agents   |
| `blockchain` | Anchored chain on decentralized ledger      |
| `hybrid`     | Local + federated fallback w/ quorum voting |

## Attestation Protocol

Agents may request a **Trust Attestation Token (TAT)**:

```json
{
  "attestation": {
    "agent_id": "k:aid:devops:deploy:x87",
    "generated": "2025-06-20T13:00:00Z",
    "valid_until": "2025-06-21T13:00:00Z",
    "signed_by": "k:aid:root:kernel:0001",
    "signature": "..."
  }
}
```

## CLI Tooling

- `kai-trust verify <agent_id>`
- `kai-trust export <agent_id>`
- `kai-trust audit --all`
- `kai-trust import trustmap.json`

## Cross-References

- [Agent Trust Protocols](agent-trust-protocols.md) - Detailed trust mechanisms
- [Agent Attestation](agent-attestation-and-verification.md) - Verification processes 