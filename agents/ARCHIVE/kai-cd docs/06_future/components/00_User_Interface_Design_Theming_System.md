---
title: "User Interface Design and Theming System (kAI / kOS)"
description: "Complete UI architecture, styling system, user theming logic, layout hierarchy, and reusable components for the kAI system UI and broader kOS interfaces"
type: "architecture"
status: "future"
priority: "high"
last_updated: "2024-12-28"
related_docs: [
  "documentation/current/components/01_ui-architecture.md",
  "documentation/current/components/02_ui-component-system.md",
  "documentation/future/components/user-interface-design.md"
]
implementation_status: "planned"
---

# User Interface Design and Theming System (kAI / kOS)

## Agent Context
**For AI Agents**: This document defines the complete UI architecture for both kAI and kOS systems. When implementing UI components, follow the React + TypeScript + Tailwind CSS framework specified here. Use the provided component hierarchy and theming system. All UI components must support accessibility features and the theming engine. Pay special attention to the rendering targets and responsive design requirements.

## UI System Overview

### Framework & Tooling Stack

```typescript
interface UITechStack {
  framework: 'React 18+';
  language: 'TypeScript';
  styling: 'Tailwind CSS';
  components: 'ShadCN/UI (customized)';
  animation: 'Framer Motion';
  icons: 'Heroicons & Lucide';
  themes: 'Tailwind + Context Providers';
  mobile: 'NativeScript Bridge (future)';
}

// Core dependencies
const coreDependencies = {
  "react": "^18.2.0",
  "typescript": "^5.0.0",
  "tailwindcss": "^3.3.0",
  "@headlessui/react": "^1.7.0",
  "framer-motion": "^10.0.0",
  "@heroicons/react": "^2.0.0",
  "lucide-react": "^0.263.0",
  "i18next": "^23.0.0",
  "react-i18next": "^13.0.0"
};
```

### Rendering Targets

```typescript
type RenderingTarget = 
  | 'tab.html'          // Full-page browser extension panel
  | 'popup.html'        // Extension popup view
  | 'sidepanel.html'    // Chrome side panel injection
  | 'web.html'          // Embedded iframe (for kOS services)
  | 'mobile'            // Native-like PWA mode (planned)
  | 'desktop';          // Electron wrapper (future)

interface RenderingConfig {
  target: RenderingTarget;
  dimensions: {
    width: number | 'auto';
    height: number | 'auto';
  };
  features: {
    fullscreen: boolean;
    resizable: boolean;
    modal: boolean;
  };
  layout: 'single-panel' | 'multi-panel' | 'sidebar' | 'overlay';
}

const renderingConfigs: Record<RenderingTarget, RenderingConfig> = {
  'tab.html': {
    target: 'tab.html',
    dimensions: { width: 'auto', height: 'auto' },
    features: { fullscreen: true, resizable: true, modal: false },
    layout: 'multi-panel'
  },
  'popup.html': {
    target: 'popup.html',
    dimensions: { width: 400, height: 600 },
    features: { fullscreen: false, resizable: false, modal: true },
    layout: 'single-panel'
  },
  'sidepanel.html': {
    target: 'sidepanel.html',
    dimensions: { width: 320, height: 'auto' },
    features: { fullscreen: false, resizable: true, modal: false },
    layout: 'sidebar'
  }
};
```

## Layout & Component Tree

### Application Architecture

```typescript
interface AppArchitecture {
  root: 'AppRoot';
  navigation: 'SidebarNav';
  main: 'MainContentPanel';
  overlay: 'NotificationCenter | ThemeManager | ModalRoot';
}

// Component hierarchy
const componentTree = `
AppRoot
├── SidebarNav (Left dock, icons)
├── MainContentPanel
│   ├── Header (breadcrumbs, active service)
│   ├── CapabilityUI (dynamic renderer)
│   │   └── capability/ComponentX
│   └── FooterStatus (memory, connection, context)
├── NotificationCenter
├── ThemeManager
└── ModalRoot
`;
```

### Layout Components

```typescript
// Layout directory structure
interface LayoutStructure {
  'src/layouts/RootLayout.tsx': 'Base application wrapper';
  'src/layouts/TabbedLayout.tsx': 'Multi-tab interface';
  'src/layouts/SidepanelLayout.tsx': 'Side panel specific layout';
  'src/layouts/ResponsiveLayout.tsx': 'Adaptive layout system';
}

// Root Layout Component
interface RootLayoutProps {
  children: React.ReactNode;
  target: RenderingTarget;
  theme: ThemeConfig;
  accessibility: AccessibilityConfig;
}

class RootLayout extends React.Component<RootLayoutProps> {
  render() {
    return (
      <div className={`app-root ${this.props.target}`}>
        <ThemeProvider theme={this.props.theme}>
          <AccessibilityProvider config={this.props.accessibility}>
            <SidebarNav />
            <MainContentPanel>
              {this.props.children}
            </MainContentPanel>
            <NotificationCenter />
            <ModalRoot />
          </AccessibilityProvider>
        </ThemeProvider>
      </div>
    );
  }
}
```

## Theming System

### Theme Token Architecture

```typescript
interface ThemeTokens {
  colors: ColorPalette;
  typography: TypographyScale;
  spacing: SpacingScale;
  borderRadius: BorderRadiusScale;
  shadows: ShadowScale;
  animation: AnimationConfig;
}

interface ColorPalette {
  // Primary brand colors
  primary: string;        // '#6366f1' - Kind Blue
  secondary: string;      // '#f472b6' - Friendly Pink
  accent: string;         // '#22d3ee' - Sky Accent
  
  // Background colors
  background: string;     // '#0f0f15' - Midnight BG
  surface: string;        // '#1e1e2e' - Surface
  
  // UI colors
  border: string;         // '#3c3c3c'
  muted: string;          // '#9ca3af'
  
  // Status colors
  success: string;        // '#4ade80'
  error: string;          // '#f87171'
  warning: string;        // '#facc15'
  info: string;           // '#3b82f6'
}

interface TypographyScale {
  fontFamily: {
    sans: string[];       // ['Inter', 'ui-sans-serif']
    mono: string[];       // ['Fira Code', 'ui-monospace']
    display: string[];    // ['Inter', 'ui-sans-serif']
  };
  fontSize: {
    xs: string;           // '0.75rem'
    sm: string;           // '0.875rem'
    base: string;         // '1rem' (14px base)
    lg: string;           // '1.125rem'
    xl: string;           // '1.25rem'
    '2xl': string;        // '1.5rem'
    '3xl': string;        // '1.875rem'
  };
  fontWeight: {
    normal: number;       // 400
    medium: number;       // 500
    semibold: number;     // 600
    bold: number;         // 700
  };
  lineHeight: {
    tight: number;        // 1.25
    normal: number;       // 1.5
    relaxed: number;      // 1.75
  };
}
```

### Tailwind Configuration

```typescript
// tailwind.config.js implementation
const tailwindConfig = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './public/*.html'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#6366f1',
          600: '#5b21b6',
          900: '#312e81'
        },
        secondary: {
          50: '#fdf2f8',
          100: '#fce7f3',
          500: '#f472b6',
          600: '#ec4899',
          900: '#831843'
        },
        accent: {
          50: '#ecfeff',
          100: '#cffafe',
          500: '#22d3ee',
          600: '#0891b2',
          900: '#164e63'
        },
        surface: {
          50: '#f8fafc',
          100: '#f1f5f9',
          500: '#1e1e2e',
          600: '#1a1a28',
          900: '#0f0f15'
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['Fira Code', 'ui-monospace', 'monospace']
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }]
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem'
      },
      borderRadius: {
        '4xl': '2rem'
      },
      boxShadow: {
        'glow': '0 0 20px rgba(99, 102, 241, 0.3)',
        'inner-glow': 'inset 0 0 20px rgba(99, 102, 241, 0.1)'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio')
  ]
};
```

### Dark / Light Mode System

```typescript
interface ThemeMode {
  mode: 'light' | 'dark' | 'auto';
  systemPreference: boolean;
  customThemes: CustomTheme[];
}

interface CustomTheme {
  id: string;
  name: string;
  colors: Partial<ColorPalette>;
  preview: string;        // Base64 preview image
}

class ThemeManager {
  private currentMode: ThemeMode['mode'] = 'dark';
  private customThemes: Map<string, CustomTheme> = new Map();
  
  async setTheme(mode: ThemeMode['mode']): Promise<void> {
    this.currentMode = mode;
    
    if (mode === 'auto') {
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.applyTheme(systemPrefersDark ? 'dark' : 'light');
    } else {
      this.applyTheme(mode);
    }
    
    // Persist to localStorage
    localStorage.setItem('kai-theme-mode', mode);
  }
  
  private applyTheme(mode: 'light' | 'dark'): void {
    const root = document.documentElement;
    
    if (mode === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    // Emit theme change event
    window.dispatchEvent(new CustomEvent('theme-changed', { 
      detail: { mode } 
    }));
  }
  
  async loadCustomTheme(themeId: string): Promise<void> {
    const theme = this.customThemes.get(themeId);
    if (!theme) {
      throw new Error(`Theme ${themeId} not found`);
    }
    
    // Apply custom CSS variables
    const root = document.documentElement;
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
  }
  
  async createCustomTheme(theme: Omit<CustomTheme, 'id'>): Promise<string> {
    const id = `custom-${Date.now()}`;
    const customTheme: CustomTheme = { ...theme, id };
    
    this.customThemes.set(id, customTheme);
    
    // Persist to storage
    await this.saveCustomThemes();
    
    return id;
  }
}
```

## Reusable UI Components

### Component Library Structure

```typescript
interface ComponentLibrary {
  'forms/': 'Form controls and inputs';
  'layout/': 'Layout and container components';
  'navigation/': 'Navigation and menu components';
  'feedback/': 'Status and notification components';
  'capability/': 'AI capability-specific components';
  'global/': 'App-wide utility components';
}
```

### Form Controls

```typescript
// Input components with full TypeScript support
interface InputTextProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  label?: string;
  required?: boolean;
  type?: 'text' | 'email' | 'password' | 'url';
  autoComplete?: string;
  'aria-describedby'?: string;
}

const InputText: React.FC<InputTextProps> = ({
  value,
  onChange,
  placeholder,
  disabled = false,
  error,
  label,
  required = false,
  type = 'text',
  autoComplete,
  ...ariaProps
}) => {
  const inputId = `input-${Math.random().toString(36).substr(2, 9)}`;
  const errorId = error ? `${inputId}-error` : undefined;
  
  return (
    <div className="input-group">
      {label && (
        <label 
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        id={inputId}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        autoComplete={autoComplete}
        aria-describedby={errorId}
        className={`
          block w-full px-3 py-2 border rounded-md shadow-sm
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
          disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
          ${error 
            ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500' 
            : 'border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white'
          }
        `}
        {...ariaProps}
      />
      {error && (
        <p id={errorId} className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  );
};

// Select component
interface InputSelectProps<T = string> {
  value: T;
  onChange: (value: T) => void;
  options: Array<{ value: T; label: string; disabled?: boolean }>;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  label?: string;
  required?: boolean;
}

const InputSelect = <T extends string | number>({
  value,
  onChange,
  options,
  placeholder,
  disabled = false,
  error,
  label,
  required = false
}: InputSelectProps<T>) => {
  return (
    <Listbox value={value} onChange={onChange} disabled={disabled}>
      {({ open }) => (
        <div className="relative">
          {label && (
            <Listbox.Label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {label}
              {required && <span className="text-red-500 ml-1">*</span>}
            </Listbox.Label>
          )}
          <Listbox.Button className={`
            relative w-full cursor-pointer rounded-md border py-2 pl-3 pr-10 text-left shadow-sm
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            ${error 
              ? 'border-red-300' 
              : 'border-gray-300 dark:border-gray-600 dark:bg-gray-700'
            }
            ${disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'bg-white dark:bg-gray-700'}
          `}>
            <span className="block truncate">
              {options.find(opt => opt.value === value)?.label || placeholder}
            </span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronUpDownIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
            </span>
          </Listbox.Button>
          
          <Transition
            show={open}
            as={Fragment}
            leave="transition ease-in duration-100"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <Listbox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white dark:bg-gray-700 py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
              {options.map((option) => (
                <Listbox.Option
                  key={String(option.value)}
                  value={option.value}
                  disabled={option.disabled}
                  className={({ active, selected }) => `
                    relative cursor-pointer select-none py-2 pl-3 pr-9
                    ${active ? 'bg-primary-600 text-white' : 'text-gray-900 dark:text-gray-100'}
                    ${option.disabled ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                >
                  {({ selected }) => (
                    <>
                      <span className={`block truncate ${selected ? 'font-semibold' : 'font-normal'}`}>
                        {option.label}
                      </span>
                      {selected && (
                        <span className="absolute inset-y-0 right-0 flex items-center pr-4">
                          <CheckIcon className="h-5 w-5" aria-hidden="true" />
                        </span>
                      )}
                    </>
                  )}
                </Listbox.Option>
              ))}
            </Listbox.Options>
          </Transition>
        </div>
      )}
    </Listbox>
  );
};
```

### Layout Widgets

```typescript
// Card component with variants
interface CardProps {
  children: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outlined' | 'filled';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  className?: string;
}

const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  padding = 'md',
  className = ''
}) => {
  const variantClasses = {
    default: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
    elevated: 'bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700',
    outlined: 'border-2 border-primary-300 dark:border-primary-700',
    filled: 'bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800'
  };
  
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6'
  };
  
  return (
    <div className={`
      rounded-lg
      ${variantClasses[variant]}
      ${paddingClasses[padding]}
      ${className}
    `}>
      {children}
    </div>
  );
};

// Accordion component
interface AccordionProps {
  items: Array<{
    id: string;
    title: string;
    content: React.ReactNode;
    disabled?: boolean;
  }>;
  allowMultiple?: boolean;
  defaultOpen?: string[];
}

const Accordion: React.FC<AccordionProps> = ({
  items,
  allowMultiple = false,
  defaultOpen = []
}) => {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set(defaultOpen));
  
  const toggleItem = (id: string) => {
    const newOpenItems = new Set(openItems);
    
    if (newOpenItems.has(id)) {
      newOpenItems.delete(id);
    } else {
      if (!allowMultiple) {
        newOpenItems.clear();
      }
      newOpenItems.add(id);
    }
    
    setOpenItems(newOpenItems);
  };
  
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item.id} className="border border-gray-200 dark:border-gray-700 rounded-lg">
          <button
            onClick={() => !item.disabled && toggleItem(item.id)}
            disabled={item.disabled}
            className={`
              w-full px-4 py-3 text-left font-medium
              flex items-center justify-between
              hover:bg-gray-50 dark:hover:bg-gray-700
              focus:outline-none focus:ring-2 focus:ring-primary-500
              ${item.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <span>{item.title}</span>
            <ChevronDownIcon 
              className={`
                h-5 w-5 transform transition-transform duration-200
                ${openItems.has(item.id) ? 'rotate-180' : ''}
              `}
            />
          </button>
          
          <AnimatePresence>
            {openItems.has(item.id) && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="px-4 pb-3 border-t border-gray-200 dark:border-gray-700">
                  {item.content}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  );
};
```

### Navigation Elements

```typescript
// Sidebar navigation component
interface SidebarNavProps {
  items: NavItem[];
  currentPath: string;
  onNavigate: (path: string) => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

interface NavItem {
  id: string;
  label: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string | number;
  children?: NavItem[];
  disabled?: boolean;
}

const SidebarNav: React.FC<SidebarNavProps> = ({
  items,
  currentPath,
  onNavigate,
  collapsed = false,
  onToggleCollapse
}) => {
  return (
    <nav className={`
      bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700
      transition-all duration-300 ease-in-out
      ${collapsed ? 'w-16' : 'w-64'}
    `}>
      <div className="p-4">
        {onToggleCollapse && (
          <button
            onClick={onToggleCollapse}
            className="w-full flex items-center justify-center p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <Bars3Icon className="h-5 w-5" />
          </button>
        )}
      </div>
      
      <div className="px-2">
        {items.map((item) => (
          <NavItemComponent
            key={item.id}
            item={item}
            currentPath={currentPath}
            onNavigate={onNavigate}
            collapsed={collapsed}
          />
        ))}
      </div>
    </nav>
  );
};

const NavItemComponent: React.FC<{
  item: NavItem;
  currentPath: string;
  onNavigate: (path: string) => void;
  collapsed: boolean;
  level?: number;
}> = ({ item, currentPath, onNavigate, collapsed, level = 0 }) => {
  const [expanded, setExpanded] = useState(false);
  const isActive = currentPath === item.path;
  const hasChildren = item.children && item.children.length > 0;
  
  return (
    <div className="mb-1">
      <button
        onClick={() => {
          if (hasChildren && !collapsed) {
            setExpanded(!expanded);
          } else if (!item.disabled) {
            onNavigate(item.path);
          }
        }}
        disabled={item.disabled}
        className={`
          w-full flex items-center px-3 py-2 rounded-md text-sm font-medium
          transition-colors duration-150 ease-in-out
          ${isActive 
            ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300' 
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
          }
          ${item.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        style={{ paddingLeft: `${0.75 + level * 0.5}rem` }}
      >
        <item.icon className="h-5 w-5 flex-shrink-0" />
        
        {!collapsed && (
          <>
            <span className="ml-3 flex-1 text-left">{item.label}</span>
            
            {item.badge && (
              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200">
                {item.badge}
              </span>
            )}
            
            {hasChildren && (
              <ChevronDownIcon 
                className={`
                  ml-2 h-4 w-4 transform transition-transform duration-150
                  ${expanded ? 'rotate-180' : ''}
                `}
              />
            )}
          </>
        )}
      </button>
      
      {hasChildren && expanded && !collapsed && (
        <div className="mt-1">
          {item.children!.map((child) => (
            <NavItemComponent
              key={child.id}
              item={child}
              currentPath={currentPath}
              onNavigate={onNavigate}
              collapsed={collapsed}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};
```

## Accessibility & Internationalization

### Accessibility Implementation

```typescript
interface AccessibilityConfig {
  screenReader: boolean;
  highContrast: boolean;
  reducedMotion: boolean;
  fontSize: 'small' | 'medium' | 'large' | 'extra-large';
  keyboardNavigation: boolean;
}

class AccessibilityManager {
  private config: AccessibilityConfig;
  
  constructor(config: AccessibilityConfig) {
    this.config = config;
    this.applyAccessibilitySettings();
  }
  
  private applyAccessibilitySettings(): void {
    const root = document.documentElement;
    
    // High contrast mode
    if (this.config.highContrast) {
      root.classList.add('high-contrast');
    }
    
    // Reduced motion
    if (this.config.reducedMotion) {
      root.classList.add('reduce-motion');
    }
    
    // Font size scaling
    root.style.setProperty('--font-scale', this.getFontScale());
    
    // Keyboard navigation indicators
    if (this.config.keyboardNavigation) {
      root.classList.add('keyboard-navigation');
    }
  }
  
  private getFontScale(): string {
    const scales = {
      small: '0.875',
      medium: '1',
      large: '1.125',
      'extra-large': '1.25'
    };
    return scales[this.config.fontSize];
  }
  
  // ARIA live region management
  announceToScreenReader(message: string, priority: 'polite' | 'assertive' = 'polite'): void {
    const liveRegion = document.getElementById(`aria-live-${priority}`) || this.createLiveRegion(priority);
    liveRegion.textContent = message;
    
    // Clear after announcement
    setTimeout(() => {
      liveRegion.textContent = '';
    }, 1000);
  }
  
  private createLiveRegion(priority: 'polite' | 'assertive'): HTMLElement {
    const region = document.createElement('div');
    region.id = `aria-live-${priority}`;
    region.setAttribute('aria-live', priority);
    region.setAttribute('aria-atomic', 'true');
    region.className = 'sr-only';
    document.body.appendChild(region);
    return region;
  }
}
```

### Internationalization System

```typescript
interface I18nConfig {
  defaultLanguage: string;
  supportedLanguages: string[];
  fallbackLanguage: string;
  namespaces: string[];
}

const i18nConfig: I18nConfig = {
  defaultLanguage: 'en',
  supportedLanguages: ['en', 'es', 'de', 'zh', 'fr', 'ja'],
  fallbackLanguage: 'en',
  namespaces: ['common', 'ui', 'errors', 'capabilities']
};

// Translation hook
const useTranslation = (namespace: string = 'common') => {
  const { t, i18n } = useI18next(namespace);
  
  return {
    t,
    changeLanguage: i18n.changeLanguage,
    currentLanguage: i18n.language,
    supportedLanguages: i18nConfig.supportedLanguages
  };
};

// Language selector component
const LanguageSelector: React.FC = () => {
  const { currentLanguage, changeLanguage, supportedLanguages } = useTranslation();
  
  const languageNames: Record<string, string> = {
    en: 'English',
    es: 'Español',
    de: 'Deutsch',
    zh: '中文',
    fr: 'Français',
    ja: '日本語'
  };
  
  return (
    <InputSelect
      value={currentLanguage}
      onChange={changeLanguage}
      options={supportedLanguages.map(lang => ({
        value: lang,
        label: languageNames[lang] || lang
      }))}
      label="Language"
    />
  );
};
```

## Visual Design Guidelines

### Typography System

```typescript
interface TypographyGuidelines {
  headings: {
    font: 'Inter';
    weight: 'semi-bold' | 'bold';
    spacing: 'tight';
  };
  body: {
    font: 'Inter';
    weight: 'regular';
    spacing: 'normal';
  };
  code: {
    font: 'Fira Code';
    weight: 'regular';
    spacing: 'normal';
  };
  baseFontSize: '14px';
}

// Typography utility classes
const typographyClasses = {
  'heading-1': 'text-3xl font-bold leading-tight',
  'heading-2': 'text-2xl font-semibold leading-tight',
  'heading-3': 'text-xl font-semibold leading-tight',
  'heading-4': 'text-lg font-semibold leading-tight',
  'body-large': 'text-base font-normal leading-normal',
  'body-medium': 'text-sm font-normal leading-normal',
  'body-small': 'text-xs font-normal leading-normal',
  'code-inline': 'font-mono text-sm bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded',
  'code-block': 'font-mono text-sm bg-gray-100 dark:bg-gray-800 p-4 rounded-lg overflow-x-auto'
};
```

### Spacing & Layout

```typescript
interface SpacingGuidelines {
  paddingScale: ['p-2', 'p-4', 'p-6', 'p-8'];
  marginScale: ['m-2', 'm-4', 'm-6', 'm-8'];
  sectionGap: 'gap-6';
  componentGap: 'gap-4';
  elementGap: 'gap-2';
}

interface BorderAndElevation {
  borderRadius: {
    small: 'rounded-md';     // 6px
    medium: 'rounded-lg';    // 8px
    large: 'rounded-xl';     // 12px
    extraLarge: 'rounded-2xl'; // 16px
  };
  elevation: {
    none: 'shadow-none';
    subtle: 'shadow-sm';
    medium: 'shadow-md';
    high: 'shadow-lg';
    highest: 'shadow-xl';
  };
}
```

### Motion & Animation

```typescript
interface MotionGuidelines {
  transitions: {
    fast: 'duration-150';      // 150ms
    normal: 'duration-200';    // 200ms
    slow: 'duration-300';      // 300ms
  };
  easing: {
    default: 'ease-in-out';
    enter: 'ease-out';
    exit: 'ease-in';
  };
  animations: {
    fadeIn: 'animate-fade-in';
    slideIn: 'animate-slide-in';
    scaleIn: 'animate-scale-in';
  };
}

// Framer Motion variants
const motionVariants = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.2 }
  },
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.3, ease: 'easeOut' }
  },
  scaleIn: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
    transition: { duration: 0.2 }
  }
};
```

## Branding & Visual Identity

### Brand Palette

```typescript
interface BrandIdentity {
  colors: {
    kindBlue: '#6366f1';      // Primary brand color
    friendlyPink: '#f472b6';  // Secondary accent
    skyAccent: '#22d3ee';     // Tertiary accent
    midnightBG: '#0f0f15';    // Dark background
  };
  logos: {
    primary: 'assets/logos/kai-logo.svg';
    icon: 'assets/logos/kai-icon.svg';
    wordmark: 'assets/logos/kai-wordmark.svg';
  };
  gradients: {
    primary: 'bg-gradient-to-r from-indigo-500 to-purple-600';
    accent: 'bg-gradient-to-r from-cyan-400 to-blue-500';
    surface: 'bg-gradient-to-br from-gray-900 to-gray-800';
  };
}
```

## Future Enhancements

### Planned Features

| Feature | Description | Target Version | Implementation Status |
| ------- | ----------- | -------------- | -------------------- |
| ThemeEditor | Live theming editor with JSON export/import | v1.2 | Planned |
| Voice Navigation | Speech input for navigation and commands | v1.3 | Research |
| Advanced Animations | Complex motion choreography | v1.4 | Planned |
| Mobile PWA | Progressive web app optimizations | v1.5 | Planned |
| Desktop App | Electron wrapper with native features | v2.0 | Future |
| AR/VR Interface | Immersive interface modes | v3.0 | Research |

### Research Areas

```typescript
interface FutureUICapabilities {
  adaptiveUI: boolean;          // AI-driven interface adaptation
  voiceControl: boolean;        // Voice navigation and commands
  gestureInput: boolean;        // Touch and gesture recognition
  contextualHelp: boolean;      // Smart help system
  personalizedLayouts: boolean; // User-specific interface optimization
}
```

## Implementation Status

- **Core Framework**: React + TypeScript + Tailwind CSS established
- **Component Library**: Basic components implemented
- **Theming System**: Dark/light mode with custom theme support
- **Accessibility**: WCAG 2.1 AA compliance framework
- **Internationalization**: Multi-language support architecture
- **Animation System**: Framer Motion integration
- **Reference Implementation**: Active in Kai-CD project 