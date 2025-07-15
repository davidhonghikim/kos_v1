---
title: "System Ledger"
description: "Immutable event audit and agent provenance tracking system"
type: "architecture"
status: "future"
priority: "critical"
last_updated: "2025-01-03"
related_docs: ["agent-trust-identity.md", "consent-ledger-user-override.md"]
implementation_status: "planned"
---

# System Ledger - Immutable Event Audit & Agent Provenance

## Agent Context

The System Ledger is the central, immutable, append-only record of all major operations, events, and agent activities across kAI and kOS systems. Agents must understand the complete technical implementation of event recording, cryptographic verification, audit trail management, and compliance reporting systems.

## Core Functions

- Immutable event recording with cryptographic integrity
- Agent provenance tracking with complete action history
- Forensic and compliance audits with queryable timeline
- Real-time event streaming and alerting
- Cross-system event correlation and analysis

## Ledger Architecture

### Storage Backend Implementation

```typescript
interface LedgerConfig {
  storage: {
    backend: 'postgresql' | 'bigchaindb' | 'hyperledger' | 'ipfs';
    connection_string: string;
    encryption_at_rest: boolean;
    replication_factor: number;
  };
  immutability: {
    enforce_triggers: boolean;
    merkle_tree: boolean;
    blockchain_anchoring: boolean;
    signature_required: boolean;
  };
  retention: {
    policy: 'indefinite' | 'time_based' | 'size_based';
    max_age_days?: number;
    max_size_gb?: number;
    archive_strategy: 'compress' | 'cold_storage' | 'delete';
  };
}

class SystemLedger {
  private storage: LedgerStorage;
  private eventBus: EventBus;
  private merkleTree: MerkleTree;
  private signingKey: CryptoKey;
  private eventBuffer: LedgerEvent[];

  constructor(config: LedgerConfig) {
    this.storage = this.createStorage(config.storage);
    this.eventBus = new EventBus();
    this.merkleTree = new MerkleTree();
    this.eventBuffer = [];
    this.initializeSigningKey();
  }

  async recordEvent(event: LedgerEventInput): Promise<string> {
    // Create immutable event record
    const ledgerEvent: LedgerEvent = {
      id: this.generateEventId(),
      timestamp: new Date().toISOString(),
      agent_id: event.agent_id,
      agent_type: event.agent_type || 'unknown',
      event_type: event.event_type,
      event_scope: event.event_scope,
      subject_id: event.subject_id,
      description: event.description,
      data: event.data,
      metadata: {
        ...event.metadata,
        recorded_at: new Date().toISOString(),
        ledger_version: this.getLedgerVersion(),
        parent_hash: await this.getLastEventHash()
      },
      signature: ''
    };

    // Sign the event
    ledgerEvent.signature = await this.signEvent(ledgerEvent);

    // Add to buffer for batch processing
    this.eventBuffer.push(ledgerEvent);

    // Flush buffer if needed
    if (this.eventBuffer.length >= 100) {
      await this.flushEventBuffer();
    }

    // Emit real-time event
    this.eventBus.emit('event:recorded', ledgerEvent);

    return ledgerEvent.id;
  }

  async queryEvents(query: LedgerQuery): Promise<LedgerQueryResult> {
    const sqlBuilder = new SQLQueryBuilder();
    let sql = 'SELECT * FROM ledger_events WHERE 1=1';
    const params: any[] = [];

    // Build query conditions
    if (query.agent_id) {
      sql += ' AND agent_id = ?';
      params.push(query.agent_id);
    }

    if (query.event_type) {
      sql += ' AND event_type = ?';
      params.push(query.event_type);
    }

    if (query.start_time) {
      sql += ' AND timestamp >= ?';
      params.push(query.start_time);
    }

    if (query.end_time) {
      sql += ' AND timestamp <= ?';
      params.push(query.end_time);
    }

    if (query.subject_id) {
      sql += ' AND subject_id = ?';
      params.push(query.subject_id);
    }

    // Add ordering and pagination
    sql += ' ORDER BY timestamp DESC';
    if (query.limit) {
      sql += ' LIMIT ?';
      params.push(query.limit);
    }

    if (query.offset) {
      sql += ' OFFSET ?';
      params.push(query.offset);
    }

    const events = await this.storage.query(sql, params);
    const total = await this.storage.count('ledger_events', query);

    return {
      events: events,
      total: total,
      query: query,
      generated_at: new Date().toISOString()
    };
  }

  async verifyIntegrity(startId?: string, endId?: string): Promise<IntegrityReport> {
    const events = await this.getEventsInRange(startId, endId);
    const report: IntegrityReport = {
      total_events: events.length,
      verified_events: 0,
      failed_events: 0,
      corrupted_events: [],
      merkle_root_valid: false,
      chain_integrity_valid: true,
      verification_timestamp: new Date().toISOString()
    };

    // Verify each event signature
    for (const event of events) {
      const isValid = await this.verifyEventSignature(event);
      if (isValid) {
        report.verified_events++;
      } else {
        report.failed_events++;
        report.corrupted_events.push({
          event_id: event.id,
          reason: 'Invalid signature',
          timestamp: event.timestamp
        });
      }
    }

    // Verify chain integrity
    report.chain_integrity_valid = await this.verifyChainIntegrity(events);

    // Verify Merkle tree
    if (this.merkleTree) {
      report.merkle_root_valid = await this.verifyMerkleRoot(events);
    }

    return report;
  }

  private async signEvent(event: LedgerEvent): Promise<string> {
    const eventWithoutSignature = { ...event, signature: '' };
    const encoder = new TextEncoder();
    const data = encoder.encode(JSON.stringify(eventWithoutSignature));
    
    const signature = await crypto.subtle.sign('Ed25519', this.signingKey, data);
    return btoa(String.fromCharCode(...new Uint8Array(signature)));
  }

  private async flushEventBuffer(): Promise<void> {
    if (this.eventBuffer.length === 0) return;

    const eventsToFlush = [...this.eventBuffer];
    this.eventBuffer.length = 0;

    try {
      await this.storage.insertBatch(eventsToFlush);
      
      // Update Merkle tree
      for (const event of eventsToFlush) {
        await this.merkleTree.addEvent(event);
      }
    } catch (error) {
      console.error('Failed to flush event buffer:', error);
      // Re-add events to buffer for retry
      this.eventBuffer.unshift(...eventsToFlush);
      throw error;
    }
  }
}
```

### Event Schema & Types

```typescript
interface LedgerEvent {
  id: string; // UUID
  timestamp: string; // ISO date
  agent_id: string;
  agent_type: 'human' | 'autonomous' | 'supervised' | 'system';
  event_type: EventType;
  event_scope: string; // kAI.module, kOS.service
  subject_id: string; // ID of affected object
  description: string;
  data: Record<string, any>; // Full payload snapshot
  metadata: EventMetadata;
  signature: string; // Cryptographic signature
}

type EventType = 
  | 'config_change'
  | 'model_invocation'
  | 'data_upload'
  | 'access_granted'
  | 'permission_used'
  | 'credential_used'
  | 'error_logged'
  | 'task_run'
  | 'agent_created'
  | 'agent_terminated'
  | 'trust_updated'
  | 'security_violation'
  | 'system_startup'
  | 'system_shutdown';

interface EventMetadata {
  recorded_at: string;
  ledger_version: string;
  parent_hash: string;
  session_id?: string;
  conversation_id?: string;
  user_id?: string;
  device_fingerprint?: string;
  ip_address?: string;
  user_agent?: string;
  correlation_id?: string;
  tags: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'security' | 'performance' | 'business' | 'system' | 'audit';
}

interface LedgerEventInput {
  agent_id: string;
  agent_type?: string;
  event_type: EventType;
  event_scope: string;
  subject_id: string;
  description: string;
  data: Record<string, any>;
  metadata?: Partial<EventMetadata>;
}
```

### Event Ingestion Pipeline

```typescript
class EventIngestionPipeline {
  private validators: EventValidator[];
  private enrichers: EventEnricher[];
  private filters: EventFilter[];
  private ledger: SystemLedger;

  constructor(ledger: SystemLedger) {
    this.ledger = ledger;
    this.validators = [
      new SchemaValidator(),
      new TimestampValidator(),
      new AgentIdentityValidator()
    ];
    this.enrichers = [
      new ContextEnricher(),
      new GeolocationEnricher(),
      new ThreatIntelEnricher()
    ];
    this.filters = [
      new DuplicateFilter(),
      new NoiseFilter(),
      new SensitiveDataFilter()
    ];
  }

  async ingestEvent(rawEvent: any): Promise<string> {
    try {
      // Step 1: Validate event structure
      for (const validator of this.validators) {
        await validator.validate(rawEvent);
      }

      // Step 2: Enrich with additional context
      let enrichedEvent = rawEvent;
      for (const enricher of this.enrichers) {
        enrichedEvent = await enricher.enrich(enrichedEvent);
      }

      // Step 3: Apply filters
      for (const filter of this.filters) {
        const shouldRecord = await filter.shouldRecord(enrichedEvent);
        if (!shouldRecord) {
          return ''; // Event filtered out
        }
      }

      // Step 4: Record in ledger
      const eventId = await this.ledger.recordEvent(enrichedEvent);

      return eventId;
    } catch (error) {
      console.error('Event ingestion failed:', error);
      
      // Record the ingestion failure itself
      await this.ledger.recordEvent({
        agent_id: 'system.ledger',
        event_type: 'error_logged',
        event_scope: 'ledger.ingestion',
        subject_id: 'ingestion_pipeline',
        description: 'Event ingestion failed',
        data: {
          original_event: rawEvent,
          error: error.message,
          stack_trace: error.stack
        }
      });

      throw error;
    }
  }
}

class ContextEnricher implements EventEnricher {
  async enrich(event: any): Promise<any> {
    const enriched = { ...event };

    // Add system context
    enriched.metadata = {
      ...enriched.metadata,
      system_version: process.env.KAI_VERSION,
      node_id: process.env.NODE_ID,
      environment: process.env.NODE_ENV,
      memory_usage: process.memoryUsage(),
      cpu_usage: await this.getCPUUsage()
    };

    // Add request context if available
    if (event.request_context) {
      enriched.metadata.request_id = event.request_context.id;
      enriched.metadata.user_agent = event.request_context.user_agent;
      enriched.metadata.ip_address = event.request_context.ip;
    }

    return enriched;
  }

  private async getCPUUsage(): Promise<number> {
    // Implementation for CPU usage calculation
    return 0;
  }
}
```

## Provenance Tracking

### Agent Action Tracing

```typescript
class ProvenanceTracker {
  private ledger: SystemLedger;
  private actionGraph: ActionGraph;

  constructor(ledger: SystemLedger) {
    this.ledger = ledger;
    this.actionGraph = new ActionGraph();
  }

  async trackAgentAction(
    agentId: string,
    action: AgentAction,
    context: ActionContext
  ): Promise<ProvenanceRecord> {
    const provenanceRecord: ProvenanceRecord = {
      id: this.generateProvenanceId(),
      agent_id: agentId,
      action: action,
      context: context,
      timestamp: new Date().toISOString(),
      parent_actions: await this.findParentActions(action),
      derived_outputs: [],
      verification_status: 'pending'
    };

    // Record in ledger
    await this.ledger.recordEvent({
      agent_id: agentId,
      event_type: 'task_run',
      event_scope: 'provenance.tracking',
      subject_id: provenanceRecord.id,
      description: `Agent action: ${action.type}`,
      data: {
        action: action,
        context: context,
        provenance_record: provenanceRecord
      }
    });

    // Add to action graph
    await this.actionGraph.addAction(provenanceRecord);

    return provenanceRecord;
  }

  async getProvenanceChain(actionId: string): Promise<ProvenanceChain> {
    const action = await this.actionGraph.getAction(actionId);
    if (!action) {
      throw new Error(`Action not found: ${actionId}`);
    }

    const chain: ProvenanceChain = {
      root_action: action,
      ancestors: [],
      descendants: [],
      timeline: []
    };

    // Build ancestor chain
    await this.buildAncestorChain(action, chain.ancestors);

    // Build descendant chain
    await this.buildDescendantChain(action, chain.descendants);

    // Create timeline
    chain.timeline = this.createTimeline(chain.ancestors, action, chain.descendants);

    return chain;
  }

  async verifyProvenance(actionId: string): Promise<ProvenanceVerification> {
    const chain = await this.getProvenanceChain(actionId);
    const verification: ProvenanceVerification = {
      action_id: actionId,
      verified: true,
      issues: [],
      verification_timestamp: new Date().toISOString()
    };

    // Verify each link in the chain
    for (const action of chain.timeline) {
      const linkVerification = await this.verifyProvenanceLink(action);
      if (!linkVerification.valid) {
        verification.verified = false;
        verification.issues.push({
          action_id: action.id,
          issue: linkVerification.issue,
          severity: linkVerification.severity
        });
      }
    }

    return verification;
  }

  private async verifyProvenanceLink(action: ProvenanceRecord): Promise<LinkVerification> {
    // Verify action signature
    const signatureValid = await this.verifyActionSignature(action);
    if (!signatureValid) {
      return {
        valid: false,
        issue: 'Invalid action signature',
        severity: 'high'
      };
    }

    // Verify temporal consistency
    const temporalValid = await this.verifyTemporalConsistency(action);
    if (!temporalValid) {
      return {
        valid: false,
        issue: 'Temporal inconsistency detected',
        severity: 'medium'
      };
    }

    // Verify causal relationships
    const causalValid = await this.verifyCausalRelationships(action);
    if (!causalValid) {
      return {
        valid: false,
        issue: 'Causal relationship violation',
        severity: 'high'
      };
    }

    return { valid: true };
  }
}

interface ProvenanceRecord {
  id: string;
  agent_id: string;
  action: AgentAction;
  context: ActionContext;
  timestamp: string;
  parent_actions: string[];
  derived_outputs: string[];
  verification_status: 'pending' | 'verified' | 'failed';
}

interface AgentAction {
  type: string;
  description: string;
  inputs: Record<string, any>;
  outputs: Record<string, any>;
  parameters: Record<string, any>;
  model_used?: string;
  duration_ms: number;
}
```

## Audit & Compliance

### Compliance Reporting

```typescript
class ComplianceReporter {
  private ledger: SystemLedger;
  private regulations: Map<string, ComplianceFramework>;

  constructor(ledger: SystemLedger) {
    this.ledger = ledger;
    this.regulations = new Map();
    this.initializeFrameworks();
  }

  async generateComplianceReport(
    framework: string,
    startDate: string,
    endDate: string
  ): Promise<ComplianceReport> {
    const complianceFramework = this.regulations.get(framework);
    if (!complianceFramework) {
      throw new Error(`Unknown compliance framework: ${framework}`);
    }

    const events = await this.ledger.queryEvents({
      start_time: startDate,
      end_time: endDate,
      event_type: complianceFramework.relevant_events
    });

    const report: ComplianceReport = {
      framework: framework,
      period: { start: startDate, end: endDate },
      total_events: events.total,
      compliant_events: 0,
      violations: [],
      recommendations: [],
      generated_at: new Date().toISOString()
    };

    // Analyze each event for compliance
    for (const event of events.events) {
      const analysis = await this.analyzeEventCompliance(event, complianceFramework);
      
      if (analysis.compliant) {
        report.compliant_events++;
      } else {
        report.violations.push({
          event_id: event.id,
          violation_type: analysis.violation_type,
          severity: analysis.severity,
          description: analysis.description,
          remediation_required: analysis.remediation_required
        });
      }
    }

    // Generate recommendations
    report.recommendations = await this.generateRecommendations(report.violations);

    return report;
  }

  async exportAuditTrail(
    query: LedgerQuery,
    format: 'json' | 'csv' | 'pdf'
  ): Promise<string> {
    const events = await this.ledger.queryEvents(query);
    
    switch (format) {
      case 'json':
        return JSON.stringify(events, null, 2);
      
      case 'csv':
        return this.convertToCSV(events.events);
      
      case 'pdf':
        return await this.generatePDFReport(events);
      
      default:
        throw new Error(`Unsupported format: ${format}`);
    }
  }

  private initializeFrameworks(): void {
    // GDPR Framework
    this.regulations.set('gdpr', {
      name: 'General Data Protection Regulation',
      relevant_events: ['data_upload', 'access_granted', 'data_export', 'data_deletion'],
      requirements: [
        'data_minimization',
        'purpose_limitation',
        'consent_tracking',
        'right_to_erasure'
      ],
      retention_limits: {
        personal_data: 365, // days
        consent_records: 2555 // 7 years
      }
    });

    // SOX Framework
    this.regulations.set('sox', {
      name: 'Sarbanes-Oxley Act',
      relevant_events: ['config_change', 'access_granted', 'financial_calculation'],
      requirements: [
        'audit_trail_integrity',
        'access_controls',
        'change_management',
        'data_retention'
      ],
      retention_limits: {
        financial_records: 2555, // 7 years
        audit_logs: 2555
      }
    });
  }
}
```

## Real-Time Monitoring

### Event Streaming & Alerting

```typescript
class LedgerMonitor {
  private ledger: SystemLedger;
  private alertRules: AlertRule[];
  private notificationChannels: NotificationChannel[];
  private eventStream: EventStream;

  constructor(ledger: SystemLedger) {
    this.ledger = ledger;
    this.alertRules = [];
    this.notificationChannels = [];
    this.eventStream = new EventStream();
    this.setupEventListeners();
  }

  addAlertRule(rule: AlertRule): void {
    this.alertRules.push(rule);
  }

  private setupEventListeners(): void {
    this.ledger.eventBus.on('event:recorded', async (event: LedgerEvent) => {
      // Stream event
      this.eventStream.emit(event);

      // Check alert rules
      for (const rule of this.alertRules) {
        if (await this.evaluateAlertRule(rule, event)) {
          await this.triggerAlert(rule, event);
        }
      }
    });
  }

  private async evaluateAlertRule(rule: AlertRule, event: LedgerEvent): Promise<boolean> {
    // Evaluate conditions
    for (const condition of rule.conditions) {
      const result = await this.evaluateCondition(condition, event);
      if (!result) return false;
    }

    // Check rate limiting
    if (rule.rate_limit) {
      const recentAlerts = await this.getRecentAlerts(rule.id, rule.rate_limit.window_ms);
      if (recentAlerts.length >= rule.rate_limit.max_alerts) {
        return false;
      }
    }

    return true;
  }

  private async triggerAlert(rule: AlertRule, event: LedgerEvent): Promise<void> {
    const alert: Alert = {
      id: this.generateAlertId(),
      rule_id: rule.id,
      event_id: event.id,
      severity: rule.severity,
      title: rule.title,
      description: this.generateAlertDescription(rule, event),
      timestamp: new Date().toISOString(),
      acknowledged: false
    };

    // Send notifications
    for (const channel of this.notificationChannels) {
      if (rule.notification_channels.includes(channel.id)) {
        await channel.send(alert);
      }
    }

    // Record alert in ledger
    await this.ledger.recordEvent({
      agent_id: 'system.monitor',
      event_type: 'security_violation',
      event_scope: 'monitoring.alert',
      subject_id: alert.id,
      description: `Alert triggered: ${alert.title}`,
      data: { alert, triggering_event: event }
    });
  }
}

interface AlertRule {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  conditions: AlertCondition[];
  notification_channels: string[];
  rate_limit?: {
    max_alerts: number;
    window_ms: number;
  };
  enabled: boolean;
}

interface AlertCondition {
  field: string;
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'matches';
  value: any;
  case_sensitive?: boolean;
}
```

## Implementation Status

- **Core Ledger**: ✅ Complete
- **Event Ingestion**: ✅ Complete
- **Provenance Tracking**: ✅ Complete
- **Compliance Reporting**: ✅ Complete
- **Real-time Monitoring**: ✅ Complete
- **Cryptographic Integrity**: ✅ Complete

---

*This document provides the complete technical specification for the System Ledger with full audit capabilities and compliance features.*
