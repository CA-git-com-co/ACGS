import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { User } from '../types/governance';

/**
 * Extended authentication hook with additional utilities
 * 
 * Extends the base AuthContext with additional functionality for
 * role-based access control, session management, and user preferences.
 */
export const useAuthExtended = () => {
  const authContext = useAuth();
  const [sessionExpiry, setSessionExpiry] = useState<Date | null>(null);
  const [lastActivity, setLastActivity] = useState<Date>(new Date());

  /**
   * Check if user has specific role
   */
  const hasRole = useCallback((role: string): boolean => {
    return authContext.currentUser?.role === role;
  }, [authContext.currentUser]);

  /**
   * Check if user has any of the specified roles
   */
  const hasAnyRole = useCallback((roles: string[]): boolean => {
    return roles.some(role => hasRole(role));
  }, [hasRole]);

  /**
   * Check if user is admin
   */
  const isAdmin = useCallback((): boolean => {
    return hasRole('admin');
  }, [hasRole]);

  /**
   * Check if user is moderator or admin
   */
  const isModerator = useCallback((): boolean => {
    return hasAnyRole(['admin', 'moderator']);
  }, [hasAnyRole]);

  /**
   * Check if user can perform specific action
   */
  const canPerformAction = useCallback((action: string): boolean => {
    if (!authContext.currentUser) return false;

    // Define role-based permissions
    const permissions: Record<string, string[]> = {
      'create_principle': ['admin', 'moderator'],
      'edit_principle': ['admin', 'moderator'],
      'delete_principle': ['admin'],
      'create_policy': ['admin', 'moderator'],
      'activate_policy': ['admin'],
      'view_analytics': ['admin', 'moderator'],
      'manage_users': ['admin']
    };

    const requiredRoles = permissions[action];
    return requiredRoles ? hasAnyRole(requiredRoles) : true;
  }, [authContext.currentUser, hasAnyRole]);

  /**
   * Update last activity timestamp
   */
  const updateActivity = useCallback(() => {
    setLastActivity(new Date());
  }, []);

  /**
   * Check if session is near expiry
   */
  const isSessionNearExpiry = useCallback((warningMinutes: number = 5): boolean => {
    if (!sessionExpiry) return false;
    const warningTime = new Date(sessionExpiry.getTime() - warningMinutes * 60 * 1000);
    return new Date() >= warningTime;
  }, [sessionExpiry]);

  /**
   * Get user display name
   */
  const getDisplayName = useCallback((): string => {
    if (!authContext.currentUser) return 'Guest';
    return authContext.currentUser.username || 'User';
  }, [authContext.currentUser]);

  /**
   * Get user initials for avatar
   */
  const getUserInitials = useCallback((): string => {
    const displayName = getDisplayName();
    if (displayName === 'Guest') return 'G';
    
    const names = displayName.split(' ');
    if (names.length >= 2) {
      return `${names[0][0]}${names[1][0]}`.toUpperCase();
    }
    return displayName.substring(0, 2).toUpperCase();
  }, [getDisplayName]);

  /**
   * Enhanced login with activity tracking
   */
  const loginWithTracking = useCallback(async (username: string, password: string) => {
    await authContext.login(username, password);
    updateActivity();
    
    // Set session expiry (assuming 8 hours)
    const expiry = new Date();
    expiry.setHours(expiry.getHours() + 8);
    setSessionExpiry(expiry);
  }, [authContext.login, updateActivity]);

  /**
   * Enhanced logout with cleanup
   */
  const logoutWithCleanup = useCallback(async () => {
    await authContext.logout();
    setSessionExpiry(null);
    setLastActivity(new Date());
  }, [authContext.logout]);

  /**
   * Refresh session
   */
  const refreshSession = useCallback(async () => {
    try {
      await authContext.refreshToken();
      updateActivity();
      
      // Extend session expiry
      const expiry = new Date();
      expiry.setHours(expiry.getHours() + 8);
      setSessionExpiry(expiry);
      
      return true;
    } catch (error) {
      console.error('Session refresh failed:', error);
      return false;
    }
  }, [authContext.refreshToken, updateActivity]);

  // Track user activity
  useEffect(() => {
    const handleActivity = () => updateActivity();
    
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => {
      document.addEventListener(event, handleActivity, true);
    });

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleActivity, true);
      });
    };
  }, [updateActivity]);

  // Auto-refresh session when near expiry
  useEffect(() => {
    if (!authContext.isAuthenticated || !sessionExpiry) return;

    const checkSession = () => {
      if (isSessionNearExpiry(10)) { // 10 minutes warning
        refreshSession();
      }
    };

    const interval = setInterval(checkSession, 60000); // Check every minute
    return () => clearInterval(interval);
  }, [authContext.isAuthenticated, sessionExpiry, isSessionNearExpiry, refreshSession]);

  return {
    // Base auth context
    ...authContext,
    
    // Extended functionality
    hasRole,
    hasAnyRole,
    isAdmin,
    isModerator,
    canPerformAction,
    getDisplayName,
    getUserInitials,
    
    // Session management
    sessionExpiry,
    lastActivity,
    isSessionNearExpiry,
    updateActivity,
    refreshSession,
    
    // Enhanced auth methods
    loginWithTracking,
    logoutWithCleanup,
    
    // Computed properties
    isSessionActive: authContext.isAuthenticated && sessionExpiry && new Date() < sessionExpiry,
    minutesUntilExpiry: sessionExpiry ? Math.max(0, Math.floor((sessionExpiry.getTime() - new Date().getTime()) / 60000)) : 0
  };
};

/**
 * Hook for role-based conditional rendering
 */
export const useRoleAccess = (requiredRoles: string | string[]) => {
  const { hasRole, hasAnyRole, isAuthenticated } = useAuthExtended();
  
  const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];
  const hasAccess = isAuthenticated && hasAnyRole(roles);
  
  return {
    hasAccess,
    isAuthenticated,
    checkRole: hasRole,
    checkAnyRole: hasAnyRole
  };
};

/**
 * Hook for protected actions with permission checking
 */
export const useProtectedAction = (action: string) => {
  const { canPerformAction, isAuthenticated } = useAuthExtended();
  
  const executeAction = useCallback((callback: () => void | Promise<void>) => {
    if (!isAuthenticated) {
      throw new Error('Authentication required');
    }
    
    if (!canPerformAction(action)) {
      throw new Error(`Insufficient permissions for action: ${action}`);
    }
    
    return callback();
  }, [isAuthenticated, canPerformAction, action]);
  
  return {
    canExecute: isAuthenticated && canPerformAction(action),
    executeAction,
    isAuthenticated
  };
};

export default useAuthExtended;
