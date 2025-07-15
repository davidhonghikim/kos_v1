---
version: "1.0.0"
last_updated: "2025-01-27"
status: "draft"
type: "specification"
category: "security"
tags: ["identity", "cryptography", "did", "zero-knowledge", "protocols"]
related_docs: 
  - "current/security/01_security-framework.md"
  - "future/security/05_comprehensive-security-architecture.md"
  - "future/protocols/04_agent-system-protocols.md"
complexity: "high"
implementation_status: "planned"
code_references:
  - "src/utils/crypto.ts"
  - "src/store/securityStateStore.ts"
  - "src/components/security/VaultManager.tsx"
decision_scope: "system-wide"
external_references:
  - "https://www.w3.org/TR/did-core/"
  - "https://w3c.github.io/vc-data-model/"
  - "https://tools.ietf.org/html/rfc8037"
changelog:
  - "2025-01-27: Initial migration from brainstorm file 167"
---

# kID Identity Protocols: Federated Agent Credentialing & Decentralized Identity

**Agent Context**: This document defines the complete decentralized identity and credentialing system powering the trust framework for kAI agents, kOS services, and human users across the Kind ecosystem. Agents should understand this as the foundational identity layer that enables secure, verifiable interactions between all entities in the kOS network.

## Purpose & Objectives

The kID (Kind Identity) system enables:
- Decentralized, cryptographically verifiable identities for all agents, humans, and services
- Progressive disclosure and zero-knowledge proofs of credentials
- Federated trust across devices, organizations, and social contracts
- Composable identity stacks for multi-role entities

## kID: Kind Identity Specification

### Core Structure

```typescript
interface KindIdentityDocument {
  kid: string; // DID identifier
  publicKey: CryptoKey;
  controllers: string[];
  service?: ServiceEndpoint[];
  proof: IdentityProof;
  created: string;
  updated: string;
  revoked?: boolean;
}

interface ServiceEndpoint {
  type: string;
  endpoint: string;
  priority?: number;
}

interface IdentityProof {
  type: 'Ed25519Signature2020';
  created: string;
  proofPurpose: 'assertionMethod' | 'authentication' | 'keyAgreement';
  verificationMethod: string;
  signatureValue: string;
}

// Example kID document
const exampleKID: KindIdentityDocument = {
  kid: "did:klp:node123:agent456",
  publicKey: await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode('ed25519:abc123'),
    { name: 'Ed25519', namedCurve: 'Ed25519' },
    false,
    ['verify']
  ),
  controllers: ["did:klp:node123:admin"],
  service: [
    { type: "PromptSync", endpoint: "https://node1.kos/prompt" },
    { type: "VectorQuery", endpoint: "https://node1.kos/vector" }
  ],
  proof: {
    type: "Ed25519Signature2020",
    created: "2025-06-22T08:00:00Z",
    proofPurpose: "assertionMethod",
    verificationMethod: "did:klp:node123#key-1",
    signatureValue: "xyz..."
  },
  created: "2025-06-22T08:00:00Z",
  updated: "2025-06-22T08:00:00Z"
};
```

### Naming Convention

kID identifiers follow the pattern: `did:klp:<cluster_id>:<entity_id>`

```typescript
class KIDIdentifier {
  constructor(
    public readonly clusterId: string,
    public readonly entityId: string
  ) {}

  toString(): string {
    return `did:klp:${this.clusterId}:${this.entityId}`;
  }

  static parse(did: string): KIDIdentifier {
    const parts = did.split(':');
    if (parts.length !== 4 || parts[0] !== 'did' || parts[1] !== 'klp') {
      throw new Error('Invalid kID format');
    }
    return new KIDIdentifier(parts[2], parts[3]);
  }
}

// Examples
const schoolTeacher = new KIDIdentifier('school123', 'teacher456');
const homeDevice = new KIDIdentifier('home789', 'device42');
```

## Verifiable Credentials System

### Credential Structure

```typescript
interface VerifiableCredential {
  '@context': string[];
  type: string[];
  issuer: string;
  credentialSubject: CredentialSubject;
  issuanceDate: string;
  expirationDate?: string;
  proof: CredentialProof;
}

interface CredentialSubject {
  id: string; // kID of the subject
  role?: string;
  trustLevel?: 'low' | 'medium' | 'high' | 'critical';
  permissions?: string[];
  capabilities?: string[];
  metadata?: Record<string, any>;
}

interface CredentialProof {
  type: string;
  created: string;
  proofPurpose: string;
  verificationMethod: string;
  signatureValue: string;
}

// Credential types
type CredentialType = 
  | 'AgentRoleCredential'
  | 'HumanIdentityCredential'
  | 'ServiceContractCredential'
  | 'CapabilityGrant'
  | 'AuditRight';

class CredentialManager {
  async issueCredential(
    issuerKID: string,
    subjectKID: string,
    credentialType: CredentialType,
    claims: Record<string, any>,
    privateKey: CryptoKey
  ): Promise<VerifiableCredential> {
    const credential: VerifiableCredential = {
      '@context': ['https://www.w3.org/2018/credentials/v1'],
      type: ['VerifiableCredential', credentialType],
      issuer: issuerKID,
      credentialSubject: {
        id: subjectKID,
        ...claims
      },
      issuanceDate: new Date().toISOString(),
      expirationDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
      proof: await this.generateProof(credential, privateKey)
    };

    return credential;
  }

  async verifyCredential(credential: VerifiableCredential): Promise<boolean> {
    try {
      // Verify proof signature
      const isValidSignature = await this.verifyProofSignature(credential);
      
      // Check expiration
      if (credential.expirationDate && new Date() > new Date(credential.expirationDate)) {
        return false;
      }

      // Verify issuer authority
      const issuerTrusted = await this.verifyIssuerAuthority(credential.issuer);

      return isValidSignature && issuerTrusted;
    } catch (error) {
      console.error('Credential verification failed:', error);
      return false;
    }
  }

  private async generateProof(credential: any, privateKey: CryptoKey): Promise<CredentialProof> {
    const dataToSign = JSON.stringify(credential);
    const signature = await crypto.subtle.sign(
      'Ed25519',
      privateKey,
      new TextEncoder().encode(dataToSign)
    );

    return {
      type: 'Ed25519Signature2020',
      created: new Date().toISOString(),
      proofPurpose: 'assertionMethod',
      verificationMethod: `${credential.issuer}#key-1`,
      signatureValue: Array.from(new Uint8Array(signature))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('')
    };
  }

  private async verifyProofSignature(credential: VerifiableCredential): Promise<boolean> {
    // Implementation would verify Ed25519 signature
    return true; // Simplified for example
  }

  private async verifyIssuerAuthority(issuerKID: string): Promise<boolean> {
    // Check if issuer is authorized to issue this type of credential
    return true; // Simplified for example
  }
}
```

## Trust Verification Protocols

### kID Registry System

```typescript
interface KIDRegistryNode {
  nodeId: string;
  endpoint: string;
  trustLevel: number;
  lastSeen: string;
}

class KIDRegistry {
  private nodes: Map<string, KIDRegistryNode> = new Map();
  private cache: Map<string, KindIdentityDocument> = new Map();

  async resolveDID(kid: string): Promise<KindIdentityDocument | null> {
    // Check local cache first
    if (this.cache.has(kid)) {
      return this.cache.get(kid)!;
    }

    // Query federated registry nodes
    for (const node of this.nodes.values()) {
      try {
        const response = await fetch(`${node.endpoint}/did/${encodeURIComponent(kid)}`);
        if (response.ok) {
          const document = await response.json() as KindIdentityDocument;
          
          // Verify document integrity
          if (await this.verifyDocument(document)) {
            this.cache.set(kid, document);
            return document;
          }
        }
      } catch (error) {
        console.warn(`Failed to query registry node ${node.nodeId}:`, error);
      }
    }

    return null;
  }

  async registerDID(document: KindIdentityDocument): Promise<boolean> {
    // Verify document before registration
    if (!await this.verifyDocument(document)) {
      throw new Error('Invalid DID document');
    }

    // Register with federated nodes
    const registrationPromises = Array.from(this.nodes.values()).map(async (node) => {
      try {
        const response = await fetch(`${node.endpoint}/did`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(document)
        });
        return response.ok;
      } catch {
        return false;
      }
    });

    const results = await Promise.all(registrationPromises);
    const successCount = results.filter(Boolean).length;

    // Require majority consensus for registration
    return successCount > this.nodes.size / 2;
  }

  private async verifyDocument(document: KindIdentityDocument): Promise<boolean> {
    try {
      // Verify signature
      const dataToVerify = JSON.stringify({
        kid: document.kid,
        publicKey: document.publicKey,
        controllers: document.controllers,
        service: document.service,
        created: document.created
      });

      // In a real implementation, this would verify the Ed25519 signature
      return true;
    } catch (error) {
      console.error('Document verification failed:', error);
      return false;
    }
  }

  addRegistryNode(node: KIDRegistryNode): void {
    this.nodes.set(node.nodeId, node);
  }

  removeRegistryNode(nodeId: string): void {
    this.nodes.delete(nodeId);
  }
}
```

### Trust Score Calculation

```typescript
interface TrustMetrics {
  verifiedCredentials: number;
  auditLogs: number;
  uptime: number; // percentage
  behaviorScore: number; // 0-100
  peerEndorsements: number;
  userApprovals: number;
  honestFailureReports: number;
}

class TrustScoreCalculator {
  calculateTrustScore(metrics: TrustMetrics, timeDecayFactor: number = 0.95): number {
    const weights = {
      credentials: 0.25,
      audits: 0.15,
      uptime: 0.20,
      behavior: 0.25,
      endorsements: 0.10,
      approvals: 0.15,
      honesty: 0.10
    };

    const baseScore = 
      (metrics.verifiedCredentials * weights.credentials) +
      (Math.min(metrics.auditLogs, 100) * weights.audits) +
      (metrics.uptime * weights.uptime) +
      (metrics.behaviorScore * weights.behavior) +
      (Math.min(metrics.peerEndorsements, 50) * weights.endorsements) +
      (Math.min(metrics.userApprovals, 100) * weights.approvals) +
      (Math.min(metrics.honestFailureReports, 20) * weights.honesty);

    // Apply time decay to enforce continuous contribution
    return Math.min(100, baseScore * timeDecayFactor);
  }

  async getTrustScore(kid: string): Promise<number> {
    // In implementation, this would query the metrics from various sources
    const metrics = await this.fetchTrustMetrics(kid);
    return this.calculateTrustScore(metrics);
  }

  private async fetchTrustMetrics(kid: string): Promise<TrustMetrics> {
    // Simplified - would fetch from distributed ledger and audit logs
    return {
      verifiedCredentials: 5,
      auditLogs: 25,
      uptime: 95.5,
      behaviorScore: 87,
      peerEndorsements: 12,
      userApprovals: 34,
      honestFailureReports: 3
    };
  }
}
```

## Zero-Knowledge Proof System

```typescript
interface ZKProofRequest {
  requirement: string; // e.g., "hasRole:HomeAssistant"
  context: string;
  challenge: string;
}

interface ZKProofResponse {
  proof: string;
  publicInputs: string[];
  verified: boolean;
}

class ZKProofManager {
  async generateProof(
    credential: VerifiableCredential,
    request: ZKProofRequest
  ): Promise<ZKProofResponse> {
    // Simplified ZK proof generation
    // In practice, this would use a ZK library like snarkjs or circom
    
    const hasRequiredRole = this.checkRequirement(credential, request.requirement);
    
    if (!hasRequiredRole) {
      throw new Error('Credential does not satisfy requirement');
    }

    // Generate proof without revealing the full credential
    const proof = await this.generateZKProof(credential, request);
    
    return {
      proof: proof.proofData,
      publicInputs: proof.publicInputs,
      verified: true
    };
  }

  async verifyProof(response: ZKProofResponse, request: ZKProofRequest): Promise<boolean> {
    try {
      // Verify the ZK proof
      return await this.verifyZKProof(response.proof, response.publicInputs, request);
    } catch (error) {
      console.error('ZK proof verification failed:', error);
      return false;
    }
  }

  private checkRequirement(credential: VerifiableCredential, requirement: string): boolean {
    const [type, value] = requirement.split(':');
    
    switch (type) {
      case 'hasRole':
        return credential.credentialSubject.role === value;
      case 'hasTrustLevel':
        return credential.credentialSubject.trustLevel === value;
      case 'hasPermission':
        return credential.credentialSubject.permissions?.includes(value) || false;
      default:
        return false;
    }
  }

  private async generateZKProof(credential: VerifiableCredential, request: ZKProofRequest) {
    // Simplified - would use actual ZK proof library
    return {
      proofData: 'zkp_proof_data_here',
      publicInputs: [request.challenge]
    };
  }

  private async verifyZKProof(proof: string, publicInputs: string[], request: ZKProofRequest): Promise<boolean> {
    // Simplified - would use actual ZK verification
    return true;
  }
}
```

## Agent-to-Agent Authentication Flow

```typescript
class AgentAuthenticationFlow {
  private kidRegistry: KIDRegistry;
  private credentialManager: CredentialManager;
  private zkProofManager: ZKProofManager;

  constructor() {
    this.kidRegistry = new KIDRegistry();
    this.credentialManager = new CredentialManager();
    this.zkProofManager = new ZKProofManager();
  }

  async authenticateAgent(agentKID: string, requiredCapabilities: string[]): Promise<boolean> {
    try {
      // 1. Resolve agent's DID document
      const didDocument = await this.kidRegistry.resolveDID(agentKID);
      if (!didDocument) {
        throw new Error('Agent DID not found');
      }

      // 2. Verify DID document integrity
      if (didDocument.revoked) {
        throw new Error('Agent identity has been revoked');
      }

      // 3. Request agent's role credentials
      const credentials = await this.requestCredentials(agentKID);
      
      // 4. Verify each credential
      for (const credential of credentials) {
        const isValid = await this.credentialManager.verifyCredential(credential);
        if (!isValid) {
          throw new Error('Invalid credential presented');
        }
      }

      // 5. Check if agent has required capabilities
      const hasRequiredCapabilities = this.verifyCapabilities(credentials, requiredCapabilities);
      if (!hasRequiredCapabilities) {
        throw new Error('Agent lacks required capabilities');
      }

      // 6. Optionally request ZK proof for sensitive operations
      if (requiredCapabilities.some(cap => cap.includes('sensitive'))) {
        const zkProofValid = await this.requestZKProof(agentKID, requiredCapabilities);
        if (!zkProofValid) {
          throw new Error('ZK proof verification failed');
        }
      }

      return true;
    } catch (error) {
      console.error('Agent authentication failed:', error);
      return false;
    }
  }

  private async requestCredentials(agentKID: string): Promise<VerifiableCredential[]> {
    // In practice, this would use the KLP protocol to request credentials
    return [];
  }

  private verifyCapabilities(credentials: VerifiableCredential[], required: string[]): boolean {
    const agentCapabilities = credentials.flatMap(cred => 
      cred.credentialSubject.capabilities || []
    );

    return required.every(cap => agentCapabilities.includes(cap));
  }

  private async requestZKProof(agentKID: string, capabilities: string[]): Promise<boolean> {
    // Generate challenge
    const challenge = crypto.getRandomValues(new Uint8Array(32));
    const challengeString = Array.from(challenge).map(b => b.toString(16)).join('');

    const request: ZKProofRequest = {
      requirement: `hasCapabilities:${capabilities.join(',')}`,
      context: 'authentication',
      challenge: challengeString
    };

    // In practice, this would be sent via KLP
    // For now, assume we get a response
    const response: ZKProofResponse = {
      proof: 'mock_proof',
      publicInputs: [challengeString],
      verified: true
    };

    return this.zkProofManager.verifyProof(response, request);
  }
}
```

## Integration with kOS

### Local Identity Hub

```typescript
class LocalIdentityHub {
  private identityStore: Map<string, KindIdentityDocument> = new Map();
  private credentialStore: Map<string, VerifiableCredential[]> = new Map();
  private privateKeys: Map<string, CryptoKey> = new Map();

  async createIdentity(entityType: 'agent' | 'service' | 'user'): Promise<string> {
    // Generate key pair
    const keyPair = await crypto.subtle.generateKey(
      { name: 'Ed25519', namedCurve: 'Ed25519' },
      true,
      ['sign', 'verify']
    );

    // Create kID
    const clusterId = await this.getClusterId();
    const entityId = crypto.randomUUID();
    const kid = `did:klp:${clusterId}:${entityId}`;

    // Create DID document
    const didDocument: KindIdentityDocument = {
      kid,
      publicKey: keyPair.publicKey,
      controllers: [kid], // Self-controlled initially
      proof: await this.generateIdentityProof(kid, keyPair.privateKey),
      created: new Date().toISOString(),
      updated: new Date().toISOString()
    };

    // Store locally
    this.identityStore.set(kid, didDocument);
    this.privateKeys.set(kid, keyPair.privateKey);
    this.credentialStore.set(kid, []);

    return kid;
  }

  async signData(kid: string, data: any): Promise<string> {
    const privateKey = this.privateKeys.get(kid);
    if (!privateKey) {
      throw new Error('Private key not found for identity');
    }

    const dataBytes = new TextEncoder().encode(JSON.stringify(data));
    const signature = await crypto.subtle.sign('Ed25519', privateKey, dataBytes);
    
    return Array.from(new Uint8Array(signature))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  async getIdentity(kid: string): Promise<KindIdentityDocument | null> {
    return this.identityStore.get(kid) || null;
  }

  async addCredential(kid: string, credential: VerifiableCredential): Promise<void> {
    const credentials = this.credentialStore.get(kid) || [];
    credentials.push(credential);
    this.credentialStore.set(kid, credentials);
  }

  async getCredentials(kid: string): Promise<VerifiableCredential[]> {
    return this.credentialStore.get(kid) || [];
  }

  private async getClusterId(): Promise<string> {
    // In practice, this would be configured or derived from network
    return 'local';
  }

  private async generateIdentityProof(kid: string, privateKey: CryptoKey): Promise<IdentityProof> {
    const proofData = {
      kid,
      created: new Date().toISOString(),
      proofPurpose: 'assertionMethod'
    };

    const signature = await this.signData(kid, proofData);

    return {
      type: 'Ed25519Signature2020',
      created: proofData.created,
      proofPurpose: 'assertionMethod',
      verificationMethod: `${kid}#key-1`,
      signatureValue: signature
    };
  }
}
```

## Security Considerations

### Key Management

```typescript
class SecureKeyManager {
  private keyStorage: Map<string, CryptoKey> = new Map();

  async rotateKeys(kid: string, oldPrivateKey: CryptoKey): Promise<CryptoKey> {
    // Generate new key pair
    const newKeyPair = await crypto.subtle.generateKey(
      { name: 'Ed25519', namedCurve: 'Ed25519' },
      true,
      ['sign', 'verify']
    );

    // Sign rotation certificate with old key
    const rotationCert = await this.createRotationCertificate(kid, oldPrivateKey, newKeyPair.publicKey);
    
    // Update identity document
    await this.updateIdentityDocument(kid, newKeyPair.publicKey, rotationCert);

    // Store new key
    this.keyStorage.set(kid, newKeyPair.privateKey);

    return newKeyPair.privateKey;
  }

  async revokeIdentity(kid: string, reason: string): Promise<void> {
    // Create revocation certificate
    const revocationCert = {
      kid,
      revoked: true,
      reason,
      timestamp: new Date().toISOString()
    };

    // Sign and publish revocation
    await this.publishRevocation(revocationCert);
  }

  private async createRotationCertificate(
    kid: string, 
    oldKey: CryptoKey, 
    newPublicKey: CryptoKey
  ): Promise<any> {
    const cert = {
      type: 'KeyRotation',
      subject: kid,
      oldKey: await crypto.subtle.exportKey('raw', oldKey),
      newKey: await crypto.subtle.exportKey('raw', newPublicKey),
      timestamp: new Date().toISOString()
    };

    const signature = await crypto.subtle.sign(
      'Ed25519',
      oldKey,
      new TextEncoder().encode(JSON.stringify(cert))
    );

    return { ...cert, signature };
  }

  private async updateIdentityDocument(kid: string, newPublicKey: CryptoKey, rotationCert: any): Promise<void> {
    // Implementation would update the DID document with new key
  }

  private async publishRevocation(revocationCert: any): Promise<void> {
    // Implementation would publish to revocation registry
  }
}
```

## Implementation Roadmap

### Phase 1: Core Identity Infrastructure
- [ ] Basic kID document structure and validation
- [ ] Ed25519 key generation and management
- [ ] Local identity hub implementation
- [ ] Simple credential issuance and verification

### Phase 2: Registry and Federation
- [ ] Federated registry node implementation
- [ ] DID resolution protocol
- [ ] Network synchronization mechanisms
- [ ] Trust score calculation engine

### Phase 3: Advanced Features
- [ ] Zero-knowledge proof integration
- [ ] Cross-device identity synchronization
- [ ] Advanced revocation mechanisms
- [ ] Hardware security module integration

### Phase 4: Integration and Optimization
- [ ] kOS platform integration
- [ ] Performance optimization
- [ ] Security audit and hardening
- [ ] Documentation and developer tools

## Related Documentation

- [Security Framework](../current/security/01_security-framework.md) - Overall security architecture
- [Comprehensive Security Architecture](./05_comprehensive-security-architecture.md) - Multi-layered security design
- [Agent System Protocols](../protocols/04_agent-system-protocols.md) - Communication protocols
- [Trust Frameworks](./10_trust-frameworks.md) - Social trust and reputation systems

This kID system provides the foundational identity layer for all secure interactions within the kOS ecosystem, enabling trust, accountability, and privacy-preserving interactions between agents, services, and users. 