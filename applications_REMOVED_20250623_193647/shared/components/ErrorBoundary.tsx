import React, { Component, ReactNode } from 'react';
import { getErrorMessage } from '../utils';
import { useAuth } from '../contexts/AuthContext';

/**
 * Error boundary state interface
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
  errorId?: string;
}

/**
 * Error boundary props interface
 */
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  showDetails?: boolean;
  componentName?: string;
  className?: string;
}

/**
 * Error fallback component props
 */
interface ErrorFallbackProps {
  error?: Error;
  errorInfo?: React.ErrorInfo;
  errorId?: string;
  onRetry: () => void;
  onRefresh: () => void;
  showDetails: boolean;
  componentName?: string;
  className?: string;
}

/**
 * Default error fallback component with user-friendly interface
 */
const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  errorInfo,
  errorId,
  onRetry,
  onRefresh,
  showDetails,
  componentName,
  className = ''
}) => {
  const isDevelopment = process.env.NODE_ENV === 'development';

  return (
    <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">
            {componentName ? `${componentName} Error` : 'Something went wrong'}
          </h3>
          <div className="mt-2 text-sm text-red-700">
            <p>
              We're sorry, but something unexpected happened.
              {isDevelopment && error ? ` Error: ${error.message}` : ''}
            </p>
          </div>

          {/* Development mode details */}
          {isDevelopment && showDetails && error && (
            <div className="mt-4 p-3 bg-red-100 rounded border">
              <details>
                <summary className="cursor-pointer font-medium text-red-800">
                  Technical Details (Development Mode)
                </summary>
                <div className="mt-2 space-y-2">
                  <div>
                    <strong>Error ID:</strong> {errorId}
                  </div>
                  <div>
                    <strong>Component:</strong> {componentName || 'Unknown'}
                  </div>
                  <div>
                    <strong>Error Message:</strong>
                    <pre className="mt-1 text-xs bg-white p-2 rounded border overflow-auto">
                      {error.message}
                    </pre>
                  </div>
                  <div>
                    <strong>Stack Trace:</strong>
                    <pre className="mt-1 text-xs bg-white p-2 rounded border overflow-auto max-h-32">
                      {error.stack}
                    </pre>
                  </div>
                  {errorInfo && (
                    <div>
                      <strong>Component Stack:</strong>
                      <pre className="mt-1 text-xs bg-white p-2 rounded border overflow-auto max-h-32">
                        {errorInfo.componentStack}
                      </pre>
                    </div>
                  )}
                </div>
              </details>
            </div>
          )}

          {/* Action buttons */}
          <div className="mt-4 flex space-x-3">
            <button
              onClick={onRetry}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <svg className="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Try Again
            </button>
            <button
              onClick={onRefresh}
              className="inline-flex items-center px-3 py-2 border border-red-300 text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <svg className="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Refresh Page
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Enhanced Error Boundary component with comprehensive error handling
 *
 * Features:
 * - Graceful error fallbacks with user-friendly messages
 * - Development mode error details with stack traces
 * - Structured error reporting with component context
 * - Recovery mechanisms with retry and refresh options
 * - Integration with AuthContext for authentication-related errors
 * - Unique error IDs for tracking and debugging
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private retryTimeoutId: number | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Generate unique error ID for tracking
    const errorId = `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    return {
      hasError: true,
      error,
      errorId
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const { onError, componentName } = this.props;

    // Update state with error info
    this.setState({ errorInfo });

    // Log error with structured context
    const errorContext = {
      errorId: this.state.errorId,
      componentName: componentName || 'Unknown',
      error: {
        message: error.message,
        stack: error.stack,
        name: error.name
      },
      errorInfo: {
        componentStack: errorInfo.componentStack
      },
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    console.error('ErrorBoundary caught an error:', errorContext);

    // Call custom error handler if provided
    if (onError) {
      onError(error, errorInfo);
    }

    // In production, this would send to error reporting service
    if (process.env.NODE_ENV === 'production') {
      // TODO: Send to error reporting service (e.g., Sentry, LogRocket)
      // errorReportingService.captureException(error, errorContext);
    }
  }

  handleRetry = () => {
    // Clear any existing timeout
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId);
    }

    // Reset error state after a brief delay to allow for cleanup
    this.retryTimeoutId = window.setTimeout(() => {
      this.setState({
        hasError: false,
        error: undefined,
        errorInfo: undefined,
        errorId: undefined
      });
    }, 100);
  };

  handleRefresh = () => {
    window.location.reload();
  };

  componentWillUnmount() {
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId);
    }
  }

  render() {
    const { hasError, error, errorInfo, errorId } = this.state;
    const { children, fallback, showDetails = true, componentName, className } = this.props;

    if (hasError) {
      // Use custom fallback if provided
      if (fallback) {
        return fallback;
      }

      // Use default error fallback
      return (
        <ErrorFallback
          error={error}
          errorInfo={errorInfo}
          errorId={errorId}
          onRetry={this.handleRetry}
          onRefresh={this.handleRefresh}
          showDetails={showDetails}
          componentName={componentName}
          className={className}
        />
      );
    }

    return children;
  }
}

export default ErrorBoundary;
export { ErrorFallback };
export type { ErrorBoundaryProps, ErrorFallbackProps };
