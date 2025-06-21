import React from 'react';
import { useAuthExtended, useRoleAccess } from '../../hooks/useAuthExtended';
import { Spinner } from '../LoadingStates';

/**
 * Authentication HOC configuration options
 */
interface WithAuthOptions {
  /** Required roles for access */
  requiredRoles?: string | string[];
  /** Required permissions for access */
  requiredPermissions?: string | string[];
  /** Redirect URL for unauthenticated users */
  redirectTo?: string;
  /** Custom unauthorized component */
  unauthorizedComponent?: React.ComponentType<any>;
  /** Custom loading component */
  loadingComponent?: React.ComponentType<any>;
  /** Whether to show loading during auth check */
  showLoadingDuringCheck?: boolean;
}

/**
 * Props that will be injected into the wrapped component
 */
interface AuthInjectedProps {
  currentUser: any;
  isAuthenticated: boolean;
  hasRole: (role: string) => boolean;
  canPerformAction: (action: string) => boolean;
  logout: () => Promise<void>;
}

/**
 * Default unauthorized component
 */
const DefaultUnauthorizedComponent: React.FC<{ message?: string }> = ({
  message = "You don't have permission to access this resource."
}) => (
  <div className="unauthorized-access flex items-center justify-center min-h-64">
    <div className="text-center p-8 bg-yellow-50 border border-yellow-200 rounded-lg max-w-md">
      <svg
        className="mx-auto h-12 w-12 text-yellow-400 mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z"
        />
      </svg>
      <h3 className="text-lg font-medium text-yellow-800 mb-2">Access Denied</h3>
      <p className="text-yellow-700">{message}</p>
    </div>
  </div>
);

/**
 * Default unauthenticated component
 */
const DefaultUnauthenticatedComponent: React.FC = () => (
  <div className="unauthenticated-access flex items-center justify-center min-h-64">
    <div className="text-center p-8 bg-blue-50 border border-blue-200 rounded-lg max-w-md">
      <svg
        className="mx-auto h-12 w-12 text-blue-400 mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
        />
      </svg>
      <h3 className="text-lg font-medium text-blue-800 mb-2">Authentication Required</h3>
      <p className="text-blue-700 mb-4">Please log in to access this resource.</p>
      <button
        onClick={() => (window.location.href = '/login')}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Go to Login
      </button>
    </div>
  </div>
);

/**
 * Higher-order component that adds authentication and authorization
 *
 * @param WrappedComponent - Component to wrap with auth functionality
 * @param options - Configuration options for auth behavior
 * @returns Component with authentication and authorization
 *
 * @example
 * ```typescript
 * // Require authentication
 * const ProtectedComponent = withAuth(MyComponent);
 *
 * // Require specific role
 * const AdminComponent = withAuth(MyComponent, {
 *   requiredRoles: 'admin'
 * });
 *
 * // Require multiple roles
 * const ModeratorComponent = withAuth(MyComponent, {
 *   requiredRoles: ['admin', 'moderator']
 * });
 *
 * // Require specific permissions
 * const EditComponent = withAuth(MyComponent, {
 *   requiredPermissions: ['edit_principle', 'create_policy']
 * });
 * ```
 */
export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: WithAuthOptions = {}
) {
  const {
    requiredRoles,
    requiredPermissions,
    redirectTo,
    unauthorizedComponent: UnauthorizedComponent = DefaultUnauthorizedComponent,
    loadingComponent: LoadingComponent,
    showLoadingDuringCheck = true
  } = options;

  const WithAuthComponent: React.FC<P> = props => {
    const auth = useAuthExtended();
    const roleAccess = useRoleAccess(requiredRoles || []);

    // Show loading during auth check
    if (auth.isLoading && showLoadingDuringCheck) {
      if (LoadingComponent) {
        return <LoadingComponent />;
      }
      return (
        <div className="auth-loading flex justify-center items-center min-h-64">
          <Spinner size="lg" showText text="Checking authentication..." />
        </div>
      );
    }

    // Check authentication
    if (!auth.isAuthenticated) {
      if (redirectTo) {
        window.location.href = redirectTo;
        return null;
      }
      return <DefaultUnauthenticatedComponent />;
    }

    // Check role-based access
    if (requiredRoles && !roleAccess.hasAccess) {
      const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];
      return (
        <UnauthorizedComponent
          message={`This resource requires one of the following roles: ${roles.join(', ')}`}
        />
      );
    }

    // Check permission-based access
    if (requiredPermissions) {
      const permissions = Array.isArray(requiredPermissions)
        ? requiredPermissions
        : [requiredPermissions];
      const hasAllPermissions = permissions.every(permission => auth.canPerformAction(permission));

      if (!hasAllPermissions) {
        return (
          <UnauthorizedComponent
            message={`This resource requires the following permissions: ${permissions.join(', ')}`}
          />
        );
      }
    }

    // Inject auth props into wrapped component
    const authProps: AuthInjectedProps = {
      currentUser: auth.currentUser,
      isAuthenticated: auth.isAuthenticated,
      hasRole: auth.hasRole,
      canPerformAction: auth.canPerformAction,
      logout: auth.logoutWithCleanup
    };

    return <WrappedComponent {...props} {...authProps} />;
  };

  WithAuthComponent.displayName = `withAuth(${WrappedComponent.displayName || WrappedComponent.name})`;

  return WithAuthComponent;
}

/**
 * HOC for admin-only components
 */
export function withAdminAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: Omit<WithAuthOptions, 'requiredRoles'> = {}
) {
  return withAuth(WrappedComponent, {
    ...options,
    requiredRoles: 'admin'
  });
}

/**
 * HOC for moderator and admin components
 */
export function withModeratorAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: Omit<WithAuthOptions, 'requiredRoles'> = {}
) {
  return withAuth(WrappedComponent, {
    ...options,
    requiredRoles: ['admin', 'moderator']
  });
}

/**
 * HOC for components that require specific permissions
 */
export function withPermissionAuth<P extends object>(permissions: string | string[]) {
  return (
    WrappedComponent: React.ComponentType<P>,
    options: Omit<WithAuthOptions, 'requiredPermissions'> = {}
  ) => {
    return withAuth(WrappedComponent, {
      ...options,
      requiredPermissions: permissions
    });
  };
}

/**
 * Utility function to create custom auth HOCs
 */
export function createAuthHOC<P extends object>(defaultOptions: WithAuthOptions) {
  return (WrappedComponent: React.ComponentType<P>, options: WithAuthOptions = {}) => {
    return withAuth(WrappedComponent, { ...defaultOptions, ...options });
  };
}

// Export commonly used auth HOCs
export const withBasicAuth = createAuthHOC({
  showLoadingDuringCheck: true
});

export const withQuietAuth = createAuthHOC({
  showLoadingDuringCheck: false
});

export const withRedirectAuth = (redirectTo: string) =>
  createAuthHOC({
    redirectTo,
    showLoadingDuringCheck: true
  });

export default withAuth;
