---
title: "Agent Deployment Scheduler"
description: "Core orchestration system for managing agent execution timelines and resources"
type: "service"
status: "future"
priority: "high"
last_updated: "2025-01-27"
related_docs: ["agent-lifecycle-management.md", "agent-result-dispatcher.md"]
implementation_status: "planned"
---

# Agent Deployment Scheduler

## Agent Context
Core orchestration system managing execution timelines, priorities, dependencies, and resource allocation for AI agents across connected devices with minimal latency and maximal parallelism.

## Scheduler Architecture

```typescript
interface AgentSchedule {
  id: string;
  agentId: string;
  type: ScheduleType;
  priority: Priority;
  trigger: ScheduleTrigger;
  resourceRequirements: ResourceRequirements;
  dependencies: string[];
  constraints: ScheduleConstraint[];
  lifecycle: ScheduleLifecycle;
  created: string;
  nextExecution?: string;
}

interface ScheduleTrigger {
  type: TriggerType;
  configuration: TriggerConfiguration;
  conditions?: TriggerCondition[];
}

interface ResourceRequirements {
  cpu: number; // cores
  memory: number; // MB
  gpu?: number; // count
  bandwidth?: number; // Mbps
  storage?: number; // MB
  battery?: number; // percentage threshold
}

type ScheduleType = 
  | 'on_demand'
  | 'recurring'
  | 'conditional'
  | 'cascading';

type Priority = 
  | 'critical'
  | 'high'
  | 'medium'
  | 'low'
  | 'background';

type TriggerType = 
  | 'manual'
  | 'cron'
  | 'event'
  | 'sensor'
  | 'api'
  | 'dependency';
```

## Deployment Scheduler Engine

```typescript
class AgentDeploymentScheduler {
  private schedules: Map<string, AgentSchedule>;
  private taskQueue: PriorityTaskQueue;
  private resourceManager: ResourceManager;
  private agentRegistry: AgentRegistry;
  private statusMonitor: AgentStatusMonitor;
  private lifecycleHooks: LifecycleHookManager;

  constructor(config: SchedulerConfig) {
    this.taskQueue = new PriorityTaskQueue(config.queueConfig);
    this.resourceManager = new ResourceManager(config.resourceConfig);
    this.agentRegistry = new AgentRegistry(config.registryConfig);
    this.statusMonitor = new AgentStatusMonitor(config.monitoringConfig);
    this.lifecycleHooks = new LifecycleHookManager(config.hooksConfig);
    this.schedules = new Map();
  }

  async scheduleAgent(
    agentId: string,
    scheduleConfig: ScheduleConfiguration
  ): Promise<AgentSchedule> {
    // Validate agent exists
    const agent = await this.agentRegistry.getAgent(agentId);
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }

    // Create schedule
    const schedule: AgentSchedule = {
      id: crypto.randomUUID(),
      agentId,
      type: scheduleConfig.type,
      priority: scheduleConfig.priority || 'medium',
      trigger: scheduleConfig.trigger,
      resourceRequirements: scheduleConfig.resources || agent.defaultResources,
      dependencies: scheduleConfig.dependencies || [],
      constraints: scheduleConfig.constraints || [],
      lifecycle: 'scheduled',
      created: new Date().toISOString()
    };

    // Validate resource requirements
    const resourceValidation = await this.resourceManager.validateRequirements(
      schedule.resourceRequirements
    );
    
    if (!resourceValidation.valid) {
      throw new Error(`Invalid resource requirements: ${resourceValidation.reason}`);
    }

    // Calculate next execution time
    if (schedule.type === 'recurring') {
      schedule.nextExecution = await this.calculateNextExecution(schedule.trigger);
    }

    // Store schedule
    this.schedules.set(schedule.id, schedule);
    
    // Add to task queue if immediate execution needed
    if (this.shouldExecuteImmediately(schedule)) {
      await this.queueForExecution(schedule);
    }

    return schedule;
  }

  async executeSchedule(scheduleId: string): Promise<ExecutionResult> {
    const schedule = this.schedules.get(scheduleId);
    if (!schedule) {
      throw new Error(`Schedule not found: ${scheduleId}`);
    }

    // Check dependencies
    const dependenciesReady = await this.checkDependencies(schedule.dependencies);
    if (!dependenciesReady.ready) {
      return {
        success: false,
        reason: 'Dependencies not ready',
        missingDependencies: dependenciesReady.missing
      };
    }

    // Check resource availability
    const resourcesAvailable = await this.resourceManager.checkAvailability(
      schedule.resourceRequirements
    );

    if (!resourcesAvailable.available) {
      // Check if we can preempt lower priority agents
      if (this.canPreempt(schedule.priority)) {
        await this.preemptLowerPriorityAgents(schedule.resourceRequirements);
      } else {
        return {
          success: false,
          reason: 'Insufficient resources',
          requiredResources: schedule.resourceRequirements,
          availableResources: resourcesAvailable.available
        };
      }
    }

    try {
      // Execute pre-start hooks
      await this.lifecycleHooks.executePreStartHooks(schedule);
      
      // Reserve resources
      const reservation = await this.resourceManager.reserveResources(
        schedule.resourceRequirements,
        schedule.id
      );

      // Start agent
      const execution = await this.startAgent(schedule, reservation);
      
      // Execute post-start hooks
      await this.lifecycleHooks.executePostStartHooks(schedule, execution);
      
      // Update schedule status
      schedule.lifecycle = 'running';
      
      // Start monitoring
      await this.statusMonitor.startMonitoring(execution.instanceId, schedule);

      return {
        success: true,
        instanceId: execution.instanceId,
        reservation: reservation.id,
        startedAt: execution.startedAt
      };

    } catch (error) {
      // Clean up resources on failure
      await this.cleanupFailedExecution(schedule, error);
      
      return {
        success: false,
        reason: error.message,
        error: error.stack
      };
    }
  }

  private async startAgent(
    schedule: AgentSchedule,
    reservation: ResourceReservation
  ): Promise<AgentExecution> {
    const agent = await this.agentRegistry.getAgent(schedule.agentId);
    const instanceId = crypto.randomUUID();

    const execution: AgentExecution = {
      instanceId,
      scheduleId: schedule.id,
      agentId: schedule.agentId,
      status: 'starting',
      startedAt: new Date().toISOString(),
      reservation,
      environment: await this.prepareEnvironment(agent, reservation)
    };

    // Start agent based on execution environment
    switch (agent.executionEnvironment) {
      case 'docker':
        await this.startDockerAgent(execution, agent);
        break;
      
      case 'subprocess':
        await this.startSubprocessAgent(execution, agent);
        break;
      
      case 'sandbox':
        await this.startSandboxedAgent(execution, agent);
        break;
      
      case 'systemd':
        await this.startSystemdAgent(execution, agent);
        break;
      
      default:
        throw new Error(`Unknown execution environment: ${agent.executionEnvironment}`);
    }

    execution.status = 'running';
    return execution;
  }

  private async startDockerAgent(
    execution: AgentExecution,
    agent: AgentDefinition
  ): Promise<void> {
    const containerConfig = {
      image: agent.dockerImage,
      name: `agent-${execution.instanceId}`,
      environment: execution.environment,
      resources: {
        memory: execution.reservation.memory * 1024 * 1024, // Convert MB to bytes
        cpus: execution.reservation.cpu,
        gpus: execution.reservation.gpu
      },
      networks: agent.networks || ['kai-agent-network'],
      volumes: agent.volumes || [],
      entrypoint: agent.entryPoint,
      command: agent.command
    };

    const container = await this.dockerClient.createContainer(containerConfig);
    await container.start();
    
    execution.containerId = container.id;
  }

  private async startSubprocessAgent(
    execution: AgentExecution,
    agent: AgentDefinition
  ): Promise<void> {
    const processConfig = {
      command: agent.command,
      args: agent.args || [],
      environment: execution.environment,
      workingDirectory: agent.workingDirectory,
      timeout: agent.timeout || 600000 // 10 minutes default
    };

    const process = spawn(processConfig.command, processConfig.args, {
      env: { ...process.env, ...processConfig.environment },
      cwd: processConfig.workingDirectory,
      stdio: ['pipe', 'pipe', 'pipe']
    });

    execution.processId = process.pid;
    
    // Set up process monitoring
    process.on('exit', (code) => {
      this.handleAgentExit(execution.instanceId, code);
    });

    process.on('error', (error) => {
      this.handleAgentError(execution.instanceId, error);
    });
  }

  async stopAgent(instanceId: string, reason: string = 'Manual stop'): Promise<void> {
    const execution = await this.getExecution(instanceId);
    if (!execution) {
      throw new Error(`Execution not found: ${instanceId}`);
    }

    const schedule = this.schedules.get(execution.scheduleId);
    if (!schedule) {
      throw new Error(`Schedule not found for execution: ${instanceId}`);
    }

    try {
      // Execute pre-shutdown hooks
      await this.lifecycleHooks.executePreShutdownHooks(schedule, execution);
      
      // Stop the agent based on execution environment
      await this.stopAgentInstance(execution);
      
      // Release resources
      await this.resourceManager.releaseReservation(execution.reservation.id);
      
      // Execute post-shutdown hooks
      await this.lifecycleHooks.executePostShutdownHooks(schedule, execution);
      
      // Update status
      execution.status = 'stopped';
      execution.stoppedAt = new Date().toISOString();
      execution.stopReason = reason;
      
      // Update schedule lifecycle
      schedule.lifecycle = 'completed';

    } catch (error) {
      console.error(`Error stopping agent ${instanceId}:`, error);
      execution.status = 'error';
      execution.error = error.message;
    }
  }

  private async preemptLowerPriorityAgents(
    requiredResources: ResourceRequirements
  ): Promise<void> {
    const runningExecutions = await this.getRunningExecutions();
    const candidates: AgentExecution[] = [];

    // Find preemption candidates
    for (const execution of runningExecutions) {
      const schedule = this.schedules.get(execution.scheduleId);
      if (schedule && this.canBePreempted(schedule.priority)) {
        candidates.push(execution);
      }
    }

    // Sort by priority (lowest first) and resource usage
    candidates.sort((a, b) => {
      const scheduleA = this.schedules.get(a.scheduleId)!;
      const scheduleB = this.schedules.get(b.scheduleId)!;
      
      const priorityDiff = this.getPriorityValue(scheduleA.priority) - 
                          this.getPriorityValue(scheduleB.priority);
      
      if (priorityDiff !== 0) return priorityDiff;
      
      // If same priority, preempt larger resource consumers first
      return b.reservation.totalScore - a.reservation.totalScore;
    });

    // Preempt agents until we have enough resources
    let freedResources = { cpu: 0, memory: 0, gpu: 0 };
    
    for (const candidate of candidates) {
      await this.stopAgent(candidate.instanceId, 'Preempted for higher priority task');
      
      freedResources.cpu += candidate.reservation.cpu;
      freedResources.memory += candidate.reservation.memory;
      freedResources.gpu += candidate.reservation.gpu || 0;
      
      // Check if we have enough resources now
      if (this.hasEnoughResources(freedResources, requiredResources)) {
        break;
      }
    }
  }
}
```

## Task Queue Management

```typescript
class PriorityTaskQueue {
  private queues: Map<Priority, TaskQueue>;
  private processing: boolean = false;
  private maxConcurrent: number;
  private currentExecutions: number = 0;

  constructor(config: QueueConfig) {
    this.maxConcurrent = config.maxConcurrent || 10;
    this.queues = new Map([
      ['critical', new TaskQueue()],
      ['high', new TaskQueue()],
      ['medium', new TaskQueue()],
      ['low', new TaskQueue()],
      ['background', new TaskQueue()]
    ]);
  }

  async enqueue(task: ScheduledTask): Promise<void> {
    const queue = this.queues.get(task.priority);
    if (!queue) {
      throw new Error(`Invalid priority: ${task.priority}`);
    }

    await queue.enqueue(task);
    
    if (!this.processing) {
      this.startProcessing();
    }
  }

  private async startProcessing(): Promise<void> {
    this.processing = true;
    
    while (this.hasTasksToProcess()) {
      if (this.currentExecutions >= this.maxConcurrent) {
        await this.waitForCapacity();
        continue;
      }

      const task = await this.getNextTask();
      if (task) {
        this.executeTask(task); // Fire and forget
      } else {
        await this.sleep(100); // Brief pause if no tasks
      }
    }
    
    this.processing = false;
  }

  private async getNextTask(): Promise<ScheduledTask | null> {
    // Process in priority order
    const priorities: Priority[] = ['critical', 'high', 'medium', 'low', 'background'];
    
    for (const priority of priorities) {
      const queue = this.queues.get(priority);
      if (queue && !queue.isEmpty()) {
        return await queue.dequeue();
      }
    }
    
    return null;
  }

  private async executeTask(task: ScheduledTask): Promise<void> {
    this.currentExecutions++;
    
    try {
      await this.scheduler.executeSchedule(task.scheduleId);
    } catch (error) {
      console.error(`Task execution failed:`, error);
    } finally {
      this.currentExecutions--;
    }
  }

  private hasTasksToProcess(): boolean {
    return Array.from(this.queues.values()).some(queue => !queue.isEmpty());
  }

  private async waitForCapacity(): Promise<void> {
    return new Promise(resolve => {
      const check = () => {
        if (this.currentExecutions < this.maxConcurrent) {
          resolve();
        } else {
          setTimeout(check, 100);
        }
      };
      check();
    });
  }
}
```

## Resource Management

```typescript
class ResourceManager {
  private reservations: Map<string, ResourceReservation>;
  private systemResources: SystemResources;
  private thresholds: ResourceThresholds;

  async checkAvailability(requirements: ResourceRequirements): Promise<AvailabilityCheck> {
    const current = await this.getCurrentUsage();
    const available = {
      cpu: this.systemResources.cpu - current.cpu,
      memory: this.systemResources.memory - current.memory,
      gpu: this.systemResources.gpu - current.gpu,
      bandwidth: this.systemResources.bandwidth - current.bandwidth
    };

    const sufficient = {
      cpu: available.cpu >= requirements.cpu,
      memory: available.memory >= requirements.memory,
      gpu: (requirements.gpu || 0) <= available.gpu,
      bandwidth: (requirements.bandwidth || 0) <= available.bandwidth
    };

    const allSufficient = Object.values(sufficient).every(Boolean);

    return {
      available: allSufficient,
      resources: available,
      sufficient,
      recommendations: allSufficient ? [] : this.generateRecommendations(requirements, available)
    };
  }

  async reserveResources(
    requirements: ResourceRequirements,
    scheduleId: string
  ): Promise<ResourceReservation> {
    const reservation: ResourceReservation = {
      id: crypto.randomUUID(),
      scheduleId,
      cpu: requirements.cpu,
      memory: requirements.memory,
      gpu: requirements.gpu || 0,
      bandwidth: requirements.bandwidth || 0,
      reserved: new Date().toISOString(),
      totalScore: this.calculateResourceScore(requirements)
    };

    this.reservations.set(reservation.id, reservation);
    return reservation;
  }

  async releaseReservation(reservationId: string): Promise<void> {
    const reservation = this.reservations.get(reservationId);
    if (reservation) {
      this.reservations.delete(reservationId);
      console.log(`Released reservation ${reservationId}`);
    }
  }

  private async getCurrentUsage(): Promise<ResourceUsage> {
    const totalReserved = Array.from(this.reservations.values()).reduce(
      (total, reservation) => ({
        cpu: total.cpu + reservation.cpu,
        memory: total.memory + reservation.memory,
        gpu: total.gpu + reservation.gpu,
        bandwidth: total.bandwidth + reservation.bandwidth
      }),
      { cpu: 0, memory: 0, gpu: 0, bandwidth: 0 }
    );

    return totalReserved;
  }

  private calculateResourceScore(requirements: ResourceRequirements): number {
    return (
      requirements.cpu * 10 +
      requirements.memory * 0.01 +
      (requirements.gpu || 0) * 100 +
      (requirements.bandwidth || 0) * 0.1
    );
  }
}
```
