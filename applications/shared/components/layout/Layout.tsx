import React, { useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { theme } from '../../styles/theme';
import { getNavigationItems, logRouteAccess, getRouteMetadata } from '../../utils/routing';

interface LayoutProps {
  children: React.ReactNode;
  className?: string;
}

const Layout: React.FC<LayoutProps> = ({ children, className = '' }) => {
  const { currentUser, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Log route access for analytics
  useEffect(() => {
    logRouteAccess(location.pathname);
  }, [location.pathname]);

  // Update document title based on route
  useEffect(() => {
    const metadata = getRouteMetadata(location.pathname);
    document.title = `${metadata.title} | ACGS-PGP`;
  }, [location.pathname]);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Get navigation items based on user role and authentication status
  const navigationItems = getNavigationItems(currentUser?.role, isAuthenticated);

  const isActivePath = (path: string): boolean => {
    return location.pathname === path ||
           (path !== '/' && location.pathname.startsWith(path));
  };

  const renderNavItem = (item: any) => (
    <li key={item.path}>
      <Link
        to={item.path}
        className={`
          px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 flex items-center space-x-1
          ${isActivePath(item.path)
            ? 'bg-blue-700 text-white'
            : 'text-gray-300 hover:bg-gray-700 hover:text-white'
          }
        `}
      >
        {item.icon && <span className="text-sm">{item.icon}</span>}
        <span>{item.label}</span>
      </Link>
    </li>
  );

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-gray-800 shadow-lg">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex-shrink-0">
              <Link
                to="/"
                className="text-white text-xl font-bold hover:text-blue-300 transition-colors duration-200"
              >
                🏛️ ACGS-PGP
              </Link>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:block">
              <ul className="flex items-center space-x-4">
                {navigationItems.map(renderNavItem)}
                
                {/* Authentication Actions */}
                {isAuthenticated ? (
                  <li className="ml-4">
                    <div className="flex items-center space-x-3">
                      <span className="text-gray-300 text-sm">
                        Welcome, {currentUser?.username || 'User'}
                      </span>
                      <button
                        onClick={handleLogout}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                      >
                        Logout
                      </button>
                    </div>
                  </li>
                ) : (
                  <>
                    <li>
                      <Link
                        to="/login"
                        className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                      >
                        Login
                      </Link>
                    </li>
                    <li>
                      <Link
                        to="/register"
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                      >
                        Register
                      </Link>
                    </li>
                  </>
                )}
              </ul>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                type="button"
                className="text-gray-300 hover:text-white hover:bg-gray-700 p-2 rounded-md"
                aria-label="Open main menu"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className={`flex-1 ${className}`}>
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-sm text-gray-300">
              © 2024 ACGS-PGP Framework. All rights reserved.
            </div>
            <div className="flex space-x-6 mt-2 md:mt-0">
              <a
                href="/docs"
                className="text-gray-300 hover:text-white text-sm transition-colors duration-200"
              >
                Documentation
              </a>
              <a
                href="/privacy"
                className="text-gray-300 hover:text-white text-sm transition-colors duration-200"
              >
                Privacy Policy
              </a>
              <a
                href="/terms"
                className="text-gray-300 hover:text-white text-sm transition-colors duration-200"
              >
                Terms of Service
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
