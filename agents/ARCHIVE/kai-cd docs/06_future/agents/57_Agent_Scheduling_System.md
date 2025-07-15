---
title: "Agent Scheduling System"
description: "Comprehensive task scheduling, priority queues, timers, and inter-agent job delegation architecture"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs:
  - "future/agents/agent-memory-systems.md"
  - "future/protocols/kind-link-protocol-core.md"
  - "future/agents/agent-behavior-modeling.md"
implementation_status: "planned"
---

# Agent Scheduling System

## Agent Context
This document defines the complete task scheduling architecture for agents in the kOS ecosystem. Essential for agents implementing task queues, priority management, cron scheduling, timer events, and inter-agent job delegation. All scheduling operations must follow these specifications for consistency and reliability.

## Scheduling Architecture Overview

Each agent maintains an embedded scheduler runtime supporting local task queues, priority indexing, timer events, and external job delegation through the KindLink Protocol. The scheduler is pluggable and configurable for different agent requirements.

## Core Scheduling Components

### Task Definition Schema

```typescript
interface AgentTask {
  id: string;
  type: TaskType;
  run_at: Date;
  repeat?: CronExpression;
  priority: TaskPriority;
  action: TaskAction;
  dependencies: string[];
  tags: string[];
  metadata: TaskMetadata;
  status: TaskStatus;
  created_at: Date;
  updated_at: Date;
}

type TaskType = 
  | 'once'        // Single execution
  | 'cron'        // Recurring cron schedule
  | 'stream'      // Continuous processing
  | 'reaction'    // Event-triggered
  | 'external'    // Delegated from another agent
  | 'conditional'; // Condition-based execution

type TaskPriority = 0 | 1 | 2 | 3 | 4 | 5; // 0=critical, 5=background

interface TaskAction {
  module: string;
  function: string;
  args: any[];
  timeout?: number;
  retry_policy?: RetryPolicy;
}

interface TaskMetadata {
  source: string;
  author: string;
  description: string;
  estimated_duration?: number;
  resource_requirements?: ResourceRequirements;
  security_context?: SecurityContext;
}

type TaskStatus = 
  | 'pending'
  | 'queued'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'paused';

class TaskManager {
  private tasks = new Map<string, AgentTask>();
  private scheduler: TaskScheduler;
  
  async createTask(definition: TaskDefinition): Promise<AgentTask> {
    const task: AgentTask = {
      id: this.generateTaskId(),
      type: definition.type,
      run_at: definition.run_at,
      repeat: definition.repeat,
      priority: definition.priority,
      action: definition.action,
      dependencies: definition.dependencies || [],
      tags: definition.tags || [],
      metadata: definition.metadata,
      status: 'pending',
      created_at: new Date(),
      updated_at: new Date()
    };
    
    // Validate task definition
    await this.validateTask(task);
    
    // Store task
    this.tasks.set(task.id, task);
    
    // Schedule for execution
    await this.scheduler.scheduleTask(task);
    
    return task;
  }
  
  async updateTaskStatus(taskId: string, status: TaskStatus, result?: any): Promise<void> {
    const task = this.tasks.get(taskId);
    if (!task) throw new Error(`Task not found: ${taskId}`);
    
    task.status = status;
    task.updated_at = new Date();
    
    // Handle status-specific logic
    switch (status) {
      case 'completed':
        await this.handleTaskCompletion(task, result);
        break;
      case 'failed':
        await this.handleTaskFailure(task, result);
        break;
      case 'cancelled':
        await this.handleTaskCancellation(task);
        break;
    }
    
    // Emit status change event
    await this.emitTaskStatusEvent(task, status);
  }
}
```

### Priority Queue Implementation

```typescript
interface PriorityQueue {
  enqueue(task: AgentTask): void;
  dequeue(): AgentTask | null;
  peek(): AgentTask | null;
  size(): number;
  isEmpty(): boolean;
}

interface QueueBand {
  priority: TaskPriority;
  tasks: AgentTask[];
  time_slice: number;     // Execution time slice in ms
  aging_factor: number;   // Rate of priority aging
  max_capacity: number;
}

class MultilevelFeedbackQueue implements PriorityQueue {
  private bands: Map<TaskPriority, QueueBand>;
  private currentBand: TaskPriority = 0;
  private executionHistory: ExecutionRecord[];
  
  constructor() {
    this.bands = new Map([
      [0, { priority: 0, tasks: [], time_slice: 1000, aging_factor: 0, max_capacity: 10 }],      // Critical
      [1, { priority: 1, tasks: [], time_slice: 800, aging_factor: 0.1, max_capacity: 20 }],    // Realtime
      [2, { priority: 2, tasks: [], time_slice: 600, aging_factor: 0.2, max_capacity: 50 }],    // Interactive
      [3, { priority: 3, tasks: [], time_slice: 400, aging_factor: 0.3, max_capacity: 100 }],   // Default
      [4, { priority: 4, tasks: [], time_slice: 200, aging_factor: 0.4, max_capacity: 200 }],   // Idle
      [5, { priority: 5, tasks: [], time_slice: 100, aging_factor: 0.5, max_capacity: 500 }]    // Background
    ]);
  }
  
  enqueue(task: AgentTask): void {
    const band = this.bands.get(task.priority);
    if (!band) throw new Error(`Invalid priority: ${task.priority}`);
    
    // Check capacity
    if (band.tasks.length >= band.max_capacity) {
      // Try to age tasks to lower priority bands
      this.ageTasksInBand(task.priority);
      
      // If still at capacity, reject or queue in next band
      if (band.tasks.length >= band.max_capacity) {
        if (task.priority < 5) {
          task.priority = (task.priority + 1) as TaskPriority;
          this.enqueue(task);
          return;
        } else {
          throw new Error('Queue capacity exceeded');
        }
      }
    }
    
    band.tasks.push(task);
    this.sortBandByPriority(task.priority);
  }
  
  dequeue(): AgentTask | null {
    // Round-robin through bands with tasks
    for (let i = 0; i < 6; i++) {
      const band = this.bands.get(this.currentBand);
      if (band && band.tasks.length > 0) {
        const task = band.tasks.shift()!;
        this.recordExecution(task);
        return task;
      }
      
      this.currentBand = ((this.currentBand + 1) % 6) as TaskPriority;
    }
    
    return null; // No tasks available
  }
  
  private ageTasksInBand(priority: TaskPriority): void {
    const band = this.bands.get(priority);
    if (!band || band.aging_factor === 0) return;
    
    const now = Date.now();
    const tasksToAge: AgentTask[] = [];
    
    band.tasks.forEach(task => {
      const age = now - task.created_at.getTime();
      const agingThreshold = 300000; // 5 minutes
      
      if (age > agingThreshold && Math.random() < band.aging_factor) {
        tasksToAge.push(task);
      }
    });
    
    // Move aged tasks to higher priority band
    tasksToAge.forEach(task => {
      if (task.priority > 0) {
        band.tasks = band.tasks.filter(t => t.id !== task.id);
        task.priority = (task.priority - 1) as TaskPriority;
        this.enqueue(task);
      }
    });
  }
}
```

### Cron and Timer System

```typescript
interface CronScheduler {
  schedule(task: AgentTask): void;
  unschedule(taskId: string): void;
  getNextRun(cronExpression: string): Date;
  validateExpression(expression: string): boolean;
}

interface TimerManager {
  setTimeout(callback: () => void, delay: number): string;
  setInterval(callback: () => void, interval: number): string;
  clearTimer(timerId: string): void;
  getActiveTimers(): TimerInfo[];
}

class CronSchedulerImpl implements CronScheduler {
  private scheduledTasks = new Map<string, ScheduledTask>();
  private timerManager: TimerManager;
  
  schedule(task: AgentTask): void {
    if (task.type !== 'cron' || !task.repeat) {
      throw new Error('Task must be of type "cron" with repeat expression');
    }
    
    // Validate cron expression
    if (!this.validateExpression(task.repeat)) {
      throw new Error(`Invalid cron expression: ${task.repeat}`);
    }
    
    const nextRun = this.getNextRun(task.repeat);
    const delay = nextRun.getTime() - Date.now();
    
    const timerId = this.timerManager.setTimeout(() => {
      this.executeCronTask(task);
    }, delay);
    
    this.scheduledTasks.set(task.id, {
      task,
      timerId,
      nextRun,
      lastRun: null
    });
  }
  
  getNextRun(cronExpression: string): Date {
    // Parse cron expression: "minute hour day month dayOfWeek"
    const parts = cronExpression.split(' ');
    if (parts.length !== 5) {
      throw new Error('Cron expression must have 5 parts');
    }
    
    const [minute, hour, day, month, dayOfWeek] = parts;
    const now = new Date();
    const next = new Date(now);
    
    // Simple cron parser implementation
    // This is a simplified version - production would use a full cron library
    next.setSeconds(0, 0);
    
    if (minute !== '*') {
      next.setMinutes(parseInt(minute));
    }
    
    if (hour !== '*') {
      next.setHours(parseInt(hour));
    }
    
    // If the calculated time is in the past, move to next occurrence
    if (next <= now) {
      if (minute !== '*' && hour !== '*') {
        next.setDate(next.getDate() + 1);
      } else if (minute !== '*') {
        next.setHours(next.getHours() + 1);
      } else {
        next.setMinutes(next.getMinutes() + 1);
      }
    }
    
    return next;
  }
  
  private async executeCronTask(task: AgentTask): Promise<void> {
    try {
      // Execute the task
      await this.executeTask(task);
      
      // Schedule next occurrence
      this.schedule(task);
      
    } catch (error) {
      console.error(`Cron task execution failed: ${task.id}`, error);
      
      // Apply retry policy if configured
      if (task.action.retry_policy) {
        await this.handleTaskRetry(task, error);
      }
    }
  }
}
```

### External Task Delegation

```typescript
interface TaskDelegationSystem {
  delegateTask(task: AgentTask, targetAgent: string): Promise<DelegationResult>;
  receiveTask(delegatedTask: DelegatedTask): Promise<AcceptanceResult>;
  registerAsConsumer(capabilities: string[]): Promise<void>;
  registerAsProducer(): Promise<void>;
}

interface DelegatedTask {
  original_task: AgentTask;
  delegation_metadata: DelegationMetadata;
  klp_signature: string;
}

interface DelegationMetadata {
  origin_agent: string;
  target_agent: string;
  delegation_reason: string;
  expected_completion: Date;
  resource_budget?: ResourceBudget;
  callback_endpoint?: string;
}

class KLPTaskDelegation implements TaskDelegationSystem {
  private klpClient: KLPClient;
  private capabilities: Set<string>;
  private trustManager: TrustManager;
  
  async delegateTask(task: AgentTask, targetAgent: string): Promise<DelegationResult> {
    // Verify target agent capabilities
    const targetCapabilities = await this.getAgentCapabilities(targetAgent);
    if (!this.canHandleTask(task, targetCapabilities)) {
      return {
        success: false,
        reason: 'Target agent lacks required capabilities'
      };
    }
    
    // Create delegation metadata
    const delegationMetadata: DelegationMetadata = {
      origin_agent: this.agentId,
      target_agent: targetAgent,
      delegation_reason: this.getDelegationReason(task),
      expected_completion: this.calculateExpectedCompletion(task),
      resource_budget: this.calculateResourceBudget(task),
      callback_endpoint: this.getCallbackEndpoint()
    };
    
    // Create KLP message
    const klpMessage = await this.klpClient.createMessage(
      targetAgent,
      'intent.task.delegate',
      {
        task,
        delegation_metadata: delegationMetadata
      }
    );
    
    // Send delegation request
    const response = await this.klpClient.sendMessage(klpMessage);
    
    if (response.status === 'accepted') {
      // Update local task status
      await this.updateTaskStatus(task.id, 'delegated', {
        target_agent: targetAgent,
        delegation_id: response.delegation_id
      });
      
      return {
        success: true,
        delegation_id: response.delegation_id,
        estimated_completion: response.estimated_completion
      };
    }
    
    return {
      success: false,
      reason: response.rejection_reason
    };
  }
  
  async receiveTask(delegatedTask: DelegatedTask): Promise<AcceptanceResult> {
    // Verify signature and trust level
    const isValid = await this.trustManager.verifyTaskDelegation(delegatedTask);
    if (!isValid) {
      return {
        accepted: false,
        reason: 'Invalid signature or insufficient trust level'
      };
    }
    
    // Check if we can handle the task
    const canHandle = this.canHandleTask(
      delegatedTask.original_task,
      Array.from(this.capabilities)
    );
    
    if (!canHandle) {
      return {
        accepted: false,
        reason: 'Insufficient capabilities to handle task'
      };
    }
    
    // Check resource availability
    const resourcesAvailable = await this.checkResourceAvailability(
      delegatedTask.delegation_metadata.resource_budget
    );
    
    if (!resourcesAvailable) {
      return {
        accepted: false,
        reason: 'Insufficient resources available'
      };
    }
    
    // Accept and queue the task
    const localTask = this.convertToLocalTask(delegatedTask);
    await this.createTask(localTask);
    
    return {
      accepted: true,
      delegation_id: this.generateDelegationId(),
      estimated_completion: this.calculateCompletionTime(localTask)
    };
  }
}
```

### Failure Handling and Retry Logic

```typescript
interface RetryPolicy {
  max_attempts: number;
  initial_delay: number;
  backoff_strategy: 'exponential' | 'linear' | 'fixed';
  backoff_factor: number;
  max_delay: number;
  retry_conditions: RetryCondition[];
}

interface RetryCondition {
  error_type: string;
  should_retry: boolean;
  custom_delay?: number;
}

interface FailureHandler {
  handleTaskFailure(task: AgentTask, error: TaskError): Promise<FailureResult>;
  shouldRetry(task: AgentTask, error: TaskError, attemptCount: number): boolean;
  calculateRetryDelay(policy: RetryPolicy, attemptCount: number): number;
}

class TaskFailureManager implements FailureHandler {
  async handleTaskFailure(task: AgentTask, error: TaskError): Promise<FailureResult> {
    const attemptCount = this.getAttemptCount(task.id);
    const retryPolicy = task.action.retry_policy;
    
    // Log failure
    await this.logTaskFailure(task, error, attemptCount);
    
    if (!retryPolicy || !this.shouldRetry(task, error, attemptCount)) {
      // Mark as permanently failed
      await this.markTaskFailed(task, error);
      
      // Trigger failure hooks
      await this.triggerFailureHooks(task, error);
      
      // Emit failure signal
      await this.emitFailureSignal(task, error);
      
      return {
        action: 'failed',
        retry_scheduled: false,
        final_attempt: true
      };
    }
    
    // Schedule retry
    const retryDelay = this.calculateRetryDelay(retryPolicy, attemptCount);
    await this.scheduleRetry(task, retryDelay);
    
    return {
      action: 'retry_scheduled',
      retry_scheduled: true,
      retry_delay: retryDelay,
      attempt_count: attemptCount + 1
    };
  }
  
  shouldRetry(task: AgentTask, error: TaskError, attemptCount: number): boolean {
    const policy = task.action.retry_policy;
    if (!policy) return false;
    
    // Check max attempts
    if (attemptCount >= policy.max_attempts) {
      return false;
    }
    
    // Check retry conditions
    for (const condition of policy.retry_conditions) {
      if (error.type === condition.error_type) {
        return condition.should_retry;
      }
    }
    
    // Default retry for transient errors
    const transientErrors = ['network_error', 'timeout', 'resource_unavailable'];
    return transientErrors.includes(error.type);
  }
  
  calculateRetryDelay(policy: RetryPolicy, attemptCount: number): number {
    let delay = policy.initial_delay;
    
    switch (policy.backoff_strategy) {
      case 'exponential':
        delay = policy.initial_delay * Math.pow(policy.backoff_factor, attemptCount);
        break;
      case 'linear':
        delay = policy.initial_delay + (policy.backoff_factor * attemptCount);
        break;
      case 'fixed':
        delay = policy.initial_delay;
        break;
    }
    
    return Math.min(delay, policy.max_delay);
  }
}
```

### Runtime Control Interface

```typescript
interface TaskControlAPI {
  listTasks(filters?: TaskFilter): Promise<AgentTask[]>;
  getTask(taskId: string): Promise<AgentTask>;
  createTask(definition: TaskDefinition): Promise<AgentTask>;
  updateTask(taskId: string, updates: Partial<AgentTask>): Promise<AgentTask>;
  deleteTask(taskId: string): Promise<void>;
  pauseTask(taskId: string): Promise<void>;
  resumeTask(taskId: string): Promise<void>;
  cancelTask(taskId: string): Promise<void>;
  getTaskHistory(taskId: string): Promise<TaskExecutionHistory>;
  exportTaskGraph(format: 'mermaid' | 'dot' | 'json'): Promise<string>;
}

class TaskControlManager implements TaskControlAPI {
  async listTasks(filters?: TaskFilter): Promise<AgentTask[]> {
    let tasks = Array.from(this.taskManager.getAllTasks());
    
    if (filters) {
      tasks = this.applyFilters(tasks, filters);
    }
    
    return tasks.sort((a, b) => a.created_at.getTime() - b.created_at.getTime());
  }
  
  async pauseTask(taskId: string): Promise<void> {
    const task = await this.getTask(taskId);
    
    if (task.status === 'running') {
      // Signal running task to pause
      await this.signalTaskPause(taskId);
    }
    
    // Update status
    await this.updateTaskStatus(taskId, 'paused');
    
    // Remove from scheduler
    await this.scheduler.unscheduleTask(taskId);
  }
  
  async resumeTask(taskId: string): Promise<void> {
    const task = await this.getTask(taskId);
    
    if (task.status !== 'paused') {
      throw new Error(`Cannot resume task with status: ${task.status}`);
    }
    
    // Update status
    await this.updateTaskStatus(taskId, 'queued');
    
    // Re-add to scheduler
    await this.scheduler.scheduleTask(task);
  }
  
  async exportTaskGraph(format: 'mermaid' | 'dot' | 'json'): Promise<string> {
    const tasks = await this.listTasks();
    const graph = this.buildTaskDependencyGraph(tasks);
    
    switch (format) {
      case 'mermaid':
        return this.generateMermaidDiagram(graph);
      case 'dot':
        return this.generateDotGraph(graph);
      case 'json':
        return JSON.stringify(graph, null, 2);
      default:
        throw new Error(`Unsupported format: ${format}`);
    }
  }
}
```

## Security and Trust Framework

### Task Security Model

```typescript
interface TaskSecurityContext {
  required_trust_level: TrustLevel;
  required_capabilities: string[];
  resource_limits: ResourceLimits;
  sandbox_enabled: boolean;
  signature_required: boolean;
}

interface TaskValidator {
  validateTask(task: AgentTask, context: SecurityContext): Promise<ValidationResult>;
  validateDelegation(delegation: DelegatedTask): Promise<ValidationResult>;
  enforceResourceLimits(task: AgentTask): Promise<void>;
}

class TaskSecurityManager implements TaskValidator {
  async validateTask(task: AgentTask, context: SecurityContext): Promise<ValidationResult> {
    const validations: ValidationCheck[] = [];
    
    // Check trust level
    if (task.metadata.security_context?.required_trust_level) {
      const trustValid = await this.validateTrustLevel(
        context.executor_identity,
        task.metadata.security_context.required_trust_level
      );
      validations.push({
        type: 'trust_level',
        passed: trustValid,
        message: trustValid ? 'Trust level sufficient' : 'Insufficient trust level'
      });
    }
    
    // Check capabilities
    if (task.metadata.security_context?.required_capabilities) {
      const capabilitiesValid = await this.validateCapabilities(
        context.executor_identity,
        task.metadata.security_context.required_capabilities
      );
      validations.push({
        type: 'capabilities',
        passed: capabilitiesValid,
        message: capabilitiesValid ? 'Capabilities sufficient' : 'Missing required capabilities'
      });
    }
    
    // Check signature if required
    if (task.metadata.security_context?.signature_required) {
      const signatureValid = await this.validateTaskSignature(task);
      validations.push({
        type: 'signature',
        passed: signatureValid,
        message: signatureValid ? 'Signature valid' : 'Invalid or missing signature'
      });
    }
    
    const allPassed = validations.every(v => v.passed);
    
    return {
      valid: allPassed,
      checks: validations,
      security_level: this.calculateSecurityLevel(validations)
    };
  }
}
```

## Performance Optimization

### Scheduler Performance Features

1. **Queue Optimization**: Efficient priority queue implementation with O(log n) operations
2. **Task Batching**: Group similar tasks for batch execution
3. **Resource Pooling**: Reuse execution contexts and resources
4. **Lazy Loading**: Load task details only when needed
5. **Caching**: Cache frequently accessed task metadata

### Monitoring and Metrics

```typescript
interface SchedulerMetrics {
  tasks_scheduled: number;
  tasks_completed: number;
  tasks_failed: number;
  average_execution_time: number;
  queue_depths: Record<TaskPriority, number>;
  resource_utilization: ResourceUtilization;
  delegation_success_rate: number;
}

class SchedulerMonitor {
  async collectMetrics(): Promise<SchedulerMetrics> {
    return {
      tasks_scheduled: this.getTasksScheduled(),
      tasks_completed: this.getTasksCompleted(),
      tasks_failed: this.getTasksFailed(),
      average_execution_time: this.calculateAverageExecutionTime(),
      queue_depths: this.getQueueDepths(),
      resource_utilization: this.getResourceUtilization(),
      delegation_success_rate: this.getDelegationSuccessRate()
    };
  }
}
```

## Related Documentation

- [Agent Memory Systems](../agents/agent-memory-systems.md)
- [Kind Link Protocol Core](../protocols/kind-link-protocol-core.md)
- [Agent Behavior Modeling](../agents/agent-behavior-modeling.md)
- [Agent Trust Protocols](../security/agent-trust-protocols.md)

---

*This scheduling system provides the foundation for sophisticated task management, enabling agents to efficiently handle complex workflows, coordinate with other agents, and maintain reliable execution across the kOS ecosystem.* 