import React from 'react';
import { Spinner, LoadingOverlay, CardSkeleton } from '../LoadingStates';

/**
 * Loading HOC configuration options
 */
interface WithLoadingOptions {
  /** Loading component to display */
  loadingComponent?: React.ComponentType<any>;
  /** Whether to use overlay mode */
  useOverlay?: boolean;
  /** Whether to blur content when loading */
  blurContent?: boolean;
  /** Loading text to display */
  loadingText?: string;
  /** Minimum loading time in milliseconds */
  minLoadingTime?: number;
}

/**
 * Props that the wrapped component should have for loading functionality
 */
interface LoadingProps {
  isLoading?: boolean;
  error?: Error | string | null;
}

/**
 * Higher-order component that adds loading state management
 *
 * @param WrappedComponent - Component to wrap with loading functionality
 * @param options - Configuration options for loading behavior
 * @returns Component with loading state management
 *
 * @example
 * ```typescript
 * const LoadingUserList = withLoading(UserList, {
 *   loadingComponent: () => <CardSkeleton />,
 *   useOverlay: false,
 *   loadingText: 'Loading users...'
 * });
 *
 * // Usage
 * <LoadingUserList isLoading={isLoading} error={error} users={users} />
 * ```
 */
export function withLoading<P extends LoadingProps>(
  WrappedComponent: React.ComponentType<P>,
  options: WithLoadingOptions = {}
) {
  const {
    loadingComponent: LoadingComponent,
    useOverlay = false,
    blurContent = true,
    loadingText = 'Loading...',
    minLoadingTime = 0
  } = options;

  const WithLoadingComponent: React.FC<P> = props => {
    const { isLoading = false, error, ...restProps } = props;
    const [showLoading, setShowLoading] = React.useState(isLoading);
    const [minTimeElapsed, setMinTimeElapsed] = React.useState(minLoadingTime === 0);

    // Handle minimum loading time
    React.useEffect(() => {
      if (isLoading && minLoadingTime > 0) {
        setMinTimeElapsed(false);
        const timer = setTimeout(() => {
          setMinTimeElapsed(true);
        }, minLoadingTime);

        return () => clearTimeout(timer);
      } else {
        setMinTimeElapsed(true);
      }
    }, [isLoading, minLoadingTime]);

    // Update show loading state
    React.useEffect(() => {
      setShowLoading(isLoading && !minTimeElapsed);
    }, [isLoading, minTimeElapsed]);

    // Error state
    if (error) {
      return (
        <div className="error-state p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center">
            <svg
              className="h-5 w-5 text-red-400 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-red-700">
              {typeof error === 'string' ? error : error.message}
            </span>
          </div>
        </div>
      );
    }

    // Loading state with overlay
    if (useOverlay) {
      return (
        <LoadingOverlay
          isLoading={showLoading}
          blur={blurContent}
          spinner={
            LoadingComponent ? (
              <LoadingComponent />
            ) : (
              <Spinner size="lg" showText text={loadingText} />
            )
          }
        >
          <WrappedComponent {...(restProps as P)} />
        </LoadingOverlay>
      );
    }

    // Loading state without overlay
    if (showLoading) {
      if (LoadingComponent) {
        return <LoadingComponent />;
      }
      return <Spinner size="lg" showText text={loadingText} className="flex justify-center py-8" />;
    }

    return <WrappedComponent {...(restProps as P)} />;
  };

  WithLoadingComponent.displayName = `withLoading(${WrappedComponent.displayName || WrappedComponent.name})`;

  return WithLoadingComponent;
}

/**
 * HOC specifically for card-based components
 */
export function withCardLoading<P extends LoadingProps>(
  WrappedComponent: React.ComponentType<P>,
  options: Omit<WithLoadingOptions, 'loadingComponent'> = {}
) {
  return withLoading(WrappedComponent, {
    ...options,
    loadingComponent: CardSkeleton
  });
}

/**
 * HOC for list components with skeleton loading
 */
export function withListLoading<P extends LoadingProps>(
  WrappedComponent: React.ComponentType<P>,
  skeletonCount: number = 3
) {
  const ListSkeleton = () => (
    <div className="space-y-4">
      {Array.from({ length: skeletonCount }).map((_, index) => (
        <CardSkeleton key={index} />
      ))}
    </div>
  );

  return withLoading(WrappedComponent, {
    loadingComponent: ListSkeleton,
    useOverlay: false
  });
}

/**
 * HOC for form components with loading states
 */
export function withFormLoading<P extends LoadingProps>(
  WrappedComponent: React.ComponentType<P>,
  options: WithLoadingOptions = {}
) {
  return withLoading(WrappedComponent, {
    ...options,
    useOverlay: true,
    blurContent: true,
    loadingText: 'Processing...'
  });
}

/**
 * HOC for data fetching components
 */
export function withDataLoading<P extends LoadingProps>(
  WrappedComponent: React.ComponentType<P>,
  options: WithLoadingOptions = {}
) {
  return withLoading(WrappedComponent, {
    ...options,
    minLoadingTime: 500, // Prevent flash of loading state
    loadingText: 'Loading data...'
  });
}

/**
 * Utility function to create custom loading HOCs
 */
export function createLoadingHOC<P extends LoadingProps>(defaultOptions: WithLoadingOptions) {
  return (WrappedComponent: React.ComponentType<P>, options: WithLoadingOptions = {}) => {
    return withLoading(WrappedComponent, { ...defaultOptions, ...options });
  };
}

// Export commonly used loading HOCs
export const withSpinnerLoading = createLoadingHOC({
  loadingComponent: () => <Spinner size="lg" showText text="Loading..." />,
  useOverlay: false
});

export const withOverlayLoading = createLoadingHOC({
  useOverlay: true,
  blurContent: true
});

export const withMinimalLoading = createLoadingHOC({
  loadingComponent: () => <Spinner size="sm" />,
  useOverlay: false,
  minLoadingTime: 200
});

export default withLoading;
