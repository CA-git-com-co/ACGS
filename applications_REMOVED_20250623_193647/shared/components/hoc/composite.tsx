import React from 'react';
import { withAuth, WithAuthOptions } from './withAuth';
import { withLoading, WithLoadingOptions } from './withLoading';
import { withErrorBoundary, WithErrorBoundaryOptions } from './withErrorBoundary';
import { ServiceType } from '../ServiceErrorBoundary';

/**
 * Composite HOC configuration for protected components
 */
interface ProtectedComponentOptions {
  auth?: WithAuthOptions;
  loading?: WithLoadingOptions;
  errorBoundary?: WithErrorBoundaryOptions;
}

/**
 * Composite HOC that combines auth, loading, and error boundary functionality
 *
 * @param WrappedComponent - Component to wrap
 * @param options - Configuration for each HOC layer
 * @returns Component with auth, loading, and error boundary protection
 *
 * @example
 * ```typescript
 * const ProtectedAdminPanel = withProtectedComponent(AdminPanel, {
 *   auth: { requiredRoles: 'admin' },
 *   loading: { useOverlay: true },
 *   errorBoundary: { boundaryType: 'service', serviceName: 'AC' }
 * });
 * ```
 */
export function withProtectedComponent<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: ProtectedComponentOptions = {}
) {
  const { auth = {}, loading = {}, errorBoundary = {} } = options;

  // Apply HOCs in order: ErrorBoundary -> Auth -> Loading -> Component
  let EnhancedComponent = WrappedComponent;

  // Apply loading HOC
  EnhancedComponent = withLoading(EnhancedComponent, loading);

  // Apply auth HOC
  EnhancedComponent = withAuth(EnhancedComponent, auth);

  // Apply error boundary HOC
  EnhancedComponent = withErrorBoundary(EnhancedComponent, errorBoundary);

  EnhancedComponent.displayName = `withProtectedComponent(${WrappedComponent.displayName || WrappedComponent.name})`;

  return EnhancedComponent;
}

/**
 * HOC for admin-only components with full protection
 */
export function withAdminProtection<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  serviceName?: ServiceType,
  serviceUrl?: string
) {
  return withProtectedComponent(WrappedComponent, {
    auth: { requiredRoles: 'admin' },
    loading: { useOverlay: true, blurContent: true },
    errorBoundary: {
      boundaryType: serviceName ? 'service' : 'auth',
      serviceName,
      serviceUrl
    }
  });
}

/**
 * HOC for moderator components with protection
 */
export function withModeratorProtection<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  serviceName?: ServiceType,
  serviceUrl?: string
) {
  return withProtectedComponent(WrappedComponent, {
    auth: { requiredRoles: ['admin', 'moderator'] },
    loading: { useOverlay: true },
    errorBoundary: {
      boundaryType: serviceName ? 'service' : 'auth',
      serviceName,
      serviceUrl
    }
  });
}

/**
 * HOC for service-specific components with full protection
 */
export function withServiceProtection<P extends object>(
  serviceName: ServiceType,
  serviceUrl?: string,
  requiredRoles?: string | string[]
) {
  return (WrappedComponent: React.ComponentType<P>) => {
    return withProtectedComponent(WrappedComponent, {
      auth: requiredRoles ? { requiredRoles } : {},
      loading: { useOverlay: true },
      errorBoundary: {
        boundaryType: 'service',
        serviceName,
        serviceUrl
      }
    });
  };
}

/**
 * HOC for data-heavy components with skeleton loading
 */
export function withDataProtection<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  skeletonCount: number = 3
) {
  return withProtectedComponent(WrappedComponent, {
    auth: {},
    loading: {
      loadingComponent: () => (
        <div className="space-y-4">
          {Array.from({ length: skeletonCount }).map((_, index) => (
            <div key={index} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      )
    },
    errorBoundary: { boundaryType: 'basic' }
  });
}

/**
 * HOC for form components with comprehensive protection
 */
export function withFormProtection<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  requiredPermissions?: string | string[]
) {
  return withProtectedComponent(WrappedComponent, {
    auth: requiredPermissions ? { requiredPermissions } : {},
    loading: {
      useOverlay: true,
      blurContent: true,
      loadingText: 'Processing form...'
    },
    errorBoundary: { boundaryType: 'basic' }
  });
}

// Service-specific composite HOCs
export const withACProtection = withServiceProtection(
  'AC',
  process.env.REACT_APP_AC_API_URL || 'http://localhost:8001/api/v1'
);

export const withGSProtection = withServiceProtection(
  'GS',
  process.env.REACT_APP_GS_API_URL || 'http://localhost:8003/api/v1'
);

export const withPGCProtection = withServiceProtection(
  'PGC',
  process.env.REACT_APP_PGC_API_URL || 'http://localhost:8005/api/v1'
);

export const withIntegrityProtection = withServiceProtection(
  'Integrity',
  process.env.REACT_APP_INTEGRITY_API_URL || 'http://localhost:8006/api/v1'
);

export const withFVProtection = withServiceProtection(
  'FV',
  process.env.REACT_APP_FV_API_URL || 'http://localhost:8004/api/v1'
);

export const withECProtection = withServiceProtection(
  'EC',
  process.env.REACT_APP_EC_API_URL || 'http://localhost:8007/api/v1'
);

/**
 * Utility function to create domain-specific protection HOCs
 */
export function createDomainProtection<P extends object>(domain: {
  serviceName: ServiceType;
  serviceUrl?: string;
  defaultRoles?: string | string[];
  defaultPermissions?: string | string[];
}) {
  return (WrappedComponent: React.ComponentType<P>, options: ProtectedComponentOptions = {}) => {
    const mergedOptions: ProtectedComponentOptions = {
      auth: {
        requiredRoles: domain.defaultRoles,
        requiredPermissions: domain.defaultPermissions,
        ...options.auth
      },
      loading: {
        useOverlay: true,
        ...options.loading
      },
      errorBoundary: {
        boundaryType: 'service',
        serviceName: domain.serviceName,
        serviceUrl: domain.serviceUrl,
        ...options.errorBoundary
      }
    };

    return withProtectedComponent(WrappedComponent, mergedOptions);
  };
}

// Domain-specific protection HOCs
export const withGovernanceProtection = createDomainProtection({
  serviceName: 'AC',
  serviceUrl: process.env.REACT_APP_AC_API_URL || 'http://localhost:8001/api/v1',
  defaultRoles: ['admin', 'moderator'],
  defaultPermissions: ['view_principles', 'create_principle']
});

export const withPolicyProtection = createDomainProtection({
  serviceName: 'GS',
  serviceUrl: process.env.REACT_APP_GS_API_URL || 'http://localhost:8003/api/v1',
  defaultRoles: ['admin', 'moderator'],
  defaultPermissions: ['view_policies', 'create_policy']
});

export const withComplianceProtection = createDomainProtection({
  serviceName: 'PGC',
  serviceUrl: process.env.REACT_APP_PGC_API_URL || 'http://localhost:8005/api/v1',
  defaultPermissions: ['check_compliance']
});

export const withAnalyticsProtection = createDomainProtection({
  serviceName: 'Integrity',
  serviceUrl: process.env.REACT_APP_INTEGRITY_API_URL || 'http://localhost:8006/api/v1',
  defaultRoles: ['admin', 'moderator'],
  defaultPermissions: ['view_analytics']
});

/**
 * HOC for public components that still need error boundaries
 */
export function withPublicProtection<P extends object>(WrappedComponent: React.ComponentType<P>) {
  return withProtectedComponent(WrappedComponent, {
    auth: { showLoadingDuringCheck: false },
    loading: { minLoadingTime: 200 },
    errorBoundary: { boundaryType: 'basic' }
  });
}

export default withProtectedComponent;
