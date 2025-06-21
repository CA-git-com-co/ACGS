import React from 'react';

/**
 * Loading component props
 */
interface LoadingProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'gray' | 'indigo';
  className?: string;
}

/**
 * Spinner loading component props
 */
interface SpinnerProps extends LoadingProps {
  text?: string;
  showText?: boolean;
}

/**
 * Skeleton loader props
 */
interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  className?: string;
  rounded?: boolean;
  lines?: number;
}

/**
 * Progress indicator props
 */
interface ProgressProps {
  progress: number;
  max?: number;
  label?: string;
  showPercentage?: boolean;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'indigo';
  className?: string;
}

/**
 * Loading overlay props
 */
interface LoadingOverlayProps {
  isLoading: boolean;
  children: React.ReactNode;
  spinner?: React.ReactNode;
  className?: string;
  blur?: boolean;
}

/**
 * Size configurations for loading components
 */
const SIZE_CONFIG = {
  sm: { spinner: 'h-4 w-4', text: 'text-sm' },
  md: { spinner: 'h-6 w-6', text: 'text-base' },
  lg: { spinner: 'h-8 w-8', text: 'text-lg' },
  xl: { spinner: 'h-12 w-12', text: 'text-xl' }
};

/**
 * Color configurations for loading components
 */
const COLOR_CONFIG = {
  blue: 'text-blue-600 border-blue-600',
  green: 'text-green-600 border-green-600',
  yellow: 'text-yellow-600 border-yellow-600',
  red: 'text-red-600 border-red-600',
  gray: 'text-gray-600 border-gray-600',
  indigo: 'text-indigo-600 border-indigo-600'
};

/**
 * Basic spinner component
 */
export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'blue',
  text = 'Loading...',
  showText = false,
  className = ''
}) => {
  const sizeClasses = SIZE_CONFIG[size];
  const colorClasses = COLOR_CONFIG[color];

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div className="flex items-center space-x-2">
        <div
          className={`animate-spin rounded-full border-2 border-t-transparent ${sizeClasses.spinner} ${colorClasses}`}
          role="status"
          aria-label="Loading"
        />
        {showText && (
          <span className={`${sizeClasses.text} ${colorClasses.split(' ')[0]}`}>{text}</span>
        )}
      </div>
    </div>
  );
};

/**
 * Skeleton loader component for content placeholders
 */
export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '1rem',
  className = '',
  rounded = false,
  lines = 1
}) => {
  const skeletonClass = `bg-gray-200 animate-pulse ${rounded ? 'rounded-full' : 'rounded'} ${className}`;

  if (lines === 1) {
    return (
      <div
        className={skeletonClass}
        style={{ width, height }}
        role="status"
        aria-label="Loading content"
      />
    );
  }

  return (
    <div className="space-y-2" role="status" aria-label="Loading content">
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={skeletonClass}
          style={{
            width: index === lines - 1 ? '75%' : width,
            height
          }}
        />
      ))}
    </div>
  );
};

/**
 * Progress indicator component
 */
export const Progress: React.FC<ProgressProps> = ({
  progress,
  max = 100,
  label,
  showPercentage = true,
  color = 'blue',
  className = ''
}) => {
  const percentage = Math.min(Math.max((progress / max) * 100, 0), 100);
  const colorClass =
    color === 'blue'
      ? 'bg-blue-600'
      : color === 'green'
        ? 'bg-green-600'
        : color === 'yellow'
          ? 'bg-yellow-600'
          : color === 'red'
            ? 'bg-red-600'
            : color === 'indigo'
              ? 'bg-indigo-600'
              : 'bg-blue-600';

  return (
    <div className={`w-full ${className}`}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-2">
          {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
          {showPercentage && (
            <span className="text-sm text-gray-500">{Math.round(percentage)}%</span>
          )}
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ease-out ${colorClass}`}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
    </div>
  );
};

/**
 * Loading overlay component
 */
export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  children,
  spinner,
  className = '',
  blur = true
}) => {
  if (!isLoading) {
    return <>{children}</>;
  }

  return (
    <div className={`relative ${className}`}>
      <div
        className={blur ? 'filter blur-sm pointer-events-none' : 'pointer-events-none opacity-50'}
      >
        {children}
      </div>
      <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75">
        {spinner || <Spinner size="lg" showText text="Loading..." />}
      </div>
    </div>
  );
};

/**
 * Card skeleton for dashboard components
 */
export const CardSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
    <div className="space-y-4">
      <Skeleton height="1.5rem" width="60%" />
      <Skeleton lines={3} height="1rem" />
      <div className="flex space-x-2">
        <Skeleton height="2rem" width="5rem" rounded />
        <Skeleton height="2rem" width="5rem" rounded />
      </div>
    </div>
  </div>
);

/**
 * Table skeleton for data tables
 */
export const TableSkeleton: React.FC<{ rows?: number; columns?: number; className?: string }> = ({
  rows = 5,
  columns = 4,
  className = ''
}) => (
  <div className={`bg-white rounded-lg shadow overflow-hidden ${className}`}>
    {/* Header */}
    <div className="bg-gray-50 px-6 py-3 border-b">
      <div className="flex space-x-4">
        {Array.from({ length: columns }).map((_, index) => (
          <Skeleton key={index} height="1rem" width="6rem" />
        ))}
      </div>
    </div>
    {/* Rows */}
    <div className="divide-y divide-gray-200">
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="px-6 py-4">
          <div className="flex space-x-4">
            {Array.from({ length: columns }).map((_, colIndex) => (
              <Skeleton key={colIndex} height="1rem" width="8rem" />
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

/**
 * Form skeleton for forms
 */
export const FormSkeleton: React.FC<{ fields?: number; className?: string }> = ({
  fields = 4,
  className = ''
}) => (
  <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
    <div className="space-y-6">
      <Skeleton height="2rem" width="40%" />
      {Array.from({ length: fields }).map((_, index) => (
        <div key={index} className="space-y-2">
          <Skeleton height="1rem" width="25%" />
          <Skeleton height="2.5rem" width="100%" />
        </div>
      ))}
      <div className="flex space-x-3 pt-4">
        <Skeleton height="2.5rem" width="6rem" rounded />
        <Skeleton height="2.5rem" width="6rem" rounded />
      </div>
    </div>
  </div>
);

/**
 * Loading button component
 */
export const LoadingButton: React.FC<{
  isLoading: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
  loadingText?: string;
}> = ({
  isLoading,
  children,
  onClick,
  disabled = false,
  className = '',
  loadingText = 'Loading...'
}) => (
  <button
    onClick={onClick}
    disabled={disabled || isLoading}
    className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
  >
    {isLoading && <Spinner size="sm" className="mr-2" />}
    {isLoading ? loadingText : children}
  </button>
);

/**
 * Timeout wrapper component that shows loading state with timeout handling
 */
export const TimeoutLoader: React.FC<{
  children: React.ReactNode;
  timeout?: number;
  onTimeout?: () => void;
  loadingComponent?: React.ReactNode;
  timeoutComponent?: React.ReactNode;
}> = ({
  children,
  timeout = 30000, // 30 seconds default
  onTimeout,
  loadingComponent,
  timeoutComponent
}) => {
  const [isTimeout, setIsTimeout] = React.useState(false);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setIsTimeout(true);
      if (onTimeout) {
        onTimeout();
      }
    }, timeout);

    return () => clearTimeout(timer);
  }, [timeout, onTimeout]);

  if (isTimeout) {
    return (
      <>
        {timeoutComponent || (
          <div className="text-center py-8">
            <div className="text-yellow-600 mb-2">
              <svg
                className="mx-auto h-12 w-12"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Request Timeout</h3>
            <p className="text-gray-600">The request is taking longer than expected.</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              Refresh Page
            </button>
          </div>
        )}
      </>
    );
  }

  return (
    <>
      {loadingComponent || <Spinner size="lg" showText text="Loading..." />}
      {children}
    </>
  );
};

export type { LoadingProps, SpinnerProps, SkeletonProps, ProgressProps, LoadingOverlayProps };
