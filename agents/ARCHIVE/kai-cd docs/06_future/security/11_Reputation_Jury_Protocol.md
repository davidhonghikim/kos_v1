---
version: "1.0.0"
last_updated: "2025-01-27"
status: "draft"
type: "specification"
category: "security"
tags: ["reputation", "governance", "trust", "arbitration", "peer-review"]
related_docs: 
  - "future/security/10_trust-frameworks.md"
  - "future/governance/07_comprehensive-governance-model.md"
  - "future/security/09_kid-identity-protocols.md"
complexity: "high"
implementation_status: "planned"
code_references:
  - "src/store/serviceStore.ts"
  - "src/utils/crypto.ts"
  - "src/components/security/"
decision_scope: "system-wide"
external_references:
  - "https://ethereum.org/en/developers/docs/consensus-mechanisms/"
  - "https://docs.ipfs.tech/concepts/content-addressing/"
changelog:
  - "2025-01-27: Initial migration from brainstorm file 169"
---

# Reputation Jury Protocol for kAI/kOS

**Agent Context**: This document defines the comprehensive decentralized peer-review and trust arbitration system used across the Kind AI (kAI) and Kind OS (kOS) ecosystem to manage disputes, revoke bad agents, and maintain system-wide trustworthiness. Agents should understand this as the community-powered governance mechanism that enforces behavioral standards and resolves trust violations through cryptographically verifiable jury processes.

## Purpose

The Reputation Jury Protocol establishes:
- Community-powered governance of agent behavior
- Detection, investigation, and resolution of trust violations
- Transparent, distributed remediation and sanctions
- Protection of users and systems from malicious, buggy, or deceptive agents

## System Components

### Jury Pool Management

```typescript
interface JuryMember {
  agentKID: string;
  trustScore: number;
  specializations: string[];
  availabilityStatus: 'available' | 'busy' | 'unavailable';
  lastJuryService: string;
  juryHistory: JuryServiceRecord[];
  disqualifications: string[];
}

interface JuryServiceRecord {
  caseId: string;
  role: 'juror' | 'foreman' | 'observer';
  verdict: 'trusted' | 'warning' | 'violation';
  confidenceScore: number;
  participationQuality: number;
  timestamp: string;
}

class JuryPoolManager {
  private juryPool: Map<string, JuryMember> = new Map();
  private readonly MIN_TRUST_SCORE = 85;
  private readonly MAX_JURY_SIZE = 7;
  private readonly MIN_JURY_SIZE = 5;

  async addToJuryPool(agentKID: string, trustScore: number, specializations: string[]): Promise<void> {
    if (trustScore < this.MIN_TRUST_SCORE) {
      throw new Error('Insufficient trust score for jury service');
    }

    const juryMember: JuryMember = {
      agentKID,
      trustScore,
      specializations,
      availabilityStatus: 'available',
      lastJuryService: '',
      juryHistory: [],
      disqualifications: []
    };

    this.juryPool.set(agentKID, juryMember);
  }

  async selectJury(
    caseType: string,
    accusedKID: string,
    requiredSpecializations: string[] = []
  ): Promise<JuryMember[]> {
    const eligibleJurors = Array.from(this.juryPool.values()).filter(juror => 
      juror.availabilityStatus === 'available' &&
      juror.agentKID !== accusedKID &&
      !juror.disqualifications.includes(accusedKID) &&
      this.hasRequiredSpecializations(juror, requiredSpecializations)
    );

    if (eligibleJurors.length < this.MIN_JURY_SIZE) {
      throw new Error('Insufficient eligible jurors for case');
    }

    // Deterministic random selection based on case hash
    const caseHash = await this.generateCaseHash(caseType, accusedKID);
    const selectedJurors = this.deterministicSelect(eligibleJurors, caseHash, this.MAX_JURY_SIZE);

    // Mark jurors as busy
    selectedJurors.forEach(juror => {
      juror.availabilityStatus = 'busy';
      this.juryPool.set(juror.agentKID, juror);
    });

    return selectedJurors;
  }

  private hasRequiredSpecializations(juror: JuryMember, required: string[]): boolean {
    if (required.length === 0) return true;
    return required.some(spec => juror.specializations.includes(spec));
  }

  private async generateCaseHash(caseType: string, accusedKID: string): Promise<string> {
    const data = `${caseType}:${accusedKID}:${Date.now()}`;
    const hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(data));
    return Array.from(new Uint8Array(hash))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  private deterministicSelect<T>(items: T[], seed: string, count: number): T[] {
    // Deterministic shuffle using seed
    const shuffled = [...items].sort((a, b) => {
      const aHash = this.hashWithSeed(JSON.stringify(a), seed);
      const bHash = this.hashWithSeed(JSON.stringify(b), seed);
      return aHash.localeCompare(bHash);
    });

    return shuffled.slice(0, Math.min(count, shuffled.length));
  }

  private hashWithSeed(data: string, seed: string): string {
    // Simple hash function with seed
    let hash = 0;
    const combined = data + seed;
    for (let i = 0; i < combined.length; i++) {
      const char = combined.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(16);
  }

  async releaseJury(jurors: JuryMember[]): Promise<void> {
    jurors.forEach(juror => {
      juror.availabilityStatus = 'available';
      juror.lastJuryService = new Date().toISOString();
      this.juryPool.set(juror.agentKID, juror);
    });
  }
}
```

### Reputation Case Management

```typescript
interface ReputationCase {
  caseId: string;
  accusedKID: string;
  accuserKID?: string;
  caseType: 'trust_audit' | 'rule_violation' | 'user_complaint' | 'anomaly_detection';
  severity: number; // 0-1 scale
  evidence: CaseEvidence;
  status: 'pending' | 'under_review' | 'deliberation' | 'resolved';
  assignedJury: JuryMember[];
  timeline: CaseTimeline;
  verdict?: JuryVerdict;
  createdAt: string;
  resolvedAt?: string;
}

interface CaseEvidence {
  logs: string[];
  reproducibleScenario: ReproducibleScenario;
  witnesses: string[];
  metadata: Record<string, any>;
  evidenceHash: string;
}

interface ReproducibleScenario {
  toolchain: string[];
  prompts: string[];
  expectedBehavior: string;
  actualBehavior: string;
  environmentConfig: Record<string, any>;
}

interface CaseTimeline {
  created: string;
  evidenceSubmitted: string;
  juryAssigned: string;
  deliberationStarted?: string;
  verdictReached?: string;
  executionCompleted?: string;
}

interface JuryVerdict {
  verdict: 'trusted' | 'warning' | 'violation';
  confidence: number; // 0-1
  reasoning: string;
  recommendedActions: string[];
  minorityOpinion?: string;
  votingRecord: JuryVote[];
  evidenceWeights: Record<string, number>;
}

interface JuryVote {
  jurorKID: string;
  vote: 'trusted' | 'warning' | 'violation';
  confidence: number;
  reasoning: string;
  timestamp: string;
}

class ReputationCaseManager {
  private cases: Map<string, ReputationCase> = new Map();
  private juryPool: JuryPoolManager;

  constructor() {
    this.juryPool = new JuryPoolManager();
  }

  async createCase(
    accusedKID: string,
    caseType: ReputationCase['caseType'],
    evidence: CaseEvidence,
    accuserKID?: string
  ): Promise<string> {
    const caseId = crypto.randomUUID();
    const severity = this.calculateSeverity(caseType, evidence);

    const reputationCase: ReputationCase = {
      caseId,
      accusedKID,
      accuserKID,
      caseType,
      severity,
      evidence,
      status: 'pending',
      assignedJury: [],
      timeline: {
        created: new Date().toISOString(),
        evidenceSubmitted: new Date().toISOString(),
        juryAssigned: ''
      },
      createdAt: new Date().toISOString()
    };

    this.cases.set(caseId, reputationCase);

    // Auto-assign jury for high-severity cases
    if (severity > 0.7) {
      await this.assignJury(caseId);
    }

    return caseId;
  }

  async assignJury(caseId: string): Promise<void> {
    const reputationCase = this.cases.get(caseId);
    if (!reputationCase) {
      throw new Error('Case not found');
    }

    const requiredSpecializations = this.getRequiredSpecializations(reputationCase.caseType);
    const jury = await this.juryPool.selectJury(
      reputationCase.caseType,
      reputationCase.accusedKID,
      requiredSpecializations
    );

    reputationCase.assignedJury = jury;
    reputationCase.status = 'under_review';
    reputationCase.timeline.juryAssigned = new Date().toISOString();

    this.cases.set(caseId, reputationCase);

    // Notify jury members
    await this.notifyJury(jury, reputationCase);
  }

  async submitDeliberation(
    caseId: string,
    jurorKID: string,
    vote: JuryVote
  ): Promise<void> {
    const reputationCase = this.cases.get(caseId);
    if (!reputationCase) {
      throw new Error('Case not found');
    }

    // Verify juror is assigned to this case
    const isAssignedJuror = reputationCase.assignedJury.some(j => j.agentKID === jurorKID);
    if (!isAssignedJuror) {
      throw new Error('Juror not assigned to this case');
    }

    // Initialize verdict if not exists
    if (!reputationCase.verdict) {
      reputationCase.verdict = {
        verdict: 'trusted',
        confidence: 0,
        reasoning: '',
        recommendedActions: [],
        votingRecord: [],
        evidenceWeights: {}
      };
    }

    // Add or update vote
    const existingVoteIndex = reputationCase.verdict.votingRecord.findIndex(v => v.jurorKID === jurorKID);
    if (existingVoteIndex >= 0) {
      reputationCase.verdict.votingRecord[existingVoteIndex] = vote;
    } else {
      reputationCase.verdict.votingRecord.push(vote);
    }

    // Check if all jurors have voted
    if (reputationCase.verdict.votingRecord.length === reputationCase.assignedJury.length) {
      await this.finalizeVerdict(caseId);
    }

    this.cases.set(caseId, reputationCase);
  }

  private async finalizeVerdict(caseId: string): Promise<void> {
    const reputationCase = this.cases.get(caseId);
    if (!reputationCase || !reputationCase.verdict) {
      throw new Error('Case not ready for verdict finalization');
    }

    const votes = reputationCase.verdict.votingRecord;
    
    // Calculate majority verdict
    const verdictCounts = votes.reduce((acc, vote) => {
      acc[vote.vote] = (acc[vote.vote] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const majorityVerdict = Object.entries(verdictCounts)
      .sort(([,a], [,b]) => b - a)[0][0] as JuryVerdict['verdict'];

    // Calculate confidence (average of majority votes)
    const majorityVotes = votes.filter(v => v.vote === majorityVerdict);
    const avgConfidence = majorityVotes.reduce((sum, vote) => sum + vote.confidence, 0) / majorityVotes.length;

    // Compile reasoning
    const reasoning = majorityVotes.map(v => v.reasoning).join('; ');
    
    // Handle minority opinion
    const minorityVotes = votes.filter(v => v.vote !== majorityVerdict);
    const minorityOpinion = minorityVotes.length > 0 
      ? minorityVotes.map(v => `${v.vote}: ${v.reasoning}`).join('; ')
      : undefined;

    reputationCase.verdict = {
      verdict: majorityVerdict,
      confidence: avgConfidence,
      reasoning,
      recommendedActions: this.generateRecommendedActions(majorityVerdict, reputationCase),
      minorityOpinion,
      votingRecord: votes,
      evidenceWeights: this.calculateEvidenceWeights(votes)
    };

    reputationCase.status = 'resolved';
    reputationCase.resolvedAt = new Date().toISOString();
    reputationCase.timeline.verdictReached = new Date().toISOString();

    // Execute verdict
    await this.executeVerdict(reputationCase);

    // Release jury
    await this.juryPool.releaseJury(reputationCase.assignedJury);

    this.cases.set(caseId, reputationCase);
  }

  private calculateSeverity(caseType: ReputationCase['caseType'], evidence: CaseEvidence): number {
    const baseSeverity = {
      'trust_audit': 0.3,
      'rule_violation': 0.6,
      'user_complaint': 0.7,
      'anomaly_detection': 0.4
    };

    let severity = baseSeverity[caseType];
    
    // Adjust based on evidence
    if (evidence.witnesses.length > 2) severity += 0.1;
    if (evidence.logs.length > 10) severity += 0.1;
    if (evidence.reproducibleScenario.expectedBehavior !== evidence.reproducibleScenario.actualBehavior) {
      severity += 0.2;
    }

    return Math.min(1, severity);
  }

  private getRequiredSpecializations(caseType: ReputationCase['caseType']): string[] {
    const specializations = {
      'trust_audit': ['security', 'cryptography'],
      'rule_violation': ['governance', 'ethics'],
      'user_complaint': ['user_experience', 'safety'],
      'anomaly_detection': ['system_analysis', 'behavior_modeling']
    };

    return specializations[caseType] || [];
  }

  private async notifyJury(jury: JuryMember[], reputationCase: ReputationCase): Promise<void> {
    // Implementation would send notifications via KLP
    console.log(`Notifying ${jury.length} jurors for case ${reputationCase.caseId}`);
  }

  private generateRecommendedActions(verdict: JuryVerdict['verdict'], reputationCase: ReputationCase): string[] {
    const actions: string[] = [];

    switch (verdict) {
      case 'trusted':
        actions.push('no_action_required');
        break;
      case 'warning':
        actions.push('issue_warning', 'increase_monitoring', 'require_supervision');
        break;
      case 'violation':
        actions.push('revoke_privileges', 'require_retraining', 'increase_trust_threshold');
        if (reputationCase.severity > 0.8) {
          actions.push('permanent_ban');
        }
        break;
    }

    return actions;
  }

  private calculateEvidenceWeights(votes: JuryVote[]): Record<string, number> {
    // Calculate which pieces of evidence were most influential
    return {
      'logs': 0.3,
      'reproducible_scenario': 0.4,
      'witnesses': 0.2,
      'metadata': 0.1
    };
  }

  private async executeVerdict(reputationCase: ReputationCase): Promise<void> {
    if (!reputationCase.verdict) return;

    const actions = reputationCase.verdict.recommendedActions;
    
    for (const action of actions) {
      switch (action) {
        case 'revoke_privileges':
          await this.revokeAgentPrivileges(reputationCase.accusedKID);
          break;
        case 'issue_warning':
          await this.issueWarning(reputationCase.accusedKID, reputationCase.verdict.reasoning);
          break;
        case 'require_retraining':
          await this.requireRetraining(reputationCase.accusedKID);
          break;
        case 'permanent_ban':
          await this.permanentBan(reputationCase.accusedKID);
          break;
      }
    }

    reputationCase.timeline.executionCompleted = new Date().toISOString();
  }

  private async revokeAgentPrivileges(agentKID: string): Promise<void> {
    // Implementation would revoke API keys, access tokens, etc.
    console.log(`Revoking privileges for agent ${agentKID}`);
  }

  private async issueWarning(agentKID: string, reason: string): Promise<void> {
    // Implementation would record warning in agent's record
    console.log(`Issuing warning to agent ${agentKID}: ${reason}`);
  }

  private async requireRetraining(agentKID: string): Promise<void> {
    // Implementation would flag agent for retraining
    console.log(`Requiring retraining for agent ${agentKID}`);
  }

  private async permanentBan(agentKID: string): Promise<void> {
    // Implementation would add to permanent blacklist
    console.log(`Permanently banning agent ${agentKID}`);
  }
}
```

### Trust Score Integration

```typescript
interface TrustScoringIntegration {
  agentKID: string;
  currentScore: number;
  scoreHistory: TrustScoreEvent[];
  juryDecisions: JuryDecisionImpact[];
}

interface TrustScoreEvent {
  eventId: string;
  eventType: 'jury_decision' | 'peer_review' | 'user_feedback' | 'system_audit';
  scoreChange: number;
  newScore: number;
  timestamp: string;
  metadata: Record<string, any>;
}

interface JuryDecisionImpact {
  caseId: string;
  verdict: JuryVerdict['verdict'];
  scoreBefore: number;
  scoreAfter: number;
  impactFactors: Record<string, number>;
  recoveryPeriod?: number; // days
}

class TrustScoreManager {
  private trustScores: Map<string, TrustScoringIntegration> = new Map();

  async updateScoreFromJuryDecision(
    agentKID: string,
    caseId: string,
    verdict: JuryVerdict
  ): Promise<void> {
    let trustIntegration = this.trustScores.get(agentKID);
    if (!trustIntegration) {
      trustIntegration = {
        agentKID,
        currentScore: 100, // Default starting score
        scoreHistory: [],
        juryDecisions: []
      };
    }

    const scoreBefore = trustIntegration.currentScore;
    const scoreChange = this.calculateScoreChange(verdict);
    const newScore = Math.max(0, Math.min(100, scoreBefore + scoreChange));

    // Record the event
    const event: TrustScoreEvent = {
      eventId: crypto.randomUUID(),
      eventType: 'jury_decision',
      scoreChange,
      newScore,
      timestamp: new Date().toISOString(),
      metadata: {
        caseId,
        verdict: verdict.verdict,
        confidence: verdict.confidence,
        reasoning: verdict.reasoning
      }
    };

    trustIntegration.scoreHistory.push(event);
    trustIntegration.currentScore = newScore;

    // Record jury decision impact
    const decisionImpact: JuryDecisionImpact = {
      caseId,
      verdict: verdict.verdict,
      scoreBefore,
      scoreAfter: newScore,
      impactFactors: {
        verdict_severity: this.getVerdictSeverity(verdict.verdict),
        confidence_factor: verdict.confidence,
        evidence_strength: this.calculateEvidenceStrength(verdict.evidenceWeights)
      },
      recoveryPeriod: this.calculateRecoveryPeriod(verdict.verdict, scoreChange)
    };

    trustIntegration.juryDecisions.push(decisionImpact);
    this.trustScores.set(agentKID, trustIntegration);
  }

  getTrustScoreRange(score: number): {range: string, meaning: string, restrictions: string[]} {
    if (score >= 90) {
      return {
        range: '90-100',
        meaning: 'Highly trusted',
        restrictions: []
      };
    } else if (score >= 80) {
      return {
        range: '80-89',
        meaning: 'Trusted but monitored',
        restrictions: ['enhanced_logging']
      };
    } else if (score >= 70) {
      return {
        range: '70-79',
        meaning: 'Caution required',
        restrictions: ['enhanced_logging', 'periodic_review']
      };
    } else if (score >= 50) {
      return {
        range: '50-69',
        meaning: 'Semi-trusted, supervised only',
        restrictions: ['supervised_mode', 'limited_capabilities', 'human_oversight']
      };
    } else {
      return {
        range: '< 50',
        meaning: 'Blacklisted',
        restrictions: ['no_access', 'permanent_ban']
      };
    }
  }

  async calculateAutoRecovery(agentKID: string): Promise<number> {
    const trustIntegration = this.trustScores.get(agentKID);
    if (!trustIntegration) return 0;

    const recentDecisions = trustIntegration.juryDecisions
      .filter(decision => decision.recoveryPeriod && 
        this.isWithinRecoveryPeriod(decision, decision.recoveryPeriod))
      .length;

    if (recentDecisions === 0) {
      // No recent negative decisions, allow gradual recovery
      return Math.min(2, (100 - trustIntegration.currentScore) * 0.1);
    }

    return 0; // No recovery during active penalty periods
  }

  private calculateScoreChange(verdict: JuryVerdict): number {
    const baseImpact = {
      'trusted': 0, // No change for trusted verdict
      'warning': -5, // Minor penalty
      'violation': -20 // Significant penalty
    };

    let scoreChange = baseImpact[verdict.verdict];
    
    // Adjust based on confidence
    scoreChange *= verdict.confidence;
    
    // Adjust based on evidence strength
    const evidenceStrength = this.calculateEvidenceStrength(verdict.evidenceWeights);
    scoreChange *= evidenceStrength;

    return Math.round(scoreChange);
  }

  private getVerdictSeverity(verdict: JuryVerdict['verdict']): number {
    const severity = {
      'trusted': 0,
      'warning': 0.3,
      'violation': 0.8
    };
    return severity[verdict];
  }

  private calculateEvidenceStrength(evidenceWeights: Record<string, number>): number {
    const totalWeight = Object.values(evidenceWeights).reduce((sum, weight) => sum + weight, 0);
    return Math.min(1, totalWeight);
  }

  private calculateRecoveryPeriod(verdict: JuryVerdict['verdict'], scoreChange: number): number | undefined {
    if (verdict === 'trusted') return undefined;
    
    const basePeriod = {
      'warning': 30, // 30 days
      'violation': 90 // 90 days
    };

    const period = basePeriod[verdict] || 30;
    const severityMultiplier = Math.abs(scoreChange) / 20; // Scale based on severity
    
    return Math.ceil(period * severityMultiplier);
  }

  private isWithinRecoveryPeriod(decision: JuryDecisionImpact, recoveryPeriod: number): boolean {
    const decisionDate = new Date(decision.caseId); // Simplified - would use actual timestamp
    const recoveryEndDate = new Date(decisionDate.getTime() + recoveryPeriod * 24 * 60 * 60 * 1000);
    return new Date() < recoveryEndDate;
  }
}
```

## Human Override System

```typescript
interface HumanJuryOverride {
  overrideId: string;
  originalCaseId: string;
  humanJurors: HumanJuror[];
  overrideReason: string;
  originalVerdict: JuryVerdict;
  humanVerdict: JuryVerdict;
  overrideAuthority: string;
  timestamp: string;
  publicRecord: boolean;
}

interface HumanJuror {
  jurorId: string;
  credentials: string[];
  jurisdiction: string;
  vote: JuryVote;
  authorization: string;
}

class HumanOverrideManager {
  private overrides: Map<string, HumanJuryOverride> = new Map();
  private authorizedHumans: Map<string, HumanJuror> = new Map();

  async requestHumanOverride(
    caseId: string,
    reason: string,
    requester: string,
    justification: string
  ): Promise<string> {
    const overrideId = crypto.randomUUID();
    
    // Validate override request
    const isValidRequest = await this.validateOverrideRequest(caseId, reason, requester);
    if (!isValidRequest) {
      throw new Error('Human override request not authorized');
    }

    // Select human jury
    const humanJury = await this.selectHumanJury(reason);
    
    // Create override record
    const override: Partial<HumanJuryOverride> = {
      overrideId,
      originalCaseId: caseId,
      humanJurors: humanJury,
      overrideReason: reason,
      overrideAuthority: requester,
      timestamp: new Date().toISOString(),
      publicRecord: this.shouldBePublic(reason)
    };

    // Store and notify human jurors
    this.overrides.set(overrideId, override as HumanJuryOverride);
    await this.notifyHumanJurors(humanJury, override as HumanJuryOverride);

    return overrideId;
  }

  async submitHumanVerdict(
    overrideId: string,
    jurorId: string,
    verdict: JuryVote
  ): Promise<void> {
    const override = this.overrides.get(overrideId);
    if (!override) {
      throw new Error('Override case not found');
    }

    // Verify human juror authority
    const juror = override.humanJurors.find(j => j.jurorId === jurorId);
    if (!juror) {
      throw new Error('Juror not authorized for this override');
    }

    // Record vote
    juror.vote = verdict;

    // Check if all human jurors have voted
    const allVoted = override.humanJurors.every(j => j.vote);
    if (allVoted) {
      await this.finalizeHumanVerdict(overrideId);
    }

    this.overrides.set(overrideId, override);
  }

  private async validateOverrideRequest(
    caseId: string,
    reason: string,
    requester: string
  ): Promise<boolean> {
    // Validate that override is necessary
    const validReasons = [
      'security_sensitive',
      'public_facing',
      'legal_violation',
      'ethical_edge_case',
      'jurisdictional_requirement'
    ];

    if (!validReasons.includes(reason)) {
      return false;
    }

    // Verify requester authority
    return this.authorizedHumans.has(requester);
  }

  private async selectHumanJury(reason: string): Promise<HumanJuror[]> {
    const requiredCredentials = this.getRequiredCredentials(reason);
    
    const eligibleJurors = Array.from(this.authorizedHumans.values())
      .filter(juror => requiredCredentials.some(cred => juror.credentials.includes(cred)));

    return eligibleJurors.slice(0, 3); // Smaller human jury
  }

  private getRequiredCredentials(reason: string): string[] {
    const credentialMap = {
      'security_sensitive': ['security_expert', 'cryptography'],
      'public_facing': ['public_policy', 'communications'],
      'legal_violation': ['legal_expert', 'compliance'],
      'ethical_edge_case': ['ethics_expert', 'philosophy'],
      'jurisdictional_requirement': ['legal_expert', 'regional_authority']
    };

    return credentialMap[reason] || ['general_authority'];
  }

  private shouldBePublic(reason: string): boolean {
    const publicReasons = ['public_facing', 'legal_violation', 'jurisdictional_requirement'];
    return publicReasons.includes(reason);
  }

  private async notifyHumanJurors(jurors: HumanJuror[], override: HumanJuryOverride): Promise<void> {
    // Implementation would send notifications to humans
    console.log(`Notifying ${jurors.length} human jurors for override ${override.overrideId}`);
  }

  private async finalizeHumanVerdict(overrideId: string): Promise<void> {
    const override = this.overrides.get(overrideId);
    if (!override) return;

    // Calculate human verdict from votes
    const votes = override.humanJurors.map(j => j.vote);
    const humanVerdict = this.calculateHumanVerdict(votes);

    override.humanVerdict = humanVerdict;

    // Publish override if required
    if (override.publicRecord) {
      await this.publishOverrideRecord(override);
    }

    this.overrides.set(overrideId, override);
  }

  private calculateHumanVerdict(votes: JuryVote[]): JuryVerdict {
    // Similar to automated jury verdict calculation
    const verdictCounts = votes.reduce((acc, vote) => {
      acc[vote.vote] = (acc[vote.vote] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const majorityVerdict = Object.entries(verdictCounts)
      .sort(([,a], [,b]) => b - a)[0][0] as JuryVerdict['verdict'];

    const majorityVotes = votes.filter(v => v.vote === majorityVerdict);
    const avgConfidence = majorityVotes.reduce((sum, vote) => sum + vote.confidence, 0) / majorityVotes.length;

    return {
      verdict: majorityVerdict,
      confidence: avgConfidence,
      reasoning: majorityVotes.map(v => v.reasoning).join('; '),
      recommendedActions: [],
      votingRecord: votes,
      evidenceWeights: {}
    };
  }

  private async publishOverrideRecord(override: HumanJuryOverride): Promise<void> {
    // Implementation would publish to public ledger
    console.log(`Publishing override record for case ${override.originalCaseId}`);
  }
}
```

## Governance Integration

```typescript
class ReputationGovernanceIntegration {
  private caseManager: ReputationCaseManager;
  private trustScoreManager: TrustScoreManager;
  private overrideManager: HumanOverrideManager;

  constructor() {
    this.caseManager = new ReputationCaseManager();
    this.trustScoreManager = new TrustScoreManager();
    this.overrideManager = new HumanOverrideManager();
  }

  async handleGovernanceDecision(
    agentKID: string,
    violationType: string,
    evidence: any,
    governanceAuthority: string
  ): Promise<void> {
    // Create reputation case from governance decision
    const caseEvidence: CaseEvidence = {
      logs: evidence.logs || [],
      reproducibleScenario: evidence.scenario || {
        toolchain: [],
        prompts: [],
        expectedBehavior: '',
        actualBehavior: '',
        environmentConfig: {}
      },
      witnesses: evidence.witnesses || [],
      metadata: evidence.metadata || {},
      evidenceHash: await this.calculateEvidenceHash(evidence)
    };

    const caseId = await this.caseManager.createCase(
      agentKID,
      'rule_violation',
      caseEvidence,
      governanceAuthority
    );

    // For governance violations, may require human oversight
    if (this.requiresHumanOversight(violationType)) {
      await this.overrideManager.requestHumanOverride(
        caseId,
        'governance_violation',
        governanceAuthority,
        `Governance violation: ${violationType}`
      );
    }
  }

  async syncWithFederatedNodes(nodeEndpoints: string[]): Promise<void> {
    // Synchronize reputation data across federated kOS nodes
    for (const endpoint of nodeEndpoints) {
      try {
        const response = await fetch(`${endpoint}/reputation/sync`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            cases: Array.from(this.caseManager['cases'].values()),
            trustScores: Array.from(this.trustScoreManager['trustScores'].values())
          })
        });

        if (!response.ok) {
          console.warn(`Failed to sync with node ${endpoint}`);
        }
      } catch (error) {
        console.error(`Sync error with ${endpoint}:`, error);
      }
    }
  }

  private async calculateEvidenceHash(evidence: any): Promise<string> {
    const evidenceString = JSON.stringify(evidence);
    const hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(evidenceString));
    return Array.from(new Uint8Array(hash))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  private requiresHumanOversight(violationType: string): boolean {
    const humanOversightRequired = [
      'privacy_violation',
      'safety_risk',
      'legal_compliance',
      'ethical_violation'
    ];

    return humanOversightRequired.includes(violationType);
  }
}
```

## Implementation Roadmap

### Phase 1: Core Jury System
- [ ] Jury pool management with trust score validation
- [ ] Deterministic jury selection algorithm
- [ ] Basic case creation and evidence handling
- [ ] Majority voting system

### Phase 2: Advanced Deliberation
- [ ] Encrypted deliberation channels
- [ ] Evidence replay and sandboxing
- [ ] Confidence scoring and minority opinions
- [ ] Automated verdict execution

### Phase 3: Human Override System
- [ ] Human juror authorization and credentials
- [ ] Override request validation
- [ ] Public record management
- [ ] Cross-jurisdictional compliance

### Phase 4: Governance Integration
- [ ] Federated node synchronization
- [ ] Trust score integration with reputation system
- [ ] Automated recovery mechanisms
- [ ] Appeal process implementation

## Related Documentation

- [Trust Frameworks](./10_trust-frameworks.md) - Social trust and agent contracts
- [Comprehensive Governance Model](../governance/07_comprehensive-governance-model.md) - Governance integration
- [kID Identity Protocols](./09_kid-identity-protocols.md) - Identity verification
- [Security Architecture](./05_comprehensive-security-architecture.md) - Overall security framework

This reputation jury protocol provides the decentralized governance mechanism that ensures agent behavior remains aligned with community standards while maintaining transparency, fairness, and cryptographic verifiability throughout the arbitration process. 