---
title: "Prompt Management"
description: "Technical specification for prompt management"
type: "developer-guide"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing prompt management"
---

# 01: kOS Prompt Management System

> **Source**: `documentation/brainstorm/kOS/106_prompt_manager.md`  
> **Migrated**: 2025-01-20  
> **Status**: Core System Document

## Overview

This document defines the complete architecture and operational practices for the Prompt Manager in the kAI/kOS system. The system supports centralized prompt workflows, prompt injection safety, multi-agent version control, and distributed delivery to edge agents.

## System Architecture

### Purpose & Scope

The Prompt Manager serves as the central control system for:
- **Centralized Management**: Control prompts across all agents and services
- **Consistency Maintenance**: Ensure uniform agent behavior and responses
- **Safety Integration**: Implement prompt injection safety and sanitization
- **Customization Support**: Enable user and context-specific prompt variations
- **Developer Integration**: Integrate prompt logic into UI, services, agents, and pipelines

### Supported Prompt Types

| Type | Purpose | Use Cases |
|------|---------|-----------|
| **System Prompts** | Boot/initialization personality | Agent startup behavior, core personality traits |
| **Instruction Prompts** | Task-specific guidance | Specific task execution instructions |
| **Reflex Prompts** | Event/trigger-based responses | Automated responses to specific conditions |
| **RAG Templates** | Retrieval-augmented query formatters | Context-aware information retrieval |
| **Dialog Scripts** | Chat sequences for simulation/tutorials | User onboarding, training scenarios |
| **Safety Injection Rules** | Sanitization and fallback prompts | Security, content filtering, error handling |

## System Architecture

### Directory Structure

```plaintext
/prompt-manager/
├── config/
│   ├── prompt_roles.yaml         # Role-specific prompt assignments
│   ├── injection_rules.yaml      # Regex + fallback prompt mappings
│   ├── environment_tags.yaml     # Tag-based prompt injection (dev, prod, etc)
│   └── security_policies.yaml    # Safety and security configurations
├── ui/
│   ├── prompt_editor.tsx         # GUI prompt editor component
│   ├── prompt_browser.tsx        # Prompt library browser
│   └── testing_interface.tsx     # Prompt testing and validation UI
├── registry/
│   ├── agents/
│   │   ├── planner_agent.md      # Agent-specific prompts
│   │   ├── executor_agent.md
│   │   └── reviewer_agent.md
│   ├── workflows/
│   │   ├── onboarding_dialog.md  # Workflow-specific prompts
│   │   └── task_planning.md
│   ├── core/
│   │   ├── system_default.md     # Core system prompts
│   │   ├── fallback_persona.md   # Fallback behavior definitions
│   │   └── safety_templates.md   # Security and safety prompts
│   └── custom/
│       └── user_personas.md      # User-customized prompts
├── pipelines/
│   ├── test_runner.py            # Automated prompt testing
│   ├── hallucination_detector.py # Safety and accuracy analysis
│   ├── version_sync.py           # GitOps + CDN deployment
│   └── quality_analyzer.py       # Prompt effectiveness metrics
├── sandbox/
│   ├── prompt_playground.ipynb   # Local experimentation environment
│   ├── behavior_tracer.py        # Prompt impact analysis
│   └── a_b_testing.py           # Prompt variant testing
├── vault/
│   ├── encrypted_prompts/        # AES-256 secured sensitive prompts
│   ├── signed_hashes.json        # Integrity verification
│   └── access_logs.json          # Audit trail for prompt access
```

## Core System Modules

### Prompt Registry

**Storage Format**: Markdown-based with YAML frontmatter

**Metadata Structure**:
```yaml
---
id: planner_agent_v2.1
agent: kPlanner
role: task_decomposition
version: 2.1.0
status: active
author: system
created: 2025-01-20T10:00:00Z
updated: 2025-01-20T15:30:00Z
tags: [planning, task_management, core]
security_level: standard
---

# Task Planning Prompt

You are a task planning agent responsible for...
```

**Version Control**:
- Git-based versioning with full audit trail
- Semantic versioning for all prompts
- Automated changelog generation
- Branch-based development workflow

### Prompt Router

**Request Interception**: Centralized prompt request handling

**Rule Application Hierarchy**:
1. **Environment Tags**: Development, staging, production overrides
2. **Agent Roles**: Agent-type specific prompt logic
3. **Injection Rules**: Security, safety, and content filtering
4. **User Customization**: Personal preference overlays

**Configuration Files**:
```yaml
# prompt_roles.yaml
roles:
  kPlanner:
    default_prompt: planner_agent_v2.1
    fallback_prompt: planner_fallback_v1.0
    safety_level: standard
  
  kExecutor:
    default_prompt: executor_agent_v1.5
    fallback_prompt: executor_safe_v1.0
    safety_level: high

# injection_rules.yaml
rules:
  - pattern: "(?i)(hack|exploit|bypass)"
    action: redirect
    target: security_warning_prompt
  - pattern: "(?i)(personal|private|confidential)"
    action: filter
    replacement: "[REDACTED]"
```

### Prompt Editor UI

**Features**:
- **Tree View**: Hierarchical organization of agents and prompt slots
- **Git Integration**: Built-in version control and change history
- **Testing Sandbox**: Role-based prompt testing environment
- **Collaboration Tools**: Multi-user editing with conflict resolution
- **Preview Mode**: Real-time prompt rendering and validation

**Interface Components**:
```typescript
interface PromptEditorProps {
  promptId: string;
  agentType: AgentType;
  editMode: 'edit' | 'view' | 'test';
  onSave: (prompt: PromptDefinition) => void;
  onTest: (prompt: string, context: TestContext) => void;
}
```

### PromptOps CLI

**Command Line Interface**:
```bash
# Prompt Validation
promptops validate registry/agents/trust_guardian.md
promptops validate --all --strict

# Deployment Management
promptops deploy registry/core/system_default.md --env beta
promptops deploy --agent kPlanner --version 2.1.0

# Security Scanning
promptops scan --all --strict
promptops audit --since "2025-01-01"

# Testing Operations
promptops test registry/agents/planner_agent.md --scenarios critical
promptops benchmark --agent kExecutor --iterations 100

# Version Management
promptops version bump registry/core/system_default.md --patch
promptops rollback --agent kPlanner --version 2.0.0
```

## PromptOps Best Practices

### Development Guidelines

#### ✅ **Recommended Practices**
- **Separation of Concerns**: Separate personality from task instructions
- **Safety First**: Always include fallback safety prompts
- **Structured Format**: Use consistent delimiters for prompt sections
- **Comprehensive Testing**: Test edge-case queries and adversarial inputs
- **Audit Trail**: Log and trace all output generation paths
- **Version Control**: Maintain detailed changelog entries for all modifications

#### ❌ **Practices to Avoid**
- **Live Modifications**: Never modify production prompts without proper testing
- **Unvalidated Deployment**: Don't deploy unvalidated prompt sets to production
- **Hardcoded Values**: Avoid embedding sensitive information directly in prompts
- **Single Point of Failure**: Don't rely on single prompts without fallbacks

### Quality Assurance

**Testing Framework**:
```python
class PromptTestSuite:
    def test_safety_compliance(self, prompt: str) -> bool:
        """Verify prompt meets safety guidelines"""
        
    def test_output_consistency(self, prompt: str, iterations: int) -> float:
        """Measure output consistency across multiple runs"""
        
    def test_adversarial_resistance(self, prompt: str) -> SecurityReport:
        """Test resistance to prompt injection attacks"""
        
    def test_performance_impact(self, prompt: str) -> PerformanceMetrics:
        """Measure computational and response time impact"""
```

## Prompt Versioning & Distribution

### Version Management

**Semantic Versioning**: All prompts follow semantic versioning (MAJOR.MINOR.PATCH)
- **MAJOR**: Breaking changes to prompt structure or behavior
- **MINOR**: New features or significant improvements
- **PATCH**: Bug fixes and minor adjustments

**Distribution Pipeline**:
1. **Development**: Local testing and validation
2. **Staging**: Integration testing with beta agents
3. **Production**: Deployment to live agents with monitoring
4. **Rollback**: Automated rollback on performance degradation

### CDN Distribution

**Hash-Stamped Deployment**:
```json
{
  "prompt_pack": "kos-prompts-v2.1.0",
  "hash": "sha256:a1b2c3d4e5f6...",
  "agents": {
    "kPlanner": "planner_agent_v2.1.0",
    "kExecutor": "executor_agent_v1.5.2"
  },
  "deployment_time": "2025-01-20T16:00:00Z"
}
```

## Security & Safety Framework

### Security Controls

**Encryption & Storage**:
- **AES-256 Encryption**: Sensitive prompts stored with strong encryption
- **SHA-256 Verification**: Hash verification on prompt loading
- **Access Control**: Role-based access to sensitive prompt categories
- **Audit Logging**: Comprehensive access and modification logging

**Safety Mechanisms**:
```python
class PromptSafetyController:
    def validate_prompt(self, prompt: str) -> ValidationResult:
        """Comprehensive prompt safety validation"""
        
    def detect_hallucination_risk(self, prompt: str) -> RiskAssessment:
        """Analyze potential for hallucination generation"""
        
    def apply_content_filters(self, prompt: str) -> str:
        """Apply content filtering and sanitization"""
        
    def generate_fallback(self, failed_prompt: str) -> str:
        """Generate safe fallback prompt for failed prompts"""
```

### Injection Prevention

**Multi-Layer Defense**:
1. **Input Sanitization**: Clean and validate all prompt inputs
2. **Pattern Matching**: Detect and block known injection patterns
3. **Context Isolation**: Isolate user input from system prompts
4. **Output Monitoring**: Monitor agent outputs for unexpected behavior

## Integration Architecture

### System Integration Points

**kAI Browser Extension**:
- Local editable prompt workspace
- Real-time prompt synchronization
- User customization interface
- Offline prompt caching

**kOS Core Agents**:
- Prompt router API integration
- Dynamic prompt loading
- Performance monitoring
- Fallback handling

**Workflow Engine**:
- Template-based prompt injection
- Context-aware prompt selection
- Workflow-specific customizations
- Progress tracking integration

**Persona System**:
- Persona-aligned prompt selection
- Dynamic personality adjustment
- Context-sensitive behavior modification
- User preference integration

## Development Roadmap

### Phase 1: Foundation (Current)
- ✅ Basic prompt registry and versioning
- ✅ Core prompt router functionality
- ✅ Essential safety controls
- ✅ CLI tooling for basic operations

### Phase 2: Advanced Features
- 🔄 **Multi-language Support**: Prompt translations and localization
- 🔄 **Advanced Testing**: Comprehensive A/B testing framework
- 🔄 **Performance Analytics**: Detailed prompt effectiveness metrics
- 🔄 **Automated Optimization**: ML-driven prompt improvement

### Phase 3: Ecosystem Integration
- 🌐 **Prompt Marketplace**: Web-based community prompt sharing
- 🔍 **AI-Powered Auditing**: Automated prompt quality and safety analysis
- 🧠 **Evolutionary Optimization**: Reinforcement learning-based prompt evolution
- �� **Cross-Platform Sync**: Seamless prompt synchronization across all platforms

## Implementation Examples

### Prompt Definition Example

```markdown
---
id: task_planner_v3.0
agent: kPlanner
role: task_decomposition
version: 3.0.0
status: active
safety_level: standard
tags: [planning, core, production]
---

# Task Planning Agent

## Core Behavior
You are a sophisticated task planning agent responsible for breaking down complex goals into actionable subtasks.

## Guidelines
- Always provide clear, actionable steps
- Consider dependencies between tasks
- Estimate time and resources required
- Include validation criteria for each step

## Safety Constraints
- Never suggest actions that could harm users or systems
- Always include appropriate warnings for potentially risky operations
- Escalate to human oversight for ambiguous or high-risk tasks

## Output Format
Provide your response in structured JSON format with the following schema:
```json
{
  "tasks": [...],
  "dependencies": [...],
  "estimated_time": "...",
  "risk_level": "low|medium|high"
}
```
```

---

### Related Documents
- [Agent Framework](../agents/01_Agent_Framework.md) - Agent system integration
- [Security Architecture](../security/01_Security_Architecture.md) - Security framework
- [Service Architecture](../services/01_Service_Architecture.md) - Service integration

### External References
- [Prompt Engineering Best Practices](https://example.com/prompt-engineering)
- [AI Safety Guidelines](https://example.com/ai-safety)
- [Version Control Best Practices](https://example.com/version-control)

