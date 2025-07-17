'use client';

import React, { Component, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Bug } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CONFIG } from '@/config';

interface ErrorInfo {
  componentStack: string;
  errorBoundary?: string;
  errorBoundaryStack?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
  errorId?: string;
  retryCount: number;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, retry: () => void) => ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo, errorId: string) => void;
  showDetails?: boolean;
  maxRetries?: number;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private retryTimeoutId?: NodeJS.Timeout;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      retryCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    const errorId = `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    return {
      hasError: true,
      error,
      errorId,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const errorId = this.state.errorId || 'unknown';
    
    // Log error with constitutional context
    const errorReport = {
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
      },
      errorInfo,
      errorId,
      constitutionalHash: CONFIG.constitutional.hash,
      timestamp: new Date().toISOString(),
      userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : 'unknown',
      url: typeof window !== 'undefined' ? window.location.href : 'unknown',
    };

    console.error('Error Boundary caught an error:', errorReport);

    // Call custom error handler
    this.props.onError?.(error, errorInfo, errorId);

    // Send to error reporting service if audit logging is enabled
    if (CONFIG.features.enableAuditLogging && typeof window !== 'undefined') {
      this.reportError(errorReport);
    }
  }

  private async reportError(errorReport: any) {
    try {
      await fetch('/api/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Constitutional-Hash': CONFIG.constitutional.hash,
        },
        body: JSON.stringify(errorReport),
      });
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  }

  private handleRetry = () => {
    const { maxRetries = 3 } = this.props;
    
    if (this.state.retryCount >= maxRetries) {
      console.warn('Maximum retry attempts reached');
      return;
    }

    this.setState(prevState => ({
      hasError: false,
      error: undefined,
      errorInfo: undefined,
      errorId: undefined,
      retryCount: prevState.retryCount + 1,
    }));

    // Add a small delay before retry to prevent immediate re-error
    this.retryTimeoutId = setTimeout(() => {
      this.forceUpdate();
    }, 1000);
  };

  private handleReload = () => {
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
  };

  componentWillUnmount() {
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId);
    }
  }

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleRetry);
      }

      return (
        <ErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          errorId={this.state.errorId}
          retryCount={this.state.retryCount}
          maxRetries={this.props.maxRetries || 3}
          showDetails={this.props.showDetails}
          onRetry={this.handleRetry}
          onReload={this.handleReload}
        />
      );
    }

    return this.props.children;
  }
}

interface ErrorFallbackProps {
  error: Error;
  errorInfo?: ErrorInfo;
  errorId?: string;
  retryCount: number;
  maxRetries: number;
  showDetails?: boolean;
  onRetry: () => void;
  onReload: () => void;
}

function ErrorFallback({
  error,
  errorInfo,
  errorId,
  retryCount,
  maxRetries,
  showDetails = false,
  onRetry,
  onReload,
}: ErrorFallbackProps) {
  const canRetry = retryCount < maxRetries;

  return (
    <div className="min-h-[400px] flex items-center justify-center p-6">
      <Card className="w-full max-w-2xl border-red-200">
        <CardHeader>
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-8 w-8 text-red-500" />
            <div>
              <CardTitle className="text-red-700">Something went wrong</CardTitle>
              <p className="text-sm text-red-600 mt-1">
                An unexpected error occurred while rendering this component
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2">
            <Badge variant="destructive" className="text-xs">
              Error ID: {errorId || 'Unknown'}
            </Badge>
            <Badge variant="outline" className="text-xs">
              Constitutional Hash: {CONFIG.constitutional.hash}
            </Badge>
            {retryCount > 0 && (
              <Badge variant="secondary" className="text-xs">
                Retry {retryCount}/{maxRetries}
              </Badge>
            )}
          </div>

          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <h4 className="text-sm font-medium text-red-700 mb-2">Error Details</h4>
            <p className="text-sm text-red-600 font-mono break-all">
              {error.name}: {error.message}
            </p>
          </div>

          {showDetails && error.stack && (
            <details className="bg-gray-50 border rounded-md p-4">
              <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                Stack Trace
              </summary>
              <pre className="text-xs text-gray-600 mt-2 overflow-auto max-h-40">
                {error.stack}
              </pre>
            </details>
          )}

          {showDetails && errorInfo?.componentStack && (
            <details className="bg-gray-50 border rounded-md p-4">
              <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                Component Stack
              </summary>
              <pre className="text-xs text-gray-600 mt-2 overflow-auto max-h-40">
                {errorInfo.componentStack}
              </pre>
            </details>
          )}

          <div className="flex gap-3 pt-2">
            {canRetry && (
              <Button onClick={onRetry} variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            )}
            <Button onClick={onReload} variant="outline" size="sm">
              <Bug className="h-4 w-4 mr-2" />
              Reload Page
            </Button>
          </div>

          <div className="text-xs text-gray-500 pt-2 border-t">
            <p>
              If this error persists, please contact support with the Error ID above.
              This error has been automatically reported for analysis.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Specialized error boundaries for different contexts
export function APIErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary
      maxRetries={2}
      onError={(error, errorInfo, errorId) => {
        console.error('API Error Boundary:', { error, errorInfo, errorId });
      }}
      fallback={(error, retry) => (
        <div className="p-4 border border-red-200 rounded-md bg-red-50">
          <h4 className="text-red-700 font-medium">API Error</h4>
          <p className="text-sm text-red-600 mt-1">
            Failed to communicate with the server. Please check your connection.
          </p>
          <Button onClick={retry} size="sm" variant="outline" className="mt-2">
            Retry
          </Button>
        </div>
      )}
    >
      {children}
    </ErrorBoundary>
  );
}

export function RealTimeErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary
      maxRetries={5}
      onError={(error, errorInfo, errorId) => {
        console.error('Real-time Error Boundary:', { error, errorInfo, errorId });
      }}
    >
      {children}
    </ErrorBoundary>
  );
}