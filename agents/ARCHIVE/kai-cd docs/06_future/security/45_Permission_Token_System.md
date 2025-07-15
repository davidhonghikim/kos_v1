---
title: "Permission Token System"
description: "Capability-based access control using cryptographic tokens"
type: "security"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["kid-identity-core.md", "trust-frameworks.md"]
implementation_status: "planned"
---

# Permission Token System

## Agent Context
Capability-based access control system using cryptographic tokens for fine-grained permission management across distributed agent networks.

## Token Architecture

```typescript
interface PermissionToken {
  id: string;
  issuer: string; // kID of token issuer
  subject: string; // kID of token holder
  capabilities: Capability[];
  constraints: Constraint[];
  signature: string;
  issued: string;
  expires: string;
  nonce: string;
}

interface Capability {
  resource: string; // Resource identifier
  actions: string[]; // Allowed actions
  scope: string; // Access scope
  delegation: boolean; // Can be delegated
}

interface Constraint {
  type: 'time' | 'location' | 'context' | 'usage';
  parameters: Record<string, any>;
  enforced: boolean;
}
```

## Token Manager

```typescript
class PermissionTokenManager {
  async issueToken(
    issuer: string,
    subject: string,
    capabilities: Capability[],
    constraints: Constraint[] = []
  ): Promise<PermissionToken> {
    // Verify issuer authority
    const canIssue = await this.verifyIssuerAuthority(issuer, capabilities);
    if (!canIssue) {
      throw new Error('Issuer lacks authority for requested capabilities');
    }

    const token: PermissionToken = {
      id: `perm:${crypto.randomUUID()}`,
      issuer,
      subject,
      capabilities,
      constraints,
      signature: '', // Will be set below
      issued: new Date().toISOString(),
      expires: new Date(Date.now() + 3600000).toISOString(), // 1 hour default
      nonce: crypto.randomUUID()
    };

    token.signature = await this.signToken(token, issuer);
    
    await this.storeToken(token);
    return token;
  }

  async verifyToken(token: PermissionToken): Promise<TokenVerificationResult> {
    try {
      // 1. Verify signature
      const signatureValid = await this.verifyTokenSignature(token);
      if (!signatureValid) {
        return { valid: false, reason: 'Invalid signature' };
      }

      // 2. Check expiration
      if (new Date() > new Date(token.expires)) {
        return { valid: false, reason: 'Token expired' };
      }

      // 3. Verify issuer authority
      const issuerValid = await this.verifyIssuerAuthority(token.issuer, token.capabilities);
      if (!issuerValid) {
        return { valid: false, reason: 'Issuer lacks authority' };
      }

      // 4. Check constraints
      const constraintsValid = await this.validateConstraints(token);
      if (!constraintsValid.valid) {
        return { valid: false, reason: constraintsValid.reason };
      }

      return { valid: true };

    } catch (error) {
      return { valid: false, reason: `Verification error: ${error.message}` };
    }
  }

  async checkPermission(
    token: PermissionToken,
    resource: string,
    action: string
  ): Promise<boolean> {
    const verification = await this.verifyToken(token);
    if (!verification.valid) {
      return false;
    }

    // Check if token grants requested permission
    for (const capability of token.capabilities) {
      if (this.matchesResource(capability.resource, resource) &&
          capability.actions.includes(action)) {
        return true;
      }
    }

    return false;
  }

  private async signToken(token: PermissionToken, issuerId: string): Promise<string> {
    const privateKey = await this.getPrivateKey(issuerId);
    const tokenData = {
      id: token.id,
      issuer: token.issuer,
      subject: token.subject,
      capabilities: token.capabilities,
      constraints: token.constraints,
      issued: token.issued,
      expires: token.expires,
      nonce: token.nonce
    };

    const message = new TextEncoder().encode(JSON.stringify(tokenData));
    const signature = await crypto.subtle.sign('Ed25519', privateKey, message);
    
    return base64.encode(new Uint8Array(signature));
  }
}
```

## Delegation System

```typescript
class TokenDelegationManager {
  async delegateToken(
    originalToken: PermissionToken,
    delegatee: string,
    restrictions?: Capability[]
  ): Promise<PermissionToken> {
    // Verify delegation is allowed
    const canDelegate = originalToken.capabilities.every(cap => cap.delegation);
    if (!canDelegate) {
      throw new Error('Token does not allow delegation');
    }

    // Apply restrictions if provided
    let delegatedCapabilities = originalToken.capabilities;
    if (restrictions) {
      delegatedCapabilities = this.applyRestrictions(
        originalToken.capabilities,
        restrictions
      );
    }

    // Create delegated token
    const delegatedToken: PermissionToken = {
      id: `perm:${crypto.randomUUID()}`,
      issuer: originalToken.subject, // Delegator becomes issuer
      subject: delegatee,
      capabilities: delegatedCapabilities,
      constraints: [
        ...originalToken.constraints,
        {
          type: 'context',
          parameters: { delegatedFrom: originalToken.id },
          enforced: true
        }
      ],
      signature: '',
      issued: new Date().toISOString(),
      expires: originalToken.expires, // Cannot exceed original expiration
      nonce: crypto.randomUUID()
    };

    delegatedToken.signature = await this.signToken(delegatedToken, originalToken.subject);
    
    await this.recordDelegation(originalToken.id, delegatedToken.id);
    return delegatedToken;
  }

  async revokeDelegation(
    originalTokenId: string,
    delegatedTokenId: string,
    revoker: string
  ): Promise<void> {
    const originalToken = await this.getToken(originalTokenId);
    if (!originalToken || originalToken.subject !== revoker) {
      throw new Error('Unauthorized revocation attempt');
    }

    // Add to revocation list
    await this.addToRevocationList(delegatedTokenId);
    
    // Notify relevant parties
    await this.notifyRevocation(delegatedTokenId);
  }
}
```

## Enforcement Engine

```typescript
class PermissionEnforcementEngine {
  async enforcePermission(
    token: PermissionToken,
    request: AccessRequest
  ): Promise<EnforcementResult> {
    // 1. Verify token
    const tokenValid = await this.tokenManager.verifyToken(token);
    if (!tokenValid.valid) {
      return {
        allowed: false,
        reason: `Token invalid: ${tokenValid.reason}`,
        audit: this.createAuditLog(token, request, 'DENIED')
      };
    }

    // 2. Check permission
    const hasPermission = await this.tokenManager.checkPermission(
      token,
      request.resource,
      request.action
    );

    if (!hasPermission) {
      return {
        allowed: false,
        reason: 'Insufficient permissions',
        audit: this.createAuditLog(token, request, 'DENIED')
      };
    }

    // 3. Apply rate limiting
    const rateLimitOk = await this.checkRateLimit(token, request);
    if (!rateLimitOk) {
      return {
        allowed: false,
        reason: 'Rate limit exceeded',
        audit: this.createAuditLog(token, request, 'RATE_LIMITED')
      };
    }

    // 4. Log successful access
    const audit = this.createAuditLog(token, request, 'ALLOWED');
    await this.recordAccess(audit);

    return {
      allowed: true,
      audit
    };
  }

  private createAuditLog(
    token: PermissionToken,
    request: AccessRequest,
    result: string
  ): AuditLog {
    return {
      timestamp: new Date().toISOString(),
      tokenId: token.id,
      subject: token.subject,
      resource: request.resource,
      action: request.action,
      result,
      context: request.context || {}
    };
  }
}
```
