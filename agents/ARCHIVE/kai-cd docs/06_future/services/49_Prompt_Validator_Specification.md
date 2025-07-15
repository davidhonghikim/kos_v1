---
title: "Prompt Validator Specification"
description: "Architecture, logic, and safety mechanisms for the Prompt Validator subsystem ensuring prompt compliance with security standards, policies, and contextual integrity"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2024-12-28"
related_docs: [
  "documentation/future/services/47_prompt-manager-design-system-integration.md",
  "documentation/future/services/48_prompt-transformer-engine-specification.md",
  "documentation/future/security/05_comprehensive-security-architecture.md"
]
implementation_status: "planned"
---

# Prompt Validator Specification

## Agent Context
**For AI Agents**: This document defines the Prompt Validator that enforces prompt compliance before LLM execution. All prompts must pass through this validation pipeline. Use the TypeScript interfaces for consistent validation handling. Pay attention to the security boundaries, PII filtering, and policy enforcement mechanisms. The validator must be integrated at every prompt processing stage.

## Purpose and Scope

The Prompt Validator enforces comprehensive prompt compliance across:

- **Security boundaries** and injection attack prevention
- **PII and data leakage prevention** with configurable redaction
- **Organizational prompt policies** with customizable rule sets
- **LLM safety input checks** and content filtering
- **Format and token constraints** with length validation

## Architecture & Directory Structure

```typescript
interface PromptValidatorArchitecture {
  core: {
    'src/core/prompt/validators/': {
      'PromptSchemaChecker.ts': 'Structural validation (fields, types)';
      'PromptPIIFilter.ts': 'PII detection and redaction';
      'PromptLengthLimiter.ts': 'Token and length constraints';
      'PromptPolicyEnforcer.ts': 'Custom rules per user/org/system';
      'PromptSafetyScanner.ts': 'Banned words, injection detection';
      'ValidatorPipeline.ts': 'Orchestrates validation steps';
    };
  };
  config: {
    'validator_configs/': {
      'pii_patterns.yaml': 'PII detection patterns';
      'max_lengths.yaml': 'Length limits by context';
      'policy_rules.yaml': 'Organizational policies';
      'safety_patterns.yaml': 'Security and safety rules';
    };
  };
}
```

## Validation Pipeline

```typescript
interface ValidationPipelineSteps {
  steps: [
    'Schema Validation',
    'Length Validation', 
    'PII Detection & Filtering',
    'Policy Enforcement',
    'Safety Scanning',
    'Final Verification'
  ];
}

class ValidatorPipeline {
  private validators: PromptValidator[] = [];
  private config: ValidatorConfig;
  
  constructor(config: ValidatorConfig) {
    this.config = config;
    this.initializePipeline();
  }
  
  async validate(prompt: PromptValidationRequest): Promise<ValidationResult> {
    const results: StepResult[] = [];
    let currentPrompt = prompt.content;
    let violations: ValidationViolation[] = [];
    
    for (const validator of this.validators) {
      const stepResult = await validator.validate(currentPrompt, prompt.context);
      results.push(stepResult);
      
      if (!stepResult.valid) {
        violations.push(...stepResult.violations);
        
        if (stepResult.action === 'block') {
          return {
            valid: false,
            violations,
            reason: `Blocked by ${validator.name}: ${stepResult.reason}`,
            originalPrompt: prompt.content,
            processedPrompt: currentPrompt
          };
        }
      }
      
      // Apply transformations (redaction, etc.)
      if (stepResult.transformedPrompt) {
        currentPrompt = stepResult.transformedPrompt;
      }
    }
    
    return {
      valid: violations.length === 0,
      violations,
      originalPrompt: prompt.content,
      processedPrompt: currentPrompt,
      metadata: {
        stepsExecuted: results.length,
        transformationsApplied: results.filter(r => r.transformedPrompt).length
      }
    };
  }
}

// PII Filter Implementation
class PromptPIIFilter implements PromptValidator {
  name = 'PIIFilter';
  private patterns: PIIPattern[];
  
  async validate(prompt: string, context: ValidationContext): Promise<StepResult> {
    const detectedPII: PIIDetection[] = [];
    let redactedPrompt = prompt;
    
    for (const pattern of this.patterns) {
      const matches = prompt.match(new RegExp(pattern.regex, 'gi'));
      if (matches) {
        matches.forEach(match => {
          detectedPII.push({
            type: pattern.name,
            value: match,
            position: prompt.indexOf(match),
            confidence: pattern.confidence || 0.9
          });
          
          // Apply redaction
          redactedPrompt = redactedPrompt.replace(
            new RegExp(escapeRegExp(match), 'gi'), 
            pattern.replacement || '[REDACTED]'
          );
        });
      }
    }
    
    return {
      valid: detectedPII.length === 0,
      violations: detectedPII.map(pii => ({
        type: 'pii_detected',
        severity: 'high',
        message: `${pii.type} detected: ${pii.value}`,
        action: 'redact'
      })),
      transformedPrompt: detectedPII.length > 0 ? redactedPrompt : undefined,
      metadata: { piiDetected: detectedPII }
    };
  }
}

// Safety Scanner Implementation  
class PromptSafetyScanner implements PromptValidator {
  name = 'SafetyScanner';
  private injectionPatterns: RegExp[];
  private bannedPhrases: string[];
  
  async validate(prompt: string, context: ValidationContext): Promise<StepResult> {
    const violations: ValidationViolation[] = [];
    
    // Check for injection attacks
    for (const pattern of this.injectionPatterns) {
      if (pattern.test(prompt)) {
        violations.push({
          type: 'injection_attempt',
          severity: 'critical',
          message: 'Potential prompt injection detected',
          action: 'block'
        });
      }
    }
    
    // Check for banned content
    for (const phrase of this.bannedPhrases) {
      if (prompt.toLowerCase().includes(phrase.toLowerCase())) {
        violations.push({
          type: 'banned_content',
          severity: 'high',
          message: `Banned phrase detected: ${phrase}`,
          action: 'block'
        });
      }
    }
    
    return {
      valid: violations.length === 0,
      violations,
      action: violations.some(v => v.action === 'block') ? 'block' : 'allow'
    };
  }
}

interface ValidationResult {
  valid: boolean;
  violations: ValidationViolation[];
  reason?: string;
  originalPrompt: string;
  processedPrompt: string;
  metadata?: Record<string, any>;
}

interface ValidationViolation {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  action: 'warn' | 'redact' | 'block';
}
```

## Configuration System

```typescript
// PII Patterns Configuration
interface PIIPattern {
  name: string;
  regex: string;
  replacement?: string;
  confidence?: number;
  enabled: boolean;
}

const defaultPIIPatterns: PIIPattern[] = [
  {
    name: 'email',
    regex: '[\\w.-]+@[\\w.-]+\\.[a-zA-Z]{2,}',
    replacement: '[EMAIL_REDACTED]',
    confidence: 0.95,
    enabled: true
  },
  {
    name: 'ip_address', 
    regex: '\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b',
    replacement: '[IP_REDACTED]',
    confidence: 0.9,
    enabled: true
  },
  {
    name: 'phone',
    regex: '\\b\\d{3}[-.\s]?\\d{3}[-.\s]?\\d{4}\\b',
    replacement: '[PHONE_REDACTED]',
    confidence: 0.85,
    enabled: true
  },
  {
    name: 'ssn',
    regex: '\\b\\d{3}-\\d{2}-\\d{4}\\b',
    replacement: '[SSN_REDACTED]',
    confidence: 0.98,
    enabled: true
  }
];

// Length Limits Configuration
interface LengthLimits {
  default: number;
  byTaskType: Record<string, number>;
  byUserRole: Record<string, number>;
}

const defaultLengthLimits: LengthLimits = {
  default: 2048,
  byTaskType: {
    summarizer: 1024,
    translator: 3072,
    codeGenerator: 4096,
    analyst: 8192
  },
  byUserRole: {
    basic: 1024,
    premium: 4096,
    enterprise: 16384
  }
};

// Policy Rules Configuration
interface PolicyRule {
  id: string;
  name: string;
  description: string;
  taskPattern?: string;
  personaPattern?: string;
  userRole?: string;
  action: 'allow' | 'deny' | 'require_approval';
  conditions: PolicyCondition[];
}

interface PolicyCondition {
  type: 'contains' | 'matches' | 'length' | 'custom';
  value: string | number;
  operator?: 'eq' | 'gt' | 'lt' | 'contains';
}
```

## API Integration

```typescript
class PromptValidatorAPI {
  private pipeline: ValidatorPipeline;
  
  async validatePrompt(req: Request, res: Response): Promise<void> {
    try {
      const { prompt, context } = req.body;
      
      const validationRequest: PromptValidationRequest = {
        content: prompt,
        context: {
          userId: req.user.id,
          userRole: req.user.role,
          taskType: context?.taskType,
          persona: context?.persona,
          ...context
        }
      };
      
      const result = await this.pipeline.validate(validationRequest);
      
      res.json({
        valid: result.valid,
        processedPrompt: result.processedPrompt,
        violations: result.violations,
        metadata: result.metadata
      });
      
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
}

// SDK Integration
class PromptValidatorSDK {
  async validatePrompt(prompt: string, context?: ValidationContext): Promise<ValidationResult> {
    const response = await fetch('/api/prompts/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, context })
    });
    
    return response.json();
  }
}
```

## Security & Logging

```typescript
class ValidationAuditLogger {
  async logValidation(result: ValidationResult, context: ValidationContext): Promise<void> {
    const logEntry = {
      timestamp: new Date().toISOString(),
      userId: context.userId,
      valid: result.valid,
      violationCount: result.violations.length,
      violationTypes: result.violations.map(v => v.type),
      promptLength: result.originalPrompt.length,
      transformationsApplied: result.metadata?.transformationsApplied || 0
    };
    
    await this.writeLog(logEntry);
  }
  
  async generateComplianceReport(dateRange: DateRange): Promise<ComplianceReport> {
    // Generate compliance statistics
    return {
      period: dateRange,
      totalValidations: 0,
      violationsByType: {},
      userCompliance: {},
      trends: {}
    };
  }
}
```

## Future Features

| Feature | Target Version | Status |
| ------- | -------------- | ------ |
| Context-Aware Redaction | v1.2 | Planned |
| LLM-based Violation Repair | v1.3 | Research |
| Multi-lingual PII Scrubber | v1.3 | Planned |
| Prompt Safety Score Report | v1.4 | Planned |
| Compliance Mode | v2.0 | Future |

## Implementation Status

- **Core Pipeline**: Architecture and interfaces defined
- **PII Detection**: Pattern-based system with configurable rules
- **Safety Scanning**: Injection and content filtering framework
- **Policy Enforcement**: Rule-based validation system
- **API Integration**: REST API and SDK interfaces ready
- **Audit System**: Compliance logging and reporting framework

## Changelog

- **2024-12-28**: Comprehensive prompt validator specification with TypeScript implementations
- **2025-06-20**: Initial detailed blueprint with validator pipeline and config system (legacy reference) 