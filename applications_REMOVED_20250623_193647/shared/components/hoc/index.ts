// Higher-Order Components for ACGS-PGP Framework
//
// This module exports reusable HOCs that provide common functionality
// across components following ACGS patterns and service architecture.

// Loading HOCs
export {
  default as withLoading,
  withCardLoading,
  withListLoading,
  withFormLoading,
  withDataLoading,
  withSpinnerLoading,
  withOverlayLoading,
  withMinimalLoading,
  createLoadingHOC
} from './withLoading';

// Authentication HOCs
export {
  default as withAuth,
  withAdminAuth,
  withModeratorAuth,
  withPermissionAuth,
  withBasicAuth,
  withQuietAuth,
  withRedirectAuth,
  createAuthHOC
} from './withAuth';

// Error Boundary HOCs
export {
  default as withErrorBoundary,
  withAuthErrorBoundary,
  withServiceErrorBoundary,
  withACErrorBoundary,
  withGSErrorBoundary,
  withPGCErrorBoundary,
  withAuthServiceErrorBoundary,
  withIntegrityErrorBoundary,
  withFVErrorBoundary,
  withECErrorBoundary,
  withMultipleErrorBoundaries,
  withAllServiceErrorBoundaries,
  createErrorBoundaryHOC
} from './withErrorBoundary';

// Composite HOCs for common patterns
export * from './composite';
