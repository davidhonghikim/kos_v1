---
title: "Comfyui"
description: "Technical specification for comfyui"
type: "service"
status: "current"
priority: "medium"
last_updated: "2025-06-22"
agent_notes: "AI agent guidance for implementing comfyui"
---

# ComfyUI Service Documentation

This document provides a detailed overview of the integration between Kai-CD and ComfyUI. Unlike other services with simple REST endpoints, ComfyUI operates on a graph-based system, which requires a more sophisticated integration.

-   **GitHub Repository:** [https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)
-   **Official API Documentation:** [ComfyUI API Examples](https://github.com/comfyanonymous/ComfyUI_API_Examples)

## Core Concept: Graph Execution

The fundamental difference in ComfyUI is that there is no endpoint for `/txt2img` or `/img2img`. Instead, there is a single, primary endpoint: `/prompt`. This endpoint accepts a complete workflow graph, formatted as JSON, which describes the nodes, their parameters, and the connections between them.

To generate an image, Kai-CD does not simply send parameters; it sends this entire graph object to the ComfyUI backend.

## The `GraphExecutionCapability`

To handle this, the ComfyUI service definition in Kai-CD uses the `GraphExecutionCapability`. This capability has two main components:

1.  **`baseWorkflow`**: A complete, default text-to-image workflow graph that is stored directly within the service definition file.
2.  **`parameterMapping`**: A special object that tells the Kai-CD `apiClient` how to inject the user's parameters from the UI into the `baseWorkflow` JSON before sending it to the ComfyUI server.

### Example: `parameterMapping`

Here is a snippet from the `parameterMapping` in `comfyui.ts`:

```typescript
parameterMapping: {
  prompt: {
    nodeId: "6", 
    inputKey: "text",
    parameterDefinition: { key: 'prompt', ... }
  },
  sd_model_checkpoint: {
    nodeId: "4", 
    inputKey: "ckpt_name",
    parameterDefinition: { key: 'sd_model_checkpoint', ... }
  },
  steps: {
    nodeId: "3", 
    inputKey: "steps",
    parameterDefinition: { key: 'steps', ... }
  },
}
```

This mapping means:
-   Take the value of the `prompt` parameter from the UI and inject it into the `inputs.text` field of the node with ID `6`.
-   Take the value of the `sd_model_checkpoint` parameter and inject it into the `inputs.ckpt_name` field of the node with ID `4`.
-   Take the value of the `steps` parameter and inject it into the `inputs.steps` field of the node with ID `3`.

This declarative mapping allows Kai-CD to manipulate the workflow graph dynamically based on user input.

## Real-time Progress via Websockets

ComfyUI reports all progress—such as loading models, sampling steps, and completion—through a websocket connection, not standard HTTP responses.

-   **Endpoint:** The service definition correctly identifies the `/ws` endpoint for this purpose.
-   **Future Enhancement:** For the user to see real-time progress, the `apiClient` in Kai-CD must be enhanced to establish a websocket connection after submitting a prompt. It will need to listen for progress messages and update the UI accordingly. This is a critical future improvement for a good user experience.

## Dynamic Asset Discovery

The definition uses the `/object_info/{NodeClassName}` endpoint to discover available assets.
-   **Models:** Discovered from the `CheckpointLoaderSimple` node.
-   **Samplers:** Discovered from the `KSampler` node.
-   **VAEs:** Discovered from the `VAELoader` node.

## Future Enhancements

The current implementation provides a functional text-to-image pipeline. Future work will focus on:
1.  **Websocket Client:** Implementing the client-side logic to handle real-time progress updates.
2.  **Workflow Management:** Creating a UI that allows users to import, manage, and select different workflow files (`.json`) instead of only using the hardcoded `baseWorkflow`. This would unlock the full power of ComfyUI.
3.  **Dynamic Node Discovery:** Building a system that can parse the full `/object_info` endpoint to discover all nodes available in a user's ComfyUI instance, allowing Kai-CD to adapt to custom nodes and complex workflows automatically. 

# ComfyUI Advanced Node-Based Workflow Integration

## Overview

ComfyUI is the most advanced and flexible interface for Stable Diffusion, utilizing a node-based workflow system that allows for unprecedented control over the generation process. Our integration transforms ComfyUI's powerful but complex interface into an intuitive, modern experience while preserving its full capabilities.

## Current Integration Status

### ✅ **Working Features**
- **Authentication**: None required (as designed)
- **Health Checking**: Automatic service status monitoring with GPU detection
- **Model Detection**: Dynamic loading via `/object_info` endpoint
- **Basic Connectivity**: API communication established
- **System Information**: GPU detection (GTX 1070 confirmed)

### 🔧 **Current Limitations**
- **No Workflow Management**: Missing node-based workflow system
- **No Queue Management**: No integration with ComfyUI's queue system
- **Limited Parameter Control**: Basic parameters only, no node customization
- **No State Persistence**: No synchronization with ComfyUI web interface
- **Missing Node Ecosystem**: No access to ComfyUI's extensive node library

### 🚀 **Advanced Integration Roadmap**

#### **Phase 1: Workflow Foundation (Next 3 Weeks)**

##### **Core Workflow System**
```typescript
// ComfyUI Workflow Architecture
interface ComfyUIWorkflow {
  // Workflow Definition
  id: string;
  name: string;
  description: string;
  version: string;
  
  // Node Graph
  nodes: {
    [nodeId: string]: {
      class_type: string;
      inputs: { [key: string]: any };
      outputs?: string[];
      position?: { x: number; y: number };
    };
  };
  
  // Metadata
  metadata: {
    created: timestamp;
    modified: timestamp;
    author: string;
    tags: string[];
    category: WorkflowCategory;
  };
  
  // Execution State
  executionState: {
    status: 'idle' | 'running' | 'completed' | 'error';
    progress: number;
    currentNode: string;
    queuePosition: number;
  };
}

// Workflow Template System
interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: 'text2img' | 'img2img' | 'controlnet' | 'animation' | 'upscaling' | 'custom';
  
  // Template Structure
  baseWorkflow: ComfyUIWorkflow;
  exposedParameters: ExposedParameter[];
  previewImage: string;
  
  // Usage Information
  requirements: {
    models: string[];
    customNodes: string[];
    memoryMB: number;
    vramMB: number;
  };
  
  // Compatibility
  comfyuiVersion: string;
  lastTested: timestamp;
}
```

##### **Intelligent Workflow Builder**
```typescript
class ComfyUIWorkflowBuilder {
  // Template-Based Generation
  async createFromTemplate(template: WorkflowTemplate, parameters: any): Promise<ComfyUIWorkflow> {
    const workflow = JSON.parse(JSON.stringify(template.baseWorkflow));
    
    // Apply parameters to exposed inputs
    for (const param of template.exposedParameters) {
      this.setNodeInput(workflow, param.nodeId, param.inputName, parameters[param.key]);
    }
    
    // Validate workflow integrity
    await this.validateWorkflow(workflow);
    
    return workflow;
  }
  
  // Dynamic Node Management
  async getAvailableNodes(): Promise<NodeDefinition[]> {
    const objectInfo = await this.apiClient.get('/object_info');
    return Object.entries(objectInfo).map(([className, definition]) => ({
      className,
      category: definition.category,
      inputs: definition.input,
      outputs: definition.output,
      description: definition.description
    }));
  }
  
  // Workflow Optimization
  async optimizeWorkflow(workflow: ComfyUIWorkflow): Promise<OptimizedWorkflow> {
    return {
      ...workflow,
      optimizations: {
        memoryUsage: this.calculateMemoryUsage(workflow),
        executionTime: this.estimateExecutionTime(workflow),
        suggestions: this.generateOptimizationSuggestions(workflow)
      }
    };
  }
  
  // A1111 Compatibility
  async convertFromA1111(a1111Params: A1111Parameters): Promise<ComfyUIWorkflow> {
    // Convert A1111 parameters to ComfyUI workflow
    const workflow = this.createBaseTextToImageWorkflow();
    
    // Map parameters
    this.setNodeInput(workflow, 'prompt_positive', 'text', a1111Params.prompt);
    this.setNodeInput(workflow, 'prompt_negative', 'text', a1111Params.negative_prompt);
    this.setNodeInput(workflow, 'sampler', 'sampler_name', a1111Params.sampler_name);
    this.setNodeInput(workflow, 'sampler', 'steps', a1111Params.steps);
    this.setNodeInput(workflow, 'sampler', 'cfg', a1111Params.cfg_scale);
    
    return workflow;
  }
}
```

#### **Phase 2: Advanced Node Ecosystem (Next Month)**

##### **Node Library Management**
```typescript
interface ComfyUINodeEcosystem {
  // Core Node Categories
  sampling: {
    samplers: SamplerNode[];
    schedulers: SchedulerNode[];
    conditioning: ConditioningNode[];
  };
  
  models: {
    checkpoints: CheckpointLoaderNode[];
    loras: LoRALoaderNode[];
    vaes: VAELoaderNode[];
    embeddings: EmbeddingNode[];
  };
  
  controlnet: {
    processors: ControlNetProcessorNode[];
    models: ControlNetModelNode[];
    applications: ControlNetApplyNode[];
  };
  
  // Advanced Features
  animation: {
    animateDiff: AnimateDiffNode[];
    videoHelpers: VideoHelperNode[];
    frameInterpolation: FrameInterpolationNode[];
  };
  
  upscaling: {
    esrgan: ESRGANNode[];
    realESRGAN: RealESRGANNode[];
    swinIR: SwinIRNode[];
  };
  
  // Custom Node Management
  customNodes: {
    installed: CustomNodePackage[];
    available: CustomNodePackage[];
    updates: CustomNodeUpdate[];
  };
}

// Custom Node Package Manager
class ComfyUINodeManager {
  async installNodePackage(packageId: string): Promise<InstallResult> {
    // Download and install custom node package
    const result = await this.apiClient.post('/install_custom_nodes', {
      package_id: packageId
    });
    
    // Update node registry
    await this.refreshNodeRegistry();
    
    return result;
  }
  
  async updateNodes(): Promise<UpdateResult[]> {
    const updates = await this.checkForUpdates();
    const results = [];
    
    for (const update of updates) {
      results.push(await this.updateNodePackage(update.packageId));
    }
    
    return results;
  }
  
  async validateNodeCompatibility(workflow: ComfyUIWorkflow): Promise<ValidationResult> {
    const requiredNodes = this.extractRequiredNodes(workflow);
    const missingNodes = [];
    const incompatibleNodes = [];
    
    for (const nodeClass of requiredNodes) {
      if (!this.isNodeInstalled(nodeClass)) {
        missingNodes.push(nodeClass);
      } else if (!this.isNodeCompatible(nodeClass)) {
        incompatibleNodes.push(nodeClass);
      }
    }
    
    return {
      valid: missingNodes.length === 0 && incompatibleNodes.length === 0,
      missingNodes,
      incompatibleNodes,
      suggestions: this.generateInstallSuggestions(missingNodes)
    };
  }
}
```

##### **Advanced Workflow UI - 4-Panel Layout**
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│   Node Library  │  Workflow Graph │   Properties    │  Queue & Output │
│                 │                 │                 │                 │
│ ┌─ Categories ─┐ │ ┌─────────────┐ │ ┌─ Selected ──┐ │ ┌─ Queue ─────┐ │
│ │ • Sampling   │ │ │   Visual    │ │ │ Node Props  │ │ │ Position: 3 │ │
│ │ • Models     │ │ │   Workflow  │ │ │ Parameters  │ │ │ ETA: 2m 30s │ │
│ │ • ControlNet │ │ │   Editor    │ │ │ Connections │ │ │ Progress    │ │
│ │ • Animation  │ │ │             │ │ └─────────────┘ │ │ ████████░░  │ │
│ │ • Upscaling  │ │ │   [Nodes]   │ │                 │ └─────────────┘ │
│ │ • Custom     │ │ │   [Links]   │ │ ┌─ Templates ──┐ │                 │
│ └─────────────┘ │ │   [Canvas]  │ │ │ Basic T2I    │ │ ┌─ Results ───┐ │
│                 │ └─────────────┘ │ │ ControlNet   │ │ │ Generated   │ │
│ ┌─ Templates ──┐ │                 │ │ Animation    │ │ │ Images      │ │
│ │ Text2Image   │ │ ┌─ Controls ──┐ │ │ Upscaling    │ │ │ Workflows   │ │
│ │ Img2Img      │ │ │ Queue        │ │ │ Custom       │ │ │ History     │ │
│ │ ControlNet   │ │ │ Interrupt    │ │ └─────────────┘ │ │ Metadata    │ │
│ │ Animation    │ │ │ Clear        │ │                 │ └─────────────┘ │
│ │ Batch        │ │ │ Save/Load    │ │ ┌─ Validation ─┐ │                 │
│ └─────────────┘ │ └─────────────┘ │ │ Node Status  │ │ ┌─ System ────┐ │
│                 │                 │ │ Dependencies │ │ │ GPU: GTX1070│ │
│ ┌─ Search ─────┐ │ ┌─ Minimap ───┐ │ │ Errors       │ │ │ VRAM: 8GB   │ │
│ │ Find Nodes   │ │ │ Overview    │ │ │ Warnings     │ │ │ Queue: 3    │ │
│ │ Filter       │ │ │ Navigation  │ │ └─────────────┘ │ │ Active: Yes │ │
│ └─────────────┘ │ └─────────────┘ │                 │ └─────────────┘ │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

#### **Phase 3: Professional Workflow Management (Next Quarter)**

##### **Batch Processing & Queue Management**
```typescript
interface ComfyUIBatchSystem {
  // Batch Job Management
  createBatch(baseWorkflow: ComfyUIWorkflow, variations: WorkflowVariation[]): BatchJob;
  queueBatch(batch: BatchJob, priority?: number): Promise<BatchQueueResult>;
  monitorBatch(batchId: string): Observable<BatchProgress>;
  
  // Queue Control
  getQueueStatus(): Promise<QueueStatus>;
  pauseQueue(): Promise<void>;
  resumeQueue(): Promise<void>;
  clearQueue(): Promise<void>;
  reorderQueue(queueIds: string[]): Promise<void>;
  
  // Resource Management
  estimateResourceUsage(workflow: ComfyUIWorkflow): ResourceEstimate;
  optimizeQueueOrder(queueItems: QueueItem[]): QueueItem[];
  monitorSystemResources(): Observable<SystemResources>;
}

// Advanced Workflow Templates
interface AdvancedWorkflowTemplates {
  // Animation Workflows
  animateDiffBasic: WorkflowTemplate;
  animateDiffAdvanced: WorkflowTemplate;
  videoToVideo: WorkflowTemplate;
  frameInterpolation: WorkflowTemplate;
  
  // Professional Workflows
  commercialPortrait: WorkflowTemplate;
  productPhotography: WorkflowTemplate;
  architecturalVisualization: WorkflowTemplate;
  conceptArt: WorkflowTemplate;
  
  // Technical Workflows
  multiModelEnsemble: WorkflowTemplate;
  styleTransfer: WorkflowTemplate;
  inpaintingAdvanced: WorkflowTemplate;
  upscalingPipeline: WorkflowTemplate;
}
```

##### **State Synchronization Architecture**
```typescript
class ComfyUIStateSyncManager {
  // Extract state from ComfyUI web interface
  async extractServerUIState(): Promise<ComfyUIServerState> {
    const iframe = document.querySelector('#comfyui-iframe');
    const comfyApp = iframe.contentWindow.app;
    
    return {
      currentWorkflow: comfyApp.graph.serialize(),
      queueStatus: await this.getQueueFromServer(),
      nodeStates: this.extractNodeStates(comfyApp),
      canvasState: {
        position: comfyApp.canvas.ds.offset,
        zoom: comfyApp.canvas.ds.scale,
        selectedNodes: comfyApp.canvas.selected_nodes
      },
      executionHistory: await this.getExecutionHistory()
    };
  }
  
  // Inject our workflow into ComfyUI web interface
  async injectWorkflowToServerUI(workflow: ComfyUIWorkflow): Promise<void> {
    const iframe = document.querySelector('#comfyui-iframe');
    const comfyApp = iframe.contentWindow.app;
    
    // Clear current workflow
    comfyApp.graph.clear();
    
    // Load our workflow
    comfyApp.loadGraphData(workflow);
    
    // Update UI state
    comfyApp.graph.setDirtyCanvas(true, true);
  }
  
  // Real-time synchronization
  setupBidirectionalSync(): void {
    // Listen for changes in ComfyUI web interface
    const iframe = document.querySelector('#comfyui-iframe');
    const comfyApp = iframe.contentWindow.app;
    
    // Monitor workflow changes
    comfyApp.graph.onAfterChange = (change) => {
      this.handleServerUIChange(change);
    };
    
    // Monitor queue changes
    this.pollQueueStatus();
    
    // Monitor execution progress
    this.monitorExecution();
  }
}
```

## Advanced Integration Features

### **Workflow Template Library**
```typescript
// Built-in Workflow Templates
const comfyUITemplates = {
  // Basic Templates
  textToImage: {
    name: "Text to Image",
    description: "Basic text-to-image generation",
    nodes: {
      "1": { class_type: "CheckpointLoaderSimple", inputs: {} },
      "2": { class_type: "CLIPTextEncode", inputs: { text: "{{prompt}}", clip: ["1", 1] } },
      "3": { class_type: "CLIPTextEncode", inputs: { text: "{{negative_prompt}}", clip: ["1", 1] } },
      "4": { class_type: "KSampler", inputs: { 
        seed: "{{seed}}", steps: "{{steps}}", cfg: "{{cfg_scale}}",
        sampler_name: "{{sampler}}", scheduler: "{{scheduler}}",
        model: ["1", 0], positive: ["2", 0], negative: ["3", 0]
      }},
      "5": { class_type: "VAEDecode", inputs: { samples: ["4", 0], vae: ["1", 2] } },
      "6": { class_type: "SaveImage", inputs: { images: ["5", 0] } }
    },
    exposedParameters: [
      { key: "prompt", nodeId: "2", inputName: "text", type: "string" },
      { key: "negative_prompt", nodeId: "3", inputName: "text", type: "string" },
      { key: "steps", nodeId: "4", inputName: "steps", type: "number" },
      { key: "cfg_scale", nodeId: "4", inputName: "cfg", type: "number" }
    ]
  },
  
  // Advanced Templates
  controlNetWorkflow: {
    name: "ControlNet Workflow",
    description: "Advanced ControlNet-based generation",
    category: "controlnet",
    // ... complex node structure
  },
  
  animateDiffWorkflow: {
    name: "AnimateDiff Animation",
    description: "Video generation with AnimateDiff",
    category: "animation",
    // ... animation node structure
  }
};
```

### **API Integration Points**

#### **Core ComfyUI Endpoints**
```typescript
const comfyUIEndpoints = {
  // Workflow Management
  prompt: '/prompt',          // Execute workflow
  queue: '/queue',           // Queue management
  history: '/history',       // Execution history
  interrupt: '/interrupt',   // Stop execution
  
  // System Information
  object_info: '/object_info',     // Available nodes
  embeddings: '/embeddings',       // Available embeddings
  extensions: '/extensions',       // Installed extensions
  system_stats: '/system_stats',   // System resources
  
  // File Management
  upload_image: '/upload/image',   // Upload images
  view_metadata: '/view_metadata', // Image metadata
  
  // Model Management
  checkpoints: '/checkpoints',     // Available checkpoints
  loras: '/loras',                // Available LoRAs
  vae: '/vae',                    // Available VAE models
  
  // Custom Nodes
  custom_nodes: '/custom_nodes',   // Installed custom nodes
  install_nodes: '/install_nodes', // Install new nodes
  update_nodes: '/update_nodes'    // Update existing nodes
};
```

### **Performance Optimization**

#### **Memory Management**
```typescript
class ComfyUIResourceManager {
  // Memory optimization
  async optimizeMemoryUsage(workflow: ComfyUIWorkflow): Promise<OptimizedWorkflow> {
    const analysis = this.analyzeMemoryUsage(workflow);
    
    if (analysis.peakMemory > this.getAvailableVRAM()) {
      return this.applyMemoryOptimizations(workflow, analysis);
    }
    
    return workflow;
  }
  
  // Model loading optimization
  async preloadModels(workflow: ComfyUIWorkflow): Promise<void> {
    const requiredModels = this.extractRequiredModels(workflow);
    
    for (const model of requiredModels) {
      if (!this.isModelLoaded(model)) {
        await this.loadModel(model);
      }
    }
  }
  
  // Queue optimization
  optimizeQueueOrder(queueItems: QueueItem[]): QueueItem[] {
    // Group by similar models to reduce loading overhead
    return queueItems.sort((a, b) => {
      const aModels = this.extractRequiredModels(a.workflow);
      const bModels = this.extractRequiredModels(b.workflow);
      
      return this.calculateModelSimilarity(aModels, bModels);
    });
  }
}
```

## Testing & Validation

### **Workflow Validation**
- Node compatibility checking
- Input/output type validation
- Dependency resolution
- Resource requirement verification

### **Performance Benchmarks**
- Workflow execution time analysis
- Memory usage profiling
- Queue throughput measurement
- UI responsiveness testing

### **Integration Tests**
- State synchronization accuracy
- Template instantiation correctness
- Batch processing reliability
- Error handling robustness

## Troubleshooting

### **Common Issues**
1. **Workflow execution failures**: Check node compatibility and required models
2. **Memory errors**: Optimize workflow or reduce batch size
3. **State sync issues**: Verify iframe access and ComfyUI API availability
4. **Custom node problems**: Check installation and compatibility

### **Debug Tools**
- Workflow execution tracer
- Node dependency analyzer
- Memory usage monitor
- State synchronization debugger

---

**Status**: 🚧 Planning Phase  
**Priority**: High  
**Next Milestone**: Phase 1 - Workflow Foundation (3 weeks)  
**Integration Level**: Advanced Architecture (25% complete)  
