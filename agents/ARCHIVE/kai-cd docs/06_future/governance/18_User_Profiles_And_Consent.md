---
title: "User Profiles, Role Configurations, and Consent Governance"
description: "Comprehensive system for user profiles, role permissions, and consent management in kAI and kOS"
type: "governance"
status: "future"
priority: "high"
last_updated: "2024-12-21"
related_docs: ["security-architecture-and-trust.md", "agent-trust-protocols.md"]
implementation_status: "planned"
---

# User Profiles, Role Configurations, and Consent Governance (kAI + kOS)

## Agent Context
**For AI Agents**: This document defines the user management and consent system that governs all agent interactions. All agents must respect user roles, permissions, and consent preferences. The ConsentLedger is critical for compliance and user trust.

**Implementation Priority**: Implement UserProfileManager first, then role system, then consent tracking and persona engine.

## Purpose

Ensure all user interactions are:
- Personal, flexible, and consent-driven
- Transparent and governable
- Secure and decentralized
- Configurable through local and synced profiles

## Architecture

### Directory Structure

```typescript
src/
└── user/
    ├── profiles/
    │   ├── UserProfileManager.ts         // Load/save/sync user preferences
    │   ├── ConsentLedger.ts              // Logs all consent grants/revocations
    │   └── PersonaEngine.ts              // Contextual persona switching logic
    ├── roles/
    │   ├── RoleDefinitions.ts            // Static and dynamic role schema
    │   └── RolePolicyEngine.ts           // Enforces what roles can/cannot do
    └── permissions/
        ├── AccessControlMatrix.ts       // Fine-grained access rules
        └── RoleBindingResolver.ts       // Runtime role resolution for agents/tasks
```

## Core Schema Definitions

### User Profile Schema

```typescript
interface UserProfile {
  id: string;                        // UUID
  name: string;
  email?: string;
  avatar?: string;                  // Base64 or file path
  preferences: UserPreferences;
  enabledPersonas: string[];        // Allowed persona overlays
  defaultRole: string;              // e.g., 'owner', 'admin', 'guest'
  roleOverrides: RoleOverride[];    // Fine-grained permission tweaks
  consentHistory: ConsentRecord[];
  privacySettings: PrivacySettings;
  createdAt: string;
  updatedAt: string;
}

interface UserPreferences {
  language: string;
  timezone: string;
  theme: string;
  voice: VoiceSettings;
  notifications: NotificationSettings;
  ai: AIPreferences;
}

interface ConsentRecord {
  id: string;
  action: string;                    // e.g., "use voice input", "store conversation"
  category: ConsentCategory;
  granted: boolean;
  timestamp: string;
  source: 'user' | 'agent' | 'external';
  context?: string;
  expiresAt?: string;
  note?: string;
}

enum ConsentCategory {
  DATA_COLLECTION = 'data_collection',
  DATA_PROCESSING = 'data_processing',
  DATA_SHARING = 'data_sharing',
  BIOMETRIC = 'biometric',
  LOCATION = 'location',
  COMMUNICATION = 'communication',
  AI_TRAINING = 'ai_training'
}
```

## Role System Implementation

### Role Definitions

```typescript
interface Role {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
  inherits?: string[];              // Role inheritance
  constraints: RoleConstraints;
  metadata: RoleMetadata;
}

interface Permission {
  resource: string;                 // e.g., 'agents', 'services', 'data'
  actions: string[];               // e.g., ['read', 'write', 'execute']
  conditions?: PermissionCondition[];
}

interface RoleConstraints {
  maxSessions?: number;
  maxAgents?: number;
  resourceLimits?: ResourceLimits;
  timeRestrictions?: TimeRestriction[];
  ipWhitelist?: string[];
}

// Default system roles
const DEFAULT_ROLES: Role[] = [
  {
    id: 'owner',
    name: 'Owner',
    description: 'Full system access and control',
    permissions: [{ resource: '*', actions: ['*'] }],
    inherits: [],
    constraints: {},
    metadata: { system: true, deletable: false }
  },
  {
    id: 'admin',
    name: 'Administrator',
    description: 'Manage services, agents, and users',
    permissions: [
      { resource: 'agents', actions: ['read', 'write', 'execute', 'delete'] },
      { resource: 'services', actions: ['read', 'write', 'restart'] },
      { resource: 'users', actions: ['read', 'write'] },
      { resource: 'system', actions: ['read', 'configure'] }
    ],
    inherits: ['user'],
    constraints: { maxSessions: 5 },
    metadata: { system: true, deletable: false }
  },
  {
    id: 'user',
    name: 'User',
    description: 'Standard user access',
    permissions: [
      { resource: 'agents', actions: ['read', 'execute'] },
      { resource: 'services', actions: ['read', 'use'] },
      { resource: 'data', actions: ['read', 'write'], conditions: [{ type: 'owner', value: 'self' }] }
    ],
    inherits: [],
    constraints: { maxSessions: 3, maxAgents: 10 },
    metadata: { system: true, deletable: false }
  },
  {
    id: 'guest',
    name: 'Guest',
    description: 'Temporary limited access',
    permissions: [
      { resource: 'agents', actions: ['read'], conditions: [{ type: 'public', value: true }] },
      { resource: 'services', actions: ['read'] }
    ],
    inherits: [],
    constraints: { maxSessions: 1, resourceLimits: { memory: 512, cpu: 0.5 } },
    metadata: { system: true, deletable: false }
  }
];
```

### Role Policy Engine

```typescript
class RolePolicyEngine {
  private roles: Map<string, Role> = new Map();
  private policies: Map<string, Policy> = new Map();
  
  async checkPermission(
    userId: string,
    resource: string,
    action: string,
    context?: PermissionContext
  ): Promise<PermissionResult> {
    const user = await this.getUserProfile(userId);
    const role = await this.getRole(user.defaultRole);
    
    // Check direct permissions
    const directPermission = this.checkDirectPermission(role, resource, action);
    if (directPermission.granted) {
      return directPermission;
    }
    
    // Check inherited permissions
    const inheritedPermission = await this.checkInheritedPermissions(role, resource, action);
    if (inheritedPermission.granted) {
      return inheritedPermission;
    }
    
    // Check role overrides
    const overridePermission = this.checkRoleOverrides(user.roleOverrides, resource, action);
    if (overridePermission.granted) {
      return overridePermission;
    }
    
    // Apply contextual conditions
    return await this.applyContextualConditions(role, resource, action, context);
  }
  
  async enforceConstraints(userId: string, operation: Operation): Promise<void> {
    const user = await this.getUserProfile(userId);
    const role = await this.getRole(user.defaultRole);
    
    // Check session limits
    if (role.constraints.maxSessions) {
      const activeSessions = await this.getActiveSessions(userId);
      if (activeSessions >= role.constraints.maxSessions) {
        throw new Error('Maximum session limit exceeded');
      }
    }
    
    // Check resource limits
    if (role.constraints.resourceLimits) {
      await this.enforceResourceLimits(userId, operation, role.constraints.resourceLimits);
    }
    
    // Check time restrictions
    if (role.constraints.timeRestrictions) {
      await this.enforceTimeRestrictions(operation, role.constraints.timeRestrictions);
    }
  }
}
```

## Persona System

### Persona Definitions

```typescript
interface Persona {
  id: string;
  name: string;
  description: string;
  behaviorPattern: BehaviorPattern;
  constraints: PersonaConstraints;
  requiredConsent: ConsentCategory[];
  metadata: PersonaMetadata;
}

interface BehaviorPattern {
  tone: 'formal' | 'casual' | 'friendly' | 'professional' | 'playful';
  verbosity: 'concise' | 'normal' | 'detailed' | 'verbose';
  creativity: number;              // 0-1 scale
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
  specializations: string[];       // Areas of focus
}

const DEFAULT_PERSONAS: Persona[] = [
  {
    id: 'assistant',
    name: 'Assistant',
    description: 'Helpful, context-aware assistant',
    behaviorPattern: {
      tone: 'friendly',
      verbosity: 'normal',
      creativity: 0.3,
      riskTolerance: 'conservative',
      specializations: ['general_help', 'productivity']
    },
    constraints: { maxRiskLevel: 'low' },
    requiredConsent: [],
    metadata: { system: true, safe: true }
  },
  {
    id: 'guardian',
    name: 'Guardian',
    description: 'Safety-first, parental control mode',
    behaviorPattern: {
      tone: 'formal',
      verbosity: 'detailed',
      creativity: 0.1,
      riskTolerance: 'conservative',
      specializations: ['safety', 'education', 'content_filtering']
    },
    constraints: { 
      maxRiskLevel: 'none',
      contentFiltering: true,
      requireApproval: ['web_access', 'external_communication']
    },
    requiredConsent: [ConsentCategory.DATA_PROCESSING],
    metadata: { system: true, safe: true }
  },
  {
    id: 'hacker',
    name: 'Hacker',
    description: 'Developer mode with deep system access',
    behaviorPattern: {
      tone: 'casual',
      verbosity: 'concise',
      creativity: 0.8,
      riskTolerance: 'aggressive',
      specializations: ['development', 'system_admin', 'debugging']
    },
    constraints: { 
      requiresElevatedPermissions: true,
      systemAccess: true
    },
    requiredConsent: [ConsentCategory.DATA_COLLECTION, ConsentCategory.DATA_PROCESSING],
    metadata: { system: true, safe: false, requiresConfirmation: true }
  }
];
```

### Persona Engine

```typescript
class PersonaEngine {
  private activePersona: Map<string, string> = new Map(); // userId -> personaId
  private personas: Map<string, Persona> = new Map();
  
  async switchPersona(userId: string, personaId: string): Promise<void> {
    const persona = this.personas.get(personaId);
    if (!persona) {
      throw new Error(`Persona not found: ${personaId}`);
    }
    
    // Check if user has permission to use this persona
    const user = await this.getUserProfile(userId);
    if (!user.enabledPersonas.includes(personaId)) {
      throw new Error(`Persona not enabled for user: ${personaId}`);
    }
    
    // Check required consent
    await this.verifyRequiredConsent(userId, persona.requiredConsent);
    
    // Apply persona constraints
    await this.applyPersonaConstraints(userId, persona.constraints);
    
    // Set active persona
    this.activePersona.set(userId, personaId);
    
    // Log persona switch
    await this.logPersonaSwitch(userId, personaId);
  }
  
  async getActivePersona(userId: string): Promise<Persona | null> {
    const personaId = this.activePersona.get(userId);
    return personaId ? this.personas.get(personaId) || null : null;
  }
  
  async applyPersonaBehavior(
    userId: string,
    prompt: string,
    context: AIContext
  ): Promise<string> {
    const persona = await this.getActivePersona(userId);
    if (!persona) {
      return prompt; // No persona modification
    }
    
    // Apply behavior pattern to prompt
    let modifiedPrompt = prompt;
    
    // Adjust tone
    modifiedPrompt = this.applyTone(modifiedPrompt, persona.behaviorPattern.tone);
    
    // Adjust verbosity
    modifiedPrompt = this.applyVerbosity(modifiedPrompt, persona.behaviorPattern.verbosity);
    
    // Add specialization context
    if (persona.behaviorPattern.specializations.length > 0) {
      modifiedPrompt = this.addSpecializationContext(modifiedPrompt, persona.behaviorPattern.specializations);
    }
    
    return modifiedPrompt;
  }
}
```

## Consent Management System

### Consent Ledger

```typescript
class ConsentLedger {
  private ledger: Map<string, ConsentRecord[]> = new Map();
  private storage: ConsentStorage;
  
  async grantConsent(
    userId: string,
    action: string,
    category: ConsentCategory,
    options: ConsentOptions = {}
  ): Promise<ConsentRecord> {
    const record: ConsentRecord = {
      id: generateUUID(),
      action,
      category,
      granted: true,
      timestamp: new Date().toISOString(),
      source: options.source || 'user',
      context: options.context,
      expiresAt: options.expiresAt,
      note: options.note
    };
    
    // Store consent record
    await this.addConsentRecord(userId, record);
    
    // Log consent event
    await this.logConsentEvent(userId, record);
    
    return record;
  }
  
  async revokeConsent(
    userId: string,
    consentId: string,
    reason?: string
  ): Promise<void> {
    const userConsents = this.ledger.get(userId) || [];
    const consentIndex = userConsents.findIndex(c => c.id === consentId);
    
    if (consentIndex === -1) {
      throw new Error(`Consent record not found: ${consentId}`);
    }
    
    // Create revocation record
    const revocationRecord: ConsentRecord = {
      ...userConsents[consentIndex],
      id: generateUUID(),
      granted: false,
      timestamp: new Date().toISOString(),
      note: reason
    };
    
    // Add revocation record
    await this.addConsentRecord(userId, revocationRecord);
    
    // Trigger consent revocation handlers
    await this.handleConsentRevocation(userId, userConsents[consentIndex]);
  }
  
  async checkConsent(
    userId: string,
    action: string,
    category: ConsentCategory
  ): Promise<boolean> {
    const userConsents = this.ledger.get(userId) || [];
    
    // Find most recent consent for this action/category
    const relevantConsents = userConsents
      .filter(c => c.action === action && c.category === category)
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    
    if (relevantConsents.length === 0) {
      return false; // No consent found
    }
    
    const latestConsent = relevantConsents[0];
    
    // Check if consent has expired
    if (latestConsent.expiresAt && new Date(latestConsent.expiresAt) < new Date()) {
      return false;
    }
    
    return latestConsent.granted;
  }
}
```

## Privacy and Security

### Privacy Settings

```typescript
interface PrivacySettings {
  mode: 'private' | 'trusted' | 'hybrid' | 'cloud';
  dataRetention: DataRetentionPolicy;
  sharing: SharingPolicy;
  anonymization: AnonymizationSettings;
  encryption: EncryptionSettings;
}

interface DataRetentionPolicy {
  conversations: number;           // Days to retain
  logs: number;
  analytics: number;
  autoDelete: boolean;
}

const PRIVACY_PRESETS: Record<string, PrivacySettings> = {
  private: {
    mode: 'private',
    dataRetention: { conversations: 7, logs: 1, analytics: 0, autoDelete: true },
    sharing: { external: false, analytics: false, training: false },
    anonymization: { enabled: true, level: 'high' },
    encryption: { level: 'maximum', localOnly: true }
  },
  trusted: {
    mode: 'trusted',
    dataRetention: { conversations: 30, logs: 7, analytics: 30, autoDelete: true },
    sharing: { external: 'opt-in', analytics: 'anonymized', training: 'opt-in' },
    anonymization: { enabled: true, level: 'medium' },
    encryption: { level: 'high', cloudSync: 'encrypted' }
  },
  hybrid: {
    mode: 'hybrid',
    dataRetention: { conversations: 90, logs: 30, analytics: 90, autoDelete: false },
    sharing: { external: 'selective', analytics: 'anonymized', training: 'opt-in' },
    anonymization: { enabled: true, level: 'medium' },
    encryption: { level: 'standard', cloudSync: 'encrypted' }
  },
  cloud: {
    mode: 'cloud',
    dataRetention: { conversations: 365, logs: 90, analytics: 365, autoDelete: false },
    sharing: { external: 'allowed', analytics: 'enabled', training: 'opt-out' },
    anonymization: { enabled: false, level: 'low' },
    encryption: { level: 'standard', cloudSync: 'enabled' }
  }
};
```

## Export/Import System

### Profile Export

```typescript
class ProfileExporter {
  async exportUserProfile(
    userId: string,
    passphrase: string,
    options: ExportOptions = {}
  ): Promise<string> {
    const profile = await this.getUserProfile(userId);
    
    // Sanitize sensitive data if requested
    if (options.sanitize) {
      profile = this.sanitizeProfile(profile);
    }
    
    // Encrypt profile data
    const encrypted = await this.encryptProfile(profile, passphrase);
    
    // Create export package
    const exportPackage = {
      version: '1.0',
      timestamp: new Date().toISOString(),
      profile: encrypted,
      metadata: {
        userId: profile.id,
        exportedBy: options.exportedBy || 'user',
        includeHistory: options.includeHistory || false
      }
    };
    
    return JSON.stringify(exportPackage, null, 2);
  }
  
  async importUserProfile(
    filePath: string,
    passphrase: string
  ): Promise<UserProfile> {
    const exportData = await this.readExportFile(filePath);
    const exportPackage = JSON.parse(exportData);
    
    // Decrypt profile
    const profile = await this.decryptProfile(exportPackage.profile, passphrase);
    
    // Validate profile structure
    await this.validateProfile(profile);
    
    // Import profile
    await this.saveUserProfile(profile);
    
    return profile;
  }
}
```

## Implementation Guidelines

### Development Phases

1. **Phase 1**: Basic user profiles and role system
2. **Phase 2**: Consent management and privacy controls
3. **Phase 3**: Persona system and behavior modification
4. **Phase 4**: Advanced privacy features and export/import
5. **Phase 5**: Federation and cross-system consent

### Security Considerations

- All profile data must be encrypted at rest
- Consent records must be tamper-evident
- Role changes must be audited and logged
- Persona switches must be tracked and reversible
- Privacy settings must be enforced at all system levels

This user management system ensures that all interactions with kAI and kOS are user-controlled, consent-driven, and privacy-respecting while maintaining the flexibility needed for diverse use cases. 