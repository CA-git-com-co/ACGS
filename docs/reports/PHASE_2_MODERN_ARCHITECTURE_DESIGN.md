# 🏗️ Phase 2: Modern Architecture Design

**Date:** 2025-06-21  
**Scope:** ACGS Unified Frontend Architecture  
**Status:** 🔄 IN PROGRESS

## 🎯 Executive Summary

This phase defines the modern technical architecture for the consolidated ACGS governance platform, leveraging Next.js 14+ with App Router, the existing shared component library, and validated backend services.

## 🏛️ Next.js 14+ Architecture Design

### Application Structure

```
acgs-unified-frontend/
├── app/                          # Next.js 14 App Router
│   ├── (auth)/                   # Authentication route group
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── layout.tsx            # Auth-specific layout
│   │
│   ├── (dashboard)/              # Main application route group
│   │   ├── dashboard/
│   │   │   └── page.tsx          # Main dashboard
│   │   ├── governance/
│   │   │   ├── policies/
│   │   │   │   ├── page.tsx      # Policy list
│   │   │   │   ├── [id]/
│   │   │   │   │   └── page.tsx  # Policy details
│   │   │   │   └── new/
│   │   │   │       └── page.tsx  # Create policy
│   │   │   ├── amendments/
│   │   │   │   ├── page.tsx      # Amendment list
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx  # Amendment workflow
│   │   │   └── compliance/
│   │   │       └── page.tsx      # Compliance monitoring
│   │   │
│   │   ├── constitutional/
│   │   │   ├── council/
│   │   │   │   └── page.tsx      # Council dashboard
│   │   │   ├── principles/
│   │   │   │   └── page.tsx      # AC management
│   │   │   └── monitoring/
│   │   │       └── page.tsx      # Fidelity monitoring
│   │   │
│   │   ├── public/
│   │   │   ├── consultation/
│   │   │   │   ├── page.tsx      # Public consultation
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx  # Consultation details
│   │   │   └── transparency/
│   │   │       └── page.tsx      # Transparency dashboard
│   │   │
│   │   └── layout.tsx            # Main application layout
│   │
│   ├── api/                      # API routes for server-side logic
│   │   ├── auth/
│   │   │   └── route.ts          # Authentication endpoints
│   │   ├── policies/
│   │   │   └── route.ts          # Policy API proxy
│   │   └── compliance/
│   │       └── route.ts          # Compliance API proxy
│   │
│   ├── globals.css               # Global styles
│   ├── layout.tsx                # Root layout
│   ├── loading.tsx               # Global loading UI
│   ├── error.tsx                 # Global error UI
│   └── not-found.tsx             # 404 page
│
├── components/                   # Application-specific components
│   ├── governance/
│   │   ├── PolicyEditor.tsx
│   │   ├── AmendmentWorkflow.tsx
│   │   └── ComplianceMonitor.tsx
│   ├── constitutional/
│   │   ├── CouncilDashboard.tsx
│   │   ├── PrincipleManager.tsx
│   │   └── FidelityMonitor.tsx
│   ├── public/
│   │   ├── ConsultationForm.tsx
│   │   └── TransparencyView.tsx
│   └── layout/
│       ├── Navigation.tsx
│       ├── Sidebar.tsx
│       └── Header.tsx
│
├── lib/                          # Utility libraries
│   ├── api/                      # API client libraries
│   │   ├── constitutional-ai.ts
│   │   ├── governance-synthesis.ts
│   │   ├── policy-governance.ts
│   │   └── auth.ts
│   ├── hooks/                    # Custom React hooks
│   │   ├── useGovernance.ts
│   │   ├── useCompliance.ts
│   │   └── useRealtime.ts
│   ├── utils/
│   │   ├── validation.ts
│   │   ├── formatting.ts
│   │   └── constants.ts
│   └── types/
│       ├── governance.ts
│       ├── api.ts
│       └── user.ts
│
├── providers/                    # React context providers
│   ├── AuthProvider.tsx
│   ├── ThemeProvider.tsx
│   ├── QueryProvider.tsx
│   └── RealtimeProvider.tsx
│
├── middleware.ts                 # Next.js middleware for auth/routing
├── next.config.js                # Next.js configuration
├── tailwind.config.js            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
└── package.json                  # Dependencies and scripts
```

### App Router Benefits

#### Server Components by Default

```typescript
// Server Component for initial data loading
export default async function PoliciesPage() {
  // Fetch data on the server
  const policies = await getPolicies();
  const complianceStatus = await getComplianceStatus();

  return (
    <div>
      <PolicyList policies={policies} />
      <ComplianceOverview status={complianceStatus} />
    </div>
  );
}
```

#### Streaming and Suspense

```typescript
// Streaming UI with Suspense boundaries
export default function GovernancePage() {
  return (
    <div>
      <Suspense fallback={<PolicyListSkeleton />}>
        <PolicyList />
      </Suspense>

      <Suspense fallback={<ComplianceMonitorSkeleton />}>
        <ComplianceMonitor />
      </Suspense>
    </div>
  );
}
```

#### Route Groups for Organization

```typescript
// (dashboard) route group layout
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard-layout">
      <Sidebar />
      <main className="main-content">
        <Header />
        {children}
      </main>
    </div>
  );
}
```

## 🧩 Component Strategy

### Extending Shared Component Library

#### Current Shared Components (Leverage)

```typescript
// From applications/shared/
import {
  AuthProvider, // ✅ Use as-is
  ProtectedRoute, // ✅ Adapt for App Router
  ComplianceChecker, // ✅ Enhance with real-time updates
  PolicyCard, // ✅ Extend with new features
  LoadingStates, // ✅ Use for Suspense fallbacks
  ErrorBoundary, // ✅ Integrate with Next.js error handling
} from '@acgs/shared';
```

#### New Components to Build

```typescript
// Governance-specific components
export interface GovernanceComponents {
  // Policy Management
  PolicyEditor: React.ComponentType<PolicyEditorProps>;
  PolicyWorkflow: React.ComponentType<PolicyWorkflowProps>;
  PolicyAnalytics: React.ComponentType<PolicyAnalyticsProps>;

  // Constitutional Management
  AmendmentWorkflow: React.ComponentType<AmendmentWorkflowProps>;
  ConstitutionalMonitor: React.ComponentType<ConstitutionalMonitorProps>;
  CouncilDashboard: React.ComponentType<CouncilDashboardProps>;

  // Public Engagement
  PublicConsultation: React.ComponentType<PublicConsultationProps>;
  CitizenFeedback: React.ComponentType<CitizenFeedbackProps>;
  TransparencyDashboard: React.ComponentType<TransparencyDashboardProps>;

  // Real-time Features
  RealtimeUpdates: React.ComponentType<RealtimeUpdatesProps>;
  NotificationCenter: React.ComponentType<NotificationCenterProps>;
  LiveComplianceMonitor: React.ComponentType<LiveComplianceMonitorProps>;
}
```

#### Component Architecture Pattern

```typescript
// Compound component pattern for complex governance workflows
export const AmendmentWorkflow = {
  Root: AmendmentWorkflowRoot,
  Header: AmendmentWorkflowHeader,
  Stages: AmendmentWorkflowStages,
  Stage: AmendmentWorkflowStage,
  Actions: AmendmentWorkflowActions,
  Progress: AmendmentWorkflowProgress,
  Voting: AmendmentWorkflowVoting,
  Documents: AmendmentWorkflowDocuments,
};

// Usage
<AmendmentWorkflow.Root amendmentId="123">
  <AmendmentWorkflow.Header />
  <AmendmentWorkflow.Progress />
  <AmendmentWorkflow.Stages>
    <AmendmentWorkflow.Stage stage="review" />
    <AmendmentWorkflow.Stage stage="voting" />
  </AmendmentWorkflow.Stages>
  <AmendmentWorkflow.Actions />
</AmendmentWorkflow.Root>
```

## 🔄 State Management Architecture

### React Query + Context Pattern

#### Global State Structure

```typescript
// Global state management with React Query and Context
interface AppState {
  // Authentication state (Context)
  auth: {
    user: User | null;
    permissions: Permission[];
    isLoading: boolean;
  };

  // Theme and UI state (Context)
  ui: {
    theme: 'light' | 'dark';
    sidebar: 'open' | 'closed';
    notifications: Notification[];
  };

  // Server state (React Query)
  // Policies, amendments, compliance data managed by React Query
}
```

#### React Query Configuration

```typescript
// lib/query-client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error) => {
        // Custom retry logic for governance APIs
        if (error.status === 401) return false;
        return failureCount < 3;
      },
    },
    mutations: {
      onError: (error) => {
        // Global error handling for mutations
        console.error('Mutation error:', error);
      },
    },
  },
});
```

#### Custom Hooks for Governance Data

```typescript
// lib/hooks/useGovernance.ts
export function usePolicies(filters?: PolicyFilters) {
  return useQuery({
    queryKey: ['policies', filters],
    queryFn: () => policyService.getPolicies(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes for policy data
  });
}

export function useCompliance(policyId: string) {
  return useQuery({
    queryKey: ['compliance', policyId],
    queryFn: () => complianceService.getCompliance(policyId),
    refetchInterval: 30 * 1000, // Real-time updates every 30 seconds
  });
}

export function useAmendmentWorkflow(amendmentId: string) {
  return useQuery({
    queryKey: ['amendment', amendmentId],
    queryFn: () => amendmentService.getAmendment(amendmentId),
    staleTime: 1 * 60 * 1000, // 1 minute for amendment data
  });
}
```

#### Optimistic Updates for Governance Actions

```typescript
// lib/hooks/useGovernanceMutations.ts
export function useVoteOnAmendment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (vote: Vote) => amendmentService.submitVote(vote),
    onMutate: async (vote) => {
      // Optimistic update
      await queryClient.cancelQueries(['amendment', vote.amendmentId]);

      const previousAmendment = queryClient.getQueryData(['amendment', vote.amendmentId]);

      queryClient.setQueryData(['amendment', vote.amendmentId], (old: Amendment) => ({
        ...old,
        votes: [...old.votes, vote],
        status: calculateNewStatus(old, vote),
      }));

      return { previousAmendment };
    },
    onError: (err, vote, context) => {
      // Rollback on error
      queryClient.setQueryData(['amendment', vote.amendmentId], context?.previousAmendment);
    },
    onSettled: (data, error, vote) => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries(['amendment', vote.amendmentId]);
    },
  });
}
```

## 🔌 API Integration Strategy

### Typed Service Clients

#### Constitutional AI Service Client

```typescript
// lib/api/constitutional-ai.ts
export class ConstitutionalAIClient {
  private baseURL = process.env.NEXT_PUBLIC_AC_SERVICE_URL;

  async analyzeCompliance(content: string): Promise<ComplianceAnalysis> {
    const response = await fetch(`${this.baseURL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });

    if (!response.ok) {
      throw new APIError('Failed to analyze compliance', response.status);
    }

    return response.json();
  }

  async validateAmendment(amendment: Amendment): Promise<ValidationResult> {
    const response = await fetch(`${this.baseURL}/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amendment }),
    });

    return response.json();
  }

  subscribeToViolations(callback: (violation: Violation) => void): () => void {
    const eventSource = new EventSource(`${this.baseURL}/violations/stream`);

    eventSource.onmessage = (event) => {
      const violation = JSON.parse(event.data);
      callback(violation);
    };

    return () => eventSource.close();
  }
}
```

#### Governance Synthesis Service Client

```typescript
// lib/api/governance-synthesis.ts
export class GovernanceSynthesisClient {
  private baseURL = process.env.NEXT_PUBLIC_GS_SERVICE_URL;

  async synthesizePolicy(requirements: PolicyRequirements): Promise<PolicyDraft> {
    const response = await fetch(`${this.baseURL}/synthesize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ requirements }),
    });

    return response.json();
  }

  async analyzeImpact(policy: Policy): Promise<ImpactAnalysis> {
    const response = await fetch(`${this.baseURL}/impact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ policy }),
    });

    return response.json();
  }

  async getRecommendations(context: PolicyContext): Promise<Recommendation[]> {
    const response = await fetch(`${this.baseURL}/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ context }),
    });

    return response.json();
  }
}
```

### API Error Handling Strategy

```typescript
// lib/api/error-handling.ts
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export async function handleAPIResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.message || 'API request failed',
      response.status,
      errorData.code
    );
  }

  return response.json();
}

// Global error boundary for API errors
export function APIErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary
      fallback={({ error, resetError }) => (
        <div className="error-container">
          <h2>Something went wrong</h2>
          {error instanceof APIError && (
            <p>API Error ({error.status}): {error.message}</p>
          )}
          <button onClick={resetError}>Try again</button>
        </div>
      )}
    >
      {children}
    </ErrorBoundary>
  );
}
```

## 🔐 Authentication Architecture

### NextAuth.js Integration

```typescript
// lib/auth/config.ts
import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

export const authConfig = {
  providers: [
    CredentialsProvider({
      name: 'ACGS Credentials',
      credentials: {
        username: { label: 'Username', type: 'text' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        // Integrate with existing AuthService
        const user = await authService.login(credentials);
        return user ? { id: user.id, ...user } : null;
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.permissions = user.permissions;
        token.role = user.role;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.permissions = token.permissions;
      session.user.role = token.role;
      return session;
    },
  },
  pages: {
    signIn: '/login',
    signOut: '/logout',
  },
};
```

### Role-Based Access Control

```typescript
// lib/auth/permissions.ts
export enum Permission {
  READ_POLICIES = 'read:policies',
  WRITE_POLICIES = 'write:policies',
  VOTE_AMENDMENTS = 'vote:amendments',
  MANAGE_COUNCIL = 'manage:council',
  VIEW_COMPLIANCE = 'view:compliance',
  ADMIN_SYSTEM = 'admin:system',
}

export function hasPermission(user: User, permission: Permission): boolean {
  return user.permissions.includes(permission);
}

// HOC for permission-based component rendering
export function withPermission<P extends object>(
  Component: React.ComponentType<P>,
  requiredPermission: Permission
) {
  return function PermissionWrapper(props: P) {
    const { data: session } = useSession();

    if (!session?.user || !hasPermission(session.user, requiredPermission)) {
      return <UnauthorizedMessage />;
    }

    return <Component {...props} />;
  };
}
```

## ⚡ Performance Strategy

### Code Splitting Strategy

```typescript
// Dynamic imports for route-based code splitting
const PolicyEditor = dynamic(() => import('@/components/governance/PolicyEditor'), {
  loading: () => <PolicyEditorSkeleton />,
  ssr: false, // Client-side only for complex editor
});

const AmendmentWorkflow = dynamic(() => import('@/components/constitutional/AmendmentWorkflow'), {
  loading: () => <WorkflowSkeleton />,
});

// Component-level code splitting
const ComplianceMonitor = dynamic(() => import('@/components/governance/ComplianceMonitor'), {
  loading: () => <MonitorSkeleton />,
  ssr: true, // Server-side rendering for SEO
});
```

### Caching Strategy

```typescript
// Next.js App Router caching configuration
export const revalidate = 300; // Revalidate every 5 minutes

// API route caching
export async function GET() {
  const policies = await getPolicies();

  return NextResponse.json(policies, {
    headers: {
      'Cache-Control': 'public, s-maxage=300, stale-while-revalidate=600',
    },
  });
}

// React Query caching for client-side data
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});
```

### Bundle Optimization

```typescript
// next.config.js
module.exports = {
  experimental: {
    optimizePackageImports: ['@acgs/shared'],
  },
  webpack: (config) => {
    // Optimize shared component library imports
    config.resolve.alias['@acgs/shared'] = path.resolve(__dirname, '../shared');
    return config;
  },
};
```

### Real-time Features Architecture

```typescript
// lib/realtime/websocket-client.ts
export class RealtimeClient {
  private ws: WebSocket | null = null;
  private subscribers = new Map<string, Set<(data: any) => void>>();

  connect() {
    this.ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL);

    this.ws.onmessage = (event) => {
      const { type, data } = JSON.parse(event.data);
      const callbacks = this.subscribers.get(type);
      callbacks?.forEach((callback) => callback(data));
    };
  }

  subscribe(eventType: string, callback: (data: any) => void) {
    if (!this.subscribers.has(eventType)) {
      this.subscribers.set(eventType, new Set());
    }
    this.subscribers.get(eventType)!.add(callback);

    return () => {
      this.subscribers.get(eventType)?.delete(callback);
    };
  }
}

// Custom hook for real-time compliance monitoring
export function useRealtimeCompliance(policyId: string) {
  const [complianceData, setComplianceData] = useState<ComplianceData | null>(null);

  useEffect(() => {
    const unsubscribe = realtimeClient.subscribe(`compliance:${policyId}`, setComplianceData);

    return unsubscribe;
  }, [policyId]);

  return complianceData;
}
```

## 📋 Next Steps for Phase 3

1. **Implementation Blueprint** - Detailed file structure and component specifications
2. **Migration Strategy** - Step-by-step plan for consolidating existing applications
3. **Testing Strategy** - Comprehensive testing approach for governance workflows
4. **Deployment Plan** - Production deployment strategy with rollback procedures

---

**Phase 2 Status:** ✅ COMPLETED
**Next Phase:** Implementation Blueprint
**Key Deliverable:** Complete technical architecture for consolidated governance platform
