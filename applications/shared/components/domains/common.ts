// Common Domain Components
//
// Shared components that are used across multiple domains
// and don't belong to a specific service.

// Form components
export { default as ValidatedForm } from '../ValidatedForm';

// Loading components
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
} from '../LoadingStates';

// Error boundary components
export { default as ErrorBoundary, ErrorFallback } from '../ErrorBoundary';
export { default as AuthErrorBoundary, AuthErrorFallback } from '../AuthErrorBoundary';
export { default as ServiceErrorBoundary, ServiceErrorFallback } from '../ServiceErrorBoundary';

// Navigation and routing
export { default as ProtectedRoute } from '../ProtectedRoute';

// Higher-order components
export * from '../hoc';

// Common hooks
export {
  useLoadingState,
  useAsyncOperation,
  useMultipleLoadingStates,
  useDebouncedLoading
} from '../../hooks/useLoadingState';

export {
  useAuthExtended,
  useRoleAccess,
  useProtectedAction
} from '../../hooks/useAuthExtended';

export {
  useApiExtended,
  useServiceApi
} from '../../hooks/useApiExtended';

// Validation utilities
export * from '../../utils/propValidation';
export * from '../../types/validation';
