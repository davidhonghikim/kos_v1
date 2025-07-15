---
version: "1.0.0"
last_updated: "2025-01-27"
status: "draft"
type: "specification"
category: "security"
tags: ["consent", "override", "ledger", "compliance", "sovereignty"]
related_docs:
  - "future/security/13_agent-trust-identity-protocols.md"
  - "future/security/14_agent-trust-framework-comprehensive.md"
  - "future/governance/07_comprehensive-governance-model.md"
complexity: "high"
implementation_status: "planned"
code_references:
  - "src/utils/consentManager.ts"
  - "src/store/consentStore.ts"
  - "src/components/consent/"
decision_scope: "system-wide"
external_references:
  - "https://gdpr.eu/what-is-gdpr/"
  - "https://www.hhs.gov/hipaa/index.html"
  - "https://oag.ca.gov/privacy/ccpa"
changelog:
  - "2025-01-27: Initial migration from brainstorm file 175"
---

# Consent Ledger and User Override System

**Agent Context**: This document defines the comprehensive architecture, protocols, and enforcement logic for a secure, auditable consent ledger and user override system in the kAI/kOS ecosystem. Agents should understand this as the infrastructure that ensures human sovereignty, legal compliance (GDPR, HIPAA, CCPA), and trust in automated agent behavior through immutable consent records and real-time override capabilities.

## System Architecture Overview

The Consent Ledger and User Override System provides:
- Immutable record of all user consents granted or revoked
- Local-first enforcement of user control and override rights
- Cross-agent enforceable rules via consent propagation
- Support for granular, revocable, and time-bound consent
- Self-contained modules compatible with offline-first systems

## Core Data Structures

```typescript
interface ConsentToken {
  id: string;
  issuedAt: string;
  expiresAt?: string;
  agentId: string;
  action: string;
  target: string;
  scope: ConsentScope;
  granted: boolean;
  conditions: ConsentCondition[];
  signature: string;
  nonce: string;
}

interface ConsentScope {
  resource: string;
  permissions: Permission[];
  constraints: Constraint[];
  context: ContextRequirement[];
}

interface Permission {
  type: 'read' | 'write' | 'execute' | 'delete' | 'share';
  level: 'full' | 'limited' | 'conditional';
  restrictions: string[];
}

interface Constraint {
  type: 'time' | 'location' | 'frequency' | 'amount' | 'purpose';
  value: any;
  operator: 'eq' | 'lt' | 'gt' | 'in' | 'not_in';
}

interface ContextRequirement {
  key: string;
  value: any;
  required: boolean;
}

interface ConsentCondition {
  type: 'temporal' | 'contextual' | 'behavioral' | 'approval';
  condition: string;
  parameters: Record<string, any>;
  active: boolean;
}

interface OverrideLog {
  id: string;
  timestamp: string;
  agentId: string;
  action: string;
  target: string;
  overrideBy: string;
  reason: string;
  outcome: 'action_blocked' | 'action_modified' | 'action_allowed' | 'escalated';
  context: OverrideContext;
  signature: string;
}

interface OverrideContext {
  originalRequest: any;
  userLocation?: string;
  deviceInfo?: string;
  sessionInfo?: string;
  riskAssessment?: RiskAssessment;
}

interface RiskAssessment {
  level: 'low' | 'medium' | 'high' | 'critical';
  factors: string[];
  score: number;
  recommendation: string;
}

class ConsentManager {
  private consentLedger: Map<string, ConsentToken> = new Map();
  private overrideLogs: Map<string, OverrideLog> = new Map();
  private policyEngine: ConsentPolicyEngine;
  private cryptoManager: ConsentCryptoManager;
  private storageManager: ConsentStorageManager;

  constructor() {
    this.policyEngine = new ConsentPolicyEngine();
    this.cryptoManager = new ConsentCryptoManager();
    this.storageManager = new ConsentStorageManager();
  }

  async hasConsent(agentId: string, action: string, target: string, context?: any): Promise<boolean> {
    const relevantConsents = this.findRelevantConsents(agentId, action, target);
    
    for (const consent of relevantConsents) {
      // Check if consent is still valid
      if (!this.isConsentValid(consent)) {
        continue;
      }

      // Check conditions
      const conditionsMet = await this.checkConditions(consent, context);
      if (!conditionsMet) {
        continue;
      }

      // Check constraints
      const constraintsSatisfied = await this.checkConstraints(consent, context);
      if (!constraintsSatisfied) {
        continue;
      }

      return consent.granted;
    }

    return false; // No valid consent found, default to deny
  }

  async grantConsent(
    agentId: string,
    action: string,
    target: string,
    scope: ConsentScope,
    conditions: ConsentCondition[] = [],
    expiresAt?: string
  ): Promise<ConsentToken> {
    const consentId = crypto.randomUUID();
    const nonce = crypto.randomUUID();
    const issuedAt = new Date().toISOString();

    const consentToken: Omit<ConsentToken, 'signature'> = {
      id: consentId,
      issuedAt,
      expiresAt,
      agentId,
      action,
      target,
      scope,
      granted: true,
      conditions,
      nonce
    };

    // Sign the consent token
    const signature = await this.cryptoManager.signConsent(consentToken);
    const fullToken: ConsentToken = { ...consentToken, signature };

    // Store in ledger
    this.consentLedger.set(consentId, fullToken);

    // Persist to storage
    await this.storageManager.storeConsent(fullToken);

    // Log the grant
    await this.logConsentAction('grant', fullToken);

    return fullToken;
  }

  async revokeConsent(tokenId: string, reason: string = 'User revocation'): Promise<void> {
    const consent = this.consentLedger.get(tokenId);
    if (!consent) {
      throw new Error('Consent token not found');
    }

    // Create revocation token
    const revocationToken: ConsentToken = {
      ...consent,
      id: crypto.randomUUID(),
      issuedAt: new Date().toISOString(),
      granted: false,
      conditions: [...consent.conditions, {
        type: 'approval',
        condition: 'revoked',
        parameters: { reason, originalTokenId: tokenId },
        active: true
      }]
    };

    // Sign revocation
    revocationToken.signature = await this.cryptoManager.signConsent(revocationToken);

    // Store revocation
    this.consentLedger.set(revocationToken.id, revocationToken);
    await this.storageManager.storeConsent(revocationToken);

    // Log the revocation
    await this.logConsentAction('revoke', revocationToken);
  }

  async listConsents(agentId?: string, active?: boolean): Promise<ConsentToken[]> {
    let consents = Array.from(this.consentLedger.values());

    if (agentId) {
      consents = consents.filter(c => c.agentId === agentId);
    }

    if (active !== undefined) {
      consents = consents.filter(c => {
        const isValid = this.isConsentValid(c);
        return active ? (isValid && c.granted) : (!isValid || !c.granted);
      });
    }

    return consents.sort((a, b) => new Date(b.issuedAt).getTime() - new Date(a.issuedAt).getTime());
  }

  async overrideAction(
    agentId: string,
    action: string,
    target: string,
    overrideBy: string,
    reason: string,
    context: OverrideContext
  ): Promise<OverrideResult> {
    const overrideId = crypto.randomUUID();
    
    // Assess risk of the action
    const riskAssessment = await this.assessActionRisk(agentId, action, target, context);
    
    // Determine override outcome based on risk and policy
    const outcome = await this.determineOverrideOutcome(riskAssessment, reason, context);

    // Create override log
    const overrideLog: Omit<OverrideLog, 'signature'> = {
      id: overrideId,
      timestamp: new Date().toISOString(),
      agentId,
      action,
      target,
      overrideBy,
      reason,
      outcome,
      context: {
        ...context,
        riskAssessment
      }
    };

    // Sign the override log
    const signature = await this.cryptoManager.signOverride(overrideLog);
    const fullLog: OverrideLog = { ...overrideLog, signature };

    // Store override log
    this.overrideLogs.set(overrideId, fullLog);
    await this.storageManager.storeOverride(fullLog);

    // Execute override action
    await this.executeOverride(fullLog);

    return {
      overrideId,
      outcome,
      riskLevel: riskAssessment.level,
      message: this.getOverrideMessage(outcome, riskAssessment)
    };
  }

  private findRelevantConsents(agentId: string, action: string, target: string): ConsentToken[] {
    return Array.from(this.consentLedger.values()).filter(consent => {
      // Exact match
      if (consent.agentId === agentId && consent.action === action && consent.target === target) {
        return true;
      }

      // Wildcard matching
      if (consent.agentId === agentId || consent.agentId === '*') {
        if (consent.action === action || consent.action === '*') {
          if (consent.target === target || consent.target === '*' || target.startsWith(consent.target)) {
            return true;
          }
        }
      }

      return false;
    });
  }

  private isConsentValid(consent: ConsentToken): boolean {
    // Check expiration
    if (consent.expiresAt && new Date() > new Date(consent.expiresAt)) {
      return false;
    }

    // Check if revoked
    const revocations = Array.from(this.consentLedger.values()).filter(c => 
      c.conditions.some(cond => 
        cond.type === 'approval' && 
        cond.condition === 'revoked' && 
        cond.parameters?.originalTokenId === consent.id
      )
    );

    return revocations.length === 0;
  }

  private async checkConditions(consent: ConsentToken, context?: any): Promise<boolean> {
    for (const condition of consent.conditions) {
      if (!condition.active) continue;

      const conditionMet = await this.evaluateCondition(condition, context);
      if (!conditionMet) {
        return false;
      }
    }

    return true;
  }

  private async checkConstraints(consent: ConsentToken, context?: any): Promise<boolean> {
    for (const constraint of consent.scope.constraints) {
      const constraintSatisfied = await this.evaluateConstraint(constraint, context);
      if (!constraintSatisfied) {
        return false;
      }
    }

    return true;
  }

  private async evaluateCondition(condition: ConsentCondition, context?: any): Promise<boolean> {
    switch (condition.type) {
      case 'temporal':
        return this.evaluateTemporalCondition(condition, context);
      case 'contextual':
        return this.evaluateContextualCondition(condition, context);
      case 'behavioral':
        return this.evaluateBehavioralCondition(condition, context);
      case 'approval':
        return this.evaluateApprovalCondition(condition, context);
      default:
        return true;
    }
  }

  private async evaluateConstraint(constraint: Constraint, context?: any): Promise<boolean> {
    const contextValue = context?.[constraint.type];
    
    switch (constraint.operator) {
      case 'eq':
        return contextValue === constraint.value;
      case 'lt':
        return contextValue < constraint.value;
      case 'gt':
        return contextValue > constraint.value;
      case 'in':
        return Array.isArray(constraint.value) && constraint.value.includes(contextValue);
      case 'not_in':
        return Array.isArray(constraint.value) && !constraint.value.includes(contextValue);
      default:
        return true;
    }
  }

  private evaluateTemporalCondition(condition: ConsentCondition, context?: any): boolean {
    const now = new Date();
    const params = condition.parameters;

    if (params.startTime && now < new Date(params.startTime)) {
      return false;
    }

    if (params.endTime && now > new Date(params.endTime)) {
      return false;
    }

    if (params.daysOfWeek && !params.daysOfWeek.includes(now.getDay())) {
      return false;
    }

    if (params.hoursOfDay) {
      const currentHour = now.getHours();
      if (currentHour < params.hoursOfDay.start || currentHour > params.hoursOfDay.end) {
        return false;
      }
    }

    return true;
  }

  private evaluateContextualCondition(condition: ConsentCondition, context?: any): boolean {
    const params = condition.parameters;
    
    for (const [key, expectedValue] of Object.entries(params)) {
      if (context?.[key] !== expectedValue) {
        return false;
      }
    }

    return true;
  }

  private evaluateBehavioralCondition(condition: ConsentCondition, context?: any): boolean {
    // Implementation would check behavioral patterns
    return true;
  }

  private evaluateApprovalCondition(condition: ConsentCondition, context?: any): boolean {
    return condition.condition !== 'revoked';
  }

  private async assessActionRisk(
    agentId: string,
    action: string,
    target: string,
    context: OverrideContext
  ): Promise<RiskAssessment> {
    const factors: string[] = [];
    let score = 0;

    // Assess based on action type
    const highRiskActions = ['delete', 'transfer', 'publish', 'share_external'];
    if (highRiskActions.includes(action)) {
      factors.push('high_risk_action');
      score += 30;
    }

    // Assess based on target sensitivity
    const sensitiveTargets = ['financial_data', 'personal_info', 'credentials'];
    if (sensitiveTargets.some(st => target.includes(st))) {
      factors.push('sensitive_target');
      score += 25;
    }

    // Assess based on agent trust level
    const agentTrustLevel = await this.getAgentTrustLevel(agentId);
    if (agentTrustLevel < 0.7) {
      factors.push('low_trust_agent');
      score += 20;
    }

    // Assess based on context
    if (context.userLocation && !this.isKnownLocation(context.userLocation)) {
      factors.push('unknown_location');
      score += 15;
    }

    if (context.deviceInfo && !this.isTrustedDevice(context.deviceInfo)) {
      factors.push('untrusted_device');
      score += 10;
    }

    // Determine risk level
    let level: RiskAssessment['level'];
    let recommendation: string;

    if (score >= 70) {
      level = 'critical';
      recommendation = 'Block action and require explicit approval';
    } else if (score >= 50) {
      level = 'high';
      recommendation = 'Require additional verification';
    } else if (score >= 25) {
      level = 'medium';
      recommendation = 'Log and monitor action';
    } else {
      level = 'low';
      recommendation = 'Allow with standard logging';
    }

    return {
      level,
      factors,
      score,
      recommendation
    };
  }

  private async determineOverrideOutcome(
    riskAssessment: RiskAssessment,
    reason: string,
    context: OverrideContext
  ): Promise<OverrideLog['outcome']> {
    // Critical risk always blocks
    if (riskAssessment.level === 'critical') {
      return 'action_blocked';
    }

    // High risk requires explicit user approval
    if (riskAssessment.level === 'high') {
      const hasExplicitApproval = reason.includes('user_approved');
      return hasExplicitApproval ? 'action_allowed' : 'escalated';
    }

    // Medium risk can be modified or allowed based on reason
    if (riskAssessment.level === 'medium') {
      const isPreventive = reason.includes('preventive') || reason.includes('safety');
      return isPreventive ? 'action_modified' : 'action_allowed';
    }

    // Low risk is generally allowed
    return 'action_allowed';
  }

  private async executeOverride(overrideLog: OverrideLog): Promise<void> {
    switch (overrideLog.outcome) {
      case 'action_blocked':
        await this.blockAction(overrideLog);
        break;
      case 'action_modified':
        await this.modifyAction(overrideLog);
        break;
      case 'action_allowed':
        await this.allowAction(overrideLog);
        break;
      case 'escalated':
        await this.escalateAction(overrideLog);
        break;
    }
  }

  private async blockAction(overrideLog: OverrideLog): Promise<void> {
    // Implementation would prevent the action from executing
    console.log(`Action blocked: ${overrideLog.action} on ${overrideLog.target}`);
  }

  private async modifyAction(overrideLog: OverrideLog): Promise<void> {
    // Implementation would modify the action parameters
    console.log(`Action modified: ${overrideLog.action} on ${overrideLog.target}`);
  }

  private async allowAction(overrideLog: OverrideLog): Promise<void> {
    // Implementation would allow the action to proceed with logging
    console.log(`Action allowed: ${overrideLog.action} on ${overrideLog.target}`);
  }

  private async escalateAction(overrideLog: OverrideLog): Promise<void> {
    // Implementation would escalate to human oversight
    console.log(`Action escalated: ${overrideLog.action} on ${overrideLog.target}`);
  }

  private getOverrideMessage(outcome: OverrideLog['outcome'], riskAssessment: RiskAssessment): string {
    const messages = {
      'action_blocked': `Action blocked due to ${riskAssessment.level} risk: ${riskAssessment.recommendation}`,
      'action_modified': `Action modified to reduce risk: ${riskAssessment.recommendation}`,
      'action_allowed': `Action allowed with monitoring: ${riskAssessment.recommendation}`,
      'escalated': `Action escalated for human review: ${riskAssessment.recommendation}`
    };

    return messages[outcome];
  }

  private async logConsentAction(action: string, token: ConsentToken): Promise<void> {
    // Implementation would log consent actions for audit
    console.log(`Consent ${action}: ${token.id} for ${token.agentId}`);
  }

  private async getAgentTrustLevel(agentId: string): Promise<number> {
    // Implementation would retrieve agent trust level
    return 0.8; // Mock value
  }

  private isKnownLocation(location: string): boolean {
    // Implementation would check against known/trusted locations
    return true; // Mock value
  }

  private isTrustedDevice(deviceInfo: string): boolean {
    // Implementation would check device trust status
    return true; // Mock value
  }
}
```

## Cryptographic Security Layer

```typescript
class ConsentCryptoManager {
  private signingKey: CryptoKey | null = null;
  private verificationKey: CryptoKey | null = null;

  async initialize(): Promise<void> {
    const keyPair = await crypto.subtle.generateKey(
      { name: 'Ed25519', namedCurve: 'Ed25519' },
      true,
      ['sign', 'verify']
    );

    this.signingKey = keyPair.privateKey;
    this.verificationKey = keyPair.publicKey;
  }

  async signConsent(consent: Omit<ConsentToken, 'signature'>): Promise<string> {
    if (!this.signingKey) {
      throw new Error('Crypto manager not initialized');
    }

    const consentData = JSON.stringify({
      id: consent.id,
      issuedAt: consent.issuedAt,
      expiresAt: consent.expiresAt,
      agentId: consent.agentId,
      action: consent.action,
      target: consent.target,
      scope: consent.scope,
      granted: consent.granted,
      conditions: consent.conditions,
      nonce: consent.nonce
    });

    const signature = await crypto.subtle.sign(
      'Ed25519',
      this.signingKey,
      new TextEncoder().encode(consentData)
    );

    return Array.from(new Uint8Array(signature))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  async signOverride(override: Omit<OverrideLog, 'signature'>): Promise<string> {
    if (!this.signingKey) {
      throw new Error('Crypto manager not initialized');
    }

    const overrideData = JSON.stringify({
      id: override.id,
      timestamp: override.timestamp,
      agentId: override.agentId,
      action: override.action,
      target: override.target,
      overrideBy: override.overrideBy,
      reason: override.reason,
      outcome: override.outcome,
      context: override.context
    });

    const signature = await crypto.subtle.sign(
      'Ed25519',
      this.signingKey,
      new TextEncoder().encode(overrideData)
    );

    return Array.from(new Uint8Array(signature))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  async verifyConsentSignature(consent: ConsentToken): Promise<boolean> {
    if (!this.verificationKey) {
      throw new Error('Crypto manager not initialized');
    }

    try {
      const consentData = JSON.stringify({
        id: consent.id,
        issuedAt: consent.issuedAt,
        expiresAt: consent.expiresAt,
        agentId: consent.agentId,
        action: consent.action,
        target: consent.target,
        scope: consent.scope,
        granted: consent.granted,
        conditions: consent.conditions,
        nonce: consent.nonce
      });

      const signatureBytes = new Uint8Array(
        consent.signature.match(/.{2}/g)!.map(byte => parseInt(byte, 16))
      );

      return await crypto.subtle.verify(
        'Ed25519',
        this.verificationKey,
        signatureBytes,
        new TextEncoder().encode(consentData)
      );
    } catch (error) {
      console.error('Consent signature verification failed:', error);
      return false;
    }
  }

  async verifyOverrideSignature(override: OverrideLog): Promise<boolean> {
    if (!this.verificationKey) {
      throw new Error('Crypto manager not initialized');
    }

    try {
      const overrideData = JSON.stringify({
        id: override.id,
        timestamp: override.timestamp,
        agentId: override.agentId,
        action: override.action,
        target: override.target,
        overrideBy: override.overrideBy,
        reason: override.reason,
        outcome: override.outcome,
        context: override.context
      });

      const signatureBytes = new Uint8Array(
        override.signature.match(/.{2}/g)!.map(byte => parseInt(byte, 16))
      );

      return await crypto.subtle.verify(
        'Ed25519',
        this.verificationKey,
        signatureBytes,
        new TextEncoder().encode(overrideData)
      );
    } catch (error) {
      console.error('Override signature verification failed:', error);
      return false;
    }
  }
}
```

## Storage & Persistence Layer

```typescript
class ConsentStorageManager {
  private storageKey = 'kos_consent_ledger';
  private overrideKey = 'kos_override_logs';

  async storeConsent(consent: ConsentToken): Promise<void> {
    try {
      const existingData = await this.getStoredData(this.storageKey);
      const consents = existingData || [];
      
      consents.push({
        ...consent,
        storedAt: new Date().toISOString()
      });

      await this.saveStoredData(this.storageKey, consents);
    } catch (error) {
      console.error('Failed to store consent:', error);
      throw new Error('Consent storage failed');
    }
  }

  async storeOverride(override: OverrideLog): Promise<void> {
    try {
      const existingData = await this.getStoredData(this.overrideKey);
      const overrides = existingData || [];
      
      overrides.push({
        ...override,
        storedAt: new Date().toISOString()
      });

      await this.saveStoredData(this.overrideKey, overrides);
    } catch (error) {
      console.error('Failed to store override:', error);
      throw new Error('Override storage failed');
    }
  }

  async loadConsents(): Promise<ConsentToken[]> {
    try {
      const data = await this.getStoredData(this.storageKey);
      return data || [];
    } catch (error) {
      console.error('Failed to load consents:', error);
      return [];
    }
  }

  async loadOverrides(): Promise<OverrideLog[]> {
    try {
      const data = await this.getStoredData(this.overrideKey);
      return data || [];
    } catch (error) {
      console.error('Failed to load overrides:', error);
      return [];
    }
  }

  private async getStoredData(key: string): Promise<any> {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      const result = await chrome.storage.local.get(key);
      return result[key];
    } else if (typeof localStorage !== 'undefined') {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : null;
    } else {
      throw new Error('No storage mechanism available');
    }
  }

  private async saveStoredData(key: string, data: any): Promise<void> {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      await chrome.storage.local.set({ [key]: data });
    } else if (typeof localStorage !== 'undefined') {
      localStorage.setItem(key, JSON.stringify(data));
    } else {
      throw new Error('No storage mechanism available');
    }
  }
}
```

This comprehensive Consent Ledger and User Override System provides enterprise-grade consent management with cryptographic security, risk assessment, and compliance features essential for maintaining human sovereignty and trust in automated agent behavior across the kOS ecosystem. 