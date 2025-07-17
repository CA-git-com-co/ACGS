/**
 * Core types for ACGS-2 Frontend
 * Constitutional Hash: cdd01ef066bc6cf2
 */

export interface ConstitutionalCompliance {
  hash: 'cdd01ef066bc6cf2';
  compliant: boolean;
  score: number;
  violations: string[];
  lastValidated: string;
  metadata: Record<string, any>;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  avatar?: string;
  preferences: UserPreferences;
  behaviorPatterns: BehaviorPatterns;
  constitutionalContext: ConstitutionalContext;
  createdAt: string;
  updatedAt: string;
}

export type UserRole = 
  | 'admin'
  | 'governance_officer'
  | 'policy_analyst'
  | 'compliance_auditor'
  | 'researcher'
  | 'observer';

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: string;
  timezone: string;
  density: 'compact' | 'comfortable' | 'spacious';
  layout: 'sidebar' | 'topbar' | 'minimal';
  complexity: 'beginner' | 'intermediate' | 'expert';
  notifications: NotificationSettings;
  accessibility: AccessibilitySettings;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  governance: boolean;
  compliance: boolean;
  system: boolean;
  frequency: 'immediate' | 'daily' | 'weekly';
}

export interface AccessibilitySettings {
  highContrast: boolean;
  largeText: boolean;
  reducedMotion: boolean;
  screenReader: boolean;
  keyboardNavigation: boolean;
}

export interface BehaviorPatterns {
  frequentActions: string[];
  timeOfDayUsage: Record<string, number>;
  devicePreferences: string[];
  averageSessionDuration: number;
  preferredWorkflows: string[];
}

export interface ConstitutionalContext {
  hash: 'cdd01ef066bc6cf2';
  principles: string[];
  complianceLevel: 'strict' | 'moderate' | 'flexible';
  auditLevel: 'full' | 'summary' | 'minimal';
  validationRules: ConstitutionalRule[];
}

export interface ConstitutionalRule {
  id: string;
  name: string;
  description: string;
  category: 'ethics' | 'legal' | 'operational' | 'security';
  severity: 'critical' | 'high' | 'medium' | 'low';
  active: boolean;
  parameters: Record<string, any>;
}

export interface PersonalizedDashboard {
  user: User;
  widgets: DashboardWidget[];
  insights: GovernanceInsight[];
  recommendations: AIRecommendation[];
  quickActions: QuickAction[];
  lastUpdated: string;
}

export interface DashboardWidget {
  id: string;
  type: 'chart' | 'metric' | 'list' | 'text' | 'custom';
  title: string;
  description?: string;
  position: { x: number; y: number; width: number; height: number };
  data: any;
  config: Record<string, any>;
  permissions: string[];
}

export interface GovernanceInsight {
  id: string;
  title: string;
  description: string;
  type: 'trend' | 'alert' | 'recommendation' | 'metric';
  severity: 'info' | 'warning' | 'error' | 'success';
  data: any;
  constitutionalCompliance: ConstitutionalCompliance;
  createdAt: string;
  expiresAt?: string;
}

export interface AIRecommendation {
  id: string;
  title: string;
  description: string;
  type: 'action' | 'policy' | 'workflow' | 'optimization';
  confidence: number;
  impact: 'low' | 'medium' | 'high';
  effort: 'low' | 'medium' | 'high';
  constitutionalCompliance: ConstitutionalCompliance;
  actionUrl?: string;
  metadata: Record<string, any>;
  createdAt: string;
}

export interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  action: 'navigate' | 'execute' | 'modal' | 'external';
  target: string;
  permissions: string[];
  constitutionalValidation: boolean;
}

export interface CustomWorkflow {
  id: string;
  name: string;
  description: string;
  version: string;
  createdBy: string;
  steps: WorkflowStep[];
  triggers: WorkflowTrigger[];
  conditions: WorkflowCondition[];
  actions: WorkflowAction[];
  constitutionalCompliance: ConstitutionalCompliance;
  status: 'draft' | 'active' | 'paused' | 'archived';
  createdAt: string;
  updatedAt: string;
}

export interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  type: 'manual' | 'automated' | 'decision' | 'validation';
  order: number;
  config: Record<string, any>;
  dependencies: string[];
  timeout?: number;
}

export interface WorkflowTrigger {
  id: string;
  type: 'schedule' | 'event' | 'manual' | 'webhook';
  config: Record<string, any>;
  active: boolean;
}

export interface WorkflowCondition {
  id: string;
  type: 'expression' | 'rule' | 'approval' | 'constitutional';
  config: Record<string, any>;
  required: boolean;
}

export interface WorkflowAction {
  id: string;
  type: 'api' | 'notification' | 'approval' | 'log' | 'constitutional';
  config: Record<string, any>;
  retryConfig?: RetryConfig;
}

export interface RetryConfig {
  maxAttempts: number;
  backoffStrategy: 'fixed' | 'exponential' | 'linear';
  initialDelay: number;
  maxDelay: number;
}

export interface SearchResults {
  query: string;
  results: SearchResult[];
  suggestions: SearchSuggestion[];
  filters: SearchFilter[];
  pagination: PaginationInfo;
  processingTime: number;
  constitutionalCompliance: ConstitutionalCompliance;
}

export interface SearchResult {
  id: string;
  title: string;
  description: string;
  type: 'policy' | 'governance' | 'workflow' | 'insight' | 'user';
  url: string;
  score: number;
  highlight: string;
  metadata: Record<string, any>;
  constitutionalCompliance: ConstitutionalCompliance;
}

export interface SearchSuggestion {
  text: string;
  type: 'query' | 'filter' | 'entity';
  score: number;
}

export interface SearchFilter {
  key: string;
  label: string;
  type: 'text' | 'select' | 'date' | 'range' | 'boolean';
  options?: FilterOption[];
  value?: any;
}

export interface FilterOption {
  label: string;
  value: any;
  count?: number;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface APIResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
  errors?: APIError[];
  pagination?: PaginationInfo;
  constitutionalCompliance: ConstitutionalCompliance;
  timestamp: string;
}

export interface APIError {
  code: string;
  message: string;
  field?: string;
  details?: Record<string, any>;
}

export interface LayoutConfig {
  theme: 'light' | 'dark' | 'system';
  layout: 'sidebar' | 'topbar' | 'minimal';
  density: 'compact' | 'comfortable' | 'spacious';
  complexity: 'beginner' | 'intermediate' | 'expert';
  sidebar: {
    collapsed: boolean;
    width: number;
    position: 'left' | 'right';
  };
  header: {
    height: number;
    sticky: boolean;
    breadcrumbs: boolean;
  };
  content: {
    maxWidth: string;
    padding: string;
    spacing: string;
  };
}

export interface AdaptiveUIConfig {
  userId: string;
  preferences: UserPreferences;
  behaviorPatterns: BehaviorPatterns;
  deviceInfo: DeviceInfo;
  contextualFactors: ContextualFactors;
}

export interface DeviceInfo {
  type: 'desktop' | 'tablet' | 'mobile';
  os: string;
  browser: string;
  screenSize: { width: number; height: number };
  touchCapable: boolean;
  darkModeSupported: boolean;
}

export interface ContextualFactors {
  timeOfDay: string;
  dayOfWeek: string;
  location?: string;
  networkSpeed: 'slow' | 'medium' | 'fast';
  batteryLevel?: number;
  isOnline: boolean;
}

export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  interactionTime: number;
  memoryUsage: number;
  networkRequests: number;
  cacheHitRate: number;
  errorRate: number;
}

export interface AnalyticsEvent {
  id: string;
  type: 'page_view' | 'user_action' | 'error' | 'performance' | 'constitutional';
  properties: Record<string, any>;
  userId?: string;
  sessionId: string;
  timestamp: string;
  constitutionalCompliance: ConstitutionalCompliance;
}

export interface NotificationMessage {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  duration?: number;
  actions?: NotificationAction[];
  constitutionalCompliance: ConstitutionalCompliance;
  createdAt: string;
}

export interface NotificationAction {
  label: string;
  action: 'dismiss' | 'navigate' | 'execute';
  target?: string;
  style?: 'primary' | 'secondary' | 'destructive';
}

export interface Theme {
  name: string;
  colors: Record<string, string>;
  typography: Record<string, any>;
  spacing: Record<string, string>;
  borderRadius: Record<string, string>;
  animations: Record<string, any>;
  accessibility: {
    highContrast: boolean;
    reducedMotion: boolean;
  };
}

export interface FeatureFlag {
  key: string;
  name: string;
  description: string;
  enabled: boolean;
  rolloutPercentage: number;
  conditions: FeatureFlagCondition[];
  constitutionalCompliance: ConstitutionalCompliance;
}

export interface FeatureFlagCondition {
  type: 'user_role' | 'user_id' | 'environment' | 'date' | 'custom';
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than';
  value: any;
}

// Utility types
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Constants
export const CONSTITUTIONAL_HASH = 'cdd01ef066bc6cf2' as const;
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8010';
export const GRAPHQL_URL = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8010/graphql';
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8010/ws';