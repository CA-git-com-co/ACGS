# ⚡ Phase 4: Modern React Implementation

**Date:** 2025-06-21
**Scope:** ACGS Modern React Patterns & Production Implementation
**Status:** 🔄 IN PROGRESS

## 🎯 Executive Summary

This final phase implements modern React patterns, performance optimizations, accessibility features, and production-ready deployment for the consolidated ACGS governance platform.

## 🖥️ Server Components Implementation

### Server Component Architecture

#### Governance Data Server Components

```typescript
// app/(dashboard)/governance/policies/page.tsx
import { Suspense } from 'react';
import { getPolicies, getComplianceOverview } from '@/lib/api/governance';
import { PolicyList } from '@/components/governance/PolicyList';
import { ComplianceOverview } from '@/components/governance/ComplianceOverview';
import { PolicyListSkeleton, ComplianceOverviewSkeleton } from '@/components/ui/Skeletons';

// Server Component - runs on server, no JavaScript sent to client
export default async function PoliciesPage({
  searchParams,
}: {
  searchParams: { status?: string; category?: string; page?: string };
}) {
  // Server-side data fetching with search parameters
  const filters = {
    status: searchParams.status,
    category: searchParams.category,
    page: parseInt(searchParams.page || '1'),
  };

  // Parallel data fetching on server
  const [policies, complianceData] = await Promise.all([
    getPolicies(filters),
    getComplianceOverview(),
  ]);

  return (
    <div className="governance-policies-page">
      <div className="page-header">
        <h1 className="text-3xl font-bold">Policy Management</h1>
        <p className="text-gray-600">Manage and monitor governance policies</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content area */}
        <div className="lg:col-span-2">
          <Suspense fallback={<PolicyListSkeleton />}>
            <PolicyList
              initialPolicies={policies}
              filters={filters}
            />
          </Suspense>
        </div>

        {/* Sidebar with compliance overview */}
        <div className="lg:col-span-1">
          <Suspense fallback={<ComplianceOverviewSkeleton />}>
            <ComplianceOverview
              initialData={complianceData}
              realTimeUpdates={true}
            />
          </Suspense>
        </div>
      </div>
    </div>
  );
}

// Generate metadata for SEO
export async function generateMetadata({
  searchParams,
}: {
  searchParams: { status?: string; category?: string };
}) {
  const title = searchParams.status
    ? `${searchParams.status} Policies - ACGS Governance`
    : 'Policy Management - ACGS Governance';

  return {
    title,
    description: 'Manage governance policies with AI-assisted analysis and constitutional compliance monitoring.',
  };
}
```

#### Constitutional Amendment Server Components

```typescript
// app/(dashboard)/constitutional/amendments/[id]/page.tsx
import { notFound } from 'next/navigation';
import { getAmendment, getAmendmentHistory, getVotingRecords } from '@/lib/api/constitutional';
import { AmendmentDetails } from '@/components/constitutional/AmendmentDetails';
import { AmendmentWorkflow } from '@/components/constitutional/AmendmentWorkflow';
import { VotingInterface } from '@/components/constitutional/VotingInterface';

interface AmendmentPageProps {
  params: { id: string };
}

export default async function AmendmentPage({ params }: AmendmentPageProps) {
  const amendmentId = params.id;

  try {
    // Server-side data fetching with error handling
    const [amendment, history, votingRecords] = await Promise.all([
      getAmendment(amendmentId),
      getAmendmentHistory(amendmentId),
      getVotingRecords(amendmentId),
    ]);

    if (!amendment) {
      notFound();
    }

    return (
      <div className="amendment-page">
        <AmendmentDetails
          amendment={amendment}
          history={history}
        />

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mt-8">
          <AmendmentWorkflow
            amendment={amendment}
            votingRecords={votingRecords}
          />

          {amendment.status === 'voting' && (
            <VotingInterface
              amendmentId={amendmentId}
              currentUserVote={votingRecords.currentUserVote}
            />
          )}
        </div>
      </div>
    );
  } catch (error) {
    console.error('Failed to load amendment:', error);
    throw error; // Will be caught by error.tsx
  }
}

// Static generation for public amendments
export async function generateStaticParams() {
  const publicAmendments = await getPublicAmendments();

  return publicAmendments.map((amendment) => ({
    id: amendment.id,
  }));
}
```

### Client Component Boundaries

#### Interactive Policy Editor

```typescript
// components/governance/PolicyEditor/PolicyEditor.tsx
'use client';

import { useState, useCallback, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { PolicyContent, PolicyValidation } from '@/lib/types/governance';
import { validatePolicy, savePolicy } from '@/lib/api/governance';
import { RichTextEditor } from '@/components/ui/RichTextEditor';
import { AIAssistant } from '@/components/governance/AIAssistant';

interface PolicyEditorProps {
  initialPolicy?: PolicyContent;
  mode: 'create' | 'edit';
  onSave?: (policy: PolicyContent) => void;
}

export function PolicyEditor({ initialPolicy, mode, onSave }: PolicyEditorProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [isPending, startTransition] = useTransition();

  const [policy, setPolicy] = useState<PolicyContent>(
    initialPolicy || {
      title: '',
      content: '',
      category: '',
      status: 'draft',
    }
  );

  const [validation, setValidation] = useState<PolicyValidation | null>(null);
  const [isAIAssistantOpen, setIsAIAssistantOpen] = useState(false);

  // Real-time validation with debouncing
  const validatePolicyMutation = useMutation({
    mutationFn: validatePolicy,
    onSuccess: (validationResult) => {
      setValidation(validationResult);
    },
  });

  // Auto-save functionality
  const savePolicyMutation = useMutation({
    mutationFn: savePolicy,
    onSuccess: (savedPolicy) => {
      queryClient.invalidateQueries(['policies']);
      onSave?.(savedPolicy);

      if (mode === 'create') {
        startTransition(() => {
          router.push(`/governance/policies/${savedPolicy.id}`);
        });
      }
    },
  });

  const handleContentChange = useCallback((content: string) => {
    setPolicy(prev => ({ ...prev, content }));

    // Debounced validation
    const timeoutId = setTimeout(() => {
      validatePolicyMutation.mutate({ ...policy, content });
    }, 1000);

    return () => clearTimeout(timeoutId);
  }, [policy, validatePolicyMutation]);

  const handleSave = useCallback(() => {
    savePolicyMutation.mutate(policy);
  }, [policy, savePolicyMutation]);

  const handleAIAssist = useCallback((suggestion: string) => {
    setPolicy(prev => ({
      ...prev,
      content: prev.content + '\n\n' + suggestion,
    }));
    setIsAIAssistantOpen(false);
  }, []);

  return (
    <div className="policy-editor">
      <div className="editor-header">
        <input
          type="text"
          value={policy.title}
          onChange={(e) => setPolicy(prev => ({ ...prev, title: e.target.value }))}
          placeholder="Policy Title"
          className="text-2xl font-bold border-none outline-none w-full"
        />

        <div className="editor-actions">
          <button
            onClick={() => setIsAIAssistantOpen(true)}
            className="ai-assist-button"
            disabled={validatePolicyMutation.isLoading}
          >
            🤖 AI Assist
          </button>

          <button
            onClick={handleSave}
            disabled={savePolicyMutation.isLoading || isPending}
            className="save-button"
          >
            {savePolicyMutation.isLoading ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      <div className="editor-content">
        <RichTextEditor
          value={policy.content}
          onChange={handleContentChange}
          placeholder="Start writing your policy..."
        />

        {validation && (
          <div className="validation-panel">
            <h3>Constitutional Compliance</h3>
            <div className={`compliance-score ${validation.score >= 0.8 ? 'good' : 'warning'}`}>
              Score: {(validation.score * 100).toFixed(1)}%
            </div>
            {validation.issues.map((issue, index) => (
              <div key={index} className="validation-issue">
                {issue.message}
              </div>
            ))}
          </div>
        )}
      </div>

      {isAIAssistantOpen && (
        <AIAssistant
          context={policy}
          onSuggestion={handleAIAssist}
          onClose={() => setIsAIAssistantOpen(false)}
        />
      )}
    </div>
  );
}
```

## 🔄 Suspense Boundaries Implementation

### Governance Workflow Suspense

```typescript
// components/governance/GovernanceWorkflow.tsx
import { Suspense } from 'react';
import { ErrorBoundary } from '@/components/shared/ErrorBoundary';
import {
  PolicyListSkeleton,
  ComplianceMonitorSkeleton,
  WorkflowStagesSkeleton
} from '@/components/ui/Skeletons';

export function GovernanceWorkflow() {
  return (
    <div className="governance-workflow">
      <div className="workflow-grid">
        {/* Policy Management Section */}
        <ErrorBoundary fallback={<PolicyErrorFallback />}>
          <Suspense fallback={<PolicyListSkeleton />}>
            <PolicyManagementSection />
          </Suspense>
        </ErrorBoundary>

        {/* Compliance Monitoring Section */}
        <ErrorBoundary fallback={<ComplianceErrorFallback />}>
          <Suspense fallback={<ComplianceMonitorSkeleton />}>
            <ComplianceMonitoringSection />
          </Suspense>
        </ErrorBoundary>

        {/* Workflow Stages Section */}
        <ErrorBoundary fallback={<WorkflowErrorFallback />}>
          <Suspense fallback={<WorkflowStagesSkeleton />}>
            <WorkflowStagesSection />
          </Suspense>
        </ErrorBoundary>
      </div>
    </div>
  );
}

// Nested suspense for granular loading
function PolicyManagementSection() {
  return (
    <div className="policy-management">
      <h2>Policy Management</h2>

      <Suspense fallback={<div>Loading active policies...</div>}>
        <ActivePoliciesList />
      </Suspense>

      <Suspense fallback={<div>Loading draft policies...</div>}>
        <DraftPoliciesList />
      </Suspense>

      <Suspense fallback={<div>Loading policy analytics...</div>}>
        <PolicyAnalytics />
      </Suspense>
    </div>
  );
}
```

### Streaming UI with Progressive Enhancement

```typescript
// components/constitutional/AmendmentTimeline.tsx
'use client';

import { Suspense, use } from 'react';
import { getAmendmentTimeline } from '@/lib/api/constitutional';

interface AmendmentTimelineProps {
  amendmentId: string;
  timelinePromise: Promise<TimelineEvent[]>;
}

export function AmendmentTimeline({ amendmentId, timelinePromise }: AmendmentTimelineProps) {
  return (
    <div className="amendment-timeline">
      <h3>Amendment Timeline</h3>

      <Suspense fallback={<TimelineLoadingSkeleton />}>
        <TimelineEvents timelinePromise={timelinePromise} />
      </Suspense>

      <Suspense fallback={<div>Loading related documents...</div>}>
        <RelatedDocuments amendmentId={amendmentId} />
      </Suspense>
    </div>
  );
}

function TimelineEvents({ timelinePromise }: { timelinePromise: Promise<TimelineEvent[]> }) {
  const timeline = use(timelinePromise);

  return (
    <div className="timeline-events">
      {timeline.map((event, index) => (
        <div key={event.id} className="timeline-event">
          <div className="event-marker" />
          <div className="event-content">
            <h4>{event.title}</h4>
            <p>{event.description}</p>
            <time>{new Date(event.timestamp).toLocaleDateString()}</time>
          </div>
        </div>
      ))}
    </div>
  );
}
```

## 🚨 Error Boundaries Implementation

### Governance-Specific Error Boundaries

```typescript
// components/shared/ErrorBoundary/GovernanceErrorBoundary.tsx
'use client';

import { Component, ReactNode } from 'react';
import { ErrorInfo } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface GovernanceErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

interface GovernanceErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

export class GovernanceErrorBoundary extends Component<
  GovernanceErrorBoundaryProps,
  GovernanceErrorBoundaryState
> {
  constructor(props: GovernanceErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<GovernanceErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // Log error to monitoring service
    console.error('Governance Error Boundary caught an error:', error, errorInfo);

    // Call custom error handler
    this.props.onError?.(error, errorInfo);

    // Send to error tracking service
    if (typeof window !== 'undefined') {
      // Send error to monitoring service (e.g., Sentry)
      window.gtag?.('event', 'exception', {
        description: error.message,
        fatal: false,
      });
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="governance-error-boundary">
          <div className="error-container">
            <div className="error-icon">
              <AlertTriangle className="w-16 h-16 text-red-500" />
            </div>

            <div className="error-content">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Governance System Error
              </h2>

              <p className="text-gray-600 mb-6">
                An error occurred in the governance system. This has been logged and
                our team has been notified. You can try refreshing the page or
                return to the dashboard.
              </p>

              {process.env.NODE_ENV === 'development' && (
                <details className="error-details">
                  <summary>Error Details (Development)</summary>
                  <pre className="error-stack">
                    {this.state.error?.message}
                    {this.state.error?.stack}
                  </pre>
                </details>
              )}

              <div className="error-actions">
                <button
                  onClick={this.handleRetry}
                  className="retry-button"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Try Again
                </button>

                <a
                  href="/dashboard"
                  className="home-button"
                >
                  <Home className="w-4 h-4 mr-2" />
                  Return to Dashboard
                </a>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Specialized error boundaries for different governance areas
export function PolicyErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <GovernanceErrorBoundary
      fallback={
        <div className="policy-error-fallback">
          <h3>Policy System Unavailable</h3>
          <p>The policy management system is temporarily unavailable.</p>
        </div>
      }
      onError={(error) => {
        console.error('Policy system error:', error);
      }}
    >
      {children}
    </GovernanceErrorBoundary>
  );
}

export function ComplianceErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <GovernanceErrorBoundary
      fallback={
        <div className="compliance-error-fallback">
          <h3>Compliance Monitor Unavailable</h3>
          <p>Constitutional compliance monitoring is temporarily unavailable.</p>
        </div>
      }
      onError={(error) => {
        console.error('Compliance system error:', error);
      }}
    >
      {children}
    </GovernanceErrorBoundary>
  );
}
```

### API Error Handling

```typescript
// lib/api/error-handling.ts
export class GovernanceAPIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public context?: string
  ) {
    super(message);
    this.name = 'GovernanceAPIError';
  }
}

export async function handleGovernanceAPIResponse<T>(
  response: Response,
  context: string
): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));

    throw new GovernanceAPIError(
      errorData.message || `${context} request failed`,
      response.status,
      errorData.code,
      context
    );
  }

  return response.json();
}

// React Query error handling
export function useGovernanceErrorHandler() {
  return (error: unknown) => {
    if (error instanceof GovernanceAPIError) {
      switch (error.status) {
        case 401:
          // Redirect to login
          window.location.href = '/login';
          break;
        case 403:
          // Show permission denied message
          console.error('Permission denied:', error.message);
          break;
        case 500:
          // Show system error message
          console.error('System error:', error.message);
          break;
        default:
          console.error('API error:', error.message);
      }
    } else {
      console.error('Unexpected error:', error);
    }
  };
}
```

## ⚡ Performance Optimization

### Code Splitting & Lazy Loading

```typescript
// Dynamic imports for heavy components
import dynamic from 'next/dynamic';

// Lazy load complex governance components
const PolicyEditor = dynamic(
  () => import('@/components/governance/PolicyEditor'),
  {
    loading: () => <PolicyEditorSkeleton />,
    ssr: false, // Client-side only for rich text editor
  }
);

const AmendmentWorkflow = dynamic(
  () => import('@/components/constitutional/AmendmentWorkflow'),
  {
    loading: () => <WorkflowSkeleton />,
    ssr: true, // Server-side rendering for SEO
  }
);

const ComplianceMonitor = dynamic(
  () => import('@/components/governance/ComplianceMonitor'),
  {
    loading: () => <MonitorSkeleton />,
    ssr: true,
  }
);

// Route-based code splitting
const GovernanceDashboard = dynamic(
  () => import('@/components/governance/GovernanceDashboard'),
  {
    loading: () => <DashboardSkeleton />,
  }
);

// Conditional loading based on user permissions
function ConditionalAdminPanel({ userPermissions }: { userPermissions: string[] }) {
  const hasAdminAccess = userPermissions.includes('admin:system');

  const AdminPanel = dynamic(
    () => import('@/components/admin/AdminPanel'),
    {
      loading: () => <AdminPanelSkeleton />,
      ssr: false,
    }
  );

  return hasAdminAccess ? <AdminPanel /> : null;
}
```

### React.memo & useMemo Optimization

```typescript
// components/governance/PolicyCard.tsx
import { memo, useMemo } from 'react';
import { Policy, ComplianceStatus } from '@/lib/types/governance';

interface PolicyCardProps {
  policy: Policy;
  complianceStatus: ComplianceStatus;
  onEdit: (policyId: string) => void;
  onDelete: (policyId: string) => void;
}

export const PolicyCard = memo(function PolicyCard({
  policy,
  complianceStatus,
  onEdit,
  onDelete,
}: PolicyCardProps) {
  // Memoize expensive calculations
  const complianceScore = useMemo(() => {
    return calculateComplianceScore(policy, complianceStatus);
  }, [policy.content, policy.lastModified, complianceStatus.lastCheck]);

  const statusColor = useMemo(() => {
    return getStatusColor(policy.status, complianceScore);
  }, [policy.status, complianceScore]);

  const formattedDate = useMemo(() => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(new Date(policy.lastModified));
  }, [policy.lastModified]);

  return (
    <div className={`policy-card ${statusColor}`}>
      <div className="policy-header">
        <h3>{policy.title}</h3>
        <span className="policy-status">{policy.status}</span>
      </div>

      <div className="policy-content">
        <p>{policy.summary}</p>
        <div className="policy-metadata">
          <span>Last modified: {formattedDate}</span>
          <span>Compliance: {(complianceScore * 100).toFixed(1)}%</span>
        </div>
      </div>

      <div className="policy-actions">
        <button onClick={() => onEdit(policy.id)}>Edit</button>
        <button onClick={() => onDelete(policy.id)}>Delete</button>
      </div>
    </div>
  );
});

// Memoize expensive calculations
function calculateComplianceScore(policy: Policy, status: ComplianceStatus): number {
  // Complex calculation that should be memoized
  return status.violations.length === 0 ? 1.0 :
    Math.max(0, 1 - (status.violations.length * 0.1));
}
```

### Virtual Scrolling for Large Lists

```typescript
// components/governance/VirtualizedPolicyList.tsx
import { FixedSizeList as List } from 'react-window';
import { memo } from 'react';

interface VirtualizedPolicyListProps {
  policies: Policy[];
  height: number;
  itemHeight: number;
  onPolicySelect: (policy: Policy) => void;
}

export function VirtualizedPolicyList({
  policies,
  height,
  itemHeight,
  onPolicySelect,
}: VirtualizedPolicyListProps) {
  const Row = memo(({ index, style }: { index: number; style: React.CSSProperties }) => {
    const policy = policies[index];

    return (
      <div style={style}>
        <PolicyCard
          policy={policy}
          onSelect={() => onPolicySelect(policy)}
        />
      </div>
    );
  });

  return (
    <List
      height={height}
      itemCount={policies.length}
      itemSize={itemHeight}
      width="100%"
    >
      {Row}
    </List>
  );
}
```

## ♿ Accessibility Implementation

### WCAG 2.1 AA Compliance

```typescript
// components/ui/AccessibleButton.tsx
import { forwardRef, ButtonHTMLAttributes } from 'react';
import { VariantProps, cva } from 'class-variance-authority';

const buttonVariants = cva(
  // Base styles with accessibility considerations
  [
    'inline-flex items-center justify-center rounded-md text-sm font-medium',
    'transition-colors focus-visible:outline-none focus-visible:ring-2',
    'focus-visible:ring-ring focus-visible:ring-offset-2',
    'disabled:opacity-50 disabled:pointer-events-none',
    'ring-offset-background',
  ],
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'underline-offset-4 hover:underline text-primary',
      },
      size: {
        default: 'h-10 py-2 px-4',
        sm: 'h-9 px-3 rounded-md',
        lg: 'h-11 px-8 rounded-md',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

interface AccessibleButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  loadingText?: string;
}

export const AccessibleButton = forwardRef<HTMLButtonElement, AccessibleButtonProps>(
  ({ className, variant, size, loading, loadingText, children, ...props }, ref) => {
    return (
      <button
        className={buttonVariants({ variant, size, className })}
        ref={ref}
        disabled={loading || props.disabled}
        aria-disabled={loading || props.disabled}
        aria-describedby={loading ? 'loading-description' : undefined}
        {...props}
      >
        {loading && (
          <>
            <span className="sr-only" id="loading-description">
              {loadingText || 'Loading, please wait'}
            </span>
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </>
        )}
        {children}
      </button>
    );
  }
);

AccessibleButton.displayName = 'AccessibleButton';
```

### Keyboard Navigation

```typescript
// hooks/useKeyboardNavigation.ts
import { useEffect, useCallback } from 'react';

interface KeyboardNavigationOptions {
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
  onEnter?: () => void;
  onEscape?: () => void;
  onTab?: () => void;
  enabled?: boolean;
}

export function useKeyboardNavigation({
  onArrowUp,
  onArrowDown,
  onArrowLeft,
  onArrowRight,
  onEnter,
  onEscape,
  onTab,
  enabled = true,
}: KeyboardNavigationOptions) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      switch (event.key) {
        case 'ArrowUp':
          event.preventDefault();
          onArrowUp?.();
          break;
        case 'ArrowDown':
          event.preventDefault();
          onArrowDown?.();
          break;
        case 'ArrowLeft':
          event.preventDefault();
          onArrowLeft?.();
          break;
        case 'ArrowRight':
          event.preventDefault();
          onArrowRight?.();
          break;
        case 'Enter':
          event.preventDefault();
          onEnter?.();
          break;
        case 'Escape':
          event.preventDefault();
          onEscape?.();
          break;
        case 'Tab':
          onTab?.();
          break;
      }
    },
    [enabled, onArrowUp, onArrowDown, onArrowLeft, onArrowRight, onEnter, onEscape, onTab]
  );

  useEffect(() => {
    if (enabled) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [enabled, handleKeyDown]);
}

// Usage in governance components
export function PolicyList({ policies }: { policies: Policy[] }) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useKeyboardNavigation({
    onArrowUp: () => setSelectedIndex(prev => Math.max(0, prev - 1)),
    onArrowDown: () => setSelectedIndex(prev => Math.min(policies.length - 1, prev + 1)),
    onEnter: () => setIsModalOpen(true),
    onEscape: () => setIsModalOpen(false),
    enabled: !isModalOpen,
  });

  return (
    <div role="listbox" aria-label="Policy list">
      {policies.map((policy, index) => (
        <div
          key={policy.id}
          role="option"
          aria-selected={index === selectedIndex}
          tabIndex={index === selectedIndex ? 0 : -1}
          className={`policy-item ${index === selectedIndex ? 'selected' : ''}`}
        >
          {policy.title}
        </div>
      ))}
    </div>
  );
}
```

### Screen Reader Support

```typescript
// components/governance/ComplianceStatus.tsx
interface ComplianceStatusProps {
  score: number;
  violations: Violation[];
  trend: 'improving' | 'declining' | 'stable';
}

export function ComplianceStatus({ score, violations, trend }: ComplianceStatusProps) {
  const scorePercentage = Math.round(score * 100);
  const statusLevel = score >= 0.9 ? 'excellent' : score >= 0.7 ? 'good' : 'needs-attention';

  return (
    <div className="compliance-status" role="region" aria-labelledby="compliance-heading">
      <h3 id="compliance-heading">Constitutional Compliance Status</h3>

      {/* Screen reader accessible score */}
      <div
        className="compliance-score"
        role="progressbar"
        aria-valuenow={scorePercentage}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Compliance score: ${scorePercentage} percent`}
        aria-describedby="compliance-description"
      >
        <div
          className="score-bar"
          style={{ width: `${scorePercentage}%` }}
          aria-hidden="true"
        />
        <span className="score-text">{scorePercentage}%</span>
      </div>

      <div id="compliance-description" className="sr-only">
        Current compliance score is {scorePercentage} percent, which is considered {statusLevel}.
        The trend is {trend}. There are {violations.length} active violations.
      </div>

      {/* Violations list with proper semantics */}
      {violations.length > 0 && (
        <div className="violations-section">
          <h4>Active Violations</h4>
          <ul role="list" aria-label={`${violations.length} compliance violations`}>
            {violations.map((violation, index) => (
              <li key={violation.id} role="listitem">
                <span className="violation-severity" aria-label={`Severity: ${violation.severity}`}>
                  {violation.severity}
                </span>
                <span className="violation-message">{violation.message}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Live region for real-time updates */}
      <div
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
        id="compliance-updates"
      >
        {/* Dynamic updates will be announced here */}
      </div>
    </div>
  );
}
```

## 🔧 TypeScript Integration

### Strict Type Safety

```typescript
// lib/types/governance.ts
export interface Policy {
  readonly id: string;
  title: string;
  content: string;
  category: PolicyCategory;
  status: PolicyStatus;
  author: User;
  createdAt: Date;
  lastModified: Date;
  version: number;
  tags: readonly string[];
  complianceScore?: number;
}

export type PolicyCategory = 'constitutional' | 'administrative' | 'procedural' | 'enforcement';

export type PolicyStatus = 'draft' | 'review' | 'voting' | 'approved' | 'rejected' | 'archived';

export interface Amendment {
  readonly id: string;
  title: string;
  description: string;
  proposedChanges: readonly ConstitutionalChange[];
  status: AmendmentStatus;
  proposer: User;
  supporters: readonly User[];
  votingRecord?: VotingRecord;
  timeline: readonly TimelineEvent[];
  createdAt: Date;
  votingDeadline?: Date;
}

export type AmendmentStatus =
  | 'proposed'
  | 'under-review'
  | 'voting'
  | 'passed'
  | 'failed'
  | 'withdrawn';

// Branded types for enhanced type safety
export type PolicyId = string & { readonly __brand: 'PolicyId' };
export type AmendmentId = string & { readonly __brand: 'AmendmentId' };
export type UserId = string & { readonly __brand: 'UserId' };

// Utility types for API responses
export type APIResponse<T> = {
  data: T;
  meta: {
    timestamp: string;
    requestId: string;
    version: string;
  };
};

export type PaginatedResponse<T> = APIResponse<{
  items: readonly T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}>;

// Form types with validation
export interface PolicyFormData {
  title: string;
  content: string;
  category: PolicyCategory;
  tags: string[];
}

export interface PolicyFormErrors {
  title?: string;
  content?: string;
  category?: string;
  tags?: string;
  general?: string;
}

// API client types
export interface GovernanceAPIClient {
  policies: {
    list(filters?: PolicyFilters): Promise<PaginatedResponse<Policy>>;
    get(id: PolicyId): Promise<APIResponse<Policy>>;
    create(data: PolicyFormData): Promise<APIResponse<Policy>>;
    update(id: PolicyId, data: Partial<PolicyFormData>): Promise<APIResponse<Policy>>;
    delete(id: PolicyId): Promise<APIResponse<void>>;
    validate(content: string): Promise<APIResponse<ValidationResult>>;
  };
  amendments: {
    list(filters?: AmendmentFilters): Promise<PaginatedResponse<Amendment>>;
    get(id: AmendmentId): Promise<APIResponse<Amendment>>;
    create(data: AmendmentFormData): Promise<APIResponse<Amendment>>;
    vote(id: AmendmentId, vote: Vote): Promise<APIResponse<VotingRecord>>;
  };
  compliance: {
    check(policyId: PolicyId): Promise<APIResponse<ComplianceResult>>;
    monitor(policyId: PolicyId): Promise<APIResponse<ComplianceMonitor>>;
    violations(): Promise<PaginatedResponse<Violation>>;
  };
}
```

### Component Props with Strict Typing

```typescript
// components/governance/PolicyEditor/types.ts
export interface PolicyEditorProps {
  /** Initial policy data for editing, undefined for new policy */
  initialPolicy?: Policy;
  /** Editor mode */
  mode: 'create' | 'edit' | 'view';
  /** Callback when policy is saved */
  onSave?: (policy: Policy) => void | Promise<void>;
  /** Callback when editor is closed */
  onClose?: () => void;
  /** Whether the editor is in read-only mode */
  readOnly?: boolean;
  /** Auto-save interval in milliseconds */
  autoSaveInterval?: number;
  /** Custom validation rules */
  validationRules?: ValidationRule[];
  /** AI assistance configuration */
  aiAssistance?: {
    enabled: boolean;
    model?: string;
    context?: string;
  };
}

export interface PolicyEditorState {
  policy: PolicyFormData;
  validation: ValidationResult | null;
  isDirty: boolean;
  isSaving: boolean;
  isValidating: boolean;
  lastSaved: Date | null;
  errors: PolicyFormErrors;
}

// Hook return types
export interface UsePolicyEditorReturn {
  state: PolicyEditorState;
  actions: {
    updatePolicy: (updates: Partial<PolicyFormData>) => void;
    save: () => Promise<void>;
    validate: () => Promise<ValidationResult>;
    reset: () => void;
    undo: () => void;
    redo: () => void;
  };
  canUndo: boolean;
  canRedo: boolean;
  hasUnsavedChanges: boolean;
}

// Event handler types
export type PolicyEventHandler<T = void> = (event: PolicyEvent) => T;
export type PolicyAsyncEventHandler<T = void> = (event: PolicyEvent) => Promise<T>;

export interface PolicyEvent {
  type: 'save' | 'validate' | 'delete' | 'publish';
  policy: Policy;
  timestamp: Date;
  user: User;
  metadata?: Record<string, unknown>;
}
```

## 📋 Production Deployment Strategy

### Next.js Configuration

```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
    serverComponentsExternalPackages: ['@acgs/shared'],
  },

  // Performance optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Bundle optimization
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }

    // Optimize shared component library
    config.resolve.alias['@acgs/shared'] = path.resolve(__dirname, '../shared');

    return config;
  },

  // Image optimization
  images: {
    domains: ['governance.acgs.org'],
    formats: ['image/webp', 'image/avif'],
  },

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Content-Security-Policy',
            value:
              "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
          },
        ],
      },
    ];
  },

  // Redirects for legacy routes
  async redirects() {
    return [
      {
        source: '/old-dashboard',
        destination: '/dashboard',
        permanent: true,
      },
      {
        source: '/legacy-policies',
        destination: '/governance/policies',
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig;
```

### Deployment Pipeline

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run linting
        run: pnpm run lint

      - name: Run type checking
        run: pnpm run type-check

      - name: Run unit tests
        run: pnpm run test

      - name: Run E2E tests
        run: pnpm run test:e2e

      - name: Build application
        run: pnpm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
          NEXTAUTH_SECRET: ${{ secrets.NEXTAUTH_SECRET }}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

---

**Phase 4 Status:** ✅ COMPLETED
**Final Deliverable:** Complete modern React implementation with production deployment strategy
**Ready for:** Production deployment and user acceptance testing

```

```
