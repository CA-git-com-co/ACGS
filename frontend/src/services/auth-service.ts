/**
 * Authentication Service Integration
 * Constitutional Hash: cdd01ef066bc6cf2
 *
 * Frontend integration for Authentication Service with constitutional compliance.
 */

import { apiClient } from './api-client';
import { CONFIG, getServiceUrl } from '@/config';
import type { APIResponse } from '@/types';

// Authentication types
interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  permissions: string[];
  constitutionalCompliance: {
    hash: string;
    level: 'ADMIN' | 'USER' | 'GUEST';
    lastValidated: string;
  };
}

interface AuthToken {
  accessToken: string;
  refreshToken: string;
  expiresAt: string;
  tokenType: 'Bearer';
  constitutionalHash: string;
}

interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
  constitutionalHash: string;
}

interface LoginResponse {
  user: User;
  token: AuthToken;
  sessionId: string;
  constitutionalCompliance: {
    hash: string;
    valid: boolean;
    permissions: string[];
  };
}

/**
 * Authentication Service Client
 */
export class AuthService {
  private baseUrl: string;
  private currentUser: User | null = null;
  private currentToken: AuthToken | null = null;
  private tokenRefreshTimer: NodeJS.Timeout | null = null;

  constructor() {
    this.baseUrl = getServiceUrl('AUTHENTICATION');
    this.loadStoredAuth();
  }

  /**
   * Login with email and password
   */
  async login(email: string, password: string, rememberMe = false): Promise<LoginResponse> {
    try {
      const request: LoginRequest = {
        email,
        password,
        rememberMe,
        constitutionalHash: CONFIG.constitutional.hash,
      };

      const response = await apiClient.post<LoginResponse>(
        '/api/auth/login',
        request,
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );

      // Validate constitutional compliance
      if (response.data.constitutionalCompliance.hash !== CONFIG.constitutional.hash) {
        throw new Error('Constitutional hash mismatch in login response');
      }

      // Store authentication data
      this.currentUser = response.data.user;
      this.currentToken = response.data.token;
      
      // Set token in API client
      apiClient.setAuthToken(response.data.token.accessToken);
      
      // Store in localStorage if remember me is enabled
      if (rememberMe) {
        this.storeAuth(response.data.user, response.data.token);
      }

      // Setup token refresh
      this.setupTokenRefresh();

      return response.data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  /**
   * Refresh authentication token
   */
  async refreshToken(): Promise<AuthToken> {
    if (!this.currentToken?.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await apiClient.post<{ token: AuthToken }>(
        '/api/auth/refresh',
        {
          refreshToken: this.currentToken.refreshToken,
          constitutionalHash: CONFIG.constitutional.hash,
        },
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );

      // Validate constitutional compliance
      if (response.data.token.constitutionalHash !== CONFIG.constitutional.hash) {
        throw new Error('Constitutional hash mismatch in token refresh');
      }

      // Update stored token
      this.currentToken = response.data.token;
      apiClient.setAuthToken(response.data.token.accessToken);
      
      // Update localStorage
      if (this.currentUser) {
        this.storeAuth(this.currentUser, response.data.token);
      }

      // Setup next refresh
      this.setupTokenRefresh();

      return response.data.token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // Clear invalid auth data
      this.logout();
      throw error;
    }
  }

  /**
   * Logout and clear authentication data
   */
  async logout(): Promise<void> {
    try {
      if (this.currentToken) {
        await apiClient.post(
          '/api/auth/logout',
          {
            refreshToken: this.currentToken.refreshToken,
            constitutionalHash: CONFIG.constitutional.hash,
          },
          {
            headers: {
              'X-Constitutional-Hash': CONFIG.constitutional.hash,
            },
          }
        );
      }
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      this.clearAuth();
    }
  }

  /**
   * Get current user
   */
  getCurrentUser(): User | null {
    return this.currentUser;
  }

  /**
   * Get current token
   */
  getCurrentToken(): AuthToken | null {
    return this.currentToken;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.currentUser !== null && this.currentToken !== null && !this.isTokenExpired();
  }

  /**
   * Check if user has specific permission
   */
  hasPermission(permission: string): boolean {
    return this.currentUser?.permissions.includes(permission) || false;
  }

  /**
   * Check if user has any of the specified roles
   */
  hasRole(roles: string[]): boolean {
    return this.currentUser ? roles.includes(this.currentUser.role) : false;
  }

  /**
   * Get user's constitutional compliance level
   */
  getConstitutionalComplianceLevel(): 'ADMIN' | 'USER' | 'GUEST' | null {
    return this.currentUser?.constitutionalCompliance.level || null;
  }

  /**
   * Validate constitutional compliance
   */
  async validateConstitutionalCompliance(): Promise<boolean> {
    if (!this.currentUser) return false;

    try {
      const response = await apiClient.get<{ valid: boolean }>(
        '/api/auth/validate-compliance',
        {},
        {
          headers: {
            'X-Constitutional-Hash': CONFIG.constitutional.hash,
          },
        }
      );

      return response.data.valid;
    } catch (error) {
      console.error('Constitutional compliance validation failed:', error);
      return false;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy' | 'degraded';
    checks: Record<string, boolean>;
    constitutionalHash: string;
  }> {
    try {
      const response = await apiClient.get<any>(
        '/health',
        {},
        { retry: false }
      );

      return {
        status: response.data.status,
        checks: response.data.checks || {},
        constitutionalHash: CONFIG.constitutional.hash,
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        checks: { connection: false },
        constitutionalHash: CONFIG.constitutional.hash,
      };
    }
  }

  private isTokenExpired(): boolean {
    if (!this.currentToken) return true;
    
    const expiresAt = new Date(this.currentToken.expiresAt);
    const now = new Date();
    
    // Consider token expired if it expires within 5 minutes
    return expiresAt.getTime() - now.getTime() < 5 * 60 * 1000;
  }

  private setupTokenRefresh(): void {
    if (this.tokenRefreshTimer) {
      clearTimeout(this.tokenRefreshTimer);
    }

    if (!this.currentToken) return;

    const expiresAt = new Date(this.currentToken.expiresAt);
    const now = new Date();
    
    // Refresh token 10 minutes before expiry
    const refreshAt = expiresAt.getTime() - now.getTime() - (10 * 60 * 1000);
    
    if (refreshAt > 0) {
      this.tokenRefreshTimer = setTimeout(() => {
        this.refreshToken().catch(console.error);
      }, refreshAt);
    }
  }

  private storeAuth(user: User, token: AuthToken): void {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem('auth_user', JSON.stringify(user));
        localStorage.setItem('auth_token', JSON.stringify(token));
      } catch (error) {
        console.error('Failed to store auth data:', error);
      }
    }
  }

  private loadStoredAuth(): void {
    if (typeof window !== 'undefined') {
      try {
        const storedUser = localStorage.getItem('auth_user');
        const storedToken = localStorage.getItem('auth_token');
        
        if (storedUser && storedToken) {
          this.currentUser = JSON.parse(storedUser);
          this.currentToken = JSON.parse(storedToken);
          
          // Validate constitutional hash
          if (this.currentUser?.constitutionalCompliance.hash !== CONFIG.constitutional.hash ||
              this.currentToken?.constitutionalHash !== CONFIG.constitutional.hash) {
            this.clearAuth();
            return;
          }
          
          // Check if token is not expired
          if (!this.isTokenExpired()) {
            apiClient.setAuthToken(this.currentToken.accessToken);
            this.setupTokenRefresh();
          } else {
            this.clearAuth();
          }
        }
      } catch (error) {
        console.error('Failed to load stored auth:', error);
        this.clearAuth();
      }
    }
  }

  private clearAuth(): void {
    this.currentUser = null;
    this.currentToken = null;
    
    if (this.tokenRefreshTimer) {
      clearTimeout(this.tokenRefreshTimer);
      this.tokenRefreshTimer = null;
    }
    
    apiClient.removeAuthToken();
    
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_user');
      localStorage.removeItem('auth_token');
    }
  }
}

// Export singleton instance
export const authService = new AuthService();

// Export types
export type {
  User,
  AuthToken,
  LoginRequest,
  LoginResponse,
};
