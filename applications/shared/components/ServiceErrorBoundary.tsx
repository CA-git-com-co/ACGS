import React, { Component, ReactNode } from 'react';
import ErrorBoundary, { ErrorBoundaryProps } from './ErrorBoundary';

/**
 * Service-specific error types
 */
type ServiceType = 'AC' | 'GS' | 'PGC' | 'Auth' | 'Integrity' | 'FV' | 'EC';

/**
 * Service error boundary props
 */
interface ServiceErrorBoundaryProps extends Omit<ErrorBoundaryProps, 'fallback'> {
  children: ReactNode;
  serviceName: ServiceType;
  serviceUrl?: string;
  onServiceError?: (error: Error, serviceName: ServiceType) => void;
  retryAttempts?: number;
  className?: string;
}

/**
 * Service error fallback component props
 */
interface ServiceErrorFallbackProps {
  error?: Error;
  serviceName: ServiceType;
  serviceUrl?: string;
  onRetry: () => void;
  onCheckStatus: () => void;
  retryCount: number;
  maxRetries: number;
  className?: string;
}

/**
 * Service-specific error messages and descriptions
 */
const SERVICE_INFO: Record<ServiceType, { name: string; description: string; port: number }> = {
  AC: {
    name: 'Artificial Constitution Service',
    description: 'Manages constitutional principles and governance rules',
    port: 8001
  },
  GS: {
    name: 'Governance Synthesis Service',
    description: 'Synthesizes policies from constitutional principles',
    port: 8003
  },
  PGC: {
    name: 'Prompt Governance Compiler',
    description: 'Validates compliance against governance policies',
    port: 8005
  },
  Auth: {
    name: 'Authentication Service',
    description: 'Handles user authentication and authorization',
    port: 8002
  },
  Integrity: {
    name: 'Integrity Service',
    description: 'Monitors system integrity and security',
    port: 8006
  },
  FV: {
    name: 'Formal Verification Service',
    description: 'Provides formal verification of policies and rules',
    port: 8004
  },
  EC: {
    name: 'Event Coordination Service',
    description: 'Coordinates events across the ACGS ecosystem',
    port: 8007
  }
};

/**
 * Service error fallback component
 */
const ServiceErrorFallback: React.FC<ServiceErrorFallbackProps> = ({
  error,
  serviceName,
  serviceUrl,
  onRetry,
  onCheckStatus,
  retryCount,
  maxRetries,
  className = ''
}) => {
  const serviceInfo = SERVICE_INFO[serviceName];
  const isNetworkError =
    error?.message?.toLowerCase().includes('network') ||
    error?.message?.toLowerCase().includes('fetch') ||
    error?.message?.toLowerCase().includes('connection');

  const isServiceUnavailable =
    error?.message?.toLowerCase().includes('503') ||
    error?.message?.toLowerCase().includes('502') ||
    error?.message?.toLowerCase().includes('504');

  const getErrorType = () => {
    if (isNetworkError) return 'Network Error';
    if (isServiceUnavailable) return 'Service Unavailable';
    return 'Service Error';
  };

  const getErrorDescription = () => {
    if (isNetworkError) {
      return `Unable to connect to the ${serviceInfo.name}. Please check your network connection.`;
    }
    if (isServiceUnavailable) {
      return `The ${serviceInfo.name} is temporarily unavailable. It may be starting up or undergoing maintenance.`;
    }
    return `An error occurred while communicating with the ${serviceInfo.name}.`;
  };

  return (
    <div className={`bg-orange-50 border border-orange-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-orange-400" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-orange-800">
            {getErrorType()} - {serviceName} Service
          </h3>
          <div className="mt-2 text-sm text-orange-700">
            <p>{getErrorDescription()}</p>
            <div className="mt-2 text-xs text-orange-600">
              <p>
                <strong>Service:</strong> {serviceInfo.name}
              </p>
              <p>
                <strong>Description:</strong> {serviceInfo.description}
              </p>
              {serviceUrl && (
                <p>
                  <strong>URL:</strong> {serviceUrl}
                </p>
              )}
              <p>
                <strong>Expected Port:</strong> {serviceInfo.port}
              </p>
              {retryCount > 0 && (
                <p>
                  <strong>Retry Attempts:</strong> {retryCount}/{maxRetries}
                </p>
              )}
            </div>
          </div>

          <div className="mt-4 flex space-x-3">
            <button
              onClick={onRetry}
              disabled={retryCount >= maxRetries}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-orange-700 bg-orange-100 hover:bg-orange-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg className="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              {retryCount >= maxRetries ? 'Max Retries Reached' : 'Retry Connection'}
            </button>

            <button
              onClick={onCheckStatus}
              className="inline-flex items-center px-3 py-2 border border-orange-300 text-sm leading-4 font-medium rounded-md text-orange-700 bg-white hover:bg-orange-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
            >
              <svg className="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Check Service Status
            </button>
          </div>

          {/* Service health tips */}
          <div className="mt-4 p-3 bg-orange-100 rounded border">
            <h4 className="text-xs font-medium text-orange-800 mb-2">Troubleshooting Tips:</h4>
            <ul className="text-xs text-orange-700 space-y-1">
              <li>
                • Ensure the {serviceName} service is running on port {serviceInfo.port}
              </li>
              <li>
                • Check if the service URL is correct:{' '}
                {serviceUrl || `http://localhost:${serviceInfo.port}`}
              </li>
              <li>• Verify network connectivity and firewall settings</li>
              <li>• Check service logs for detailed error information</li>
              {isServiceUnavailable && (
                <li>• The service may be starting up - wait a few moments and retry</li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Service-specific error boundary component
 *
 * Features:
 * - Service-aware error handling for ACGS microservices
 * - Automatic retry mechanisms with configurable attempts
 * - Service health status checking
 * - Network and connectivity error detection
 * - Service-specific troubleshooting guidance
 * - Integration with service monitoring
 */
class ServiceErrorBoundary extends Component<ServiceErrorBoundaryProps, { retryCount: number }> {
  constructor(props: ServiceErrorBoundaryProps) {
    super(props);
    this.state = { retryCount: 0 };
  }

  handleRetry = () => {
    const { retryAttempts = 3 } = this.props;

    if (this.state.retryCount < retryAttempts) {
      this.setState(prevState => ({ retryCount: prevState.retryCount + 1 }));

      // Reset error boundary state after a brief delay
      setTimeout(() => {
        this.forceUpdate();
      }, 1000);
    }
  };

  handleCheckStatus = async () => {
    const { serviceName, serviceUrl } = this.props;
    const serviceInfo = SERVICE_INFO[serviceName];
    const url = serviceUrl || `http://localhost:${serviceInfo.port}`;

    try {
      // Attempt to check service health
      const healthUrl = `${url}/health`;
      const response = await fetch(healthUrl, {
        method: 'GET',
        timeout: 5000
      });

      if (response.ok) {
        alert(`${serviceInfo.name} is responding normally. You can try refreshing the page.`);
      } else {
        alert(
          `${serviceInfo.name} responded with status ${response.status}. The service may be experiencing issues.`
        );
      }
    } catch (error) {
      alert(
        `Unable to reach ${serviceInfo.name} at ${url}. Please check if the service is running.`
      );
    }
  };

  render() {
    const {
      children,
      serviceName,
      serviceUrl,
      onServiceError,
      retryAttempts = 3,
      onError,
      className,
      ...errorBoundaryProps
    } = this.props;
    const { retryCount } = this.state;

    const handleError = (error: Error, errorInfo: React.ErrorInfo) => {
      // Call service-specific error handler
      if (onServiceError) {
        onServiceError(error, serviceName);
      }

      // Call general error handler
      if (onError) {
        onError(error, errorInfo);
      }

      // Log service-specific error context
      console.error(`${serviceName} Service Error:`, {
        serviceName,
        serviceUrl,
        error: error.message,
        retryCount,
        maxRetries: retryAttempts
      });
    };

    const serviceErrorFallback = (
      <ServiceErrorFallback
        serviceName={serviceName}
        serviceUrl={serviceUrl}
        onRetry={this.handleRetry}
        onCheckStatus={this.handleCheckStatus}
        retryCount={retryCount}
        maxRetries={retryAttempts}
        className={className}
      />
    );

    return (
      <ErrorBoundary
        {...errorBoundaryProps}
        fallback={serviceErrorFallback}
        onError={handleError}
        componentName={`${serviceName}ServiceErrorBoundary`}
        className={className}
      >
        {children}
      </ErrorBoundary>
    );
  }
}

export default ServiceErrorBoundary;
export { ServiceErrorFallback, SERVICE_INFO };
export type { ServiceErrorBoundaryProps, ServiceErrorFallbackProps, ServiceType };
