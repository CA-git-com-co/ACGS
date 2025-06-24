// Shared routing utilities for ACGS-PGP Framework

export interface RouteConfig {
  path: string;
  element?: React.ReactElement;
  protected?: boolean;
  legacy?: boolean;
  redirectTo?: string;
  solana?: boolean;
  title?: string;
  description?: string;
}

export interface NavigationItem {
  path: string;
  label: string;
  icon?: string;
  requiresAuth?: boolean;
  adminOnly?: boolean;
  legacy?: boolean;
  solana?: boolean;
}

// Route constants for consistency across applications
export const ROUTES = {
  // Core routes
  HOME: '/',
  DASHBOARD: '/dashboard',
  LOGIN: '/login',
  REGISTER: '/register',

  // AC Management
  AC_MANAGEMENT: '/ac-management',
  PRINCIPLES: '/principles', // Redirect to AC_MANAGEMENT

  // Policy Management
  POLICY_SYNTHESIS: '/policy-synthesis',
  POLICIES: '/policies',
  POLICY_LIST: '/policies',

  // Governance
  CONSTITUTIONAL_COUNCIL: '/constitutional-council-dashboard',
  CONSTITUTIONAL_AMENDMENT: '/constitutional-amendment',
  COMPLIANCE_CHECKER: '/compliance-checker',
  GOVERNANCE_DASHBOARD: '/governance-dashboard',

  // Public
  PUBLIC_CONSULTATION: '/public-consultation',

  // Solana-specific
  QUANTUMAGI: '/quantumagi',
  SOLANA_DASHBOARD: '/solana-dashboard',
  BLOCKCHAIN: '/blockchain',

  // Legacy redirects
  HOME_OLD: '/home',
  DASHBOARD_OLD: '/dashboard-old',
  AC_MGMT: '/ac-mgmt',
  QUANTUMAGI_DASHBOARD: '/quantumagi-dashboard'
} as const;

// Navigation items for different user types
export const getNavigationItems = (
  userRole?: string,
  isAuthenticated?: boolean
): NavigationItem[] => {
  const publicItems: NavigationItem[] = [
    { path: ROUTES.HOME, label: 'Home', icon: '🏠' },
    { path: ROUTES.PUBLIC_CONSULTATION, label: 'Public Consultation', icon: '💬' }
  ];

  const authenticatedItems: NavigationItem[] = [
    { path: ROUTES.DASHBOARD, label: 'Dashboard', icon: '📊', requiresAuth: true },
    { path: ROUTES.AC_MANAGEMENT, label: 'AC Management', icon: '📜', requiresAuth: true },
    { path: ROUTES.POLICY_SYNTHESIS, label: 'Synthesize', icon: '⚙️', requiresAuth: true },
    { path: ROUTES.POLICIES, label: 'View Policies', icon: '📋', requiresAuth: true },
    {
      path: ROUTES.CONSTITUTIONAL_COUNCIL,
      label: 'Council Dashboard',
      icon: '🏛️',
      requiresAuth: true
    },
    { path: ROUTES.COMPLIANCE_CHECKER, label: 'Compliance', icon: '🔍', requiresAuth: true }
  ];

  const solanaItems: NavigationItem[] = [
    { path: ROUTES.QUANTUMAGI, label: 'Quantumagi', icon: '⚡', solana: true },
    { path: ROUTES.BLOCKCHAIN, label: 'Blockchain', icon: '🔗', solana: true }
  ];

  const adminItems: NavigationItem[] = [
    {
      path: ROUTES.GOVERNANCE_DASHBOARD,
      label: 'Governance Admin',
      icon: '👑',
      requiresAuth: true,
      adminOnly: true
    },
    {
      path: ROUTES.CONSTITUTIONAL_AMENDMENT,
      label: 'Amendments',
      icon: '📝',
      requiresAuth: true,
      adminOnly: true
    }
  ];

  let items = [...publicItems];

  if (isAuthenticated) {
    items = [...items, ...authenticatedItems, ...solanaItems];

    if (userRole === 'admin' || userRole === 'council_member') {
      items = [...items, ...adminItems];
    }
  }

  return items;
};

// Route validation and redirection logic
export const getRedirectPath = (path: string): string | null => {
  const redirectMap: Record<string, string> = {
    [ROUTES.HOME_OLD]: ROUTES.HOME,
    [ROUTES.DASHBOARD_OLD]: ROUTES.DASHBOARD,
    [ROUTES.AC_MGMT]: ROUTES.AC_MANAGEMENT,
    [ROUTES.PRINCIPLES]: ROUTES.AC_MANAGEMENT,
    [ROUTES.QUANTUMAGI_DASHBOARD]: ROUTES.QUANTUMAGI
  };

  return redirectMap[path] || null;
};

// Check if a route requires authentication
export const isProtectedRoute = (path: string): boolean => {
  const protectedRoutes = [
    ROUTES.DASHBOARD,
    ROUTES.AC_MANAGEMENT,
    ROUTES.POLICY_SYNTHESIS,
    ROUTES.POLICIES,
    ROUTES.CONSTITUTIONAL_COUNCIL,
    ROUTES.CONSTITUTIONAL_AMENDMENT,
    ROUTES.COMPLIANCE_CHECKER,
    ROUTES.GOVERNANCE_DASHBOARD
  ];

  return protectedRoutes.includes(path as any);
};

// Check if a route is legacy
export const isLegacyRoute = (path: string): boolean => {
  const legacyRoutes = [
    ROUTES.REGISTER,
    ROUTES.POLICY_SYNTHESIS,
    ROUTES.POLICIES,
    ROUTES.PUBLIC_CONSULTATION,
    ROUTES.CONSTITUTIONAL_COUNCIL,
    ROUTES.CONSTITUTIONAL_AMENDMENT
  ];

  return legacyRoutes.includes(path as any);
};

// Check if a route is Solana-specific
export const isSolanaRoute = (path: string): boolean => {
  const solanaRoutes = [ROUTES.QUANTUMAGI, ROUTES.SOLANA_DASHBOARD, ROUTES.BLOCKCHAIN];

  return solanaRoutes.includes(path as any);
};

// Get route metadata
export const getRouteMetadata = (path: string): { title: string; description: string } => {
  const metadata: Record<string, { title: string; description: string }> = {
    [ROUTES.HOME]: {
      title: 'ACGS-PGP Dashboard',
      description: 'Constitutional governance system overview'
    },
    [ROUTES.DASHBOARD]: {
      title: 'Dashboard',
      description: 'Governance system dashboard and analytics'
    },
    [ROUTES.LOGIN]: {
      title: 'Sign In',
      description: 'Sign in to access the governance system'
    },
    [ROUTES.REGISTER]: {
      title: 'Register',
      description: 'Create a new account'
    },
    [ROUTES.AC_MANAGEMENT]: {
      title: 'AC Management',
      description: 'Manage constitutional principles and amendments'
    },
    [ROUTES.POLICY_SYNTHESIS]: {
      title: 'Policy Synthesis',
      description: 'Synthesize policies from constitutional principles'
    },
    [ROUTES.POLICIES]: {
      title: 'Policies',
      description: 'View and manage governance policies'
    },
    [ROUTES.CONSTITUTIONAL_COUNCIL]: {
      title: 'Constitutional Council',
      description: 'Constitutional council dashboard and oversight'
    },
    [ROUTES.COMPLIANCE_CHECKER]: {
      title: 'Compliance Checker',
      description: 'Validate actions against governance policies'
    },
    [ROUTES.PUBLIC_CONSULTATION]: {
      title: 'Public Consultation',
      description: 'Public participation in governance processes'
    },
    [ROUTES.QUANTUMAGI]: {
      title: 'Quantumagi',
      description: 'Solana blockchain governance dashboard'
    }
  };

  return metadata[path] || { title: 'ACGS-PGP', description: 'Constitutional governance system' };
};

// Route analytics and monitoring
export const logRouteAccess = (path: string, userAgent?: string): void => {
  const routeData = {
    path,
    timestamp: new Date().toISOString(),
    isLegacy: isLegacyRoute(path),
    isSolana: isSolanaRoute(path),
    isProtected: isProtectedRoute(path),
    userAgent: userAgent || navigator.userAgent
  };

  // In production, this would send to analytics service
  if (process.env.NODE_ENV === 'development') {
    console.log('Route Access:', routeData);
  }

  // Store in localStorage for migration analytics
  try {
    const existingData = localStorage.getItem('acgs_route_analytics') || '[]';
    const analytics = JSON.parse(existingData);
    analytics.push(routeData);

    // Keep only last 100 entries
    if (analytics.length > 100) {
      analytics.splice(0, analytics.length - 100);
    }

    localStorage.setItem('acgs_route_analytics', JSON.stringify(analytics));
  } catch (error) {
    console.warn('Failed to store route analytics:', error);
  }
};

// Get route analytics data
export const getRouteAnalytics = (): any[] => {
  try {
    const data = localStorage.getItem('acgs_route_analytics') || '[]';
    return JSON.parse(data);
  } catch (error) {
    console.warn('Failed to retrieve route analytics:', error);
    return [];
  }
};

// Clear route analytics data
export const clearRouteAnalytics = (): void => {
  try {
    localStorage.removeItem('acgs_route_analytics');
  } catch (error) {
    console.warn('Failed to clear route analytics:', error);
  }
};

// Breadcrumb generation
export const generateBreadcrumbs = (path: string): Array<{ label: string; path: string }> => {
  const segments = path.split('/').filter(Boolean);
  const breadcrumbs = [{ label: 'Home', path: '/' }];

  let currentPath = '';
  for (const segment of segments) {
    currentPath += `/${segment}`;
    const metadata = getRouteMetadata(currentPath);
    breadcrumbs.push({
      label: metadata.title,
      path: currentPath
    });
  }

  return breadcrumbs;
};
