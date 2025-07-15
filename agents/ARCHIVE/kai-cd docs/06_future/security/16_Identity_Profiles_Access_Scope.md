---
version: "1.0.0"
last_updated: "2025-01-27"
status: "draft"
type: "specification"
category: "security"
tags: ["identity", "profiles", "access", "scope", "rbac", "personas"]
related_docs:
  - "future/security/13_agent-trust-identity-protocols.md"
  - "future/security/15_consent-ledger-user-override.md"
  - "future/governance/07_comprehensive-governance-model.md"
complexity: "high"
implementation_status: "planned"
code_references:
  - "src/utils/identityManager.ts"
  - "src/store/identityStore.ts"
  - "src/components/identity/"
decision_scope: "system-wide"
external_references:
  - "https://www.w3.org/TR/did-core/"
  - "https://tools.ietf.org/html/rfc7519"
  - "https://datatracker.ietf.org/doc/html/rfc6749"
changelog:
  - "2025-01-27: Initial migration from brainstorm file 176"
---

# Identity Profiles and Access Scope System

**Agent Context**: This document defines the comprehensive identity modeling, session scoping, and dynamic access resolution logic for user profiles, roles, agents, and AI personas across the Kind AI (kAI) and Kind OS (kOS) ecosystem. Agents should understand this as the foundational identity infrastructure that enables context-specific capabilities, hierarchical permissions, and persona-aware interactions with full audit trails and federation support.

## System Architecture Overview

The Identity Profiles and Access Scope System provides:
- Comprehensive identity modeling for all actor types (human, agent, org, service)
- Dynamic session scoping with role resolution and inheritance
- Context-specific persona overlays and behavioral encoding
- Real-time access control with policy enforcement
- Federation protocols for cross-system identity synchronization

## Core Identity Model

```typescript
enum IdentityKind {
  HUMAN = 'human',
  AGENT = 'agent',
  ORG = 'org',
  SERVICE = 'service'
}

interface IdentityProfile {
  id: string;
  kind: IdentityKind;
  label: string;
  aliases: string[];
  parent?: string;
  createdAt: string;
  lastUpdated: string;
  verified: boolean;
  keys: IdentityKeys;
  permissions: string[];
  personaOverlays?: PersonaOverlay[];
  trustScore: number;
  auditLogRefs: string[];
  metadata: IdentityMetadata;
}

interface IdentityKeys {
  pgp?: string;
  jwtSigning?: string;
  walletAddr?: string;
  ed25519?: string;
  webauthn?: WebAuthnCredential[];
}

interface WebAuthnCredential {
  credentialId: string;
  publicKey: string;
  counter: number;
  transports: string[];
  createdAt: string;
}

interface PersonaOverlay {
  id: string;
  name: string;
  description: string;
  traits: Record<string, any>;
  stylePrompt: string;
  behaviorModifiers: BehaviorModifier[];
  timeBound: boolean;
  expiresAt?: string;
  activeContexts: string[];
}

interface BehaviorModifier {
  type: 'tone' | 'verbosity' | 'formality' | 'expertise' | 'caution';
  value: number; // -1 to 1 scale
  conditions: string[];
}

interface IdentityMetadata {
  displayName?: string;
  avatar?: string;
  bio?: string;
  location?: string;
  timezone?: string;
  preferences: UserPreferences;
  capabilities: string[];
  restrictions: string[];
  complianceFlags: string[];
}

interface UserPreferences {
  theme: string;
  language: string;
  notifications: NotificationPreferences;
  privacy: PrivacyPreferences;
  accessibility: AccessibilityPreferences;
}

interface NotificationPreferences {
  email: boolean;
  push: boolean;
  sms: boolean;
  inApp: boolean;
  frequency: 'immediate' | 'hourly' | 'daily' | 'weekly';
}

interface PrivacyPreferences {
  dataSharing: 'none' | 'minimal' | 'standard' | 'full';
  analytics: boolean;
  personalization: boolean;
  locationTracking: boolean;
}

interface AccessibilityPreferences {
  screenReader: boolean;
  highContrast: boolean;
  largeText: boolean;
  reducedMotion: boolean;
  keyboardNavigation: boolean;
}

class IdentityManager {
  private profiles: Map<string, IdentityProfile> = new Map();
  private personaOverlays: Map<string, PersonaOverlay> = new Map();
  private accessScopeEngine: AccessScopeEngine;
  private cryptoManager: IdentityCryptoManager;
  private federationManager: IdentityFederationManager;

  constructor() {
    this.accessScopeEngine = new AccessScopeEngine();
    this.cryptoManager = new IdentityCryptoManager();
    this.federationManager = new IdentityFederationManager();
  }

  async createIdentityProfile(
    kind: IdentityKind,
    label: string,
    options: CreateIdentityOptions = {}
  ): Promise<IdentityProfile> {
    const profileId = crypto.randomUUID();
    const now = new Date().toISOString();

    // Generate cryptographic keys
    const keys = await this.generateIdentityKeys(kind, options.keyTypes);

    const profile: IdentityProfile = {
      id: profileId,
      kind,
      label,
      aliases: options.aliases || [],
      parent: options.parent,
      createdAt: now,
      lastUpdated: now,
      verified: false,
      keys,
      permissions: this.getDefaultPermissions(kind),
      personaOverlays: [],
      trustScore: this.getInitialTrustScore(kind),
      auditLogRefs: [],
      metadata: {
        displayName: options.displayName || label,
        preferences: this.getDefaultPreferences(),
        capabilities: await this.detectCapabilities(kind),
        restrictions: [],
        complianceFlags: []
      }
    };

    // Store profile
    this.profiles.set(profileId, profile);

    // Initialize audit log
    await this.initializeAuditLog(profile);

    // Register with federation if enabled
    if (options.federate) {
      await this.federationManager.registerIdentity(profile);
    }

    return profile;
  }

  async createPersonaOverlay(
    identityId: string,
    persona: Omit<PersonaOverlay, 'id'>
  ): Promise<PersonaOverlay> {
    const profile = this.profiles.get(identityId);
    if (!profile) {
      throw new Error('Identity profile not found');
    }

    const personaId = crypto.randomUUID();
    const fullPersona: PersonaOverlay = {
      id: personaId,
      ...persona
    };

    // Store persona
    this.personaOverlays.set(personaId, fullPersona);

    // Add to profile
    if (!profile.personaOverlays) {
      profile.personaOverlays = [];
    }
    profile.personaOverlays.push(fullPersona);

    // Update profile
    profile.lastUpdated = new Date().toISOString();
    this.profiles.set(identityId, profile);

    return fullPersona;
  }

  async activatePersona(
    identityId: string,
    personaId: string,
    context: string[]
  ): Promise<void> {
    const profile = this.profiles.get(identityId);
    if (!profile) {
      throw new Error('Identity profile not found');
    }

    const persona = this.personaOverlays.get(personaId);
    if (!persona) {
      throw new Error('Persona overlay not found');
    }

    // Check if persona is time-bound and valid
    if (persona.timeBound && persona.expiresAt) {
      if (new Date() > new Date(persona.expiresAt)) {
        throw new Error('Persona overlay has expired');
      }
    }

    // Update active contexts
    persona.activeContexts = context;
    this.personaOverlays.set(personaId, persona);

    // Log persona activation
    await this.logIdentityAction(identityId, 'persona_activated', {
      personaId,
      context
    });
  }

  async verifyIdentity(
    identityId: string,
    verificationMethod: string,
    proof: any
  ): Promise<boolean> {
    const profile = this.profiles.get(identityId);
    if (!profile) {
      return false;
    }

    let verified = false;

    switch (verificationMethod) {
      case 'ed25519':
        verified = await this.verifyEd25519Signature(profile, proof);
        break;
      case 'webauthn':
        verified = await this.verifyWebAuthnAssertion(profile, proof);
        break;
      case 'jwt':
        verified = await this.verifyJWTToken(profile, proof);
        break;
      case 'pgp':
        verified = await this.verifyPGPSignature(profile, proof);
        break;
      default:
        return false;
    }

    if (verified) {
      profile.verified = true;
      profile.lastUpdated = new Date().toISOString();
      this.profiles.set(identityId, profile);

      await this.logIdentityAction(identityId, 'identity_verified', {
        method: verificationMethod
      });
    }

    return verified;
  }

  async getEffectivePermissions(
    identityId: string,
    context: AccessContext
  ): Promise<string[]> {
    const profile = this.profiles.get(identityId);
    if (!profile) {
      return [];
    }

    // Start with base permissions
    let permissions = [...profile.permissions];

    // Add inherited permissions from parent
    if (profile.parent) {
      const parentPermissions = await this.getEffectivePermissions(profile.parent, context);
      permissions = [...permissions, ...parentPermissions];
    }

    // Apply persona modifications
    const activePersona = await this.getActivePersona(identityId, context);
    if (activePersona) {
      permissions = this.applyPersonaPermissions(permissions, activePersona, context);
    }

    // Apply context-specific modifications
    permissions = await this.applyContextPermissions(permissions, context);

    // Remove duplicates and sort
    return [...new Set(permissions)].sort();
  }

  private async generateIdentityKeys(
    kind: IdentityKind,
    keyTypes: string[] = ['ed25519']
  ): Promise<IdentityKeys> {
    const keys: IdentityKeys = {};

    if (keyTypes.includes('ed25519')) {
      const keyPair = await crypto.subtle.generateKey(
        { name: 'Ed25519', namedCurve: 'Ed25519' },
        true,
        ['sign', 'verify']
      );

      const publicKeyBytes = await crypto.subtle.exportKey('raw', keyPair.publicKey);
      const publicKeyHex = Array.from(new Uint8Array(publicKeyBytes))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');

      keys.ed25519 = `ED25519:${publicKeyHex}`;
    }

    if (keyTypes.includes('jwt')) {
      const jwtKeyPair = await crypto.subtle.generateKey(
        { name: 'ECDSA', namedCurve: 'P-256' },
        true,
        ['sign', 'verify']
      );

      const publicKeyJwk = await crypto.subtle.exportKey('jwk', jwtKeyPair.publicKey);
      keys.jwtSigning = JSON.stringify(publicKeyJwk);
    }

    return keys;
  }

  private getDefaultPermissions(kind: IdentityKind): string[] {
    const basePermissions = ['read_profile', 'update_profile'];

    switch (kind) {
      case IdentityKind.HUMAN:
        return [...basePermissions, 'create_agents', 'manage_consent', 'access_vault'];
      case IdentityKind.AGENT:
        return [...basePermissions, 'execute_tasks', 'access_services'];
      case IdentityKind.ORG:
        return [...basePermissions, 'manage_members', 'create_agents', 'billing_access'];
      case IdentityKind.SERVICE:
        return [...basePermissions, 'api_access', 'webhook_receive'];
      default:
        return basePermissions;
    }
  }

  private getInitialTrustScore(kind: IdentityKind): number {
    switch (kind) {
      case IdentityKind.HUMAN:
        return 0.7; // Higher initial trust for humans
      case IdentityKind.AGENT:
        return 0.5; // Neutral starting point for agents
      case IdentityKind.ORG:
        return 0.6; // Moderate trust for organizations
      case IdentityKind.SERVICE:
        return 0.4; // Lower initial trust for services
      default:
        return 0.5;
    }
  }

  private getDefaultPreferences(): UserPreferences {
    return {
      theme: 'system',
      language: 'en',
      notifications: {
        email: true,
        push: true,
        sms: false,
        inApp: true,
        frequency: 'immediate'
      },
      privacy: {
        dataSharing: 'minimal',
        analytics: false,
        personalization: true,
        locationTracking: false
      },
      accessibility: {
        screenReader: false,
        highContrast: false,
        largeText: false,
        reducedMotion: false,
        keyboardNavigation: false
      }
    };
  }

  private async detectCapabilities(kind: IdentityKind): Promise<string[]> {
    const capabilities: string[] = [];

    // Base capabilities for all identity types
    capabilities.push('authentication', 'authorization');

    switch (kind) {
      case IdentityKind.HUMAN:
        capabilities.push('consent_management', 'override_actions', 'create_agents');
        break;
      case IdentityKind.AGENT:
        capabilities.push('task_execution', 'service_integration', 'learning');
        if (typeof crypto !== 'undefined') {
          capabilities.push('cryptographic_operations');
        }
        break;
      case IdentityKind.ORG:
        capabilities.push('member_management', 'billing', 'compliance_reporting');
        break;
      case IdentityKind.SERVICE:
        capabilities.push('api_integration', 'webhook_handling', 'data_processing');
        break;
    }

    return capabilities;
  }

  private async verifyEd25519Signature(profile: IdentityProfile, proof: any): Promise<boolean> {
    if (!profile.keys.ed25519) {
      return false;
    }

    try {
      const publicKeyHex = profile.keys.ed25519.replace('ED25519:', '');
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

      const signatureBytes = new Uint8Array(
        proof.signature.match(/.{2}/g)!.map(byte => parseInt(byte, 16))
      );

      return await crypto.subtle.verify(
        'Ed25519',
        publicKey,
        signatureBytes,
        new TextEncoder().encode(proof.message)
      );
    } catch (error) {
      console.error('Ed25519 verification failed:', error);
      return false;
    }
  }

  private async verifyWebAuthnAssertion(profile: IdentityProfile, proof: any): Promise<boolean> {
    if (!profile.keys.webauthn || profile.keys.webauthn.length === 0) {
      return false;
    }

    // Find matching credential
    const credential = profile.keys.webauthn.find(c => c.credentialId === proof.credentialId);
    if (!credential) {
      return false;
    }

    // WebAuthn verification would happen here
    // This is a simplified implementation
    return proof.verified === true;
  }

  private async verifyJWTToken(profile: IdentityProfile, proof: any): Promise<boolean> {
    if (!profile.keys.jwtSigning) {
      return false;
    }

    try {
      const publicKeyJwk = JSON.parse(profile.keys.jwtSigning);
      const publicKey = await crypto.subtle.importKey(
        'jwk',
        publicKeyJwk,
        { name: 'ECDSA', namedCurve: 'P-256' },
        false,
        ['verify']
      );

      // JWT verification would happen here
      // This is a simplified implementation
      return proof.valid === true;
    } catch (error) {
      console.error('JWT verification failed:', error);
      return false;
    }
  }

  private async verifyPGPSignature(profile: IdentityProfile, proof: any): Promise<boolean> {
    if (!profile.keys.pgp) {
      return false;
    }

    // PGP verification would happen here using a PGP library
    // This is a simplified implementation
    return proof.verified === true;
  }

  private async getActivePersona(
    identityId: string,
    context: AccessContext
  ): Promise<PersonaOverlay | null> {
    const profile = this.profiles.get(identityId);
    if (!profile || !profile.personaOverlays) {
      return null;
    }

    // Find persona active in current context
    for (const persona of profile.personaOverlays) {
      if (persona.activeContexts.some(ctx => context.contexts?.includes(ctx))) {
        // Check if time-bound persona is still valid
        if (persona.timeBound && persona.expiresAt) {
          if (new Date() > new Date(persona.expiresAt)) {
            continue;
          }
        }
        return persona;
      }
    }

    return null;
  }

  private applyPersonaPermissions(
    basePermissions: string[],
    persona: PersonaOverlay,
    context: AccessContext
  ): string[] {
    let permissions = [...basePermissions];

    // Apply behavior modifiers that affect permissions
    for (const modifier of persona.behaviorModifiers) {
      if (modifier.type === 'caution' && modifier.value > 0.5) {
        // High caution reduces risky permissions
        permissions = permissions.filter(p => !p.includes('delete') && !p.includes('admin'));
      }

      if (modifier.type === 'expertise' && modifier.value > 0.7) {
        // High expertise adds advanced permissions
        permissions.push('advanced_operations', 'system_diagnostics');
      }
    }

    return permissions;
  }

  private async applyContextPermissions(
    permissions: string[],
    context: AccessContext
  ): Promise<string[]> {
    let contextPermissions = [...permissions];

    // Apply time-based restrictions
    if (context.timestamp) {
      const hour = new Date(context.timestamp).getHours();
      if (hour < 6 || hour > 22) {
        // Reduce permissions during off-hours
        contextPermissions = contextPermissions.filter(p => !p.includes('admin'));
      }
    }

    // Apply location-based restrictions
    if (context.location && !this.isKnownLocation(context.location)) {
      // Reduce permissions from unknown locations
      contextPermissions = contextPermissions.filter(p => 
        !p.includes('sensitive') && !p.includes('financial')
      );
    }

    // Apply device trust restrictions
    if (context.deviceInfo && !this.isTrustedDevice(context.deviceInfo)) {
      // Reduce permissions from untrusted devices
      contextPermissions = contextPermissions.filter(p => !p.includes('vault'));
    }

    return contextPermissions;
  }

  private async initializeAuditLog(profile: IdentityProfile): Promise<void> {
    const logId = `audit_${profile.id}_${Date.now()}`;
    profile.auditLogRefs.push(logId);

    await this.logIdentityAction(profile.id, 'identity_created', {
      kind: profile.kind,
      label: profile.label
    });
  }

  private async logIdentityAction(
    identityId: string,
    action: string,
    details: any
  ): Promise<void> {
    const logEntry = {
      timestamp: new Date().toISOString(),
      identityId,
      action,
      details,
      signature: await this.cryptoManager.signAuditEntry({
        identityId,
        action,
        details,
        timestamp: new Date().toISOString()
      })
    };

    // Store audit log entry
    console.log('Audit log entry:', logEntry);
  }

  private isKnownLocation(location: string): boolean {
    // Implementation would check against known/trusted locations
    return true;
  }

  private isTrustedDevice(deviceInfo: string): boolean {
    // Implementation would check device trust status
    return true;
  }
}
```

## Session Scoping & Role Resolution

```typescript
interface ScopeToken {
  identityId: string;
  sessionId: string;
  role: string;
  inheritedRoles?: string[];
  permissions: string[];
  activePersona?: string;
  expiresAt: string;
  issuedBy: string;
  contexts: string[];
  signature: string;
}

interface AccessContext {
  sessionId: string;
  timestamp: string;
  location?: string;
  deviceInfo?: string;
  userAgent?: string;
  contexts?: string[];
  riskLevel?: 'low' | 'medium' | 'high';
}

interface RoleHierarchy {
  roles: Map<string, Role>;
  inheritance: Map<string, string[]>;
  delegationLimits: Map<string, DelegationLimit>;
}

interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  constraints: RoleConstraint[];
  delegatable: boolean;
  maxDelegationDepth: number;
}

interface RoleConstraint {
  type: 'time' | 'location' | 'resource' | 'frequency';
  condition: string;
  parameters: Record<string, any>;
}

interface DelegationLimit {
  maxDepth: number;
  allowedRoles: string[];
  requiredApprovals: number;
  timeLimit: number;
}

class SessionScopingEngine {
  private activeSessions: Map<string, ScopeToken> = new Map();
  private roleHierarchy: RoleHierarchy;
  private identityManager: IdentityManager;

  constructor(identityManager: IdentityManager) {
    this.identityManager = identityManager;
    this.roleHierarchy = this.initializeRoleHierarchy();
  }

  async createScopeToken(
    identityId: string,
    role: string,
    context: AccessContext,
    duration: number = 24 * 60 * 60 * 1000 // 24 hours default
  ): Promise<ScopeToken> {
    const sessionId = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + duration).toISOString();

    // Resolve role permissions
    const rolePermissions = await this.resolveRolePermissions(role, identityId);
    
    // Get inherited roles
    const inheritedRoles = this.getInheritedRoles(role);
    
    // Get effective permissions including identity and persona
    const effectivePermissions = await this.identityManager.getEffectivePermissions(
      identityId,
      context
    );

    // Combine permissions
    const allPermissions = [
      ...rolePermissions,
      ...effectivePermissions
    ];

    // Get active persona
    const activePersona = await this.getActivePersonaId(identityId, context);

    const scopeToken: Omit<ScopeToken, 'signature'> = {
      identityId,
      sessionId,
      role,
      inheritedRoles,
      permissions: [...new Set(allPermissions)],
      activePersona,
      expiresAt,
      issuedBy: 'session_manager',
      contexts: context.contexts || []
    };

    // Sign the scope token
    const signature = await this.signScopeToken(scopeToken);
    const fullToken: ScopeToken = { ...scopeToken, signature };

    // Store active session
    this.activeSessions.set(sessionId, fullToken);

    // Set cleanup timer
    setTimeout(() => {
      this.activeSessions.delete(sessionId);
    }, duration);

    return fullToken;
  }

  async validateScopeToken(sessionId: string): Promise<ScopeToken | null> {
    const token = this.activeSessions.get(sessionId);
    if (!token) {
      return null;
    }

    // Check expiration
    if (new Date() > new Date(token.expiresAt)) {
      this.activeSessions.delete(sessionId);
      return null;
    }

    // Verify signature
    const isValid = await this.verifyScopeTokenSignature(token);
    if (!isValid) {
      this.activeSessions.delete(sessionId);
      return null;
    }

    return token;
  }

  async hasPermission(
    sessionId: string,
    permission: string,
    resource?: string,
    context?: AccessContext
  ): Promise<boolean> {
    const token = await this.validateScopeToken(sessionId);
    if (!token) {
      return false;
    }

    // Check direct permission
    if (token.permissions.includes(permission)) {
      return await this.checkPermissionConstraints(token, permission, resource, context);
    }

    // Check wildcard permissions
    const wildcardPermissions = token.permissions.filter(p => p.endsWith('*'));
    for (const wildcardPerm of wildcardPermissions) {
      const prefix = wildcardPerm.slice(0, -1);
      if (permission.startsWith(prefix)) {
        return await this.checkPermissionConstraints(token, permission, resource, context);
      }
    }

    return false;
  }

  async delegateRole(
    fromSessionId: string,
    toIdentityId: string,
    role: string,
    duration: number,
    context: AccessContext
  ): Promise<ScopeToken> {
    const fromToken = await this.validateScopeToken(fromSessionId);
    if (!fromToken) {
      throw new Error('Invalid source session');
    }

    // Check if delegation is allowed
    const roleConfig = this.roleHierarchy.roles.get(role);
    if (!roleConfig?.delegatable) {
      throw new Error('Role is not delegatable');
    }

    // Check delegation limits
    const delegationLimit = this.roleHierarchy.delegationLimits.get(fromToken.role);
    if (delegationLimit) {
      if (!delegationLimit.allowedRoles.includes(role)) {
        throw new Error('Role delegation not allowed');
      }

      if (duration > delegationLimit.timeLimit) {
        throw new Error('Delegation duration exceeds limit');
      }
    }

    // Create delegated scope token
    return await this.createScopeToken(toIdentityId, role, context, duration);
  }

  private async resolveRolePermissions(role: string, identityId: string): Promise<string[]> {
    const roleConfig = this.roleHierarchy.roles.get(role);
    if (!roleConfig) {
      return [];
    }

    let permissions = [...roleConfig.permissions];

    // Add inherited permissions
    const inherited = this.roleHierarchy.inheritance.get(role);
    if (inherited) {
      for (const inheritedRole of inherited) {
        const inheritedPermissions = await this.resolveRolePermissions(inheritedRole, identityId);
        permissions = [...permissions, ...inheritedPermissions];
      }
    }

    return [...new Set(permissions)];
  }

  private getInheritedRoles(role: string): string[] {
    return this.roleHierarchy.inheritance.get(role) || [];
  }

  private async getActivePersonaId(identityId: string, context: AccessContext): Promise<string | undefined> {
    // Implementation would determine active persona based on context
    return undefined;
  }

  private async checkPermissionConstraints(
    token: ScopeToken,
    permission: string,
    resource?: string,
    context?: AccessContext
  ): Promise<boolean> {
    const roleConfig = this.roleHierarchy.roles.get(token.role);
    if (!roleConfig) {
      return false;
    }

    // Check role constraints
    for (const constraint of roleConfig.constraints) {
      const constraintMet = await this.evaluateRoleConstraint(constraint, token, context);
      if (!constraintMet) {
        return false;
      }
    }

    return true;
  }

  private async evaluateRoleConstraint(
    constraint: RoleConstraint,
    token: ScopeToken,
    context?: AccessContext
  ): Promise<boolean> {
    switch (constraint.type) {
      case 'time':
        return this.evaluateTimeConstraint(constraint, context);
      case 'location':
        return this.evaluateLocationConstraint(constraint, context);
      case 'resource':
        return this.evaluateResourceConstraint(constraint, context);
      case 'frequency':
        return this.evaluateFrequencyConstraint(constraint, token);
      default:
        return true;
    }
  }

  private evaluateTimeConstraint(constraint: RoleConstraint, context?: AccessContext): boolean {
    if (!context?.timestamp) return true;

    const now = new Date(context.timestamp);
    const params = constraint.parameters;

    if (params.allowedHours) {
      const currentHour = now.getHours();
      if (!params.allowedHours.includes(currentHour)) {
        return false;
      }
    }

    if (params.allowedDays) {
      const currentDay = now.getDay();
      if (!params.allowedDays.includes(currentDay)) {
        return false;
      }
    }

    return true;
  }

  private evaluateLocationConstraint(constraint: RoleConstraint, context?: AccessContext): boolean {
    if (!context?.location) return true;

    const params = constraint.parameters;
    
    if (params.allowedLocations && !params.allowedLocations.includes(context.location)) {
      return false;
    }

    if (params.blockedLocations && params.blockedLocations.includes(context.location)) {
      return false;
    }

    return true;
  }

  private evaluateResourceConstraint(constraint: RoleConstraint, context?: AccessContext): boolean {
    // Resource-specific constraint evaluation
    return true;
  }

  private evaluateFrequencyConstraint(constraint: RoleConstraint, token: ScopeToken): boolean {
    // Frequency-based constraint evaluation
    return true;
  }

  private async signScopeToken(token: Omit<ScopeToken, 'signature'>): Promise<string> {
    // Implementation would sign the scope token
    return 'signed_token_placeholder';
  }

  private async verifyScopeTokenSignature(token: ScopeToken): Promise<boolean> {
    // Implementation would verify the scope token signature
    return true;
  }

  private initializeRoleHierarchy(): RoleHierarchy {
    const roles = new Map<string, Role>();
    const inheritance = new Map<string, string[]>();
    const delegationLimits = new Map<string, DelegationLimit>();

    // Define standard roles
    roles.set('admin', {
      id: 'admin',
      name: 'Administrator',
      description: 'Full system access',
      permissions: ['*'],
      constraints: [],
      delegatable: true,
      maxDelegationDepth: 2
    });

    roles.set('user', {
      id: 'user',
      name: 'Standard User',
      description: 'Standard user access',
      permissions: ['read_profile', 'update_profile', 'create_agents'],
      constraints: [],
      delegatable: false,
      maxDelegationDepth: 0
    });

    roles.set('agent', {
      id: 'agent',
      name: 'Agent',
      description: 'AI agent access',
      permissions: ['execute_tasks', 'access_services', 'read_profile'],
      constraints: [
        {
          type: 'frequency',
          condition: 'max_actions_per_hour',
          parameters: { limit: 1000 }
        }
      ],
      delegatable: false,
      maxDelegationDepth: 0
    });

    // Define inheritance
    inheritance.set('admin', ['user']);
    inheritance.set('user', []);
    inheritance.set('agent', []);

    // Define delegation limits
    delegationLimits.set('admin', {
      maxDepth: 2,
      allowedRoles: ['user', 'agent'],
      requiredApprovals: 0,
      timeLimit: 7 * 24 * 60 * 60 * 1000 // 7 days
    });

    return {
      roles,
      inheritance,
      delegationLimits
    };
  }
}
```

This comprehensive Identity Profiles and Access Scope System provides enterprise-grade identity management with dynamic scoping, persona overlays, role-based access control, and federation capabilities essential for secure and flexible multi-actor interactions across the kOS ecosystem. 