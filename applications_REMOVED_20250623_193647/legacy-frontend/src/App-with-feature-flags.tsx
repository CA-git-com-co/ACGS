/**
 * Enhanced App.tsx with Feature Flag Integration
 *
 * This file demonstrates how to integrate the feature flag system
 * into the legacy-frontend application for gradual migration.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@acgs/shared/contexts/AuthContext';
import {
  FeatureFlagProvider,
  MigrationToggle,
  FeatureToggle,
  FeatureFlagDebugger,
  useFeatureFlag,
} from '@acgs/shared/utils/featureFlags';

// Shared components
import {
  Layout as SharedLayout,
  ProtectedRoute,
  DashboardPage as SharedDashboardPage,
  ACManagementPage,
  LoginPage,
} from '@acgs/shared/components';

// Legacy components
import LegacyLayout from './components/Layout/Layout';
import RegisterPage from './pages/Auth/RegisterPage';
import PolicySynthesisPage from './pages/Synthesis/PolicySynthesisPage';
import PolicyListPage from './pages/Policies/PolicyListPage';
import PublicConsultationPage from './pages/PublicConsultation/PublicConsultationPage';
import ConstitutionalCouncilDashboard from './components/ConstitutionalCouncilDashboard';
import QuantumagiApp from './components/QuantumagiDashboard';
import ConstitutionalFidelityMonitor from './components/ConstitutionalFidelityMonitor';

// Shared equivalents
import {
  ConstitutionalDashboard as SharedConstitutionalDashboard,
  QuantumagiDashboard as SharedQuantumagiDashboard,
  MonitoringDashboard as SharedMonitoringDashboard,
} from '@acgs/shared/components/dashboard';

// Feature flag configuration
import { LEGACY_OVERRIDES } from './config/featureFlags';

// Layout wrapper with feature flag
const LayoutWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <MigrationToggle
      flag="useSharedLayout"
      legacyComponent={<LegacyLayout>{children}</LegacyLayout>}
      sharedComponent={<SharedLayout>{children}</SharedLayout>}
      loadingComponent={
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      }
    />
  );
};

// Dashboard wrapper with feature flag
const DashboardWrapper: React.FC = () => {
  return (
    <MigrationToggle
      flag="useSharedDashboard"
      legacyComponent={<ConstitutionalCouncilDashboard />}
      sharedComponent={<SharedConstitutionalDashboard />}
    />
  );
};

// Quantumagi wrapper with feature flag (CRITICAL)
const QuantumagiWrapper: React.FC = () => {
  return (
    <MigrationToggle
      flag="useSharedQuantumagi"
      legacyComponent={<QuantumagiApp />}
      sharedComponent={<SharedQuantumagiDashboard />}
      loadingComponent={
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">Switching Quantumagi interface...</p>
            <p className="text-sm text-gray-500 mt-2">Validating Solana devnet connection...</p>
          </div>
        </div>
      }
    />
  );
};

// Monitoring wrapper with feature flag
const MonitoringWrapper: React.FC = () => {
  return (
    <MigrationToggle
      flag="useSharedMonitoring"
      legacyComponent={<ConstitutionalFidelityMonitor />}
      sharedComponent={<SharedMonitoringDashboard />}
    />
  );
};

// Route configuration with feature flag awareness
interface RouteConfig {
  path: string;
  element: React.ReactElement;
  protected?: boolean;
  legacy?: boolean;
  redirectTo?: string;
  solana?: boolean;
  featureFlag?: string;
}

const routeConfigs: RouteConfig[] = [
  // Core routes
  { path: '/', element: <SharedDashboardPage />, protected: false },
  { path: '/login', element: <LoginPage />, protected: false },
  { path: '/ac-management', element: <ACManagementPage />, protected: true },

  // Feature-flagged routes
  {
    path: '/dashboard',
    element: <DashboardWrapper />,
    protected: true,
    featureFlag: 'useSharedDashboard',
  },
  {
    path: '/constitutional-council-dashboard',
    element: <DashboardWrapper />,
    protected: true,
    legacy: true,
    featureFlag: 'useSharedDashboard',
  },
  {
    path: '/quantumagi',
    element: <QuantumagiWrapper />,
    protected: false,
    solana: true,
    featureFlag: 'useSharedQuantumagi',
  },
  {
    path: '/monitoring',
    element: <MonitoringWrapper />,
    protected: true,
    featureFlag: 'useSharedMonitoring',
  },

  // Legacy routes (always legacy for now)
  { path: '/register', element: <RegisterPage />, protected: false, legacy: true },
  { path: '/policy-synthesis', element: <PolicySynthesisPage />, protected: true, legacy: true },
  { path: '/policies', element: <PolicyListPage />, protected: true, legacy: true },
  {
    path: '/public-consultation',
    element: <PublicConsultationPage />,
    protected: false,
    legacy: true,
  },

  // Solana-specific routes
  { path: '/solana-dashboard', element: <QuantumagiWrapper />, protected: false, solana: true },
  { path: '/blockchain', element: <QuantumagiWrapper />, protected: false, solana: true },

  // Backward compatibility redirects
  { path: '/home', redirectTo: '/' },
  { path: '/dashboard-old', redirectTo: '/dashboard' },
  { path: '/ac-mgmt', redirectTo: '/ac-management' },
  { path: '/principles', redirectTo: '/ac-management' },
  { path: '/quantumagi-dashboard', redirectTo: '/quantumagi' },
];

// Error Boundary with feature flag awareness
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

class FeatureAwareErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Feature Flag Migration Error:', error, errorInfo);

    // Log feature flag state for debugging
    const flags = localStorage.getItem('acgs-feature-flags');
    console.error('Feature flags at time of error:', flags);

    // Trigger emergency rollback if critical error
    if (error.message.includes('Quantumagi') || error.message.includes('Solana')) {
      console.warn('Critical Solana error detected - consider emergency rollback');
    }

    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <svg
                  className="h-8 w-8 text-red-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-medium text-gray-900">Migration Error</h3>
              </div>
            </div>
            <div className="mb-4">
              <p className="text-sm text-gray-600">
                An error occurred during component migration. The system will attempt to rollback to
                legacy components.
              </p>
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="mt-4">
                  <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                    Error Details
                  </summary>
                  <pre className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded overflow-auto max-h-32">
                    {this.state.error.stack}
                  </pre>
                </details>
              )}
            </div>
            <div className="space-y-2">
              <button
                onClick={() => {
                  // Clear feature flags and reload
                  localStorage.removeItem('acgs-feature-flags');
                  window.location.reload();
                }}
                className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors duration-200"
              >
                Emergency Rollback & Reload
              </button>
              <button
                onClick={() => window.location.reload()}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors duration-200"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Loading Component
const LoadingFallback: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
      <p className="mt-4 text-gray-600">Loading governance system...</p>
      <p className="text-sm text-gray-500 mt-2">Initializing feature flags...</p>
    </div>
  </div>
);

// Route Analytics Component
const RouteAnalytics: React.FC<{ config: RouteConfig }> = ({ config }) => {
  const featureFlagEnabled = useFeatureFlag(config.featureFlag as any);

  React.useEffect(() => {
    // Enhanced analytics with feature flag information
    const analyticsData = {
      route: config.path,
      type: config.legacy ? 'legacy' : config.solana ? 'solana' : 'modern',
      featureFlag: config.featureFlag,
      featureFlagEnabled: config.featureFlag ? featureFlagEnabled : null,
      timestamp: new Date().toISOString(),
    };

    console.log('Route Analytics:', analyticsData);

    // Send to analytics service if available
    if (window.gtag) {
      window.gtag('event', 'route_access', {
        route_path: config.path,
        route_type: analyticsData.type,
        feature_flag: config.featureFlag,
        flag_enabled: featureFlagEnabled,
      });
    }
  }, [config, featureFlagEnabled]);

  return null;
};

// Main App Component with Feature Flags
const App: React.FC = () => {
  return (
    <FeatureAwareErrorBoundary>
      <FeatureFlagProvider initialFlags={LEGACY_OVERRIDES}>
        <AuthProvider>
          <Router>
            <React.Suspense fallback={<LoadingFallback />}>
              <LayoutWrapper>
                <Routes>
                  {routeConfigs.map((config) => {
                    // Handle redirects
                    if (config.redirectTo) {
                      return (
                        <Route
                          key={config.path}
                          path={config.path}
                          element={<Navigate to={config.redirectTo} replace />}
                        />
                      );
                    }

                    // Wrap element with analytics
                    const elementWithAnalytics = (
                      <>
                        <RouteAnalytics config={config} />
                        {config.element}
                      </>
                    );

                    // Handle protected routes
                    if (config.protected) {
                      return (
                        <Route
                          key={config.path}
                          path={config.path}
                          element={<ProtectedRoute>{elementWithAnalytics}</ProtectedRoute>}
                        />
                      );
                    }

                    // Handle public routes
                    return (
                      <Route key={config.path} path={config.path} element={elementWithAnalytics} />
                    );
                  })}

                  {/* Catch-all route for 404 */}
                  <Route
                    path="*"
                    element={
                      <div className="min-h-screen flex items-center justify-center bg-gray-50">
                        <div className="text-center">
                          <h1 className="text-6xl font-bold text-gray-900">404</h1>
                          <p className="text-xl text-gray-600 mt-4">Page not found</p>
                          <p className="text-gray-500 mt-2">
                            The governance page you're looking for doesn't exist.
                          </p>
                          <div className="mt-6 space-x-4">
                            <button
                              onClick={() => (window.location.href = '/')}
                              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors duration-200"
                            >
                              Go Home
                            </button>
                            <button
                              onClick={() => (window.location.href = '/quantumagi')}
                              className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors duration-200"
                            >
                              Quantumagi Dashboard
                            </button>
                          </div>
                        </div>
                      </div>
                    }
                  />
                </Routes>
              </LayoutWrapper>
            </React.Suspense>
          </Router>
        </AuthProvider>

        {/* Feature Flag Debugger (development only) */}
        <FeatureFlagDebugger />
      </FeatureFlagProvider>
    </FeatureAwareErrorBoundary>
  );
};

export default App;
