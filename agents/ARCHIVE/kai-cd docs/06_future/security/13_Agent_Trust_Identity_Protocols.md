---
version: "1.0.0"
last_updated: "2025-01-27"
status: "draft"
type: "specification"
category: "security"
tags: ["identity", "trust", "cryptography", "authentication", "verification"]
related_docs:
  - "future/security/09_kid-identity-protocols.md"
  - "future/security/10_trust-frameworks.md"
  - "future/security/11_reputation-jury-protocol.md"
complexity: "high"
implementation_status: "planned"
code_references:
  - "src/utils/crypto.ts"
  - "src/store/securityStateStore.ts"
  - "src/components/security/"
decision_scope: "system-wide"
external_references:
  - "https://tools.ietf.org/html/rfc8037"
  - "https://datatracker.ietf.org/doc/html/rfc7515"
  - "https://www.w3.org/TR/did-core/"
changelog:
  - "2025-01-27: Initial migration from brainstorm file 173"
---

# Agent Trust & Identity Protocols (ATIP)

**Agent Context**: This document defines the comprehensive low-level protocols, specifications, and systems for secure agent identity, trust scoring, credential signing, and verification across the kAI and kOS ecosystems. Agents should understand this as the foundational security layer that enables cryptographically verifiable identities, trust relationships, and secure inter-agent communication.

## System Architecture Overview

The Agent Trust & Identity Protocols establish:
- Unique, cryptographically verifiable identities for all agents
- Scalable, decentralized trust framework
- Multi-tier authentication and role-based permissions
- Agent-to-agent signed messaging and delegation
- Verifiable action logs with digital signatures

## Identity Generation System

```typescript
interface AgentKeyPair {
  privateKey: CryptoKey;
  publicKey: CryptoKey;
  algorithm: 'Ed25519';
  keyId: string;
  createdAt: string;
  expiresAt?: string;
}

interface AgentIdentity {
  agentId: string;
  publicKey: string;
  keyId: string;
  version: number;
  nickname?: string;
  roles: string[];
  metadata: IdentityMetadata;
  signature: string;
}

interface IdentityMetadata {
  hostPlatform: string;
  creationTime: string;
  lastRotation?: string;
  capabilities: string[];
  trustLevel: number;
}

class AgentIdentityManager {
  private keyStore: Map<string, AgentKeyPair> = new Map();
  private identities: Map<string, AgentIdentity> = new Map();

  async generateIdentity(
    nickname?: string,
    roles: string[] = [],
    metadata: Partial<IdentityMetadata> = {}
  ): Promise<AgentIdentity> {
    // Generate Ed25519 key pair
    const keyPair = await crypto.subtle.generateKey(
      { name: 'Ed25519', namedCurve: 'Ed25519' },
      true,
      ['sign', 'verify']
    );

    const keyId = crypto.randomUUID();
    const agentId = this.generateAgentId();

    // Store key pair
    const agentKeyPair: AgentKeyPair = {
      privateKey: keyPair.privateKey,
      publicKey: keyPair.publicKey,
      algorithm: 'Ed25519',
      keyId,
      createdAt: new Date().toISOString()
    };

    this.keyStore.set(agentId, agentKeyPair);

    // Export public key
    const publicKeyBytes = await crypto.subtle.exportKey('raw', keyPair.publicKey);
    const publicKeyHex = Array.from(new Uint8Array(publicKeyBytes))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');

    // Create identity
    const identity: Omit<AgentIdentity, 'signature'> = {
      agentId,
      publicKey: `ED25519:${publicKeyHex}`,
      keyId,
      version: 1,
      nickname,
      roles,
      metadata: {
        hostPlatform: this.detectPlatform(),
        creationTime: new Date().toISOString(),
        capabilities: await this.detectCapabilities(),
        trustLevel: 0.5, // Default starting trust
        ...metadata
      }
    };

    // Sign identity
    const signature = await this.signIdentity(identity, keyPair.privateKey);
    const fullIdentity: AgentIdentity = { ...identity, signature };

    this.identities.set(agentId, fullIdentity);
    return fullIdentity;
  }

  async rotateKeys(agentId: string): Promise<AgentIdentity> {
    const existingIdentity = this.identities.get(agentId);
    if (!existingIdentity) {
      throw new Error('Agent identity not found');
    }

    // Generate new key pair
    const newKeyPair = await crypto.subtle.generateKey(
      { name: 'Ed25519', namedCurve: 'Ed25519' },
      true,
      ['sign', 'verify']
    );

    const newKeyId = crypto.randomUUID();

    // Update key store
    const agentKeyPair: AgentKeyPair = {
      privateKey: newKeyPair.privateKey,
      publicKey: newKeyPair.publicKey,
      algorithm: 'Ed25519',
      keyId: newKeyId,
      createdAt: new Date().toISOString()
    };

    this.keyStore.set(agentId, agentKeyPair);

    // Export new public key
    const publicKeyBytes = await crypto.subtle.exportKey('raw', newKeyPair.publicKey);
    const publicKeyHex = Array.from(new Uint8Array(publicKeyBytes))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');

    // Update identity
    const updatedIdentity: Omit<AgentIdentity, 'signature'> = {
      ...existingIdentity,
      publicKey: `ED25519:${publicKeyHex}`,
      keyId: newKeyId,
      version: existingIdentity.version + 1,
      metadata: {
        ...existingIdentity.metadata,
        lastRotation: new Date().toISOString()
      }
    };

    // Sign updated identity
    const signature = await this.signIdentity(updatedIdentity, newKeyPair.privateKey);
    const newIdentity: AgentIdentity = { ...updatedIdentity, signature };

    this.identities.set(agentId, newIdentity);
    return newIdentity;
  }

  async verifyIdentity(identity: AgentIdentity): Promise<boolean> {
    try {
      // Extract public key
      const publicKeyHex = identity.publicKey.replace('ED25519:', '');
      const publicKeyBytes = new Uint8Array(
        publicKeyHex.match(/.{2}/g)!.map(byte => parseInt(byte, 16))
      );

      const publicKey = await crypto.subtle.importKey(
        'raw',
        publicKeyBytes,
        { name: 'Ed25519', namedCurve: 'Ed25519' },
        false,
        ['verify']
      );

      // Verify signature
      const identityData = JSON.stringify({
        agentId: identity.agentId,
        publicKey: identity.publicKey,
        keyId: identity.keyId,
        version: identity.version,
        nickname: identity.nickname,
        roles: identity.roles,
        metadata: identity.metadata
      });

      const signatureBytes = new Uint8Array(
        identity.signature.match(/.{2}/g)!.map(byte => parseInt(byte, 16))
      );

      return await crypto.subtle.verify(
        'Ed25519',
        publicKey,
        signatureBytes,
        new TextEncoder().encode(identityData)
      );
    } catch (error) {
      console.error('Identity verification failed:', error);
      return false;
    }
  }

  private generateAgentId(): string {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 5);
    return `kai-agent-${timestamp}-${random}`;
  }

  private async signIdentity(identity: Omit<AgentIdentity, 'signature'>, privateKey: CryptoKey): Promise<string> {
    const identityData = JSON.stringify(identity);
    const signature = await crypto.subtle.sign(
      'Ed25519',
      privateKey,
      new TextEncoder().encode(identityData)
    );

    return Array.from(new Uint8Array(signature))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  private detectPlatform(): string {
    if (typeof window !== 'undefined') {
      return `browser-${navigator.platform}`;
    } else if (typeof process !== 'undefined') {
      return `node-${process.platform}`;
    }
    return 'unknown';
  }

  private async detectCapabilities(): Promise<string[]> {
    const capabilities: string[] = [];

    // Check crypto support
    if (typeof crypto !== 'undefined' && crypto.subtle) {
      capabilities.push('crypto');
    }

    // Check storage capabilities
    if (typeof localStorage !== 'undefined') {
      capabilities.push('local_storage');
    }

    if (typeof indexedDB !== 'undefined') {
      capabilities.push('indexed_db');
    }

    // Check network capabilities
    if (typeof fetch !== 'undefined') {
      capabilities.push('fetch');
    }

    if (typeof WebSocket !== 'undefined') {
      capabilities.push('websocket');
    }

    return capabilities;
  }
}
```

## Trust Scoring System

```typescript
interface TrustComponents {
  direct: number;        // Assigned by user or higher-level agent
  reputation: number;    // Derived from observed actions
  delegated: number;     // Passed from trusted agents via signed claims
  system: number;        // System trust factors
}

interface TrustScore {
  agentId: string;
  score: number;
  components: TrustComponents;
  lastUpdated: string;
  factors: TrustFactor[];
  history: TrustScoreHistory[];
}

interface TrustFactor {
  factor: string;
  weight: number;
  value: number;
  source: string;
  timestamp: string;
}

interface TrustScoreHistory {
  timestamp: string;
  previousScore: number;
  newScore: number;
  reason: string;
  factors: TrustFactor[];
}

class TrustScoringEngine {
  private trustScores: Map<string, TrustScore> = new Map();
  private trustFactorWeights: Map<string, number> = new Map();

  constructor() {
    this.initializeFactorWeights();
  }

  async calculateTrustScore(agentId: string, factors: TrustFactor[]): Promise<TrustScore> {
    const existingScore = this.trustScores.get(agentId);
    const previousScore = existingScore?.score || 0;

    // Calculate component scores
    const components = this.calculateComponents(factors);
    
    // Weighted average of components
    const score = this.computeWeightedScore(components);

    // Create trust score object
    const trustScore: TrustScore = {
      agentId,
      score: Math.max(0, Math.min(1, score)),
      components,
      lastUpdated: new Date().toISOString(),
      factors,
      history: existingScore?.history || []
    };

    // Add history entry
    if (existingScore) {
      trustScore.history.push({
        timestamp: new Date().toISOString(),
        previousScore,
        newScore: trustScore.score,
        reason: 'Periodic recalculation',
        factors
      });

      // Keep only last 100 history entries
      if (trustScore.history.length > 100) {
        trustScore.history = trustScore.history.slice(-100);
      }
    }

    this.trustScores.set(agentId, trustScore);
    return trustScore;
  }

  async addTrustFactor(
    agentId: string,
    factor: string,
    value: number,
    source: string,
    weight?: number
  ): Promise<void> {
    const trustFactor: TrustFactor = {
      factor,
      weight: weight || this.trustFactorWeights.get(factor) || 1,
      value,
      source,
      timestamp: new Date().toISOString()
    };

    const existingScore = this.trustScores.get(agentId);
    const factors = existingScore?.factors || [];
    factors.push(trustFactor);

    await this.calculateTrustScore(agentId, factors);
  }

  async getTrustScore(agentId: string): Promise<number> {
    const trustScore = this.trustScores.get(agentId);
    return trustScore?.score || 0;
  }

  async getTrustLevel(agentId: string): Promise<string> {
    const score = await this.getTrustScore(agentId);
    
    if (score >= 0.9) return 'Gold';
    if (score >= 0.7) return 'Silver';
    if (score >= 0.5) return 'Bronze';
    return 'Untrusted';
  }

  private calculateComponents(factors: TrustFactor[]): TrustComponents {
    const components: TrustComponents = {
      direct: 0,
      reputation: 0,
      delegated: 0,
      system: 0
    };

    const componentFactors = {
      direct: ['user_assignment', 'admin_override', 'explicit_trust'],
      reputation: ['task_success_rate', 'error_frequency', 'user_feedback'],
      delegated: ['peer_endorsement', 'trust_delegation', 'certificate_chain'],
      system: ['audit_compliance', 'prompt_transparency', 'latency_metrics']
    };

    for (const [component, factorNames] of Object.entries(componentFactors)) {
      const relevantFactors = factors.filter(f => factorNames.includes(f.factor));
      if (relevantFactors.length > 0) {
        const weightedSum = relevantFactors.reduce((sum, f) => sum + (f.value * f.weight), 0);
        const totalWeight = relevantFactors.reduce((sum, f) => sum + f.weight, 0);
        components[component as keyof TrustComponents] = weightedSum / totalWeight;
      }
    }

    return components;
  }

  private computeWeightedScore(components: TrustComponents): number {
    const weights = {
      direct: 0.4,
      reputation: 0.3,
      delegated: 0.2,
      system: 0.1
    };

    return (
      components.direct * weights.direct +
      components.reputation * weights.reputation +
      components.delegated * weights.delegated +
      components.system * weights.system
    );
  }

  private initializeFactorWeights(): void {
    // Direct trust factors
    this.trustFactorWeights.set('user_assignment', 1.0);
    this.trustFactorWeights.set('admin_override', 1.0);
    this.trustFactorWeights.set('explicit_trust', 0.8);

    // Reputation factors
    this.trustFactorWeights.set('task_success_rate', 0.9);
    this.trustFactorWeights.set('error_frequency', 0.8);
    this.trustFactorWeights.set('user_feedback', 0.7);

    // Delegated trust factors
    this.trustFactorWeights.set('peer_endorsement', 0.6);
    this.trustFactorWeights.set('trust_delegation', 0.7);
    this.trustFactorWeights.set('certificate_chain', 0.8);

    // System factors
    this.trustFactorWeights.set('audit_compliance', 0.9);
    this.trustFactorWeights.set('prompt_transparency', 0.6);
    this.trustFactorWeights.set('latency_metrics', 0.4);
  }
}
```

## Authentication Protocols

```typescript
interface AuthenticationChallenge {
  challengeId: string;
  nonce: string;
  timestamp: string;
  expiresAt: string;
  requiredTrustLevel: number;
  signature: string;
}

interface AuthenticationResponse {
  challengeId: string;
  agentId: string;
  response: string;
  timestamp: string;
  signature: string;
}

interface AuthenticationResult {
  success: boolean;
  agentId: string;
  trustLevel: number;
  sessionToken?: string;
  expiresAt?: string;
  permissions: string[];
}

interface AuthenticationSession {
  sessionToken: string;
  agentId: string;
  trustLevel: number;
  permissions: string[];
  createdAt: string;
  expiresAt: string;
}

class AgentAuthenticationManager {
  private identityManager: AgentIdentityManager;
  private trustEngine: TrustScoringEngine;
  private activeChallenges: Map<string, AuthenticationChallenge> = new Map();
  private activeSessions: Map<string, AuthenticationSession> = new Map();

  constructor(identityManager: AgentIdentityManager, trustEngine: TrustScoringEngine) {
    this.identityManager = identityManager;
    this.trustEngine = trustEngine;
  }

  async createChallenge(requiredTrustLevel: number = 0.5): Promise<AuthenticationChallenge> {
    const challengeId = crypto.randomUUID();
    const nonce = crypto.randomUUID();
    const timestamp = new Date().toISOString();
    const expiresAt = new Date(Date.now() + 5 * 60 * 1000).toISOString(); // 5 minutes

    const challengeData = JSON.stringify({
      challengeId,
      nonce,
      timestamp,
      expiresAt,
      requiredTrustLevel
    });

    // Sign challenge with system key
    const signature = await this.signChallenge(challengeData);

    const challenge: AuthenticationChallenge = {
      challengeId,
      nonce,
      timestamp,
      expiresAt,
      requiredTrustLevel,
      signature
    };

    this.activeChallenges.set(challengeId, challenge);

    // Clean up expired challenges
    setTimeout(() => {
      this.activeChallenges.delete(challengeId);
    }, 5 * 60 * 1000);

    return challenge;
  }

  async respondToChallenge(
    challengeId: string,
    agentId: string,
    privateKey: CryptoKey
  ): Promise<AuthenticationResponse> {
    const challenge = this.activeChallenges.get(challengeId);
    if (!challenge) {
      throw new Error('Challenge not found or expired');
    }

    // Create response
    const responseData = JSON.stringify({
      challengeId,
      agentId,
      nonce: challenge.nonce,
      timestamp: new Date().toISOString()
    });

    // Sign response with agent's private key
    const signature = await crypto.subtle.sign(
      'Ed25519',
      privateKey,
      new TextEncoder().encode(responseData)
    );

    const signatureHex = Array.from(new Uint8Array(signature))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');

    return {
      challengeId,
      agentId,
      response: responseData,
      timestamp: new Date().toISOString(),
      signature: signatureHex
    };
  }

  async verifyAuthentication(response: AuthenticationResponse): Promise<AuthenticationResult> {
    const challenge = this.activeChallenges.get(response.challengeId);
    if (!challenge) {
      return {
        success: false,
        agentId: response.agentId,
        trustLevel: 0,
        permissions: []
      };
    }

    // Check if challenge is still valid
    if (new Date() > new Date(challenge.expiresAt)) {
      return {
        success: false,
        agentId: response.agentId,
        trustLevel: 0,
        permissions: []
      };
    }

    // Get agent identity
    const identity = await this.getAgentIdentity(response.agentId);
    if (!identity) {
      return {
        success: false,
        agentId: response.agentId,
        trustLevel: 0,
        permissions: []
      };
    }

    // Verify response signature
    const isValidSignature = await this.verifyResponseSignature(response, identity);
    if (!isValidSignature) {
      return {
        success: false,
        agentId: response.agentId,
        trustLevel: 0,
        permissions: []
      };
    }

    // Check trust level
    const trustLevel = await this.trustEngine.getTrustScore(response.agentId);
    if (trustLevel < challenge.requiredTrustLevel) {
      return {
        success: false,
        agentId: response.agentId,
        trustLevel,
        permissions: []
      };
    }

    // Create session
    const sessionToken = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(); // 24 hours

    const session: AuthenticationSession = {
      sessionToken,
      agentId: response.agentId,
      trustLevel,
      permissions: this.getPermissionsForTrustLevel(trustLevel),
      createdAt: new Date().toISOString(),
      expiresAt
    };

    this.activeSessions.set(sessionToken, session);

    // Clean up challenge
    this.activeChallenges.delete(response.challengeId);

    return {
      success: true,
      agentId: response.agentId,
      trustLevel,
      sessionToken,
      expiresAt,
      permissions: session.permissions
    };
  }

  async validateSession(sessionToken: string): Promise<AuthenticationSession | null> {
    const session = this.activeSessions.get(sessionToken);
    if (!session) return null;

    // Check expiration
    if (new Date() > new Date(session.expiresAt)) {
      this.activeSessions.delete(sessionToken);
      return null;
    }

    return session;
  }

  private async signChallenge(challengeData: string): Promise<string> {
    // In a real implementation, this would use a system key
    return 'system_signature';
  }

  private async getAgentIdentity(agentId: string): Promise<AgentIdentity | null> {
    // Implementation would retrieve from identity manager
    return null;
  }

  private async verifyResponseSignature(
    response: AuthenticationResponse,
    identity: AgentIdentity
  ): Promise<boolean> {
    try {
      // Extract public key from identity
      const publicKeyHex = identity.publicKey.replace('ED25519:', '');
      const publicKeyBytes = new Uint8Array(
        publicKeyHex.match(/.{2}/g)!.map(byte => parseInt(byte, 16))
      );

      const publicKey = await crypto.subtle.importKey(
        'raw',
        publicKeyBytes,
        { name: 'Ed25519', namedCurve: 'Ed25519' },
        false,
        ['verify']
      );

      // Verify signature
      const signatureBytes = new Uint8Array(
        response.signature.match(/.{2}/g)!.map(byte => parseInt(byte, 16))
      );

      return await crypto.subtle.verify(
        'Ed25519',
        publicKey,
        signatureBytes,
        new TextEncoder().encode(response.response)
      );
    } catch (error) {
      console.error('Signature verification failed:', error);
      return false;
    }
  }

  private getPermissionsForTrustLevel(trustLevel: number): string[] {
    const permissions: string[] = [];

    if (trustLevel >= 0.9) {
      // Gold level
      permissions.push('full_access', 'autonomous_execution', 'delegation', 'vault_access');
    } else if (trustLevel >= 0.7) {
      // Silver level
      permissions.push('monitored_execution', 'limited_vault_access', 'basic_delegation');
    } else if (trustLevel >= 0.5) {
      // Bronze level
      permissions.push('supervised_execution', 'read_only_access');
    }
    // Untrusted agents get no permissions

    return permissions;
  }
}
```

This comprehensive Agent Trust & Identity Protocol system provides the foundational security infrastructure for cryptographically verifiable agent identities, sophisticated trust scoring, secure authentication, and signed inter-agent communication across the kOS ecosystem. 