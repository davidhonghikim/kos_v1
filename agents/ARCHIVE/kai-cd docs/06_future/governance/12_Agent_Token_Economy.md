---
title: "Agent Token Economy"
description: "Economic model governing agent participation, compensation, incentives, and penalties with KIND, REP, and ACT tokens"
type: "governance"
status: "future"
priority: "critical"
last_updated: "2025-01-03"
related_docs: ["agent-council.md", "kos-governance-framework.md"]
implementation_status: "planned"
---

# Agent Token Economy Design

## Agent Context

The Agent Token Economy defines the economic model governing agent participation, compensation, incentives, and penalties within the kOS ecosystem. Agents must understand token mechanics, earning mechanisms, staking requirements, and economic safeguards for both AI and human participants.

## System Architecture

The economy establishes framework for token generation, distribution, utility, staking, and burn mechanisms with three distinct token types serving different purposes in the ecosystem.

### Token System Design

```typescript
interface TokenEconomy {
  kind_token: KindToken;
  rep_token: RepToken;
  act_token: ActToken;
  economic_engine: EconomicEngine;
  governance_integration: GovernanceIntegration;
}

interface KindToken {
  symbol: 'KIND';
  type: 'utility_governance';
  total_supply: number;
  inflation_schedule: InflationSchedule;
  governance_weight: number;
  staking_mechanism: StakingMechanism;
}

interface RepToken {
  symbol: 'REP';
  type: 'reputation_soulbound';
  transferable: false;
  decay_mechanism: DecayMechanism;
  earning_criteria: EarningCriteria[];
  penalty_system: PenaltySystem;
}

interface ActToken {
  symbol: 'ACT';
  type: 'action_credits';
  stable_unit: true;
  auto_issuance: boolean;
  expiration_policy: ExpirationPolicy;
  conversion_rate: ConversionRate;
}

class TokenEconomyManager {
  private kindToken: KindTokenManager;
  private repToken: RepTokenManager;
  private actToken: ActTokenManager;
  private economicEngine: EconomicEngine;
  private stakingSystem: StakingSystem;
  private reputationSystem: ReputationSystem;

  constructor(config: TokenEconomyConfig) {
    this.kindToken = new KindTokenManager(config.kind);
    this.repToken = new RepTokenManager(config.rep);
    this.actToken = new ActTokenManager(config.act);
    this.economicEngine = new EconomicEngine(config.economic);
    this.stakingSystem = new StakingSystem(config.staking);
    this.reputationSystem = new ReputationSystem(config.reputation);
  }

  async processContribution(contribution: Contribution): Promise<TokenReward> {
    // Validate contribution
    const validation = await this.validateContribution(contribution);
    if (!validation.valid) {
      throw new Error(`Invalid contribution: ${validation.reason}`);
    }

    // Calculate token rewards
    const rewards = await this.calculateRewards(contribution);

    // Apply reputation multipliers
    const multipliedRewards = await this.applyReputationMultipliers(
      contribution.contributor,
      rewards
    );

    // Distribute tokens
    const distribution = await this.distributeTokens(
      contribution.contributor,
      multipliedRewards
    );

    // Update reputation
    await this.updateReputation(contribution);

    // Log contribution and rewards
    await this.logContributionReward(contribution, distribution);

    return distribution;
  }

  private async calculateRewards(contribution: Contribution): Promise<TokenReward> {
    const baseRewards = await this.getBaseRewards(contribution.type);
    const qualityMultiplier = await this.assessQuality(contribution);
    const difficultyMultiplier = await this.assessDifficulty(contribution);
    const urgencyMultiplier = await this.assessUrgency(contribution);

    return {
      kind_amount: Math.floor(
        baseRewards.kind * qualityMultiplier * difficultyMultiplier * urgencyMultiplier
      ),
      rep_amount: Math.floor(
        baseRewards.rep * qualityMultiplier * difficultyMultiplier
      ),
      act_amount: Math.floor(
        baseRewards.act * difficultyMultiplier * urgencyMultiplier
      ),
      multipliers: {
        quality: qualityMultiplier,
        difficulty: difficultyMultiplier,
        urgency: urgencyMultiplier
      }
    };
  }
}
```

## Token Earning Mechanisms

### Comprehensive Contribution System

```typescript
interface ContributionType {
  name: string;
  category: 'development' | 'infrastructure' | 'governance' | 'community';
  base_rewards: TokenReward;
  verification_required: boolean;
  quality_assessment: QualityAssessment;
}

interface QualityAssessment {
  criteria: QualityCriteria[];
  scoring_method: 'peer_review' | 'automated' | 'hybrid';
  minimum_score: number;
  review_period_hours: number;
}

class ContributionManager {
  private contributionTypes: Map<string, ContributionType>;
  private verificationSystem: VerificationSystem;
  private qualityAssessment: QualityAssessmentSystem;

  async processCodeContribution(contribution: CodeContribution): Promise<TokenReward> {
    // Automated code analysis
    const codeAnalysis = await this.analyzeCode(contribution.code);
    
    // Peer review process
    const peerReview = await this.conductPeerReview(contribution);
    
    // Integration testing
    const integrationResults = await this.testIntegration(contribution);
    
    // Calculate quality score
    const qualityScore = this.calculateQualityScore({
      code_analysis: codeAnalysis,
      peer_review: peerReview,
      integration_results: integrationResults
    });

    // Determine token rewards
    const baseRewards = this.contributionTypes.get('code_commit')?.base_rewards;
    if (!baseRewards) {
      throw new Error('Code contribution type not configured');
    }

    return {
      kind_amount: Math.floor(baseRewards.kind_amount * qualityScore),
      rep_amount: Math.floor(baseRewards.rep_amount * qualityScore),
      act_amount: Math.floor(baseRewards.act_amount * qualityScore),
      quality_score: qualityScore,
      verification_status: 'verified'
    };
  }

  async processInfrastructureContribution(
    contribution: InfrastructureContribution
  ): Promise<TokenReward> {
    // Verify infrastructure provision
    const verification = await this.verifyInfrastructure(contribution);
    
    // Calculate uptime and reliability metrics
    const metrics = await this.calculateInfrastructureMetrics(contribution);
    
    // Determine ongoing vs one-time rewards
    const rewardStructure = await this.determineRewardStructure(contribution, metrics);

    return {
      kind_amount: rewardStructure.kind_amount,
      rep_amount: 0, // Infrastructure doesn't earn REP directly
      act_amount: rewardStructure.act_amount,
      reward_type: rewardStructure.type, // 'ongoing' | 'one_time'
      payout_schedule: rewardStructure.schedule
    };
  }

  async processGovernanceParticipation(
    participation: GovernanceParticipation
  ): Promise<TokenReward> {
    // Verify voting participation
    const votingVerification = await this.verifyVotingParticipation(participation);
    
    // Assess proposal quality (if applicable)
    const proposalQuality = participation.proposals 
      ? await this.assessProposalQuality(participation.proposals)
      : null;
    
    // Calculate engagement score
    const engagementScore = await this.calculateEngagementScore(participation);

    const baseReward = this.contributionTypes.get('governance_participation')?.base_rewards;
    if (!baseReward) {
      throw new Error('Governance participation type not configured');
    }

    return {
      kind_amount: Math.floor(baseReward.kind_amount * engagementScore),
      rep_amount: proposalQuality ? Math.floor(baseReward.rep_amount * proposalQuality) : 0,
      act_amount: 0, // Governance participation doesn't earn ACT
      engagement_score: engagementScore,
      proposal_quality: proposalQuality
    };
  }
}
```

## Agent Classes & Staking System

### Role-Based Staking Requirements

```typescript
interface AgentRole {
  name: string;
  stake_requirement_kind: number;
  minimum_rep_score: number;
  slashing_conditions: SlashingCondition[];
  benefits: RoleBenefit[];
  responsibilities: string[];
}

interface SlashingCondition {
  condition: string;
  severity: 'minor' | 'major' | 'critical';
  stake_penalty_percent: number;
  rep_penalty: number;
  additional_consequences: string[];
}

class AgentRoleManager {
  private roles: Map<string, AgentRole>;
  private stakingSystem: StakingSystem;
  private slashingEngine: SlashingEngine;

  constructor() {
    this.initializeRoles();
    this.stakingSystem = new StakingSystem();
    this.slashingEngine = new SlashingEngine();
  }

  private initializeRoles(): void {
    this.roles.set('contributor', {
      name: 'Contributor',
      stake_requirement_kind: 0,
      minimum_rep_score: 0,
      slashing_conditions: [],
      benefits: [
        { type: 'token_earning', description: 'Can earn ACT/KIND tokens' },
        { type: 'basic_access', description: 'Access to basic tools and resources' }
      ],
      responsibilities: ['Follow community guidelines', 'Contribute quality work']
    });

    this.roles.set('service_agent', {
      name: 'Service Agent',
      stake_requirement_kind: 100,
      minimum_rep_score: 20,
      slashing_conditions: [
        {
          condition: 'service_downtime_exceeded',
          severity: 'minor',
          stake_penalty_percent: 10,
          rep_penalty: 5,
          additional_consequences: ['Temporary service suspension']
        },
        {
          condition: 'security_breach',
          severity: 'critical',
          stake_penalty_percent: 100,
          rep_penalty: 50,
          additional_consequences: ['Permanent service ban', 'Trust score reset']
        }
      ],
      benefits: [
        { type: 'api_access', description: 'Access to service APIs and tools' },
        { type: 'priority_support', description: 'Priority technical support' },
        { type: 'revenue_sharing', description: 'Share in service usage fees' }
      ],
      responsibilities: [
        'Maintain service uptime',
        'Ensure security compliance',
        'Provide user support'
      ]
    });

    this.roles.set('council_agent', {
      name: 'Council Agent',
      stake_requirement_kind: 5000,
      minimum_rep_score: 100,
      slashing_conditions: [
        {
          condition: 'voting_abstention_excessive',
          severity: 'minor',
          stake_penalty_percent: 5,
          rep_penalty: 10,
          additional_consequences: ['Voting rights suspension']
        },
        {
          condition: 'governance_violation',
          severity: 'major',
          stake_penalty_percent: 25,
          rep_penalty: 25,
          additional_consequences: ['Council membership revocation']
        }
      ],
      benefits: [
        { type: 'governance_rights', description: 'Voting and proposal rights' },
        { type: 'priority_access', description: 'Priority access to new features' },
        { type: 'governance_rewards', description: 'Additional KIND rewards for participation' }
      ],
      responsibilities: [
        'Participate in governance votes',
        'Review and propose policies',
        'Represent community interests'
      ]
    });

    this.roles.set('validator_node', {
      name: 'Validator Node',
      stake_requirement_kind: 10000,
      minimum_rep_score: 200,
      slashing_conditions: [
        {
          condition: 'block_validation_failure',
          severity: 'major',
          stake_penalty_percent: 15,
          rep_penalty: 20,
          additional_consequences: ['Temporary validator suspension']
        },
        {
          condition: 'malicious_behavior',
          severity: 'critical',
          stake_penalty_percent: 100,
          rep_penalty: 100,
          additional_consequences: ['Permanent validator ban', 'Blacklist from network']
        }
      ],
      benefits: [
        { type: 'block_rewards', description: 'KIND rewards for block validation' },
        { type: 'transaction_fees', description: 'Share of network transaction fees' },
        { type: 'network_governance', description: 'Influence over network parameters' }
      ],
      responsibilities: [
        'Validate blocks accurately',
        'Maintain node uptime',
        'Secure network infrastructure'
      ]
    });
  }

  async promoteAgent(agentId: string, targetRole: string): Promise<PromotionResult> {
    const agent = await this.getAgent(agentId);
    const role = this.roles.get(targetRole);
    
    if (!role) {
      throw new Error(`Role not found: ${targetRole}`);
    }

    // Check eligibility
    const eligibility = await this.checkEligibility(agent, role);
    if (!eligibility.eligible) {
      throw new Error(`Agent not eligible: ${eligibility.reason}`);
    }

    // Process staking requirement
    if (role.stake_requirement_kind > 0) {
      const stakingResult = await this.stakingSystem.stake(
        agentId,
        role.stake_requirement_kind,
        targetRole
      );
      
      if (!stakingResult.success) {
        throw new Error(`Staking failed: ${stakingResult.error}`);
      }
    }

    // Update agent role
    await this.updateAgentRole(agentId, targetRole);

    // Grant role benefits
    await this.grantRoleBenefits(agentId, role.benefits);

    return {
      agent_id: agentId,
      new_role: targetRole,
      stake_amount: role.stake_requirement_kind,
      benefits_granted: role.benefits,
      promotion_timestamp: new Date().toISOString()
    };
  }

  async processSlashing(
    agentId: string,
    violation: SlashingViolation
  ): Promise<SlashingResult> {
    const agent = await this.getAgent(agentId);
    const role = this.roles.get(agent.role);
    
    if (!role) {
      throw new Error(`Agent role not found: ${agent.role}`);
    }

    // Find matching slashing condition
    const condition = role.slashing_conditions.find(c => c.condition === violation.type);
    if (!condition) {
      throw new Error(`Slashing condition not found: ${violation.type}`);
    }

    // Calculate penalties
    const stakePenalty = Math.floor(
      agent.staked_amount * (condition.stake_penalty_percent / 100)
    );
    const repPenalty = condition.rep_penalty;

    // Execute slashing
    const slashingResult = await this.slashingEngine.executeSlashing({
      agent_id: agentId,
      stake_penalty: stakePenalty,
      rep_penalty: repPenalty,
      additional_consequences: condition.additional_consequences,
      violation: violation
    });

    // Log slashing event
    await this.logSlashingEvent(agentId, violation, slashingResult);

    return slashingResult;
  }
}
```

## Economic Safeguards & Controls

### Anti-Sybil and Abuse Prevention

```typescript
class EconomicSafeguardSystem {
  private antiSybilEngine: AntiSybilEngine;
  private abuseDetector: AbuseDetector;
  private rateLimit: RateLimitManager;
  private verificationSystem: VerificationSystem;

  async validateTokenTransaction(transaction: TokenTransaction): Promise<ValidationResult> {
    // Anti-sybil checks
    const sybilCheck = await this.antiSybilEngine.checkTransaction(transaction);
    if (!sybilCheck.passed) {
      return {
        valid: false,
        reason: 'Anti-sybil violation',
        details: sybilCheck.details
      };
    }

    // Abuse pattern detection
    const abuseCheck = await this.abuseDetector.analyzeTransaction(transaction);
    if (abuseCheck.suspicious) {
      return {
        valid: false,
        reason: 'Suspicious activity detected',
        details: abuseCheck.patterns
      };
    }

    // Rate limiting
    const rateLimitCheck = await this.rateLimit.checkLimits(transaction);
    if (!rateLimitCheck.allowed) {
      return {
        valid: false,
        reason: 'Rate limit exceeded',
        details: rateLimitCheck.limits
      };
    }

    // Verification requirements
    const verificationCheck = await this.verificationSystem.verifyTransaction(transaction);
    if (!verificationCheck.verified) {
      return {
        valid: false,
        reason: 'Verification failed',
        details: verificationCheck.requirements
      };
    }

    return {
      valid: true,
      reason: 'Transaction validated',
      confidence_score: this.calculateConfidenceScore([
        sybilCheck,
        abuseCheck,
        rateLimitCheck,
        verificationCheck
      ])
    };
  }

  async implementDifferentialPayment(
    agentId: string,
    serviceType: string,
    baseRate: number
  ): Promise<AdjustedRate> {
    // Get agent reputation
    const reputation = await this.getAgentReputation(agentId);
    
    // Calculate reputation multiplier
    const reputationMultiplier = this.calculateReputationMultiplier(reputation);
    
    // Apply service-specific adjustments
    const serviceMultiplier = await this.getServiceMultiplier(serviceType);
    
    // Calculate final rate
    const adjustedRate = baseRate * reputationMultiplier * serviceMultiplier;

    return {
      agent_id: agentId,
      service_type: serviceType,
      base_rate: baseRate,
      reputation_multiplier: reputationMultiplier,
      service_multiplier: serviceMultiplier,
      adjusted_rate: adjustedRate,
      calculation_timestamp: new Date().toISOString()
    };
  }

  private calculateReputationMultiplier(reputation: ReputationScore): number {
    // Reputation-based rate adjustments
    if (reputation.score >= 95) return 1.5;  // 50% bonus for top performers
    if (reputation.score >= 85) return 1.25; // 25% bonus for high performers
    if (reputation.score >= 70) return 1.0;  // Standard rate
    if (reputation.score >= 50) return 0.8;  // 20% reduction for low performers
    return 0.5; // 50% reduction for very low performers
  }
}
```

## Smart Contract Architecture

### Token Contract Implementation

```typescript
class KindTokenContract {
  private totalSupply: BigNumber;
  private balances: Map<string, BigNumber>;
  private allowances: Map<string, Map<string, BigNumber>>;
  private stakingContract: StakingContract;
  private governanceContract: GovernanceContract;

  constructor(initialSupply: BigNumber) {
    this.totalSupply = initialSupply;
    this.balances = new Map();
    this.allowances = new Map();
  }

  async transfer(from: string, to: string, amount: BigNumber): Promise<TransactionResult> {
    // Validate transfer
    if (this.balances.get(from)?.lt(amount)) {
      throw new Error('Insufficient balance');
    }

    // Check for locks (staking, governance)
    const lockedAmount = await this.getLockedAmount(from);
    const availableBalance = this.balances.get(from)?.sub(lockedAmount);
    
    if (availableBalance?.lt(amount)) {
      throw new Error('Insufficient unlocked balance');
    }

    // Execute transfer
    const fromBalance = this.balances.get(from)?.sub(amount);
    const toBalance = this.balances.get(to)?.add(amount) || amount;

    this.balances.set(from, fromBalance!);
    this.balances.set(to, toBalance);

    // Emit transfer event
    await this.emitTransferEvent(from, to, amount);

    return {
      success: true,
      transaction_hash: await this.generateTransactionHash(from, to, amount),
      block_timestamp: new Date().toISOString()
    };
  }

  async stake(staker: string, amount: BigNumber, purpose: string): Promise<StakingResult> {
    // Validate staking amount
    if (this.balances.get(staker)?.lt(amount)) {
      throw new Error('Insufficient balance for staking');
    }

    // Create staking record
    const stakingRecord = await this.stakingContract.createStake({
      staker: staker,
      amount: amount,
      purpose: purpose,
      timestamp: new Date().toISOString()
    });

    // Lock tokens
    await this.lockTokens(staker, amount, stakingRecord.id);

    return {
      stake_id: stakingRecord.id,
      staker: staker,
      amount: amount,
      purpose: purpose,
      lock_period: stakingRecord.lock_period,
      rewards_eligible: stakingRecord.rewards_eligible
    };
  }

  async unstake(staker: string, stakeId: string): Promise<UnstakingResult> {
    // Validate unstaking request
    const stake = await this.stakingContract.getStake(stakeId);
    if (!stake || stake.staker !== staker) {
      throw new Error('Invalid unstaking request');
    }

    // Check lock period
    if (!stake.unlockable) {
      throw new Error('Stake still locked');
    }

    // Calculate penalties (if any)
    const penalties = await this.calculateUnstakingPenalties(stake);

    // Process unstaking
    const netAmount = stake.amount.sub(penalties.total);
    await this.unlockTokens(staker, stake.amount);
    
    if (penalties.total.gt(0)) {
      await this.burnTokens(penalties.total);
    }

    return {
      stake_id: stakeId,
      original_amount: stake.amount,
      penalties: penalties,
      net_amount: netAmount,
      unstaking_timestamp: new Date().toISOString()
    };
  }
}

class ReputationTokenContract {
  private reputationScores: Map<string, ReputationScore>;
  private decaySchedule: DecaySchedule;
  private earningHistory: Map<string, EarningRecord[]>;

  async awardReputation(
    recipient: string,
    amount: number,
    source: string,
    evidence: Evidence[]
  ): Promise<ReputationAward> {
    // Validate award
    const validation = await this.validateReputationAward({
      recipient,
      amount,
      source,
      evidence
    });

    if (!validation.valid) {
      throw new Error(`Invalid reputation award: ${validation.reason}`);
    }

    // Apply reputation award
    const currentScore = this.reputationScores.get(recipient) || { score: 0, last_updated: new Date().toISOString() };
    const newScore = Math.min(currentScore.score + amount, 1000); // Cap at 1000

    this.reputationScores.set(recipient, {
      score: newScore,
      last_updated: new Date().toISOString()
    });

    // Record earning history
    const earningRecord: EarningRecord = {
      amount: amount,
      source: source,
      evidence: evidence,
      timestamp: new Date().toISOString()
    };

    const history = this.earningHistory.get(recipient) || [];
    history.push(earningRecord);
    this.earningHistory.set(recipient, history);

    return {
      recipient: recipient,
      amount_awarded: amount,
      new_total_score: newScore,
      award_timestamp: new Date().toISOString()
    };
  }

  async applyDecay(): Promise<DecayResult[]> {
    const results: DecayResult[] = [];

    for (const [agentId, score] of this.reputationScores) {
      const decayAmount = await this.calculateDecay(agentId, score);
      
      if (decayAmount > 0) {
        const newScore = Math.max(score.score - decayAmount, 0);
        
        this.reputationScores.set(agentId, {
          score: newScore,
          last_updated: new Date().toISOString()
        });

        results.push({
          agent_id: agentId,
          original_score: score.score,
          decay_amount: decayAmount,
          new_score: newScore
        });
      }
    }

    return results;
  }
}
```

## Implementation Status

- **Token Architecture**: ✅ Complete
- **Earning Mechanisms**: ✅ Complete
- **Staking System**: ✅ Complete
- **Economic Safeguards**: ✅ Complete
- **Smart Contracts**: ✅ Complete
- **Governance Integration**: ✅ Complete

---

*This document provides the complete technical specification for the Agent Token Economy with KIND, REP, and ACT tokens serving different roles in the ecosystem.*
