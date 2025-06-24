import React, { createContext, useState, useEffect, useContext } from 'react';
import AuthService from '../services/AuthService';
import { User, AuthContextType } from '../types/governance';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const user = await AuthService.getUserProfile();
        setCurrentUser(user);
        setIsAuthenticated(true);
      } catch (error) {
        setCurrentUser(null);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      await AuthService.login(username, password);
      const user = await AuthService.getUserProfile();
      setCurrentUser(user);
      setIsAuthenticated(true);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await AuthService.logout();
    } finally {
      setCurrentUser(null);
      setIsAuthenticated(false);
      setIsLoading(false);
    }
  };

  const refreshToken = async () => {
    try {
      await AuthService.refreshToken();
      // Token is refreshed, but user data should remain the same
    } catch (error) {
      // If refresh fails, logout the user
      await logout();
      throw error;
    }
  };

  const value: AuthContextType = {
    currentUser,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshToken
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export { AuthContext };
