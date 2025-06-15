import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@acgs/shared/contexts/AuthContext';
import { Layout, ProtectedRoute } from '@acgs/shared/components';
import { 
  DashboardPage, 
  ACManagementPage, 
  LoginPage 
} from '@acgs/shared/pages';

// Legacy imports for backward compatibility
import RegisterPage from './pages/Auth/RegisterPage';
import PolicySynthesisPage from './pages/Synthesis/PolicySynthesisPage';
import PolicyListPage from './pages/Policies/PolicyListPage';
import PublicConsultationPage from './pages/PublicConsultation/PublicConsultationPage';
import ConstitutionalCouncilDashboard from './components/ConstitutionalCouncilDashboard';
import ConstitutionalAmendmentWorkflow from './components/ConstitutionalAmendmentWorkflow';

// Modern components
import ComplianceChecker from './components/ComplianceChecker';
import GovernanceDashboard from './components/GovernanceDashboard';

// Route configuration with backward compatibility
interface RouteConfig {
  path: string;
  element: React.ReactElement;
  protected?: boolean;
  legacy?: boolean;
  redirectTo?: string;
}

const routeConfigs: RouteConfig[] = [
  // Modern routes using shared components
  { path: '/', element: <DashboardPage />, protected: false },
  { path: '/dashboard', element: <DashboardPage />, protected: true },
  { path: '/login', element: <LoginPage />, protected: false },
  { path: '/ac-management', element: <ACManagementPage />, protected: true },
  
  // Legacy routes with backward compatibility
  { path: '/register', element: <RegisterPage />, protected: false, legacy: true },
  { path: '/policy-synthesis', element: <PolicySynthesisPage />, protected: true, legacy: true },
  { path: '/policies', element: <PolicyListPage />, protected: true, legacy: true },
  { path: '/public-consultation', element: <PublicConsultationPage />, protected: false, legacy: true },
  { path: '/constitutional-council-dashboard', element: <ConstitutionalCouncilDashboard />, protected: true, legacy: true },
  { path: '/constitutional-amendment', element: <ConstitutionalAmendmentWorkflow />, protected: true, legacy: true },
  
  // Modern governance-specific routes
  { path: '/compliance-checker', element: <ComplianceChecker />, protected: true },
  { path: '/governance-dashboard', element: <GovernanceDashboard />, protected: true },
  
  // Backward compatibility redirects
  { path: '/home', redirectTo: '/' },
  { path: '/dashboard-old', redirectTo: '/dashboard' },
  { path: '/ac-mgmt', redirectTo: '/ac-management' },
  { path: '/principles', redirectTo: '/ac-management' },
];

// Error Boundary Component
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends React.Component<
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
    console.error('Application Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-medium text-gray-900">Application Error</h3>
              </div>
            </div>
            <div className="mb-4">
              <p className="text-sm text-gray-600">
                Something went wrong. Please refresh the page or contact support if the problem persists.
              </p>
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="mt-4">
                  <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                    Error Details
                  </summary>
                  <pre className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded overflow-auto">
                    {this.state.error.stack}
                  </pre>
                </details>
              )}
            </div>
            <button
              onClick={() => window.location.reload()}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors duration-200"
            >
              Refresh Page
            </button>
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
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
      <p className="mt-4 text-gray-600">Loading application...</p>
    </div>
  </div>
);

// 404 Not Found Component
const NotFoundPage: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <h1 className="text-6xl font-bold text-gray-900">404</h1>
      <p className="text-xl text-gray-600 mt-4">Page not found</p>
      <p className="text-gray-500 mt-2">The page you're looking for doesn't exist.</p>
      <div className="mt-6">
        <Navigate to="/" replace />
      </div>
    </div>
  </div>
);

// Main App Component
const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <React.Suspense fallback={<LoadingFallback />}>
            <Layout>
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

                  // Handle protected routes
                  if (config.protected) {
                    return (
                      <Route
                        key={config.path}
                        path={config.path}
                        element={
                          <ProtectedRoute>
                            {config.element}
                          </ProtectedRoute>
                        }
                      />
                    );
                  }

                  // Handle public routes
                  return (
                    <Route
                      key={config.path}
                      path={config.path}
                      element={config.element}
                    />
                  );
                })}

                {/* Catch-all route for 404 */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </Layout>
          </React.Suspense>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
