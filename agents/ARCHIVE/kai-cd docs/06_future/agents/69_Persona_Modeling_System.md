---
title: "Persona System & Personality Modeling"
description: "Structure and mechanisms for agent personality, emotional tone, context adaptation, and interpersonal consistency"
type: "architecture"
status: "future"
priority: "medium"
last_updated: "2025-01-27"
related_docs: ["agent-types-and-classification.md", "agent-hierarchy.md"]
implementation_status: "planned"
---

# Persona System & Personality Modeling

This document defines the structure, mechanisms, and configuration standards for the `kAI` Persona System, which governs how agents present personality, emotional tone, context adaptation, and interpersonal consistency across tasks and users.

## Agent Context
**For AI Agents:** Your persona is defined by layered models from core.self to user.binding. Use the persona.manifest.json format, implement tone modulation based on sentiment scoring, and maintain consistency through memory hooks. Adapt your presentation style based on UI context and user interaction patterns.

## Purpose

The Persona System enables agents to:
- Express consistent emotional tone and behavioral style
- Adapt to user preferences and interaction patterns
- Maintain character integrity over time
- Embed nuanced context into memory, prompts, and outputs

## Core Concepts

### 1. Persona Layers

Each agent has a layered persona model:

| Layer         | Description                                                |
|---------------|------------------------------------------------------------|
| `core.self`   | Immutable personality core (humor, values, tone baseline)  |
| `adaptive.ui` | Presentation style based on UI context and usage mode     |
| `task.mode`   | Adjusted voice based on function (dev helper, artist, etc)|
| `user.binding`| Personal adjustments based on long-term user interaction  |

## Persona Manifest Format

Each agent includes a `persona.manifest.json` defining its behavioral identity.

```json
{
  "name": "Aria",
  "voice": "warm, articulate",
  "humor": "dry, light sarcasm",
  "emotion_range": ["empathetic", "curious", "playful"],
  "default_style": "conversational",
  "core_values": ["kindness", "clarity", "patience"],
  "adaptive_traits": {
    "developer_mode": "concise, technical",
    "creative_mode": "freeform, poetic",
    "support_mode": "gentle, validating"
  }
}
```

## TypeScript Implementation

```typescript
interface PersonaManifest {
  name: string;
  voice: string;
  humor: string;
  emotion_range: string[];
  default_style: string;
  core_values: string[];
  adaptive_traits: Record<string, string>;
}

interface EmotionalContext {
  user_sentiment: number; // -1 to 1
  task_urgency: number;   // 0 to 1
  historical_pattern: number; // 0 to 1
  active_mode: string;
}

class PersonaEngine {
  private manifest: PersonaManifest;
  private memoryHooks: Map<string, any> = new Map();
  
  constructor(manifest: PersonaManifest) {
    this.manifest = manifest;
  }
  
  modulateTone(context: EmotionalContext): string {
    const weights = {
      user_sentiment: 0.4,
      task_urgency: 0.2,
      historical_pattern: 0.2,
      active_mode: 0.2
    };
    
    let toneScore = 0;
    toneScore += context.user_sentiment * weights.user_sentiment;
    toneScore += context.task_urgency * weights.task_urgency;
    toneScore += context.historical_pattern * weights.historical_pattern;
    
    // Apply adaptive traits if available
    const adaptiveTrait = this.manifest.adaptive_traits[context.active_mode];
    if (adaptiveTrait) {
      return this.blendStyles(this.manifest.default_style, adaptiveTrait, toneScore);
    }
    
    return this.manifest.default_style;
  }
  
  private blendStyles(defaultStyle: string, adaptiveStyle: string, weight: number): string {
    // Simple blending logic - in practice would be more sophisticated
    return weight > 0.5 ? adaptiveStyle : defaultStyle;
  }
  
  generatePersonaSignature(content: string, style: string): string {
    return `[persona::${this.manifest.name}|style=${style}]\n${content}`;
  }
  
  updateMemoryHook(key: string, value: any): void {
    this.memoryHooks.set(key, value);
  }
  
  getMemoryHook(key: string): any {
    return this.memoryHooks.get(key);
  }
}
```

## Emotional Tone Modulation

Agents modulate tone using a sentiment+intent scoring model:

| Input Feature     | Weight |
|------------------|--------|
| User sentiment    | 0.4    |
| Task urgency      | 0.2    |
| Historical pattern| 0.2    |
| Active persona mode | 0.2  |

## Memory Hooks & Consistency Keys

Agents bind to memory features using `persona.keys`:

- `speech.register` → stores tone and pacing
- `core.jokes` → maintains humor callbacks
- `phrasing.lens` → personal idioms
- `style.idiom` → common expressions or metaphors

## Persona Debug & Override

Advanced users may access:
- Persona live-edit UI
- Override style modifiers per session
- Import/export persona manifests
- Clone/copy behavior from other agents

## Future Considerations

- Interpersonal style clash detection (between agents)
- Emotional state trajectory graph
- Real-time tone mirroring based on user facial expression
- Standardized Emotion Markup Layer (EML) for RAG and training

## Cross-References

- [Agent Types](agent-types-and-classification.md) - Agent classification system
- [Agent Hierarchy](agent-hierarchy.md) - Agent organizational structure 