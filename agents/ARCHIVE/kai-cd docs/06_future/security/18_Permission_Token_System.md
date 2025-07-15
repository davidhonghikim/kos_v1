---
title: "Permission Token System - Fine-Grained Access Control"
last_updated: "2025-01-27"
version: "1.0"
status: "future"
complexity: "high"
decision_scope: "system-wide"
implementation_status: "specification"
code_references:
  - "permission-token.ts"
  - "permission-guard.ts"
  - "token-delegation.ts"
related_documents:
  - "documentation/future/security/17_agent-trust-reputation-system.md"
  - "documentation/future/services/32_service-registry-system.md"
  - "documentation/future/governance/07_comprehensive-governance-model.md"
external_references:
  - "https://tools.ietf.org/html/rfc7519"
  - "https://www.w3.org/TR/vc-data-model/"
  - "https://cbor.io/"
---

# Permission Token System - Fine-Grained Access Control

## Agent Context

This document specifies the Permission Token System (PTS) for AI agents operating within the kAI/kOS ecosystem. Agents should understand that this system enables secure, cryptographically verifiable fine-grained access control for all components. The PTS governs agent capabilities, service access, and resource permissions through time-bound, revocable, and delegable tokens with comprehensive audit trails and minimal authority principles.

## I. System Overview

The Permission Token System provides secure, cryptographically verifiable fine-grained access control for managing permissions across all components in the kAI/kOS ecosystem, preventing unauthorized actions while enabling scoped delegation and auditability.

### Core Objectives
- **Unauthorized Action Prevention**: Cryptographically secure access control preventing unauthorized operations
- **Scoped Delegation**: Enable secure delegation of authority with reduced scope
- **Time-Bound Permissions**: Provide time-constrained, revocable permissions with automatic expiry
- **Comprehensive Auditability**: Full audit trails of access grants, usage, and delegation chains

## II. Token Architecture

### A. Permission Token Structure

```typescript
interface PermissionToken {
  // JWT Standard Claims
  sub: string;              // Subject receiving the permission (agent-id)
  iss: string;              // Issuer authority (permission.kos)
  aud: string;              // Audience (target system/service)
  exp: number;              // Expiry timestamp (UTC epoch)
  nbf: number;              // Not before time
  iat: number;              // Issued at timestamp
  jti: string;              // Unique token identifier

  // Custom Permission Claims
  scope: PermissionScope[];  // Explicit action/resource permissions
  delegable: boolean;        // Can this token be delegated?
  delegation_depth: number;  // Maximum delegation chain depth
  context_constraints: ContextConstraint[];
  resource_limits: ResourceLimit[];
  audit_metadata: AuditMetadata;
  
  // Cryptographic Security
  signature: string;         // Token signature
  key_id: string;           // Signing key identifier
}

interface PermissionScope {
  action: string;           // e.g., "read", "write", "execute"
  resource: string;         // e.g., "vector:index", "prompt:agent-429x"
  conditions: ScopeCondition[];
  constraints: ScopeConstraint[];
}

interface ScopeCondition {
  condition_type: ConditionType;
  operator: ComparisonOperator;
  value: string | number | boolean;
  metadata?: Record<string, any>;
}

enum ConditionType {
  TIME_RANGE = "time_range",
  IP_ADDRESS = "ip_address",
  USER_ID = "user_id",
  DEVICE_FINGERPRINT = "device_fingerprint",
  TRUST_LEVEL = "trust_level",
  CONTEXT = "context"
}

enum ComparisonOperator {
  EQUALS = "eq",
  NOT_EQUALS = "ne",
  GREATER_THAN = "gt",
  LESS_THAN = "lt",
  IN = "in",
  NOT_IN = "not_in",
  MATCHES = "matches"
}

interface ContextConstraint {
  constraint_type: ConstraintType;
  constraint_value: string;
  enforcement_level: EnforcementLevel;
}

enum ConstraintType {
  NETWORK_ISOLATION = "network_isolation",
  SANDBOX_LEVEL = "sandbox_level",
  RESOURCE_QUOTA = "resource_quota",
  CONCURRENT_LIMIT = "concurrent_limit",
  RATE_LIMIT = "rate_limit"
}

enum EnforcementLevel {
  ADVISORY = "advisory",
  ENFORCED = "enforced",
  STRICT = "strict"
}

interface ResourceLimit {
  resource_type: ResourceType;
  limit_value: number;
  limit_unit: string;
  enforcement_action: EnforcementAction;
}

enum ResourceType {
  MEMORY = "memory",
  CPU = "cpu",
  STORAGE = "storage",
  NETWORK_BANDWIDTH = "network_bandwidth",
  API_CALLS = "api_calls",
  TOKEN_USAGE = "token_usage"
}

enum EnforcementAction {
  WARN = "warn",
  THROTTLE = "throttle",
  BLOCK = "block",
  TERMINATE = "terminate"
}

interface AuditMetadata {
  issuer_agent_id: string;
  request_id: string;
  delegation_chain: string[];
  purpose: string;
  approval_required: boolean;
  compliance_tags: string[];
}
```

### B. Token Management Engine

```typescript
class PermissionTokenEngine {
  private cryptoService: CryptographicService;
  private tokenStorage: TokenStorage;
  private revocationRegistry: RevocationRegistry;
  private delegationManager: DelegationManager;
  private auditLogger: AuditLogger;

  constructor(config: TokenEngineConfig) {
    this.cryptoService = new CryptographicService(config.crypto);
    this.tokenStorage = new TokenStorage(config.storage);
    this.revocationRegistry = new RevocationRegistry(config.revocation);
    this.delegationManager = new DelegationManager();
    this.auditLogger = new AuditLogger(config.audit);
  }

  async issueToken(request: TokenIssuanceRequest): Promise<IssuedToken> {
    // 1. Validate issuer authority
    await this.validateIssuerAuthority(request.issuer_id, request.requested_scope);

    // 2. Apply principle of least privilege
    const minimized_scope = await this.minimizeScope(request.requested_scope, request.purpose);

    // 3. Generate token claims
    const token_claims: PermissionToken = {
      sub: request.subject_id,
      iss: request.issuer_id,
      aud: request.audience,
      exp: this.calculateExpiry(request.validity_duration),
      nbf: Math.floor(Date.now() / 1000),
      iat: Math.floor(Date.now() / 1000),
      jti: this.generateTokenId(),
      scope: minimized_scope,
      delegable: request.delegable || false,
      delegation_depth: request.max_delegation_depth || 0,
      context_constraints: request.context_constraints || [],
      resource_limits: request.resource_limits || [],
      audit_metadata: {
        issuer_agent_id: request.issuer_id,
        request_id: request.request_id,
        delegation_chain: request.delegation_chain || [],
        purpose: request.purpose,
        approval_required: request.requires_approval || false,
        compliance_tags: request.compliance_tags || []
      },
      signature: "",
      key_id: this.cryptoService.getCurrentKeyId()
    };

    // 4. Sign token
    const signed_token = await this.cryptoService.signToken(token_claims);

    // 5. Store token metadata
    await this.tokenStorage.storeTokenMetadata(signed_token);

    // 6. Log issuance
    await this.auditLogger.logTokenIssuance(signed_token, request);

    return {
      token: signed_token,
      token_id: token_claims.jti,
      expires_at: new Date(token_claims.exp * 1000),
      scope_summary: this.summarizeScope(minimized_scope)
    };
  }

  async validateToken(token: string, required_action: string, resource: string, context: ValidationContext): Promise<TokenValidationResult> {
    try {
      // 1. Parse and verify token signature
      const token_claims = await this.cryptoService.verifyAndParseToken(token);

      // 2. Check time constraints
      const current_time = Math.floor(Date.now() / 1000);
      if (current_time < token_claims.nbf || current_time >= token_claims.exp) {
        return {
          valid: false,
          reason: "Token time constraints not met",
          error_code: "TOKEN_EXPIRED"
        };
      }

      // 3. Check revocation status
      const is_revoked = await this.revocationRegistry.isRevoked(token_claims.jti);
      if (is_revoked) {
        return {
          valid: false,
          reason: "Token has been revoked",
          error_code: "TOKEN_REVOKED"
        };
      }

      // 4. Validate audience
      if (token_claims.aud !== context.service_identifier) {
        return {
          valid: false,
          reason: "Token audience mismatch",
          error_code: "AUDIENCE_MISMATCH"
        };
      }

      // 5. Check scope permissions
      const scope_check = await this.validateScopePermission(
        token_claims.scope,
        required_action,
        resource,
        context
      );

      if (!scope_check.permitted) {
        return {
          valid: false,
          reason: scope_check.reason,
          error_code: "INSUFFICIENT_SCOPE"
        };
      }

      // 6. Validate context constraints
      const context_check = await this.validateContextConstraints(
        token_claims.context_constraints,
        context
      );

      if (!context_check.satisfied) {
        return {
          valid: false,
          reason: context_check.reason,
          error_code: "CONTEXT_CONSTRAINT_VIOLATION"
        };
      }

      // 7. Check resource limits
      const resource_check = await this.validateResourceLimits(
        token_claims.resource_limits,
        context
      );

      if (!resource_check.within_limits) {
        return {
          valid: false,
          reason: resource_check.reason,
          error_code: "RESOURCE_LIMIT_EXCEEDED"
        };
      }

      // 8. Log successful validation
      await this.auditLogger.logTokenUsage(token_claims, required_action, resource, context);

      return {
        valid: true,
        token_claims,
        remaining_uses: await this.calculateRemainingUses(token_claims),
        expires_in_seconds: token_claims.exp - current_time
      };

    } catch (error) {
      return {
        valid: false,
        reason: `Token validation error: ${error.message}`,
        error_code: "VALIDATION_ERROR"
      };
    }
  }

  async delegateToken(parent_token: string, delegation_request: TokenDelegationRequest): Promise<IssuedToken> {
    // 1. Validate parent token
    const parent_validation = await this.validateToken(
      parent_token,
      "delegate",
      "token",
      delegation_request.context
    );

    if (!parent_validation.valid) {
      throw new Error(`Parent token validation failed: ${parent_validation.reason}`);
    }

    const parent_claims = parent_validation.token_claims!;

    // 2. Check delegation permissions
    if (!parent_claims.delegable) {
      throw new Error("Parent token is not delegable");
    }

    if (parent_claims.delegation_depth <= 0) {
      throw new Error("Maximum delegation depth reached");
    }

    // 3. Ensure delegated scope is subset of parent scope
    const delegated_scope = await this.intersectScopes(
      parent_claims.scope,
      delegation_request.requested_scope
    );

    if (delegated_scope.length === 0) {
      throw new Error("Requested delegation scope exceeds parent token permissions");
    }

    // 4. Create delegated token
    const delegation_token_request: TokenIssuanceRequest = {
      issuer_id: parent_claims.sub,
      subject_id: delegation_request.delegatee_id,
      audience: parent_claims.aud,
      requested_scope: delegated_scope,
      validity_duration: Math.min(
        delegation_request.validity_duration,
        parent_claims.exp - Math.floor(Date.now() / 1000)
      ),
      delegable: delegation_request.allow_further_delegation && parent_claims.delegation_depth > 1,
      max_delegation_depth: parent_claims.delegation_depth - 1,
      context_constraints: delegation_request.additional_constraints || [],
      resource_limits: delegation_request.resource_limits || parent_claims.resource_limits,
      purpose: delegation_request.purpose,
      delegation_chain: [...parent_claims.audit_metadata.delegation_chain, parent_claims.sub],
      request_id: delegation_request.request_id
    };

    const delegated_token = await this.issueToken(delegation_token_request);

    // 5. Log delegation
    await this.auditLogger.logTokenDelegation(parent_claims, delegated_token, delegation_request);

    return delegated_token;
  }

  async revokeToken(token_id: string, revocation_request: TokenRevocationRequest): Promise<RevocationResult> {
    // 1. Validate revocation authority
    const token_metadata = await this.tokenStorage.getTokenMetadata(token_id);
    if (!token_metadata) {
      throw new Error(`Token not found: ${token_id}`);
    }

    await this.validateRevocationAuthority(revocation_request.revoker_id, token_metadata);

    // 2. Add to revocation registry
    const revocation_entry: RevocationEntry = {
      token_id,
      revoked_at: new Date(),
      revoked_by: revocation_request.revoker_id,
      reason: revocation_request.reason,
      revocation_type: revocation_request.revocation_type
    };

    await this.revocationRegistry.addRevocation(revocation_entry);

    // 3. Revoke delegated tokens if requested
    if (revocation_request.revoke_delegated) {
      const delegated_tokens = await this.tokenStorage.findDelegatedTokens(token_id);
      for (const delegated_token of delegated_tokens) {
        await this.revokeToken(delegated_token.token_id, {
          revoker_id: revocation_request.revoker_id,
          reason: `Parent token ${token_id} revoked`,
          revocation_type: RevocationType.CASCADE,
          revoke_delegated: true
        });
      }
    }

    // 4. Log revocation
    await this.auditLogger.logTokenRevocation(token_metadata, revocation_request);

    return {
      token_id,
      revoked: true,
      revoked_at: revocation_entry.revoked_at,
      delegated_tokens_revoked: revocation_request.revoke_delegated ? 
        await this.tokenStorage.countDelegatedTokens(token_id) : 0
    };
  }

  private async validateScopePermission(
    token_scope: PermissionScope[],
    required_action: string,
    resource: string,
    context: ValidationContext
  ): Promise<ScopeValidationResult> {
    for (const scope of token_scope) {
      // Check if action matches
      if (!this.actionMatches(scope.action, required_action)) {
        continue;
      }

      // Check if resource matches
      if (!this.resourceMatches(scope.resource, resource)) {
        continue;
      }

      // Check scope conditions
      const conditions_met = await this.evaluateScopeConditions(scope.conditions, context);
      if (!conditions_met.satisfied) {
        continue;
      }

      // Check scope constraints
      const constraints_met = await this.evaluateScopeConstraints(scope.constraints, context);
      if (!constraints_met.satisfied) {
        continue;
      }

      return {
        permitted: true,
        matching_scope: scope
      };
    }

    return {
      permitted: false,
      reason: `No matching scope found for action '${required_action}' on resource '${resource}'`
    };
  }
}

interface TokenIssuanceRequest {
  issuer_id: string;
  subject_id: string;
  audience: string;
  requested_scope: PermissionScope[];
  validity_duration: number; // seconds
  delegable?: boolean;
  max_delegation_depth?: number;
  context_constraints?: ContextConstraint[];
  resource_limits?: ResourceLimit[];
  purpose: string;
  delegation_chain?: string[];
  request_id: string;
  requires_approval?: boolean;
  compliance_tags?: string[];
}

interface IssuedToken {
  token: string;
  token_id: string;
  expires_at: Date;
  scope_summary: string;
}

interface TokenValidationResult {
  valid: boolean;
  reason?: string;
  error_code?: string;
  token_claims?: PermissionToken;
  remaining_uses?: number;
  expires_in_seconds?: number;
}

interface ValidationContext {
  service_identifier: string;
  request_ip?: string;
  user_agent?: string;
  device_fingerprint?: string;
  trust_level?: number;
  resource_usage?: ResourceUsage;
  timestamp: Date;
}
```

### C. Permission Guard Implementation

```typescript
class PermissionGuard {
  private tokenEngine: PermissionTokenEngine;
  private cacheManager: CacheManager;

  constructor(tokenEngine: PermissionTokenEngine) {
    this.tokenEngine = tokenEngine;
    this.cacheManager = new CacheManager();
  }

  async verifyPermission(
    token: string,
    action: string,
    resource: string,
    context: ValidationContext
  ): Promise<PermissionVerificationResult> {
    // 1. Check cache first
    const cache_key = this.generateCacheKey(token, action, resource);
    const cached_result = await this.cacheManager.get(cache_key);
    
    if (cached_result && !this.isCacheExpired(cached_result)) {
      return cached_result;
    }

    // 2. Validate token
    const validation_result = await this.tokenEngine.validateToken(token, action, resource, context);

    // 3. Cache result (with appropriate TTL)
    if (validation_result.valid) {
      const cache_ttl = Math.min(
        validation_result.expires_in_seconds!,
        this.getDefaultCacheTTL()
      );
      
      await this.cacheManager.set(cache_key, validation_result, cache_ttl);
    }

    return {
      permitted: validation_result.valid,
      token_id: validation_result.token_claims?.jti,
      expires_at: validation_result.token_claims ? 
        new Date(validation_result.token_claims.exp * 1000) : undefined,
      reason: validation_result.reason,
      error_code: validation_result.error_code
    };
  }

  // Decorator for automatic permission checking
  requiresPermission(action: string, resource: string) {
    return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
      const method = descriptor.value;

      descriptor.value = async function (...args: any[]) {
        const context = this.extractValidationContext(args);
        const token = this.extractToken(args);

        const permission_result = await this.permissionGuard.verifyPermission(
          token,
          action,
          resource,
          context
        );

        if (!permission_result.permitted) {
          throw new PermissionDeniedError(
            `Access denied: ${permission_result.reason}`,
            permission_result.error_code
          );
        }

        return method.apply(this, args);
      };
    };
  }
}

interface PermissionVerificationResult {
  permitted: boolean;
  token_id?: string;
  expires_at?: Date;
  reason?: string;
  error_code?: string;
}

class PermissionDeniedError extends Error {
  constructor(message: string, public errorCode?: string) {
    super(message);
    this.name = 'PermissionDeniedError';
  }
}

// Example usage with decorator
class SecureService {
  constructor(private permissionGuard: PermissionGuard) {}

  @requiresPermission("read", "vector:index")
  async readVectorIndex(token: string, index_id: string): Promise<VectorIndex> {
    // Method implementation
    return this.vectorStore.getIndex(index_id);
  }

  @requiresPermission("write", "prompt:{{agent_id}}")
  async updatePrompt(token: string, agent_id: string, prompt_content: string): Promise<void> {
    // Method implementation with dynamic resource resolution
    await this.promptManager.updatePrompt(agent_id, prompt_content);
  }
}
```

## III. Delegation and Authority Management

### A. Token Delegation Framework

```typescript
class DelegationManager {
  async createDelegationChain(
    root_authority: string,
    delegation_requests: DelegationRequest[]
  ): Promise<DelegationChain> {
    const delegation_chain: DelegationLink[] = [];
    let current_authority = root_authority;
    let current_scope = await this.getAuthorityScope(root_authority);

    for (const request of delegation_requests) {
      // Validate delegation authority
      if (current_authority !== request.delegator_id) {
        throw new Error(`Invalid delegation authority: expected ${current_authority}, got ${request.delegator_id}`);
      }

      // Ensure requested scope is subset of current scope
      const delegated_scope = await this.intersectScopes(current_scope, request.requested_scope);
      if (delegated_scope.length === 0) {
        throw new Error("Requested delegation scope exceeds current authority");
      }

      // Create delegation link
      const delegation_link: DelegationLink = {
        delegator_id: current_authority,
        delegatee_id: request.delegatee_id,
        delegated_scope,
        delegation_timestamp: new Date(),
        delegation_reason: request.reason,
        delegation_constraints: request.constraints || [],
        signature: await this.signDelegation(current_authority, request)
      };

      delegation_chain.push(delegation_link);

      // Update for next iteration
      current_authority = request.delegatee_id;
      current_scope = delegated_scope;
    }

    return {
      chain_id: this.generateChainId(),
      root_authority,
      delegation_links: delegation_chain,
      final_authority: current_authority,
      final_scope: current_scope,
      created_at: new Date()
    };
  }

  async validateDelegationChain(chain: DelegationChain): Promise<ChainValidationResult> {
    const validation_results: LinkValidationResult[] = [];
    let current_scope = await this.getAuthorityScope(chain.root_authority);

    for (const link of chain.delegation_links) {
      // Validate delegation signature
      const signature_valid = await this.validateDelegationSignature(link);
      if (!signature_valid) {
        validation_results.push({
          link,
          valid: false,
          reason: "Invalid delegation signature"
        });
        continue;
      }

      // Validate scope subset
      const scope_valid = await this.validateScopeSubset(current_scope, link.delegated_scope);
      if (!scope_valid) {
        validation_results.push({
          link,
          valid: false,
          reason: "Delegated scope exceeds delegator authority"
        });
        continue;
      }

      // Validate constraints
      const constraints_valid = await this.validateDelegationConstraints(link.delegation_constraints);
      if (!constraints_valid.valid) {
        validation_results.push({
          link,
          valid: false,
          reason: constraints_valid.reason
        });
        continue;
      }

      validation_results.push({
        link,
        valid: true
      });

      current_scope = link.delegated_scope;
    }

    const all_valid = validation_results.every(result => result.valid);
    
    return {
      chain,
      valid: all_valid,
      link_results: validation_results,
      effective_scope: all_valid ? current_scope : [],
      validation_timestamp: new Date()
    };
  }
}

interface DelegationChain {
  chain_id: string;
  root_authority: string;
  delegation_links: DelegationLink[];
  final_authority: string;
  final_scope: PermissionScope[];
  created_at: Date;
}

interface DelegationLink {
  delegator_id: string;
  delegatee_id: string;
  delegated_scope: PermissionScope[];
  delegation_timestamp: Date;
  delegation_reason: string;
  delegation_constraints: DelegationConstraint[];
  signature: string;
}

interface DelegationConstraint {
  constraint_type: string;
  constraint_value: any;
  enforcement_level: EnforcementLevel;
}
```

## IV. CLI and Management Tools

### A. Token Management CLI

```typescript
class PermissionTokenCLI {
  async issueToken(options: CLITokenOptions): Promise<void> {
    const request: TokenIssuanceRequest = {
      issuer_id: options.issuer_id,
      subject_id: options.subject_id,
      audience: options.audience,
      requested_scope: this.parseScope(options.scope),
      validity_duration: this.parseDuration(options.duration),
      delegable: options.delegable || false,
      purpose: options.purpose,
      request_id: this.generateRequestId()
    };

    const issued_token = await this.tokenEngine.issueToken(request);
    
    console.log(`Token issued successfully:`);
    console.log(`Token ID: ${issued_token.token_id}`);
    console.log(`Expires: ${issued_token.expires_at.toISOString()}`);
    console.log(`Scope: ${issued_token.scope_summary}`);
    
    if (options.output_file) {
      await this.writeTokenToFile(options.output_file, issued_token.token);
    } else {
      console.log(`Token: ${issued_token.token}`);
    }
  }

  async verifyToken(token: string, action: string, resource: string): Promise<void> {
    const context: ValidationContext = {
      service_identifier: "cli-verification",
      timestamp: new Date()
    };

    const result = await this.tokenEngine.validateToken(token, action, resource, context);
    
    if (result.valid) {
      console.log(`✅ Token is valid`);
      console.log(`Subject: ${result.token_claims!.sub}`);
      console.log(`Expires in: ${result.expires_in_seconds} seconds`);
      console.log(`Remaining uses: ${result.remaining_uses || 'unlimited'}`);
    } else {
      console.log(`❌ Token validation failed: ${result.reason}`);
      console.log(`Error code: ${result.error_code}`);
    }
  }

  async listTokens(options: ListTokenOptions): Promise<void> {
    const tokens = await this.tokenStorage.findTokens({
      subject_id: options.subject_id,
      issuer_id: options.issuer_id,
      status: options.status,
      limit: options.limit || 20
    });

    console.log(`\nFound ${tokens.length} tokens:`);
    console.log("=".repeat(80));
    
    for (const token of tokens) {
      const status = await this.getTokenStatus(token);
      console.log(`${token.token_id}: ${token.subject_id} -> ${token.audience}`);
      console.log(`  Status: ${status} | Expires: ${new Date(token.exp * 1000).toISOString()}`);
      console.log(`  Scope: ${this.summarizeScope(token.scope)}`);
      console.log("");
    }
  }

  async revokeToken(token_id: string, reason: string): Promise<void> {
    const revocation_request: TokenRevocationRequest = {
      revoker_id: await this.getCurrentUserId(),
      reason,
      revocation_type: RevocationType.MANUAL,
      revoke_delegated: true
    };

    const result = await this.tokenEngine.revokeToken(token_id, revocation_request);
    
    console.log(`✅ Token ${token_id} revoked successfully`);
    console.log(`Delegated tokens revoked: ${result.delegated_tokens_revoked}`);
  }
}
```

## V. Implementation Status

- **Core Token Engine**: Architecture complete, cryptographic implementation required
- **Permission Guard**: Validation framework specified, caching optimization needed
- **Delegation Manager**: Chain validation system designed, signature verification implementation required
- **Revocation Registry**: Revocation framework defined, distributed storage integration needed
- **CLI Tools**: Management interface complete, file I/O implementation required

This permission token system provides comprehensive fine-grained access control with delegation capabilities essential for secure multi-agent operations within the kAI/kOS ecosystem. 