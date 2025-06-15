import React from 'react';
import ErrorBoundary from '../ErrorBoundary';
import AuthErrorBoundary from '../AuthErrorBoundary';
import ServiceErrorBoundary, { ServiceType } from '../ServiceErrorBoundary';

/**
 * Error boundary HOC configuration options
 */
interface WithErrorBoundaryOptions {
  /** Type of error boundary to use */
  boundaryType?: 'basic' | 'auth' | 'service';
  /** Service name for service error boundary */
  serviceName?: ServiceType;
  /** Service URL for service error boundary */
  serviceUrl?: string;
  /** Custom fallback component */
  fallback?: React.ReactNode;
  /** Custom error handler */
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  /** Whether to show detailed error information */
  showDetails?: boolean;
  /** Component name for error reporting */
  componentName?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Higher-order component that wraps components with error boundaries
 * 
 * @param WrappedComponent - Component to wrap with error boundary
 * @param options - Configuration options for error boundary behavior
 * @returns Component wrapped with appropriate error boundary
 * 
 * @example
 * ```typescript
 * // Basic error boundary
 * const SafeComponent = withErrorBoundary(MyComponent);
 * 
 * // Auth-aware error boundary
 * const AuthSafeComponent = withErrorBoundary(MyComponent, {
 *   boundaryType: 'auth'
 * });
 * 
 * // Service-specific error boundary
 * const ServiceSafeComponent = withErrorBoundary(MyComponent, {
 *   boundaryType: 'service',
 *   serviceName: 'AC',
 *   serviceUrl: 'http://localhost:8001/api/v1'
 * });
 * ```
 */
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: WithErrorBoundaryOptions = {}
) {
  const {
    boundaryType = 'basic',
    serviceName,
    serviceUrl,
    fallback,
    onError,
    showDetails = true,
    componentName,
    className
  } = options;

  const WithErrorBoundaryComponent: React.FC<P> = (props) => {
    const wrappedComponentName = componentName || 
      WrappedComponent.displayName || 
      WrappedComponent.name || 
      'Component';

    const errorHandler = (error: Error, errorInfo: React.ErrorInfo) => {
      // Log error with component context
      console.error(`Error in ${wrappedComponentName}:`, error, errorInfo);
      
      // Call custom error handler if provided
      if (onError) {
        onError(error, errorInfo);
      }
    };

    // Service error boundary
    if (boundaryType === 'service' && serviceName) {
      return (
        <ServiceErrorBoundary
          serviceName={serviceName}
          serviceUrl={serviceUrl}
          onError={errorHandler}
          className={className}
        >
          <WrappedComponent {...props} />
        </ServiceErrorBoundary>
      );
    }

    // Auth error boundary
    if (boundaryType === 'auth') {
      return (
        <AuthErrorBoundary
          onError={errorHandler}
          className={className}
        >
          <WrappedComponent {...props} />
        </AuthErrorBoundary>
      );
    }

    // Basic error boundary
    return (
      <ErrorBoundary
        fallback={fallback}
        onError={errorHandler}
        showDetails={showDetails}
        componentName={wrappedComponentName}
        className={className}
      >
        <WrappedComponent {...props} />
      </ErrorBoundary>
    );
  };

  WithErrorBoundaryComponent.displayName = `withErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name})`;

  return WithErrorBoundaryComponent;
}

/**
 * HOC for auth-aware error boundaries
 */
export function withAuthErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: Omit<WithErrorBoundaryOptions, 'boundaryType'> = {}
) {
  return withErrorBoundary(WrappedComponent, {
    ...options,
    boundaryType: 'auth'
  });
}

/**
 * HOC for service-specific error boundaries
 */
export function withServiceErrorBoundary<P extends object>(
  serviceName: ServiceType,
  serviceUrl?: string
) {
  return (
    WrappedComponent: React.ComponentType<P>,
    options: Omit<WithErrorBoundaryOptions, 'boundaryType' | 'serviceName' | 'serviceUrl'> = {}
  ) => {
    return withErrorBoundary(WrappedComponent, {
      ...options,
      boundaryType: 'service',
      serviceName,
      serviceUrl
    });
  };
}

/**
 * Utility function to create custom error boundary HOCs
 */
export function createErrorBoundaryHOC<P extends object>(
  defaultOptions: WithErrorBoundaryOptions
) {
  return (WrappedComponent: React.ComponentType<P>, options: WithErrorBoundaryOptions = {}) => {
    return withErrorBoundary(WrappedComponent, { ...defaultOptions, ...options });
  };
}

// Export service-specific error boundary HOCs
export const withACErrorBoundary = withServiceErrorBoundary(
  'AC',
  process.env.REACT_APP_AC_API_URL || 'http://localhost:8001/api/v1'
);

export const withGSErrorBoundary = withServiceErrorBoundary(
  'GS',
  process.env.REACT_APP_GS_API_URL || 'http://localhost:8003/api/v1'
);

export const withPGCErrorBoundary = withServiceErrorBoundary(
  'PGC',
  process.env.REACT_APP_PGC_API_URL || 'http://localhost:8005/api/v1'
);

export const withAuthServiceErrorBoundary = withServiceErrorBoundary(
  'Auth',
  process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8002/auth'
);

export const withIntegrityErrorBoundary = withServiceErrorBoundary(
  'Integrity',
  process.env.REACT_APP_INTEGRITY_API_URL || 'http://localhost:8006/api/v1'
);

export const withFVErrorBoundary = withServiceErrorBoundary(
  'FV',
  process.env.REACT_APP_FV_API_URL || 'http://localhost:8004/api/v1'
);

export const withECErrorBoundary = withServiceErrorBoundary(
  'EC',
  process.env.REACT_APP_EC_API_URL || 'http://localhost:8007/api/v1'
);

/**
 * Composite HOC that combines multiple error boundaries
 */
export function withMultipleErrorBoundaries<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  boundaries: Array<{
    type: 'basic' | 'auth' | 'service';
    serviceName?: ServiceType;
    serviceUrl?: string;
    options?: WithErrorBoundaryOptions;
  }>
) {
  return boundaries.reduce((Component, boundary) => {
    const { type, serviceName, serviceUrl, options = {} } = boundary;
    
    return withErrorBoundary(Component, {
      ...options,
      boundaryType: type,
      serviceName,
      serviceUrl
    });
  }, WrappedComponent);
}

/**
 * HOC that wraps component with all ACGS service error boundaries
 */
export function withAllServiceErrorBoundaries<P extends object>(
  WrappedComponent: React.ComponentType<P>
) {
  return withMultipleErrorBoundaries(WrappedComponent, [
    { type: 'auth' },
    { type: 'service', serviceName: 'AC' },
    { type: 'service', serviceName: 'GS' },
    { type: 'service', serviceName: 'PGC' },
    { type: 'service', serviceName: 'Integrity' },
    { type: 'service', serviceName: 'FV' },
    { type: 'service', serviceName: 'EC' }
  ]);
}

export default withErrorBoundary;
