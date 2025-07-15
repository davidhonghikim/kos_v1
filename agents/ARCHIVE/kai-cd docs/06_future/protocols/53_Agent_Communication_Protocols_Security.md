---
title: "Agent Communication Protocols - Security"
description: "Security layers for agent communication including encryption and authentication"
type: "protocol"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["agent-communication-protocols-core.md", "kid-identity-core.md"]
implementation_status: "planned"
---

# Agent Communication Protocols - Security

## Agent Context
Security implementation for agent communication including end-to-end encryption, message authentication, and secure channel establishment.

## Security Architecture

```typescript
interface SecurityLayer {
  encryption: EncryptionConfig;
  authentication: AuthenticationConfig;
  integrity: IntegrityConfig;
  authorization: AuthorizationConfig;
}

interface EncryptionConfig {
  algorithm: 'AES-256-GCM' | 'ChaCha20-Poly1305';
  keyExchange: 'ECDH' | 'X25519';
  keyRotation: boolean;
  rotationInterval: number; // seconds
}

interface AuthenticationConfig {
  method: 'signature' | 'hmac' | 'certificate';
  algorithm: 'Ed25519' | 'ECDSA-P256' | 'RSA-PSS';
  requireMutual: boolean;
}

interface SecureChannel {
  id: string;
  participants: string[]; // Agent kIDs
  encryptionKey: CryptoKey;
  authenticationKey: CryptoKey;
  nonce: Uint8Array;
  established: string;
  expires: string;
}
```

## Secure Channel Manager

```typescript
class SecureChannelManager {
  private channels: Map<string, SecureChannel>;
  private keyStore: Map<string, CryptoKey>;

  async establishSecureChannel(
    localId: string,
    remoteId: string
  ): Promise<SecureChannel> {
    // 1. Perform key exchange
    const keyExchange = await this.performKeyExchange(localId, remoteId);
    
    // 2. Derive encryption and authentication keys
    const keys = await this.deriveKeys(keyExchange.sharedSecret);
    
    // 3. Create secure channel
    const channel: SecureChannel = {
      id: `channel:${crypto.randomUUID()}`,
      participants: [localId, remoteId],
      encryptionKey: keys.encryptionKey,
      authenticationKey: keys.authenticationKey,
      nonce: crypto.getRandomValues(new Uint8Array(12)),
      established: new Date().toISOString(),
      expires: new Date(Date.now() + 3600000).toISOString() // 1 hour
    };

    this.channels.set(channel.id, channel);
    return channel;
  }

  async encryptMessage(
    message: AgentMessage,
    channelId: string
  ): Promise<EncryptedMessage> {
    const channel = this.channels.get(channelId);
    if (!channel) {
      throw new Error('Secure channel not found');
    }

    // Serialize message
    const messageData = new TextEncoder().encode(JSON.stringify(message));
    
    // Encrypt with AES-GCM
    const encrypted = await crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv: channel.nonce
      },
      channel.encryptionKey,
      messageData
    );

    // Generate authentication tag
    const authTag = await this.generateAuthTag(
      new Uint8Array(encrypted),
      channel.authenticationKey
    );

    return {
      channelId,
      encryptedData: Array.from(new Uint8Array(encrypted)),
      authTag: Array.from(authTag),
      nonce: Array.from(channel.nonce),
      timestamp: new Date().toISOString()
    };
  }

  async decryptMessage(
    encryptedMessage: EncryptedMessage
  ): Promise<AgentMessage> {
    const channel = this.channels.get(encryptedMessage.channelId);
    if (!channel) {
      throw new Error('Secure channel not found');
    }

    // Verify authentication tag
    const authValid = await this.verifyAuthTag(
      new Uint8Array(encryptedMessage.encryptedData),
      new Uint8Array(encryptedMessage.authTag),
      channel.authenticationKey
    );

    if (!authValid) {
      throw new Error('Message authentication failed');
    }

    // Decrypt message
    const decrypted = await crypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv: new Uint8Array(encryptedMessage.nonce)
      },
      channel.encryptionKey,
      new Uint8Array(encryptedMessage.encryptedData)
    );

    const messageText = new TextDecoder().decode(decrypted);
    return JSON.parse(messageText);
  }

  private async performKeyExchange(
    localId: string,
    remoteId: string
  ): Promise<KeyExchangeResult> {
    // Generate ephemeral key pair
    const localKeyPair = await crypto.subtle.generateKey(
      {
        name: 'ECDH',
        namedCurve: 'P-256'
      },
      false,
      ['deriveKey']
    );

    // Get remote public key
    const remotePublicKey = await this.getRemotePublicKey(remoteId);

    // Derive shared secret
    const sharedSecret = await crypto.subtle.deriveKey(
      {
        name: 'ECDH',
        public: remotePublicKey
      },
      localKeyPair.privateKey,
      {
        name: 'AES-GCM',
        length: 256
      },
      false,
      ['encrypt', 'decrypt']
    );

    return {
      sharedSecret,
      localPublicKey: localKeyPair.publicKey,
      remotePublicKey
    };
  }

  private async deriveKeys(sharedSecret: CryptoKey): Promise<DerivedKeys> {
    // Derive encryption key
    const encryptionKey = await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: new TextEncoder().encode('encryption'),
        iterations: 100000,
        hash: 'SHA-256'
      },
      sharedSecret,
      {
        name: 'AES-GCM',
        length: 256
      },
      false,
      ['encrypt', 'decrypt']
    );

    // Derive authentication key
    const authenticationKey = await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: new TextEncoder().encode('authentication'),
        iterations: 100000,
        hash: 'SHA-256'
      },
      sharedSecret,
      {
        name: 'HMAC',
        hash: 'SHA-256'
      },
      false,
      ['sign', 'verify']
    );

    return { encryptionKey, authenticationKey };
  }
}
```

## Message Authentication

```typescript
class MessageAuthenticator {
  async signMessage(
    message: AgentMessage,
    privateKey: CryptoKey
  ): Promise<string> {
    // Create canonical representation
    const canonical = this.canonicalizeMessage(message);
    const messageData = new TextEncoder().encode(canonical);

    // Sign with Ed25519
    const signature = await crypto.subtle.sign(
      'Ed25519',
      privateKey,
      messageData
    );

    return base64.encode(new Uint8Array(signature));
  }

  async verifySignature(
    message: AgentMessage,
    signature: string,
    publicKey: CryptoKey
  ): Promise<boolean> {
    try {
      const canonical = this.canonicalizeMessage(message);
      const messageData = new TextEncoder().encode(canonical);
      const signatureBytes = base64.decode(signature);

      return await crypto.subtle.verify(
        'Ed25519',
        publicKey,
        signatureBytes,
        messageData
      );
    } catch (error) {
      console.error('Signature verification failed:', error);
      return false;
    }
  }

  private canonicalizeMessage(message: AgentMessage): string {
    // Create deterministic representation for signing
    const canonical = {
      id: message.id,
      protocol: message.protocol,
      version: message.version,
      source: message.source,
      destination: message.destination,
      type: message.type,
      payload: message.payload,
      timestamp: message.timestamp
    };

    return JSON.stringify(canonical, Object.keys(canonical).sort());
  }
}
```

## Authorization Engine

```typescript
class CommunicationAuthorizationEngine {
  private policies: Map<string, AuthorizationPolicy>;
  private permissionTokens: Map<string, PermissionToken>;

  async authorizeMessage(
    message: AgentMessage,
    context: AuthorizationContext
  ): Promise<AuthorizationResult> {
    try {
      // 1. Get applicable policies
      const policies = await this.getApplicablePolicies(message, context);
      
      // 2. Check each policy
      for (const policy of policies) {
        const result = await this.evaluatePolicy(policy, message, context);
        if (!result.allowed) {
          return {
            allowed: false,
            reason: result.reason,
            policy: policy.id
          };
        }
      }

      // 3. Check permission tokens if required
      if (this.requiresPermissionToken(message)) {
        const tokenResult = await this.verifyPermissionToken(message, context);
        if (!tokenResult.valid) {
          return {
            allowed: false,
            reason: 'Invalid or missing permission token',
            policy: 'token_requirement'
          };
        }
      }

      return { allowed: true };

    } catch (error) {
      return {
        allowed: false,
        reason: `Authorization error: ${error.message}`,
        policy: 'error'
      };
    }
  }

  private async evaluatePolicy(
    policy: AuthorizationPolicy,
    message: AgentMessage,
    context: AuthorizationContext
  ): Promise<PolicyEvaluationResult> {
    // Evaluate conditions
    for (const condition of policy.conditions) {
      const result = await this.evaluateCondition(condition, message, context);
      if (!result) {
        return {
          allowed: false,
          reason: `Policy condition failed: ${condition.description}`
        };
      }
    }

    // Check action permissions
    if (policy.allowedActions && policy.allowedActions.length > 0) {
      const actionAllowed = policy.allowedActions.includes(message.type);
      if (!actionAllowed) {
        return {
          allowed: false,
          reason: `Action '${message.type}' not allowed by policy`
        };
      }
    }

    // Check resource permissions
    if (policy.resourcePatterns && policy.resourcePatterns.length > 0) {
      const resourceAllowed = policy.resourcePatterns.some(pattern =>
        this.matchesPattern(message.destination, pattern)
      );
      
      if (!resourceAllowed) {
        return {
          allowed: false,
          reason: 'Resource access not allowed by policy'
        };
      }
    }

    return { allowed: true };
  }

  private async evaluateCondition(
    condition: PolicyCondition,
    message: AgentMessage,
    context: AuthorizationContext
  ): Promise<boolean> {
    switch (condition.type) {
      case 'time_range':
        return this.evaluateTimeRange(condition.parameters, context.timestamp);
      
      case 'reputation_threshold':
        const reputation = await this.getAgentReputation(message.source);
        return reputation >= condition.parameters.threshold;
      
      case 'trust_level':
        const trustLevel = await this.getTrustLevel(message.source, message.destination);
        return trustLevel >= condition.parameters.minimum;
      
      case 'rate_limit':
        return await this.checkRateLimit(message.source, condition.parameters);
      
      default:
        console.warn(`Unknown condition type: ${condition.type}`);
        return false;
    }
  }
}
```
