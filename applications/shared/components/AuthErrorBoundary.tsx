import React, { Component, ReactNode } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ErrorBoundary, { ErrorBoundaryProps } from './ErrorBoundary';

/**
 * Authentication-specific error boundary props
 */
interface AuthErrorBoundaryProps extends Omit<ErrorBoundaryProps, 'fallback'> {
  children: ReactNode;
  onAuthError?: (error: Error) => void;
  redirectToLogin?: boolean;
  className?: string;
}

/**
 * Authentication error fallback component
 */
interface AuthErrorFallbackProps {
  error?: Error;
  onRetry: () => void;
  onLogin: () => void;
  isAuthenticated: boolean;
  className?: string;
}

const AuthErrorFallback: React.FC<AuthErrorFallbackProps> = ({
  error,
  onRetry,
  onLogin,
  isAuthenticated,
  className = ''
}) => {
  const isAuthError =
    error?.message?.toLowerCase().includes('auth') ||
    error?.message?.toLowerCase().includes('unauthorized') ||
    error?.message?.toLowerCase().includes('token');

  return (
    <div className={`bg-yellow-50 border border-yellow-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-yellow-800">
            {isAuthError ? 'Authentication Error' : 'Component Error'}
          </h3>
          <div className="mt-2 text-sm text-yellow-700">
            {isAuthError ? (
              <p>
                There was an issue with your authentication. This might be due to an expired session
                or insufficient permissions.
              </p>
            ) : (
              <p>
                A component error occurred. This might be related to your current authentication
                state.
              </p>
            )}
          </div>

          <div className="mt-4 flex space-x-3">
            <button
              onClick={onRetry}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-yellow-700 bg-yellow-100 hover:bg-yellow-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
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

            {(isAuthError || !isAuthenticated) && (
              <button
                onClick={onLogin}
                className="inline-flex items-center px-3 py-2 border border-yellow-300 text-sm leading-4 font-medium rounded-md text-yellow-700 bg-white hover:bg-yellow-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
              >
                <svg className="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
                  />
                </svg>
                {isAuthenticated ? 'Refresh Login' : 'Login'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Higher-order component that wraps ErrorBoundary with authentication context
 */
const withAuthErrorBoundary = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: Partial<AuthErrorBoundaryProps> = {}
) => {
  const AuthErrorBoundaryWrapper: React.FC<P> = props => {
    return (
      <AuthErrorBoundary {...options}>
        <WrappedComponent {...props} />
      </AuthErrorBoundary>
    );
  };

  AuthErrorBoundaryWrapper.displayName = `withAuthErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name})`;

  return AuthErrorBoundaryWrapper;
};

/**
 * Authentication-aware error boundary component
 *
 * Features:
 * - Detects authentication-related errors
 * - Provides login/refresh options for auth errors
 * - Integrates with AuthContext for state management
 * - Handles token expiration and unauthorized access
 * - Supports automatic redirect to login page
 */
const AuthErrorBoundary: React.FC<AuthErrorBoundaryProps> = ({
  children,
  onAuthError,
  redirectToLogin = false,
  onError,
  className,
  ...errorBoundaryProps
}) => {
  // This component needs to be wrapped with AuthContext to access auth state
  // We'll create a wrapper component that has access to the auth context
  const AuthErrorBoundaryInner: React.FC<{ authContext: any }> = ({ authContext }) => {
    const { isAuthenticated, login, logout } = authContext;

    const handleError = (error: Error, errorInfo: React.ErrorInfo) => {
      // Check if this is an authentication-related error
      const isAuthError =
        error.message?.toLowerCase().includes('auth') ||
        error.message?.toLowerCase().includes('unauthorized') ||
        error.message?.toLowerCase().includes('token') ||
        error.message?.toLowerCase().includes('403') ||
        error.message?.toLowerCase().includes('401');

      if (isAuthError) {
        console.warn('Authentication error detected:', error.message);

        // Call custom auth error handler
        if (onAuthError) {
          onAuthError(error);
        }

        // Optionally redirect to login
        if (redirectToLogin && !isAuthenticated) {
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
        }
      }

      // Call the general error handler
      if (onError) {
        onError(error, errorInfo);
      }
    };

    const handleLogin = async () => {
      try {
        // If already authenticated, try to refresh the token
        if (isAuthenticated) {
          await authContext.refreshToken();
        } else {
          // Redirect to login page
          window.location.href = '/login';
        }
      } catch (error) {
        console.error('Login/refresh failed:', error);
        // Force logout and redirect
        await logout();
        window.location.href = '/login';
      }
    };

    const authErrorFallback = (
      <AuthErrorFallback
        onRetry={() => window.location.reload()}
        onLogin={handleLogin}
        isAuthenticated={isAuthenticated}
        className={className}
      />
    );

    return (
      <ErrorBoundary
        {...errorBoundaryProps}
        fallback={authErrorFallback}
        onError={handleError}
        componentName="AuthErrorBoundary"
        className={className}
      >
        {children}
      </ErrorBoundary>
    );
  };

  // Wrapper component that provides auth context
  const AuthContextWrapper: React.FC = () => {
    // We need to use a hook to access the auth context
    // This will be handled by the consumer of this component
    try {
      const authContext = useAuth();
      return <AuthErrorBoundaryInner authContext={authContext} />;
    } catch (error) {
      // If AuthContext is not available, fall back to regular ErrorBoundary
      console.warn('AuthContext not available, falling back to regular ErrorBoundary');
      return (
        <ErrorBoundary
          {...errorBoundaryProps}
          onError={onError}
          componentName="AuthErrorBoundary (No Auth Context)"
          className={className}
        >
          {children}
        </ErrorBoundary>
      );
    }
  };

  return <AuthContextWrapper />;
};

export default AuthErrorBoundary;
export { withAuthErrorBoundary, AuthErrorFallback };
export type { AuthErrorBoundaryProps, AuthErrorFallbackProps };
