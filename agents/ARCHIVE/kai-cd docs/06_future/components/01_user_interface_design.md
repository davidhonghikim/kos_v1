---
title: "User Interface Design and Theming System"
description: "Complete UI architecture, styling system, user theming logic, layout hierarchy, and reusable components for kAI system UI and kOS interfaces"
category: "components"
subcategory: "ui-design"
context: "future/kos-vision"
implementation_status: "planned"
decision_scope: "ui-system-wide"
complexity: "high"
last_updated: "2024-01-20"
code_references: [
  "src/layouts/",
  "src/components/",
  "src/styles/",
  "tailwind.config.js"
]
related_documents: [
  "current/components/01_ui-architecture.md",
  "current/components/02_ui-component-system.md",
  "future/architecture/03_kos-technology-stack.md"
]
dependencies: [
  "React 18+",
  "TypeScript",
  "Tailwind CSS",
  "ShadCN/UI",
  "Framer Motion"
]
breaking_changes: [
  "Complete UI system redesign",
  "New theming architecture",
  "Enhanced component library"
]
agent_notes: [
  "Defines complete UI architecture and theming system",
  "Contains detailed component specifications and layouts",
  "Critical reference for UI implementation consistency",
  "Includes accessibility and internationalization guidelines"
]
---

# User Interface Design and Theming System

> **Agent Context**: This document defines the complete UI architecture, styling system, theming logic, layout hierarchy, and reusable components for the kAI system UI and broader kOS interfaces. Use this when implementing UI components, designing user interfaces, or establishing visual consistency. All specifications support accessibility, internationalization, and responsive design.

## Quick Summary
Comprehensive UI design system defining React-based architecture with Tailwind CSS styling, advanced theming capabilities, modular component library, accessibility standards, and multi-target rendering for browser extensions, web applications, and mobile interfaces.

## UI System Overview

### Framework & Technology Stack
```typescript
interface UITechnologyStack {
  framework: 'React 18+ with TypeScript';
  styling: 'Tailwind CSS + ShadCN/UI components (customized)';
  animations: 'Framer Motion for transitions';
  icons: 'Heroicons + Lucide React';
  theming: 'Tailwind + React Context providers';
  mobile: 'NativeScript Bridge (future)';
  testing: 'React Testing Library + Storybook';
}
```

### Rendering Targets
```typescript
interface RenderingTargets {
  browserExtension: {
    tab: 'tab.html - Full-page browser extension panel';
    popup: 'popup.html - Extension popup view';
    sidepanel: 'sidepanel.html - Chrome side panel injection';
  };
  webApplication: {
    embedded: 'web.html - Embedded iframe for kOS services';
    standalone: 'Progressive Web App mode';
  };
  mobile: {
    pwa: 'Native-like PWA mode (Planned)';
    native: 'React Native wrapper (Future)';
  };
}
```

## Layout & Component Architecture

### Complete Component Tree
```typescript
interface ComponentHierarchy {
  AppRoot: {
    children: [
      'SidebarNav',      // Left dock with icons
      'MainContentPanel', // Primary content area
      'NotificationCenter', // Toast notifications
      'ThemeManager',     // Theme switching
      'ModalRoot'        // Modal dialogs
    ];
  };
  MainContentPanel: {
    children: [
      'Header',          // Breadcrumbs, active service
      'CapabilityUI',    // Dynamic renderer
      'FooterStatus'     // Memory, connection, context
    ];
  };
  CapabilityUI: {
    dynamic: 'capability/ComponentX'; // Renders based on active service
  };
}
```

### Layout Directory Structure
```text
src/layouts/
├── RootLayout.tsx
├── TabbedLayout.tsx
├── SidepanelLayout.tsx
├── EmbeddedLayout.tsx
└── MobileLayout.tsx
```

### Layout Implementation Example
```typescript
// src/layouts/RootLayout.tsx
import React from 'react';
import { SidebarNav } from '@/components/navigation/SidebarNav';
import { MainContentPanel } from '@/components/layout/MainContentPanel';
import { NotificationCenter } from '@/components/feedback/NotificationCenter';
import { ThemeManager } from '@/components/theming/ThemeManager';

interface RootLayoutProps {
  children: React.ReactNode;
}

export const RootLayout: React.FC<RootLayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-background text-foreground">
      <SidebarNav />
      <MainContentPanel>
        {children}
      </MainContentPanel>
      <NotificationCenter />
      <ThemeManager />
    </div>
  );
};
```

## Theming System

### Theme Token Architecture
```typescript
// tailwind.config.js theme configuration
interface ThemeTokens {
  colors: {
    primary: '#6366f1';      // Kind Blue
    secondary: '#f472b6';    // Friendly Pink
    accent: '#22d3ee';       // Sky Accent
    surface: '#1e1e2e';      // Surface color
    background: '#0f0f15';   // Midnight background
    border: '#3c3c3c';       // Border color
    muted: '#9ca3af';        // Muted text
    success: '#4ade80';      // Success green
    error: '#f87171';        // Error red
    warning: '#facc15';      // Warning yellow
  };
  fontFamily: {
    sans: ['Inter', 'ui-sans-serif'];
    mono: ['Fira Code', 'ui-monospace'];
  };
  spacing: {
    xs: '0.25rem';   // 4px
    sm: '0.5rem';    // 8px
    md: '1rem';      // 16px
    lg: '1.5rem';    // 24px
    xl: '2rem';      // 32px
    '2xl': '3rem';   // 48px
  };
}
```

### Dark/Light Mode Implementation
```typescript
// src/contexts/ThemeContext.tsx
interface ThemeContextType {
  theme: 'dark' | 'light' | 'system';
  setTheme: (theme: 'dark' | 'light' | 'system') => void;
  resolvedTheme: 'dark' | 'light';
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'dark' | 'light' | 'system'>('dark');
  const [resolvedTheme, setResolvedTheme] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const updateTheme = () => {
      if (theme === 'system') {
        setResolvedTheme(mediaQuery.matches ? 'dark' : 'light');
      } else {
        setResolvedTheme(theme);
      }
    };

    updateTheme();
    mediaQuery.addEventListener('change', updateTheme);
    return () => mediaQuery.removeEventListener('change', updateTheme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, resolvedTheme }}>
      <div className={resolvedTheme}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
};
```

### Custom Theme Support
```typescript
interface CustomTheme {
  id: string;
  name: string;
  colors: Record<string, string>;
  fonts: Record<string, string[]>;
  spacing: Record<string, string>;
  borderRadius: Record<string, string>;
}

// Theme Editor Component
export const ThemeEditor: React.FC = () => {
  const [customTheme, setCustomTheme] = useState<CustomTheme>();
  const [previewMode, setPreviewMode] = useState(false);

  const exportTheme = () => {
    const themeJson = JSON.stringify(customTheme, null, 2);
    const blob = new Blob([themeJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${customTheme?.name || 'custom'}-theme.json`;
    a.click();
  };

  return (
    <div className="theme-editor">
      {/* Theme editing interface */}
    </div>
  );
};
```

## Reusable UI Components

### Form Controls Library
```typescript
// src/components/forms/
interface FormControls {
  InputText: {
    props: ['value', 'onChange', 'placeholder', 'error', 'disabled'];
    variants: ['default', 'outlined', 'filled'];
  };
  InputSelect: {
    props: ['options', 'value', 'onChange', 'multiple', 'searchable'];
    features: ['keyboard navigation', 'async loading'];
  };
  InputSlider: {
    props: ['min', 'max', 'step', 'value', 'onChange'];
    features: ['dual handles', 'marks', 'tooltips'];
  };
  ToggleSwitch: {
    props: ['checked', 'onChange', 'disabled', 'size'];
    variants: ['default', 'small', 'large'];
  };
  FileUpload: {
    props: ['accept', 'multiple', 'maxSize', 'onUpload'];
    features: ['drag & drop', 'progress', 'preview'];
  };
}
```

### Layout Widgets
```typescript
// Component implementations
export const Card: React.FC<CardProps> = ({ children, className, ...props }) => {
  return (
    <div 
      className={cn(
        "rounded-2xl border border-border bg-surface p-6 shadow-lg",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const Accordion: React.FC<AccordionProps> = ({ items, ...props }) => {
  return (
    <div className="space-y-2">
      {items.map((item, index) => (
        <AccordionItem key={index} {...item} />
      ))}
    </div>
  );
};
```

### Navigation Elements
```typescript
interface NavigationComponents {
  SidebarNav: {
    features: ['collapsible', 'icon-based', 'tooltips'];
    items: ['services', 'agents', 'settings', 'vault'];
  };
  ServiceSelector: {
    features: ['search', 'categories', 'status indicators'];
    display: 'dropdown with service cards';
  };
  ModelDropdown: {
    features: ['model info', 'availability status', 'performance metrics'];
    grouping: 'by provider and capability';
  };
  BreadcrumbBar: {
    features: ['navigation history', 'context switching'];
    display: 'hierarchical path with actions';
  };
}
```

### Feedback & Status Components
```typescript
// Notification system
export const NotificationToast: React.FC<ToastProps> = ({ 
  type, 
  message, 
  duration = 5000,
  onClose 
}) => {
  const variants = {
    success: 'bg-success text-success-foreground',
    error: 'bg-error text-error-foreground',
    warning: 'bg-warning text-warning-foreground',
    info: 'bg-primary text-primary-foreground'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      className={cn(
        "rounded-lg p-4 shadow-lg",
        variants[type]
      )}
    >
      <div className="flex items-center gap-3">
        <StatusIcon type={type} />
        <span>{message}</span>
        <button onClick={onClose} className="ml-auto">
          <X size={16} />
        </button>
      </div>
    </motion.div>
  );
};
```

### Capability Components
```typescript
interface CapabilityComponents {
  LlmChatView: {
    features: ['message history', 'typing indicators', 'code highlighting'];
    layout: 'conversation thread with input area';
  };
  ImageGenerationView: {
    features: ['parameter controls', 'gallery view', 'progress tracking'];
    layout: 'sidebar controls with main canvas';
  };
  DataAnalysisView: {
    features: ['data preview', 'chart generation', 'export options'];
    layout: 'tabbed interface with visualization';
  };
  PromptWorkbench: {
    features: ['template editor', 'variable substitution', 'testing'];
    layout: 'split pane with editor and preview';
  };
}
```

## Accessibility & Internationalization

### Accessibility Implementation
```typescript
interface AccessibilityStandards {
  ariaLabels: 'All interactive elements properly labeled';
  keyboardNavigation: 'Full keyboard accessibility with focus management';
  colorContrast: 'WCAG AA compliance with high contrast mode';
  screenReader: 'Semantic HTML with proper ARIA attributes';
  focusManagement: 'Logical focus order and visible focus indicators';
}

// Example accessible component
export const AccessibleButton: React.FC<ButtonProps> = ({
  children,
  onClick,
  disabled,
  ariaLabel,
  ...props
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      className={cn(
        "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        "transition-colors duration-200"
      )}
      {...props}
    >
      {children}
    </button>
  );
};
```

### Internationalization System
```typescript
// i18n configuration
interface I18nConfig {
  defaultLanguage: 'en';
  supportedLanguages: ['en', 'es', 'de', 'zh', 'fr', 'ja'];
  fallbackLanguage: 'en';
  namespaces: ['common', 'components', 'errors', 'agents'];
}

// Usage example
export const LocalizedComponent: React.FC = () => {
  const { t } = useTranslation('components');
  
  return (
    <div>
      <h1>{t('welcome.title')}</h1>
      <p>{t('welcome.description')}</p>
    </div>
  );
};
```

## Visual Design Guidelines

### Typography System
```typescript
interface TypographySystem {
  headings: {
    font: 'Inter, semi-bold';
    scale: 'h1: 2.5rem, h2: 2rem, h3: 1.5rem, h4: 1.25rem';
    lineHeight: '1.2 for headings';
  };
  body: {
    font: 'Inter, regular';
    size: '14px base';
    lineHeight: '1.5';
  };
  code: {
    font: 'Fira Code';
    size: '13px';
    lineHeight: '1.4';
  };
}
```

### Spacing & Layout
```typescript
interface SpacingSystem {
  padding: {
    scale: ['p-2: 8px', 'p-4: 16px', 'p-6: 24px', 'p-8: 32px'];
    usage: 'consistent spacing across components';
  };
  margins: {
    scale: 'same as padding';
    usage: 'component separation';
  };
  gaps: {
    section: 'gap-6: 24px between major sections';
    component: 'gap-4: 16px between related components';
  };
}
```

### Visual Effects
```typescript
interface VisualEffects {
  borderRadius: {
    cards: 'rounded-2xl: 16px';
    buttons: 'rounded-lg: 8px';
    inputs: 'rounded-md: 6px';
  };
  shadows: {
    elevation: ['shadow-sm', 'shadow-lg', 'drop-shadow'];
    usage: 'layered interface depth';
  };
  animations: {
    transitions: 'ease-in-out, duration-200';
    presence: 'framer-motion for enter/exit';
  };
}
```

## Branding & Identity

### Brand Guidelines
```typescript
interface BrandIdentity {
  logo: {
    storage: 'assets/logos/';
    formats: ['SVG', 'PNG', 'WebP'];
    variants: ['full', 'icon', 'wordmark'];
  };
  palette: {
    kindBlue: '#6366f1';
    friendlyPink: '#f472b6';
    skyAccent: '#22d3ee';
    midnightBG: '#0f0f15';
  };
  voice: {
    tone: 'friendly, professional, helpful';
    personality: 'intelligent, approachable, trustworthy';
  };
}
```

## Future Development Roadmap

### Planned Features
```typescript
interface FutureFeatures {
  v1_2: {
    themeEditor: 'Live theming editor with JSON export/import';
    customComponents: 'User-defined component library';
  };
  v1_3: {
    voiceNavigation: 'Speech input for navigation and commands';
    gestureControls: 'Touch gestures for mobile interfaces';
  };
  v2_0: {
    adaptiveUI: 'AI-powered interface adaptation';
    contextualHelp: 'Intelligent help system';
  };
}
```

---

