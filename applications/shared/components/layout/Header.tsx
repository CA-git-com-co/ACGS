import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface HeaderProps {
  className?: string;
}

interface NavItem {
  path: string;
  label: string;
  requiresAuth?: boolean;
  adminOnly?: boolean;
}

const Header: React.FC<HeaderProps> = ({ className = '' }) => {
  const { currentUser, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const publicNavItems: NavItem[] = [
    { path: '/', label: 'Home' },
    { path: '/public-consultation', label: 'Public Consultation' },
  ];

  const authenticatedNavItems: NavItem[] = [
    { path: '/ac-management', label: 'AC Management', requiresAuth: true },
    { path: '/policy-synthesis', label: 'Synthesize', requiresAuth: true },
    { path: '/policies', label: 'View Policies', requiresAuth: true },
    { path: '/constitutional-council-dashboard', label: 'Dashboard', requiresAuth: true },
    { path: '/compliance-checker', label: 'Compliance', requiresAuth: true },
  ];

  const isActivePath = (path: string): boolean => {
    return location.pathname === path || 
           (path !== '/' && location.pathname.startsWith(path));
  };

  const renderNavItem = (item: NavItem, mobile: boolean = false) => (
    <Link
      key={item.path}
      to={item.path}
      className={`
        ${mobile 
          ? 'block px-3 py-2 text-base font-medium' 
          : 'px-3 py-2 rounded-md text-sm font-medium'
        }
        transition-colors duration-200
        ${isActivePath(item.path)
          ? mobile 
            ? 'bg-gray-900 text-white' 
            : 'bg-blue-700 text-white'
          : mobile
            ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
            : 'text-gray-300 hover:bg-gray-700 hover:text-white'
        }
      `}
      onClick={() => mobile && setIsMobileMenuOpen(false)}
    >
      {item.label}
    </Link>
  );

  return (
    <header className={`bg-gray-800 shadow-lg ${className}`}>
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

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="flex items-center space-x-4">
              {publicNavItems.map(item => renderNavItem(item))}
              
              {isAuthenticated && authenticatedNavItems.map(item => renderNavItem(item))}
              
              {/* Authentication Actions */}
              {isAuthenticated ? (
                <div className="flex items-center space-x-3 ml-4">
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
              ) : (
                <div className="flex items-center space-x-2 ml-4">
                  <Link
                    to="/login"
                    className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                  >
                    Register
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              type="button"
              className="text-gray-300 hover:text-white hover:bg-gray-700 p-2 rounded-md"
              aria-label="Open main menu"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isMobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-gray-700">
              {publicNavItems.map(item => renderNavItem(item, true))}
              
              {isAuthenticated && authenticatedNavItems.map(item => renderNavItem(item, true))}
              
              {/* Mobile Authentication Actions */}
              <div className="border-t border-gray-600 pt-4 pb-3">
                {isAuthenticated ? (
                  <div className="flex items-center px-3">
                    <div className="flex-shrink-0">
                      <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center">
                        <span className="text-white text-sm font-medium">
                          {currentUser?.username?.charAt(0).toUpperCase() || 'U'}
                        </span>
                      </div>
                    </div>
                    <div className="ml-3">
                      <div className="text-base font-medium text-white">
                        {currentUser?.username || 'User'}
                      </div>
                      <button
                        onClick={handleLogout}
                        className="text-sm text-gray-300 hover:text-white"
                      >
                        Logout
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-1">
                    <Link
                      to="/login"
                      className="block px-3 py-2 text-base font-medium text-gray-300 hover:bg-gray-700 hover:text-white"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Login
                    </Link>
                    <Link
                      to="/register"
                      className="block px-3 py-2 text-base font-medium text-gray-300 hover:bg-gray-700 hover:text-white"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Register
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
};

export default Header;
