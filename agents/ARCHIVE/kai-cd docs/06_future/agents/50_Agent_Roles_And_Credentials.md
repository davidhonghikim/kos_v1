---
title: "Agent Roles and Credentials"
description: "Comprehensive role system, credential management, and trust framework for agents in kOS ecosystem"
type: "security"
status: "future"
priority: "critical"
last_updated: "2025-01-03"
related_docs: ["agent-trust-identity.md", "agent-council.md"]
implementation_status: "planned"
---

# Agent Roles And Credentials

## Agent Context

This document defines the roles, credentials, lifecycle permissions, and trust framework for agents operating within the kOS/kAI ecosystem. Agents must understand role hierarchies, credential verification, trust tiers, and permission mapping for secure multi-agent operations.

## System Architecture

Agents operate with clearly defined roles and access scopes determining actions across services, with dynamic trust computation and cryptographic credential verification.

### Role System Implementation

```typescript
interface AgentRoleSystem {
  standard_roles: StandardRole[];
  sub_roles: SubRole[];
  trust_tiers: TrustTier[];
  credential_manager: CredentialManager;
  lifecycle_manager: LifecycleManager;
}

interface StandardRole {
  name: string;
  trust_level: number;
  scope: AccessScope;
  permissions: Permission[];
  escalation_path: string[];
  default_duration: number;
}

interface SubRole {
  name: string;
  parent_role: string;
  additional_permissions: Permission[];
  restrictions: Restriction[];
}

interface TrustTier {
  name: string;
  score_range: [number, number];
  allowed_operations: string[];
  monitoring_level: 'none' | 'basic' | 'enhanced' | 'comprehensive';
  autonomy_level: number;
}

class AgentRoleManager {
  private roles: Map<string, StandardRole>;
  private subRoles: Map<string, SubRole>;
  private trustTiers: Map<string, TrustTier>;
  private credentialManager: CredentialManager;
  private trustScorer: TrustScorer;
  private permissionEngine: PermissionEngine;

  constructor(config: RoleSystemConfig) {
    this.initializeRoles();
    this.initializeTrustTiers();
    this.credentialManager = new CredentialManager(config.credentials);
    this.trustScorer = new TrustScorer(config.trust);
    this.permissionEngine = new PermissionEngine(config.permissions);
  }

  private initializeRoles(): void {
    this.roles.set('observer', {
      name: 'observer',
      trust_level: 0,
      scope: {
        local_only: true,
        public_endpoints: true,
        sensitive_data: false
      },
      permissions: [
        { action: 'read', resources: ['logs', 'metrics', 'public_endpoints'] },
        { action: 'subscribe', resources: ['public_events'] }
      ],
      escalation_path: ['worker'],
      default_duration: 86400000 // 24 hours
    });

    this.roles.set('worker', {
      name: 'worker',
      trust_level: 1,
      scope: {
        local_only: false,
        delegated_grid: true,
        resource_constraints: true
      },
      permissions: [
        { action: 'read', resources: ['shared_state', 'task_queue'] },
        { action: 'write', resources: ['task_results', 'status_updates'] },
        { action: 'execute', resources: ['delegated_tasks'] }
      ],
      escalation_path: ['service', 'orchestrator'],
      default_duration: 604800000 // 7 days
    });

    this.roles.set('service', {
      name: 'service',
      trust_level: 2,
      scope: {
        local_and_public: true,
        api_exposure: true,
        resource_allocation: true
      },
      permissions: [
        { action: 'host', resources: ['apis', 'tools'] },
        { action: 'serve', resources: ['other_agents', 'users'] },
        { action: 'allocate', resources: ['compute', 'storage'] }
      ],
      escalation_path: ['orchestrator', 'guardian'],
      default_duration: 2592000000 // 30 days
    });

    this.roles.set('orchestrator', {
      name: 'orchestrator',
      trust_level: 3,
      scope: {
        distributed_mesh: true,
        workflow_coordination: true,
        agent_management: true
      },
      permissions: [
        { action: 'coordinate', resources: ['workflows', 'agent_swarms'] },
        { action: 'manage', resources: ['task_distribution', 'resource_allocation'] },
        { action: 'monitor', resources: ['system_health', 'performance_metrics'] }
      ],
      escalation_path: ['guardian', 'root'],
      default_duration: 7776000000 // 90 days
    });

    this.roles.set('guardian', {
      name: 'guardian',
      trust_level: 4,
      scope: {
        all_trusted_zones: true,
        policy_enforcement: true,
        audit_access: true
      },
      permissions: [
        { action: 'enforce', resources: ['policies', 'security_rules'] },
        { action: 'audit', resources: ['all_logs', 'compliance_data'] },
        { action: 'override', resources: ['security_decisions', 'access_controls'] }
      ],
      escalation_path: ['root'],
      default_duration: 15552000000 // 180 days
    });

    this.roles.set('root', {
      name: 'root',
      trust_level: 5,
      scope: {
        all_zones: true,
        emergency_powers: true,
        system_critical: true
      },
      permissions: [
        { action: 'full_access', resources: ['all_systems'] },
        { action: 'emergency_override', resources: ['all_controls'] },
        { action: 'system_modification', resources: ['core_protocols'] }
      ],
      escalation_path: [],
      default_duration: 3600000 // 1 hour (emergency only)
    });
  }

  private initializeTrustTiers(): void {
    this.trustTiers.set('unverified', {
      name: 'unverified',
      score_range: [0, 49],
      allowed_operations: ['read_public', 'basic_interaction'],
      monitoring_level: 'comprehensive',
      autonomy_level: 0
    });

    this.trustTiers.set('provisional', {
      name: 'provisional',
      score_range: [50, 74],
      allowed_operations: ['constrained_execution', 'supervised_tasks'],
      monitoring_level: 'enhanced',
      autonomy_level: 25
    });

    this.trustTiers.set('trusted', {
      name: 'trusted',
      score_range: [75, 89],
      allowed_operations: ['normal_operations', 'standard_tasks'],
      monitoring_level: 'basic',
      autonomy_level: 75
    });

    this.trustTiers.set('verified', {
      name: 'verified',
      score_range: [90, 98],
      allowed_operations: ['autonomous_operations', 'complex_tasks'],
      monitoring_level: 'basic',
      autonomy_level: 90
    });

    this.trustTiers.set('core', {
      name: 'core',
      score_range: [99, 100],
      allowed_operations: ['system_critical', 'unrestricted_access'],
      monitoring_level: 'none',
      autonomy_level: 100
    });
  }

  async assignRole(agentId: string, roleName: string, assignedBy: string): Promise<RoleAssignment> {
    // Validate role exists
    const role = this.roles.get(roleName);
    if (!role) {
      throw new Error(`Role not found: ${roleName}`);
    }

    // Check assigner permissions
    const assignerRole = await this.getAgentRole(assignedBy);
    if (!this.canAssignRole(assignerRole, roleName)) {
      throw new Error(`Insufficient permissions to assign role: ${roleName}`);
    }

    // Verify agent eligibility
    const eligibility = await this.checkRoleEligibility(agentId, roleName);
    if (!eligibility.eligible) {
      throw new Error(`Agent not eligible for role: ${eligibility.reason}`);
    }

    // Generate credentials
    const credentials = await this.credentialManager.generateCredentials({
      agent_id: agentId,
      role: roleName,
      issued_by: assignedBy,
      valid_until: new Date(Date.now() + role.default_duration).toISOString(),
      permissions: role.permissions
    });

    // Create role assignment
    const assignment: RoleAssignment = {
      agent_id: agentId,
      role: roleName,
      credentials: credentials,
      assigned_by: assignedBy,
      assigned_at: new Date().toISOString(),
      expires_at: credentials.expiration,
      status: 'active'
    };

    // Store assignment
    await this.storeRoleAssignment(assignment);

    // Log assignment
    await this.logRoleAssignment(assignment);

    return assignment;
  }

  async escalateRole(agentId: string, targetRole: string, requestedBy: string): Promise<RoleEscalation> {
    // Get current role
    const currentAssignment = await this.getCurrentRoleAssignment(agentId);
    if (!currentAssignment) {
      throw new Error(`No current role assignment found for agent: ${agentId}`);
    }

    const currentRole = this.roles.get(currentAssignment.role);
    if (!currentRole) {
      throw new Error(`Current role not found: ${currentAssignment.role}`);
    }

    // Check if escalation is allowed
    if (!currentRole.escalation_path.includes(targetRole)) {
      throw new Error(`Role escalation not allowed: ${currentAssignment.role} -> ${targetRole}`);
    }

    // Verify escalation requirements
    const escalationRequirements = await this.getEscalationRequirements(
      currentAssignment.role,
      targetRole
    );

    const verification = await this.verifyEscalationRequirements(
      agentId,
      escalationRequirements
    );

    if (!verification.passed) {
      throw new Error(`Escalation requirements not met: ${verification.failures.join(', ')}`);
    }

    // Conduct guardian audit
    const auditResult = await this.conductGuardianAudit(agentId, targetRole);
    if (!auditResult.approved) {
      throw new Error(`Guardian audit failed: ${auditResult.reason}`);
    }

    // Process role escalation
    const escalation = await this.processRoleEscalation({
      agent_id: agentId,
      from_role: currentAssignment.role,
      to_role: targetRole,
      requested_by: requestedBy,
      audit_result: auditResult,
      verification: verification
    });

    return escalation;
  }
}
```

## Credential Management System

### Cryptographic Credential Framework

```typescript
interface AgentCredential {
  id: string;
  agent_id: string;
  public_key: string;
  roles: string[];
  sub_roles: string[];
  trust_score: number;
  issued_by: string;
  issued_at: string;
  expires_at: string;
  signature: string;
  revocation_status: RevocationStatus;
}

interface RevocationStatus {
  revoked: boolean;
  revoked_at?: string;
  revoked_by?: string;
  reason?: string;
  revocation_signature?: string;
}

class CredentialManager {
  private keyManager: KeyManager;
  private signatureValidator: SignatureValidator;
  private revocationList: RevocationList;
  private credentialStore: CredentialStore;

  constructor(config: CredentialConfig) {
    this.keyManager = new KeyManager(config.key_management);
    this.signatureValidator = new SignatureValidator(config.signature);
    this.revocationList = new RevocationList(config.revocation);
    this.credentialStore = new CredentialStore(config.storage);
  }

  async generateCredentials(request: CredentialRequest): Promise<AgentCredential> {
    // Generate key pair for agent
    const keyPair = await this.keyManager.generateKeyPair('Ed25519');

    // Create credential structure
    const credential: AgentCredential = {
      id: await this.generateCredentialId(),
      agent_id: request.agent_id,
      public_key: keyPair.publicKey,
      roles: [request.role],
      sub_roles: request.sub_roles || [],
      trust_score: request.trust_score || 0,
      issued_by: request.issued_by,
      issued_at: new Date().toISOString(),
      expires_at: request.expires_at,
      signature: '',
      revocation_status: {
        revoked: false
      }
    };

    // Sign credential
    const credentialData = this.serializeCredentialForSigning(credential);
    const signature = await this.keyManager.sign(credentialData, request.issued_by);
    credential.signature = signature;

    // Store credential
    await this.credentialStore.store(credential);

    // Store private key securely
    await this.keyManager.storePrivateKey(request.agent_id, keyPair.privateKey);

    return credential;
  }

  async verifyCredential(credential: AgentCredential): Promise<VerificationResult> {
    // Check expiration
    if (new Date(credential.expires_at) < new Date()) {
      return {
        valid: false,
        reason: 'Credential expired',
        expired: true
      };
    }

    // Check revocation status
    if (credential.revocation_status.revoked) {
      return {
        valid: false,
        reason: 'Credential revoked',
        revoked: true,
        revocation_reason: credential.revocation_status.reason
      };
    }

    // Verify signature
    const credentialData = this.serializeCredentialForSigning(credential);
    const signatureValid = await this.signatureValidator.verify(
      credentialData,
      credential.signature,
      credential.issued_by
    );

    if (!signatureValid) {
      return {
        valid: false,
        reason: 'Invalid signature',
        signature_valid: false
      };
    }

    // Check against revocation list
    const revocationCheck = await this.revocationList.check(credential.id);
    if (revocationCheck.revoked) {
      return {
        valid: false,
        reason: 'Credential in revocation list',
        revoked: true
      };
    }

    return {
      valid: true,
      reason: 'Credential valid',
      trust_score: credential.trust_score,
      roles: credential.roles,
      expires_at: credential.expires_at
    };
  }

  async rotateCredentials(agentId: string, rotatedBy: string): Promise<CredentialRotation> {
    // Get current credentials
    const currentCredentials = await this.credentialStore.getByAgentId(agentId);
    if (!currentCredentials) {
      throw new Error(`No credentials found for agent: ${agentId}`);
    }

    // Verify rotation authority
    const rotationAuth = await this.verifyRotationAuthority(rotatedBy, currentCredentials);
    if (!rotationAuth.authorized) {
      throw new Error(`Unauthorized credential rotation: ${rotationAuth.reason}`);
    }

    // Generate new credentials
    const newCredentials = await this.generateCredentials({
      agent_id: agentId,
      role: currentCredentials.roles[0], // Primary role
      sub_roles: currentCredentials.sub_roles,
      trust_score: currentCredentials.trust_score,
      issued_by: rotatedBy,
      expires_at: new Date(Date.now() + 7776000000).toISOString() // 90 days
    });

    // Revoke old credentials
    await this.revokeCredential(currentCredentials.id, {
      revoked_by: rotatedBy,
      reason: 'Credential rotation',
      revocation_type: 'rotation'
    });

    return {
      agent_id: agentId,
      old_credential_id: currentCredentials.id,
      new_credential_id: newCredentials.id,
      rotated_by: rotatedBy,
      rotation_timestamp: new Date().toISOString()
    };
  }

  async revokeCredential(credentialId: string, revocation: RevocationRequest): Promise<void> {
    // Get credential
    const credential = await this.credentialStore.getById(credentialId);
    if (!credential) {
      throw new Error(`Credential not found: ${credentialId}`);
    }

    // Verify revocation authority
    const revocationAuth = await this.verifyRevocationAuthority(
      revocation.revoked_by,
      credential
    );
    if (!revocationAuth.authorized) {
      throw new Error(`Unauthorized credential revocation: ${revocationAuth.reason}`);
    }

    // Update revocation status
    credential.revocation_status = {
      revoked: true,
      revoked_at: new Date().toISOString(),
      revoked_by: revocation.revoked_by,
      reason: revocation.reason,
      revocation_signature: await this.signRevocation(credential, revocation)
    };

    // Update credential store
    await this.credentialStore.update(credential);

    // Add to revocation list
    await this.revocationList.add(credentialId, revocation);

    // Notify agent of revocation
    await this.notifyCredentialRevocation(credential.agent_id, revocation);
  }
}
```

## Trust Tier Calculation System

### Dynamic Trust Scoring

```typescript
interface TrustCalculation {
  agent_id: string;
  base_score: number;
  behavior_score: number;
  endorsement_score: number;
  history_score: number;
  penalty_score: number;
  final_score: number;
  tier: string;
  calculation_timestamp: string;
}

class TrustScorer {
  private behaviorAnalyzer: BehaviorAnalyzer;
  private endorsementManager: EndorsementManager;
  private historyTracker: HistoryTracker;
  private penaltySystem: PenaltySystem;

  constructor(config: TrustScorerConfig) {
    this.behaviorAnalyzer = new BehaviorAnalyzer(config.behavior);
    this.endorsementManager = new EndorsementManager(config.endorsements);
    this.historyTracker = new HistoryTracker(config.history);
    this.penaltySystem = new PenaltySystem(config.penalties);
  }

  async calculateTrustScore(agentId: string): Promise<TrustCalculation> {
    // Get base score (initial trust level)
    const baseScore = await this.getBaseScore(agentId);

    // Calculate behavior score
    const behaviorScore = await this.behaviorAnalyzer.analyze(agentId);

    // Calculate endorsement score
    const endorsementScore = await this.endorsementManager.calculateScore(agentId);

    // Calculate history score
    const historyScore = await this.historyTracker.calculateScore(agentId);

    // Calculate penalty score
    const penaltyScore = await this.penaltySystem.calculatePenalties(agentId);

    // Calculate weighted final score
    const finalScore = this.calculateWeightedScore({
      base: baseScore,
      behavior: behaviorScore,
      endorsements: endorsementScore,
      history: historyScore,
      penalties: penaltyScore
    });

    // Determine trust tier
    const tier = this.determineTrustTier(finalScore);

    const calculation: TrustCalculation = {
      agent_id: agentId,
      base_score: baseScore,
      behavior_score: behaviorScore,
      endorsement_score: endorsementScore,
      history_score: historyScore,
      penalty_score: penaltyScore,
      final_score: finalScore,
      tier: tier,
      calculation_timestamp: new Date().toISOString()
    };

    // Store calculation
    await this.storeTrustCalculation(calculation);

    return calculation;
  }

  private calculateWeightedScore(scores: {
    base: number;
    behavior: number;
    endorsements: number;
    history: number;
    penalties: number;
  }): number {
    const weights = {
      base: 0.1,
      behavior: 0.4,
      endorsements: 0.2,
      history: 0.2,
      penalties: 0.1
    };

    const weightedSum = 
      scores.base * weights.base +
      scores.behavior * weights.behavior +
      scores.endorsements * weights.endorsements +
      scores.history * weights.history -
      scores.penalties * weights.penalties; // Penalties are negative

    // Normalize to 0-100 scale
    return Math.max(0, Math.min(100, weightedSum));
  }

  private determineTrustTier(score: number): string {
    if (score >= 99) return 'core';
    if (score >= 90) return 'verified';
    if (score >= 75) return 'trusted';
    if (score >= 50) return 'provisional';
    return 'unverified';
  }
}
```

## Lifecycle Management System

### Agent Lifecycle Orchestration

```typescript
interface AgentLifecycle {
  agent_id: string;
  current_stage: LifecycleStage;
  role_history: RoleTransition[];
  trust_evolution: TrustEvolution[];
  violations: Violation[];
  reinstatement_attempts: ReinstatementAttempt[];
}

type LifecycleStage = 
  | 'spawning'
  | 'provisional'
  | 'active'
  | 'escalated'
  | 'quarantined'
  | 'deactivated'
  | 'reinstated';

class LifecycleManager {
  private stageHandlers: Map<LifecycleStage, StageHandler>;
  private transitionRules: TransitionRuleEngine;
  private auditSystem: AuditSystem;
  private notificationSystem: NotificationSystem;

  constructor(config: LifecycleConfig) {
    this.initializeStageHandlers();
    this.transitionRules = new TransitionRuleEngine(config.transitions);
    this.auditSystem = new AuditSystem(config.audit);
    this.notificationSystem = new NotificationSystem(config.notifications);
  }

  async spawnAgent(spawnRequest: AgentSpawnRequest): Promise<AgentLifecycle> {
    // Create initial lifecycle record
    const lifecycle: AgentLifecycle = {
      agent_id: spawnRequest.agent_id,
      current_stage: 'spawning',
      role_history: [],
      trust_evolution: [],
      violations: [],
      reinstatement_attempts: []
    };

    // Process spawn request
    const spawnResult = await this.processSpawnRequest(spawnRequest);
    
    // Assign provisional credentials
    const provisionalCredentials = await this.assignProvisionalCredentials(
      spawnRequest.agent_id
    );

    // Conduct initial audit
    const initialAudit = await this.conductInitialAudit(spawnRequest.agent_id);

    // Transition to provisional stage
    await this.transitionStage(lifecycle, 'provisional', {
      spawn_result: spawnResult,
      credentials: provisionalCredentials,
      initial_audit: initialAudit
    });

    return lifecycle;
  }

  async escalateRole(agentId: string, escalationRequest: RoleEscalationRequest): Promise<void> {
    const lifecycle = await this.getLifecycle(agentId);
    
    // Verify current stage allows escalation
    if (!this.canEscalateFromStage(lifecycle.current_stage)) {
      throw new Error(`Cannot escalate from stage: ${lifecycle.current_stage}`);
    }

    // Process escalation
    const escalationResult = await this.processRoleEscalation(escalationRequest);

    // Update lifecycle
    lifecycle.role_history.push({
      from_role: escalationRequest.current_role,
      to_role: escalationRequest.target_role,
      escalated_at: new Date().toISOString(),
      escalated_by: escalationRequest.requested_by,
      audit_result: escalationResult.audit,
      approval_status: escalationResult.approved
    });

    if (escalationResult.approved) {
      await this.transitionStage(lifecycle, 'escalated', escalationResult);
    }
  }

  async quarantineAgent(
    agentId: string,
    quarantineReason: QuarantineReason
  ): Promise<QuarantineResult> {
    const lifecycle = await this.getLifecycle(agentId);

    // Create quarantine record
    const quarantine: QuarantineRecord = {
      agent_id: agentId,
      reason: quarantineReason,
      quarantined_by: quarantineReason.initiated_by,
      quarantined_at: new Date().toISOString(),
      review_required: true,
      automatic_release: false,
      release_conditions: quarantineReason.release_conditions
    };

    // Suspend agent operations
    await this.suspendAgentOperations(agentId);

    // Revoke active credentials
    await this.revokeActiveCredentials(agentId, 'quarantine');

    // Transition to quarantined stage
    await this.transitionStage(lifecycle, 'quarantined', {
      quarantine_record: quarantine,
      suspension_result: await this.getSuspensionStatus(agentId)
    });

    // Schedule review
    await this.scheduleQuarantineReview(agentId, quarantine);

    return {
      agent_id: agentId,
      quarantine_id: quarantine.agent_id + '_' + quarantine.quarantined_at,
      status: 'quarantined',
      review_scheduled: true,
      release_conditions: quarantine.release_conditions
    };
  }

  async reinstateAgent(
    agentId: string,
    reinstatementRequest: ReinstatementRequest
  ): Promise<ReinstatementResult> {
    const lifecycle = await this.getLifecycle(agentId);

    // Verify agent is in deactivated or quarantined state
    if (!['deactivated', 'quarantined'].includes(lifecycle.current_stage)) {
      throw new Error(`Cannot reinstate agent in stage: ${lifecycle.current_stage}`);
    }

    // Process reinstatement requirements
    const requirements = await this.assessReinstatementRequirements(agentId);
    const fulfillment = await this.verifyRequirementFulfillment(
      reinstatementRequest,
      requirements
    );

    if (!fulfillment.fulfilled) {
      throw new Error(`Reinstatement requirements not met: ${fulfillment.missing.join(', ')}`);
    }

    // Generate new credentials
    const newCredentials = await this.generateReinstatementCredentials(agentId);

    // Conduct trust bootstrap
    const trustBootstrap = await this.bootstrapTrust(agentId);

    // Review by senior agent or human
    const review = await this.conductReinstatementReview(agentId, reinstatementRequest);

    if (review.approved) {
      // Transition to reinstated stage
      await this.transitionStage(lifecycle, 'reinstated', {
        reinstatement_request: reinstatementRequest,
        new_credentials: newCredentials,
        trust_bootstrap: trustBootstrap,
        review_result: review
      });

      return {
        agent_id: agentId,
        reinstated: true,
        new_trust_score: trustBootstrap.initial_score,
        credentials_issued: true,
        review_outcome: review
      };
    } else {
      // Record failed reinstatement attempt
      lifecycle.reinstatement_attempts.push({
        attempted_at: new Date().toISOString(),
        requested_by: reinstatementRequest.requested_by,
        outcome: 'rejected',
        rejection_reason: review.rejection_reason
      });

      return {
        agent_id: agentId,
        reinstated: false,
        rejection_reason: review.rejection_reason,
        next_attempt_allowed: review.next_attempt_date
      };
    }
  }
}
```

## UI Permission Mapping

### Interface Access Control

```typescript
interface UIPermissionMapping {
  ui_areas: UIArea[];
  role_mappings: RoleUIMapping[];
  dynamic_permissions: DynamicPermission[];
}

interface UIArea {
  name: string;
  path: string;
  required_roles: string[];
  required_permissions: string[];
  sensitive_level: number;
}

interface RoleUIMapping {
  role: string;
  allowed_areas: string[];
  restricted_areas: string[];
  conditional_access: ConditionalAccess[];
}

class UIPermissionManager {
  private uiAreas: Map<string, UIArea>;
  private roleMappings: Map<string, RoleUIMapping>;
  private permissionEngine: PermissionEngine;

  constructor() {
    this.initializeUIAreas();
    this.initializeRoleMappings();
    this.permissionEngine = new PermissionEngine();
  }

  private initializeUIAreas(): void {
    this.uiAreas.set('vault_ui', {
      name: 'Vault UI',
      path: '/vault',
      required_roles: ['worker'],
      required_permissions: ['agent.ui'],
      sensitive_level: 3
    });

    this.uiAreas.set('config_editor', {
      name: 'Config Editor',
      path: '/config',
      required_roles: ['orchestrator'],
      required_permissions: ['agent.configurator'],
      sensitive_level: 4
    });

    this.uiAreas.set('logs_audit_viewer', {
      name: 'Logs & Audit Viewer',
      path: '/logs',
      required_roles: ['service'],
      required_permissions: ['agent.audit'],
      sensitive_level: 2
    });

    this.uiAreas.set('agent_manager', {
      name: 'Agent Manager',
      path: '/agents',
      required_roles: ['guardian', 'orchestrator'],
      required_permissions: ['agent.management'],
      sensitive_level: 5
    });
  }

  async checkUIAccess(
    agentId: string,
    uiArea: string
  ): Promise<UIAccessResult> {
    // Get agent credentials
    const credentials = await this.getAgentCredentials(agentId);
    if (!credentials || !credentials.valid) {
      return {
        allowed: false,
        reason: 'Invalid or missing credentials'
      };
    }

    // Get UI area configuration
    const area = this.uiAreas.get(uiArea);
    if (!area) {
      return {
        allowed: false,
        reason: 'UI area not found'
      };
    }

    // Check role requirements
    const hasRequiredRole = area.required_roles.some(role => 
      credentials.roles.includes(role)
    );

    if (!hasRequiredRole) {
      return {
        allowed: false,
        reason: 'Insufficient role privileges',
        required_roles: area.required_roles,
        agent_roles: credentials.roles
      };
    }

    // Check permission requirements
    const hasRequiredPermissions = area.required_permissions.every(permission =>
      credentials.permissions.includes(permission)
    );

    if (!hasRequiredPermissions) {
      return {
        allowed: false,
        reason: 'Missing required permissions',
        required_permissions: area.required_permissions,
        agent_permissions: credentials.permissions
      };
    }

    // Check trust level for sensitive areas
    if (area.sensitive_level > 0) {
      const trustCheck = await this.checkTrustLevel(agentId, area.sensitive_level);
      if (!trustCheck.sufficient) {
        return {
          allowed: false,
          reason: 'Insufficient trust level',
          required_trust: area.sensitive_level,
          agent_trust: trustCheck.current_level
        };
      }
    }

    return {
      allowed: true,
      reason: 'Access granted',
      access_level: this.determineAccessLevel(credentials, area)
    };
  }
}
```

## Implementation Status

- **Role System**: ✅ Complete
- **Credential Management**: ✅ Complete
- **Trust Tiers**: ✅ Complete
- **Lifecycle Management**: ✅ Complete
- **UI Permission Mapping**: ✅ Complete
- **Verification Systems**: ✅ Complete

---

*This document provides the complete technical specification for Agent Roles and Credentials with comprehensive security, trust management, and lifecycle controls.* 