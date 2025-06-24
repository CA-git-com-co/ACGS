// Shared components for ACGS-PGP Framework
export { default as PrincipleCard } from './PrincipleCard';
export { default as ProtectedRoute } from './ProtectedRoute';
export { default as ComplianceChecker } from './ComplianceChecker';
export { default as PolicyProposal } from './PolicyProposal';
export { default as PolicyCard } from './PolicyCard';
export { default as ValidatedForm } from './ValidatedForm';

// Error Boundary Components
export { default as ErrorBoundary, ErrorFallback } from './ErrorBoundary';
export {
  default as AuthErrorBoundary,
  withAuthErrorBoundary,
  AuthErrorFallback
} from './AuthErrorBoundary';
export {
  default as ServiceErrorBoundary,
  ServiceErrorFallback,
  SERVICE_INFO
} from './ServiceErrorBoundary';

// Loading State Components
export {
  Spinner,
  Skeleton,
  Progress,
  LoadingOverlay,
  CardSkeleton,
  TableSkeleton,
  FormSkeleton,
  LoadingButton,
  TimeoutLoader
} from './LoadingStates';

// Higher-Order Components
export * from './hoc';

// Domain-organized components
export * from './domains';

// UI Components
export { Button } from './ui/Button';
export { default as Card } from './ui/Card';
export { default as Input } from './ui/Input';

// Dashboard Components
export { default as DashboardCards } from './dashboard/DashboardCards';
export { default as QuantumagiDashboard } from './dashboard/QuantumagiDashboard';

// Layout Components
export { default as Layout } from './layout/Layout';
export { default as Header } from './layout/Header';
export { default as Footer } from './layout/Footer';
export { default as CommandBar } from './layout/CommandBar';
export { default as Sidebar } from './layout/Sidebar';
export { default as ThemeToggle } from './layout/ThemeToggle';

// Re-export types for convenience
export type {
  Principle,
  Policy,
  ComplianceResult,
  User,
  ActivePolicy,
  Amendment
} from '../types/governance';
