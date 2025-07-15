---
title: "Agent Attestation – Verification, Audit Trails, and Provenance in kAI"
description: "Comprehensive design for agent attestation protocols, cryptographic proofs, and audit trails establishing agent behavior verification and accountability"
type: "security"
status: "future"
priority: "high"
last_updated: "2024-12-28"
related_docs: [
  "documentation/future/agents/42_agent-lifecycle-management-orchestration.md",
  "documentation/future/security/06_agent-security-isolation-model.md",
  "documentation/future/protocols/41_kind-link-protocol-specification.md"
]
implementation_status: "planned"
---

# Agent Attestation – Verification, Audit Trails, and Provenance in kAI

## Agent Context
**For AI Agents**: This document defines the complete attestation system for verifying agent behavior and maintaining audit trails. When implementing agent actions, use the AttestationManager to log all significant operations. Every agent action that modifies state, communicates externally, or accesses sensitive resources must generate an AttestationRecord. Use the provided TypeScript interfaces as implementation contracts for cryptographic verification and audit logging.

## Purpose

Attestation in kAI ensures that all autonomous behavior by agents—whether modifying configs, interacting with users, or communicating via KLP—is:

- Cryptographically **verifiable**
- **Timestamped** and **auditable**
- **Traceable** to specific user intents or governing policies
- Usable for **security**, **governance**, **accountability**, and **reputation building**

## Architecture & Directory Structure

```typescript
src/
└── attestation/
    ├── AttestationManager.ts          // Core manager for logging, signing, verification
    ├── AttestationLog.ts              // Append-only log format with rotation
    ├── AttestationVerifier.ts         // Module for verifying external claims
    ├── structures/
    │   ├── AttestationRecord.ts       // Schema for single attestation entry
    │   └── AttestationProof.ts        // Cryptographic wrapper and signature
    ├── hooks/
    │   ├── AgentEventHooks.ts         // Hooks for events to auto-generate attestations
    │   └── LifecycleHooks.ts          // Agent lifecycle attestation hooks
    ├── storage/
    │   ├── LocalStorage.ts            // Local attestation storage
    │   ├── IPFSAnchor.ts              // IPFS content anchoring
    │   └── BlockchainAnchor.ts        // Blockchain attestation anchoring
    └── audit/
        ├── CLI_AuditViewer.ts         // Tool for listing/inspecting local agent attestations
        └── AuditReport.ts             // Comprehensive audit reporting
```

## Attestation Record Format

Each attestation is a structured, signed, immutable record:

```typescript
interface AttestationRecord {
  id: string;                    // UUID v4
  agentId: KindDID;              // Agent that performed the action
  timestamp: string;             // ISO 8601 timestamp
  context: AttestationContext;   // Action category and details
  payload: AttestationPayload;   // Action-specific data (redacted-sensitive)
  performedBy: KindDID;          // User or delegating entity
  verified?: boolean;            // Verification status
  metadata: AttestationMetadata; // Additional context
}

interface AttestationProof {
  record: AttestationRecord;
  signature: string;             // Ed25519 signature of SHA256(record)
  signatureAlgorithm: 'ed25519' | 'secp256k1';
  publicKey: string;             // Base64 encoded public key
  verificationMethod: string;    // DID verification method
}

type AttestationContext = 
  | 'config.save'               // Configuration changes
  | 'config.load'               // Configuration access
  | 'comms.outbound'            // Outbound communication
  | 'comms.inbound'             // Inbound message processing
  | 'klp.link'                  // KLP connection establishment
  | 'klp.capability_request'    // Capability discovery
  | 'artifact.access'           // File or resource access
  | 'artifact.create'           // Resource creation
  | 'artifact.modify'           // Resource modification
  | 'artifact.delete'           // Resource deletion
  | 'workflow.start'            // Workflow initiation
  | 'workflow.complete'         // Workflow completion
  | 'memory.read'               // Memory access
  | 'memory.write'              // Memory modification
  | 'security.auth'             // Authentication events
  | 'security.violation';       // Security policy violations

interface AttestationPayload {
  action: string;                // Specific action taken
  resource?: string;             // Resource identifier (if applicable)
  parameters?: Record<string, any>; // Action parameters (sanitized)
  result?: 'success' | 'failure' | 'partial';
  errorCode?: string;            // Error identifier (if failed)
  duration?: number;             // Action duration in milliseconds
}

interface AttestationMetadata {
  agentVersion: string;          // Agent version when action performed
  environment: 'development' | 'staging' | 'production';
  userAgent?: string;            // User agent context
  sessionId?: string;            // Session identifier
  correlationId?: string;        // Cross-service correlation
  parentAction?: string;         // Parent action ID (for workflows)
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}
```

> ⚠️ Signed attestations are stored locally and can optionally be anchored to external proof stores or IPFS.

## Event Hooks & Auto-logging

All major agent actions trigger an **Attestation Hook**:

```typescript
abstract class AttestationHook {
  constructor(protected attestationManager: AttestationManager) {}
  
  abstract shouldAttest(event: AgentEvent): boolean;
  abstract createRecord(event: AgentEvent): AttestationRecord;
  
  async onEvent(event: AgentEvent): Promise<void> {
    if (this.shouldAttest(event)) {
      const record = this.createRecord(event);
      await this.attestationManager.addRecord(record);
    }
  }
}

class ConfigurationHook extends AttestationHook {
  shouldAttest(event: AgentEvent): boolean {
    return event.type === 'config.save' || event.type === 'config.load';
  }
  
  createRecord(event: ConfigEvent): AttestationRecord {
    return {
      id: generateUUID(),
      agentId: event.agentId,
      timestamp: new Date().toISOString(),
      context: event.type as AttestationContext,
      payload: {
        action: event.action,
        resource: event.configPath,
        parameters: this.sanitizeConfig(event.config),
        result: event.success ? 'success' : 'failure'
      },
      performedBy: event.userId,
      metadata: {
        agentVersion: event.agentVersion,
        environment: process.env.NODE_ENV as any,
        riskLevel: this.assessRiskLevel(event)
      }
    };
  }
  
  private sanitizeConfig(config: any): any {
    // Remove sensitive information like passwords, tokens
    const sanitized = { ...config };
    const sensitiveKeys = ['password', 'token', 'key', 'secret'];
    
    for (const key of sensitiveKeys) {
      if (key in sanitized) {
        sanitized[key] = '[REDACTED]';
      }
    }
    
    return sanitized;
  }
  
  private assessRiskLevel(event: ConfigEvent): 'low' | 'medium' | 'high' | 'critical' {
    if (event.configPath.includes('security') || event.configPath.includes('auth')) {
      return 'high';
    }
    if (event.configPath.includes('system')) {
      return 'medium';
    }
    return 'low';
  }
}

class CommunicationHook extends AttestationHook {
  shouldAttest(event: AgentEvent): boolean {
    return event.type.startsWith('comms.') || event.type.startsWith('klp.');
  }
  
  createRecord(event: CommunicationEvent): AttestationRecord {
    return {
      id: generateUUID(),
      agentId: event.agentId,
      timestamp: new Date().toISOString(),
      context: event.type as AttestationContext,
      payload: {
        action: event.action,
        resource: event.target,
        parameters: {
          messageType: event.messageType,
          messageSize: event.messageSize
        },
        result: event.success ? 'success' : 'failure'
      },
      performedBy: event.userId,
      metadata: {
        agentVersion: event.agentVersion,
        environment: process.env.NODE_ENV as any,
        correlationId: event.messageId,
        riskLevel: event.external ? 'medium' : 'low'
      }
    };
  }
}

class SecurityHook extends AttestationHook {
  shouldAttest(event: AgentEvent): boolean {
    return event.type.startsWith('security.');
  }
  
  createRecord(event: SecurityEvent): AttestationRecord {
    return {
      id: generateUUID(),
      agentId: event.agentId,
      timestamp: new Date().toISOString(),
      context: event.type as AttestationContext,
      payload: {
        action: event.action,
        resource: event.resource,
        result: event.success ? 'success' : 'failure',
        errorCode: event.errorCode
      },
      performedBy: event.userId,
      metadata: {
        agentVersion: event.agentVersion,
        environment: process.env.NODE_ENV as any,
        riskLevel: 'critical'  // All security events are high risk
      }
    };
  }
}
```

### Hook Registration System

```typescript
class AttestationManager {
  private hooks: Map<string, AttestationHook[]> = new Map();
  private storage: AttestationStorage;
  private verifier: AttestationVerifier;
  
  registerHook(eventType: string, hook: AttestationHook): void {
    if (!this.hooks.has(eventType)) {
      this.hooks.set(eventType, []);
    }
    this.hooks.get(eventType)!.push(hook);
  }
  
  async processEvent(event: AgentEvent): Promise<void> {
    const hooks = this.hooks.get(event.type) || [];
    await Promise.all(hooks.map(hook => hook.onEvent(event)));
  }
  
  async addRecord(record: AttestationRecord): Promise<AttestationProof> {
    // Create cryptographic proof
    const proof = await this.createProof(record);
    
    // Store locally
    await this.storage.store(proof);
    
    // Optional: Anchor to external systems
    if (this.config.anchoring.enabled) {
      await this.anchorProof(proof);
    }
    
    return proof;
  }
  
  private async createProof(record: AttestationRecord): Promise<AttestationProof> {
    const recordHash = await this.hashRecord(record);
    const signature = await this.signHash(recordHash);
    
    return {
      record,
      signature,
      signatureAlgorithm: 'ed25519',
      publicKey: this.getPublicKey(),
      verificationMethod: this.getDIDVerificationMethod()
    };
  }
}
```

## Verification & Cross-Entity Sharing

### Local Verification

```typescript
class AttestationVerifier {
  async verifyProof(proof: AttestationProof): Promise<VerificationResult> {
    try {
      // 1. Verify signature
      const recordHash = await this.hashRecord(proof.record);
      const signatureValid = await this.verifySignature(
        recordHash,
        proof.signature,
        proof.publicKey
      );
      
      if (!signatureValid) {
        return { valid: false, error: 'Invalid signature' };
      }
      
      // 2. Verify DID ownership
      const didValid = await this.verifyDIDOwnership(
        proof.record.agentId,
        proof.publicKey
      );
      
      if (!didValid) {
        return { valid: false, error: 'DID ownership verification failed' };
      }
      
      // 3. Verify timestamp bounds
      const timestampValid = this.verifyTimestamp(proof.record.timestamp);
      
      if (!timestampValid) {
        return { valid: false, error: 'Invalid timestamp' };
      }
      
      // 4. Verify context validity
      const contextValid = this.verifyContext(proof.record.context, proof.record.payload);
      
      if (!contextValid) {
        return { valid: false, error: 'Invalid context or payload' };
      }
      
      return { valid: true };
      
    } catch (error) {
      return { valid: false, error: error.message };
    }
  }
  
  async verifyChain(proofs: AttestationProof[]): Promise<ChainVerificationResult> {
    const results = await Promise.all(proofs.map(proof => this.verifyProof(proof)));
    
    const invalidProofs = results.filter(r => !r.valid);
    
    return {
      valid: invalidProofs.length === 0,
      totalProofs: proofs.length,
      validProofs: results.filter(r => r.valid).length,
      invalidProofs: invalidProofs.map(r => r.error!)
    };
  }
  
  private async verifySignature(
    hash: string,
    signature: string,
    publicKey: string
  ): Promise<boolean> {
    // Implement Ed25519 signature verification
    const key = await crypto.subtle.importKey(
      'raw',
      Buffer.from(publicKey, 'base64'),
      { name: 'Ed25519' },
      false,
      ['verify']
    );
    
    return crypto.subtle.verify(
      'Ed25519',
      key,
      Buffer.from(signature, 'base64'),
      Buffer.from(hash, 'hex')
    );
  }
}

interface VerificationResult {
  valid: boolean;
  error?: string;
  warnings?: string[];
}

interface ChainVerificationResult {
  valid: boolean;
  totalProofs: number;
  validProofs: number;
  invalidProofs: string[];
}
```

### External Verification

```typescript
class FederatedVerifier {
  async shareAttestation(proof: AttestationProof, target: KindDID): Promise<void> {
    const message: KLPMessage = {
      id: generateUUID(),
      from: this.agentDID,
      to: target,
      type: 'attestation_share',
      protocol: 'klp/1.0',
      timestamp: new Date().toISOString(),
      payload: proof,
      signature: await this.signMessage(proof)
    };
    
    await this.klpRouter.sendMessage(message);
  }
  
  async requestVerification(
    proof: AttestationProof,
    verifiers: KindDID[]
  ): Promise<VerificationResponse[]> {
    const requests = verifiers.map(verifier => this.requestSingleVerification(proof, verifier));
    return Promise.all(requests);
  }
  
  private async requestSingleVerification(
    proof: AttestationProof,
    verifier: KindDID
  ): Promise<VerificationResponse> {
    const request: KLPMessage = {
      id: generateUUID(),
      from: this.agentDID,
      to: verifier,
      type: 'verification_request',
      protocol: 'klp/1.0',
      timestamp: new Date().toISOString(),
      payload: { proof },
      signature: await this.signMessage({ proof })
    };
    
    const response = await this.klpRouter.sendMessage(request);
    return response.payload as VerificationResponse;
  }
}

interface VerificationResponse {
  verifierId: KindDID;
  result: VerificationResult;
  timestamp: string;
  signature: string;
}
```

### Optional Anchoring

```typescript
interface AnchoringConfig {
  enabled: boolean;
  ipfs?: {
    gateway: string;
    pin: boolean;
  };
  blockchain?: {
    network: 'ethereum' | 'polygon' | 'custom';
    contractAddress: string;
    gasLimit: number;
  };
}

class AttestationAnchor {
  constructor(private config: AnchoringConfig) {}
  
  async anchorToIPFS(proof: AttestationProof): Promise<string> {
    if (!this.config.ipfs) {
      throw new Error('IPFS not configured');
    }
    
    const ipfs = create({ url: this.config.ipfs.gateway });
    const { cid } = await ipfs.add(JSON.stringify(proof));
    
    if (this.config.ipfs.pin) {
      await ipfs.pin.add(cid);
    }
    
    return cid.toString();
  }
  
  async anchorToBlockchain(proof: AttestationProof): Promise<string> {
    if (!this.config.blockchain) {
      throw new Error('Blockchain not configured');
    }
    
    const hash = await this.hashProof(proof);
    const txHash = await this.submitToContract(hash);
    
    return txHash;
  }
  
  async verifyIPFSAnchor(cid: string, proof: AttestationProof): Promise<boolean> {
    try {
      const ipfs = create({ url: this.config.ipfs!.gateway });
      const chunks = [];
      
      for await (const chunk of ipfs.cat(cid)) {
        chunks.push(chunk);
      }
      
      const retrievedProof = JSON.parse(Buffer.concat(chunks).toString());
      return JSON.stringify(retrievedProof) === JSON.stringify(proof);
      
    } catch (error) {
      return false;
    }
  }
}
```

## Access & CLI Tools

### CLI Audit Tool

```typescript
class CLIAuditViewer {
  async listAttestations(options: ListOptions = {}): Promise<void> {
    const attestations = await this.storage.query({
      agentId: options.agentId,
      context: options.context,
      fromDate: options.fromDate,
      toDate: options.toDate,
      limit: options.limit || 50
    });
    
    console.table(attestations.map(a => ({
      ID: a.record.id.substring(0, 8),
      Agent: a.record.agentId.split(':').pop()?.substring(0, 12),
      Context: a.record.context,
      Timestamp: new Date(a.record.timestamp).toLocaleString(),
      Verified: a.record.verified ? '✓' : '?'
    })));
  }
  
  async inspectAttestation(id: string): Promise<void> {
    const proof = await this.storage.getById(id);
    if (!proof) {
      console.error(`Attestation ${id} not found`);
      return;
    }
    
    const verification = await this.verifier.verifyProof(proof);
    
    console.log('Attestation Details:');
    console.log('==================');
    console.log(`ID: ${proof.record.id}`);
    console.log(`Agent: ${proof.record.agentId}`);
    console.log(`Context: ${proof.record.context}`);
    console.log(`Timestamp: ${proof.record.timestamp}`);
    console.log(`Performed By: ${proof.record.performedBy}`);
    console.log(`Verified: ${verification.valid ? '✓' : '✗'}`);
    
    if (!verification.valid) {
      console.log(`Error: ${verification.error}`);
    }
    
    console.log('\nPayload:');
    console.log(JSON.stringify(proof.record.payload, null, 2));
    
    console.log('\nSignature:');
    console.log(`Algorithm: ${proof.signatureAlgorithm}`);
    console.log(`Signature: ${proof.signature.substring(0, 32)}...`);
  }
  
  async exportAttestations(options: ExportOptions): Promise<void> {
    const attestations = await this.storage.query(options);
    const exportData = {
      exported_at: new Date().toISOString(),
      total_records: attestations.length,
      attestations: attestations.map(a => a.record),
      metadata: {
        export_version: '1.0',
        agent_filter: options.agentId,
        date_range: {
          from: options.fromDate,
          to: options.toDate
        }
      }
    };
    
    const filename = `attestations_${Date.now()}.json`;
    await fs.writeFile(filename, JSON.stringify(exportData, null, 2));
    console.log(`Exported ${attestations.length} attestations to ${filename}`);
  }
}

interface ListOptions {
  agentId?: string;
  context?: AttestationContext;
  fromDate?: string;
  toDate?: string;
  limit?: number;
}

interface ExportOptions extends ListOptions {
  format?: 'json' | 'csv' | 'xml';
  includeSignatures?: boolean;
}
```

## Configurable Attestation Modes

```typescript
enum AttestationMode {
  SILENT = 'silent',           // No logging (dev/test only)
  LOCAL_ONLY = 'local_only',   // Signed, local logs only
  ANCHORED = 'anchored',       // Local + blockchain/IPFS anchor
  FEDERATED = 'federated'      // Share attestation streams to trusted neighbors
}

interface AttestationConfig {
  mode: AttestationMode;
  rotation: {
    enabled: boolean;
    intervalDays: number;
    maxSize: number;           // Maximum log size in MB
  };
  anchoring: AnchoringConfig;
  filtering: {
    excludeContexts: AttestationContext[];
    minimumRiskLevel: 'low' | 'medium' | 'high' | 'critical';
  };
  federation: {
    enabled: boolean;
    trustedVerifiers: KindDID[];
    autoShare: boolean;
    shareFilter: AttestationContext[];
  };
}

// Example configuration
const defaultConfig: AttestationConfig = {
  mode: AttestationMode.LOCAL_ONLY,
  rotation: {
    enabled: true,
    intervalDays: 30,
    maxSize: 100  // 100MB
  },
  anchoring: {
    enabled: false
  },
  filtering: {
    excludeContexts: ['memory.read'],  // High-frequency, low-risk operations
    minimumRiskLevel: 'low'
  },
  federation: {
    enabled: false,
    trustedVerifiers: [],
    autoShare: false,
    shareFilter: ['security.auth', 'security.violation']
  }
};
```

## Use Cases & Extensions

### Agent Accountability
```typescript
class AccountabilityTracker {
  async investigateAgent(agentId: string): Promise<AccountabilityReport> {
    const attestations = await this.storage.query({ agentId });
    const violations = attestations.filter(a => 
      a.record.context.startsWith('security.') || 
      a.record.payload.result === 'failure'
    );
    
    return {
      agentId,
      totalActions: attestations.length,
      securityViolations: violations.length,
      riskScore: this.calculateRiskScore(attestations),
      recommendations: this.generateRecommendations(violations)
    };
  }
}
```

### Governance Voting Audits
```typescript
class GovernanceAuditor {
  async auditVote(voteId: string): Promise<VoteAuditResult> {
    const attestations = await this.storage.query({ 
      correlationId: voteId 
    });
    
    return {
      voteId,
      participantCount: new Set(attestations.map(a => a.record.performedBy)).size,
      allVerified: attestations.every(a => a.record.verified),
      timeline: attestations.map(a => ({
        timestamp: a.record.timestamp,
        action: a.record.payload.action,
        participant: a.record.performedBy
      }))
    };
  }
}
```

### Multi-agent Trust
```typescript
class TrustGraphBuilder {
  async buildTrustRelationship(
    agentA: KindDID,
    agentB: KindDID
  ): Promise<TrustRelationship> {
    const interactionsA = await this.storage.query({
      agentId: agentA,
      context: 'comms.outbound'
    });
    
    const interactionsB = await this.storage.query({
      agentId: agentB,
      context: 'comms.outbound'
    });
    
    const sharedInteractions = this.findSharedInteractions(interactionsA, interactionsB);
    
    return {
      agents: [agentA, agentB],
      trustScore: this.calculateTrustScore(sharedInteractions),
      sharedContext: sharedInteractions.length,
      lastInteraction: this.getLastInteraction(sharedInteractions)
    };
  }
}
```

## Roadmap

| Feature                             | Version | Status |
| ----------------------------------- | ------- | ------ |
| Initial Attestation Hooks           | v0.9    | Planned |
| IPFS Anchoring + View Tool          | v1.0    | Planned |
| DID Signature Verification (Remote) | v1.2    | Planned |
| zkProof Extension for Agent Claims  | v1.5    | Research |
| Blockchain Anchoring Plugin         | v2.0    | Future |
| Cross-platform Attestation Sync    | v2.1    | Future |

## Implementation Status

- **Core Attestation Framework**: Specification complete
- **Event Hook System**: Architecture defined
- **Verification Engine**: Interface designed
- **CLI Tools**: Command structure planned
- **Storage Backends**: Local and anchored options specified
- **Reference Implementation**: Planned for kOS v1.0

This attestation system provides the foundation for trust in autonomous systems, making every action provable, reviewable, and defensible across the entire kOS ecosystem. 