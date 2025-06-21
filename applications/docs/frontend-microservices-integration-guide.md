# Comprehensive Guide: Connecting Frontend Applications to ACGS-PGP Microservices

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Microservices Endpoints](#microservices-endpoints)
3. [Service Layer Implementation](#service-layer-implementation)
4. [Authentication & Security](#authentication--security)
5. [Environment Configuration](#environment-configuration)
6. [Error Handling Patterns](#error-handling-patterns)
7. [Component Integration](#component-integration)
8. [Testing Strategies](#testing-strategies)
9. [Deployment Considerations](#deployment-considerations)
10. [Troubleshooting](#troubleshooting)

## Architecture Overview

The ACGS-PGP framework consists of three core microservices that frontend applications connect to:

### Core Microservices

- **AC Service** (Artificial Constitution): Constitutional principles management
- **GS Service** (Self-Synthesizing Engine): Policy synthesis and validation
- **PGC Service** (Prompt Governance Compiler): Runtime compliance checking
- **Auth Service**: Authentication and authorization
- **Integrity Service**: System integrity monitoring

### Frontend Applications

- **governance-dashboard**: Modern React application with TypeScript
- **legacy-frontend**: Legacy React application for backward compatibility

## Microservices Endpoints

### AC Service (Constitutional Management)

```
Base URL: http://localhost:8001/api/v1
Environment Variable: REACT_APP_AC_API_URL

Endpoints:
- GET    /principles/           # List all constitutional principles
- GET    /principles/{id}       # Get specific principle
- POST   /principles/           # Create new principle
- PUT    /principles/{id}       # Update principle
- DELETE /principles/{id}       # Delete principle
- GET    /constitutional-principles/  # Get constitutional framework
```

### GS Service (Policy Synthesis)

```
Base URL: http://localhost:8003/api/v1
Environment Variable: REACT_APP_GS_API_URL

Endpoints:
- POST   /synthesize/           # Synthesize policies from principles
```

### Auth Service (Authentication)

```
Base URL: http://localhost:8002/auth
Environment Variable: REACT_APP_AUTH_API_URL

Endpoints:
- POST   /token                 # Login (get access token)
- POST   /token/refresh         # Refresh access token
- POST   /users/                # Register new user
- GET    /users/me              # Get current user profile
- POST   /logout                # Logout (clear tokens)
```

### Integrity Service (System Monitoring)

```
Base URL: http://localhost:8006/api/v1
Environment Variable: REACT_APP_INTEGRITY_API_URL

Endpoints:
- GET    /policies/             # Get system policies
- GET    /policies/?status={status}  # Filter policies by status
```

## Service Layer Implementation

### 1. Centralized API Instance

Both frontend applications use a centralized API configuration:

```javascript
// src/services/api.js
import axios from 'axios';
import Cookies from 'js-cookie';

const api = axios.create({
  withCredentials: true, // Send cookies with all requests
});

// Request interceptor for CSRF protection
api.interceptors.request.use(
  (config) => {
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(config.method.toUpperCase())) {
      const csrfToken = Cookies.get('csrf_access_token');
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken;
      } else {
        console.warn('CSRF token not found for mutating request to', config.url);
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const AuthService = (await import('./AuthService')).default;
        await AuthService.refreshToken();
        return api(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        throw refreshError;
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 2. Service Implementation Pattern

Each microservice follows a consistent pattern:

```javascript
// src/services/ACService.js
import api from './api';

const API_URL_PREFIX = process.env.REACT_APP_AC_API_URL || 'http://localhost:8001/api/v1';

const getPrinciples = async () => {
  try {
    const response = await api.get(`${API_URL_PREFIX}/principles/`);
    return response.data;
  } catch (error) {
    console.error(
      'Failed to fetch principles:',
      error.response ? error.response.data : error.message
    );
    throw error.response ? error.response.data : new Error('Failed to fetch principles');
  }
};

const createPrinciple = async (principleData) => {
  try {
    const response = await api.post(`${API_URL_PREFIX}/principles/`, principleData);
    return response.data;
  } catch (error) {
    console.error(
      'Failed to create principle:',
      error.response ? error.response.data : error.message
    );
    throw error.response ? error.response.data : new Error('Failed to create principle');
  }
};

const ACService = {
  getPrinciples,
  getPrincipleById,
  createPrinciple,
  updatePrinciple,
  deletePrinciple,
};

export default ACService;
```

## Authentication & Security

### Cookie-Based Authentication

The system uses HTTP-only cookies for secure token storage:

```javascript
// src/services/AuthService.js
import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8002/auth';

const authAxios = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

const login = async (username, password) => {
  try {
    const response = await authAxios.post('/token', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  } catch (error) {
    console.error('Login failed:', error.response ? error.response.data : error.message);
    throw error.response ? error.response.data : new Error('Login failed');
  }
};

const refreshToken = async () => {
  try {
    const response = await authAxios.post('/token/refresh');
    return response.data;
  } catch (error) {
    console.error('Token refresh failed:', error.response ? error.response.data : error.message);
    throw error.response ? error.response.data : new Error('Token refresh failed');
  }
};
```

### CSRF Protection

All mutating requests automatically include CSRF tokens:

- Token extracted from `csrf_access_token` cookie
- Added as `X-CSRF-Token` header
- Handled automatically by API interceptors

## Environment Configuration

### Required Environment Variables

Create `.env` files in your frontend application root:

```bash
# .env (Development)
REACT_APP_AC_API_URL=http://localhost:8001/api/v1
REACT_APP_GS_API_URL=http://localhost:8003/api/v1
REACT_APP_AUTH_API_URL=http://localhost:8002/auth
REACT_APP_INTEGRITY_API_URL=http://localhost:8006/api/v1
REACT_APP_PGC_API_URL=http://localhost:8004/api/v1

# .env.production
REACT_APP_AC_API_URL=https://api.governance.example.com/ac/v1
REACT_APP_GS_API_URL=https://api.governance.example.com/gs/v1
REACT_APP_AUTH_API_URL=https://auth.governance.example.com
REACT_APP_INTEGRITY_API_URL=https://api.governance.example.com/integrity/v1
REACT_APP_PGC_API_URL=https://api.governance.example.com/pgc/v1
```

### Environment Variable Usage

```javascript
const API_URL_PREFIX = process.env.REACT_APP_AC_API_URL || 'http://localhost:8001/api/v1';
```

## Error Handling Patterns

### Service-Level Error Handling

```javascript
const handleServiceError = (error, operation) => {
  const errorMessage = error.response ? error.response.data : error.message;
  console.error(`${operation} failed:`, errorMessage);
  throw error.response ? error.response.data : new Error(`${operation} failed`);
};
```

### Component-Level Error Handling

```javascript
const [error, setError] = useState('');
const [loading, setLoading] = useState(false);

const handleOperation = async () => {
  setLoading(true);
  setError('');
  try {
    const result = await ACService.getPrinciples();
    // Handle success
  } catch (err) {
    setError(err.message || 'Operation failed');
  } finally {
    setLoading(false);
  }
};
```

## Component Integration

### Authentication Context Integration

```javascript
// src/contexts/AuthContext.js
import React, { createContext, useState, useEffect, useCallback } from 'react';
import AuthService from '../services/AuthService';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  const verifyAuthStatus = useCallback(async () => {
    try {
      const profile = await AuthService.getUserProfile();
      setCurrentUser(profile);
      setIsAuthenticated(true);
    } catch (error) {
      console.warn('Auth verification failed:', error.message);
      setCurrentUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    const loginResponse = await AuthService.login(username, password);
    await verifyAuthStatus();
    return loginResponse;
  };

  const logout = async () => {
    try {
      await AuthService.logout();
    } catch (error) {
      console.error('Error during backend logout:', error);
    } finally {
      setCurrentUser(null);
      setIsAuthenticated(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        isAuthenticated,
        loading,
        login,
        logout,
        verifyAuthStatus,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
```

### Service Integration in Components

```javascript
// Example: Principles Management Component
import React, { useState, useEffect } from 'react';
import ACService from '../services/ACService';

const PrinciplesManager = () => {
  const [principles, setPrinciples] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPrinciples();
  }, []);

  const loadPrinciples = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await ACService.getPrinciples();
      setPrinciples(data);
    } catch (err) {
      setError(err.message || 'Failed to load principles');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePrinciple = async (principleData) => {
    try {
      const newPrinciple = await ACService.createPrinciple(principleData);
      setPrinciples((prev) => [...prev, newPrinciple]);
    } catch (err) {
      setError(err.message || 'Failed to create principle');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return <div>{/* Component JSX */}</div>;
};
```

### Policy Synthesis Integration

```javascript
// Example: Policy Synthesis Component
import React, { useState } from 'react';
import GSService from '../services/GSService';

const PolicySynthesis = () => {
  const [selectedPrinciples, setSelectedPrinciples] = useState([]);
  const [synthesizedPolicies, setSynthesizedPolicies] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSynthesis = async () => {
    setLoading(true);
    try {
      const synthesisRequest = {
        principles: selectedPrinciples.map((id) => ({ id })),
      };
      const result = await GSService.synthesizePolicies(synthesisRequest);
      setSynthesizedPolicies(result.policies || []);
    } catch (error) {
      console.error('Policy synthesis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return <div>{/* Synthesis interface */}</div>;
};
```

## Testing Strategies

### Service Testing

```javascript
// __tests__/services/ACService.test.js
import ACService from '../services/ACService';
import api from '../services/api';

jest.mock('../services/api');
const mockedApi = api as jest.Mocked<typeof api>;

describe('ACService', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('getPrinciples should return principles data', async () => {
        const mockPrinciples = [
            { id: 1, title: 'Test Principle', content: 'Test content' }
        ];
        mockedApi.get.mockResolvedValue({ data: mockPrinciples });

        const result = await ACService.getPrinciples();

        expect(mockedApi.get).toHaveBeenCalledWith(
            expect.stringContaining('/principles/')
        );
        expect(result).toEqual(mockPrinciples);
    });

    test('createPrinciple should handle errors', async () => {
        const errorResponse = { response: { data: 'Creation failed' } };
        mockedApi.post.mockRejectedValue(errorResponse);

        await expect(ACService.createPrinciple({})).rejects.toThrow('Creation failed');
    });
});
```

### Component Testing

```javascript
// __tests__/components/PrinciplesManager.test.js
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import PrinciplesManager from '../components/PrinciplesManager';
import ACService from '../services/ACService';

jest.mock('../services/ACService');
const mockedACService = ACService as jest.Mocked<typeof ACService>;

test('displays principles after loading', async () => {
    const mockPrinciples = [
        { id: 1, title: 'Test Principle', content: 'Test content' }
    ];
    mockedACService.getPrinciples.mockResolvedValue(mockPrinciples);

    render(<PrinciplesManager />);

    await waitFor(() => {
        expect(screen.getByText('Test Principle')).toBeInTheDocument();
    });
});
```

### Integration Testing

```javascript
// __tests__/integration/AuthFlow.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider } from '../contexts/AuthContext';
import LoginPage from '../pages/Auth/LoginPage';
import AuthService from '../services/AuthService';

jest.mock('../services/AuthService');

test('complete authentication flow', async () => {
  const mockUser = { username: 'testuser', email: 'test@example.com' };
  AuthService.login.mockResolvedValue({ message: 'Login successful' });
  AuthService.getUserProfile.mockResolvedValue(mockUser);

  render(
    <AuthProvider>
      <LoginPage />
    </AuthProvider>
  );

  fireEvent.change(screen.getByLabelText(/username/i), {
    target: { value: 'testuser' },
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'password' },
  });
  fireEvent.click(screen.getByRole('button', { name: /login/i }));

  await waitFor(() => {
    expect(AuthService.login).toHaveBeenCalledWith('testuser', 'password');
  });
});
```

## Deployment Considerations

### Production Environment Setup

```bash
# Production environment variables
REACT_APP_AC_API_URL=https://api.governance.example.com/ac/v1
REACT_APP_GS_API_URL=https://api.governance.example.com/gs/v1
REACT_APP_AUTH_API_URL=https://auth.governance.example.com
REACT_APP_INTEGRITY_API_URL=https://api.governance.example.com/integrity/v1

# Security considerations
REACT_APP_ENABLE_HTTPS_ONLY=true
REACT_APP_SECURE_COOKIES=true
```

### Docker Configuration

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

### CORS Configuration

Ensure backend services are configured for CORS:

```python
# Backend CORS configuration example
CORS_ORIGINS = [
    "http://localhost:3000",  # Development
    "https://dashboard.governance.example.com"  # Production
]
```

### Load Balancing and High Availability

```yaml
# docker-compose.yml for production
version: '3.8'
services:
  frontend:
    build: .
    ports:
      - '3000:3000'
    environment:
      - NODE_ENV=production
    depends_on:
      - nginx
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped
```

## Troubleshooting

### Common Issues and Solutions

#### 1. CSRF Token Missing

**Problem**: `CSRF token not found for mutating request`
**Solution**:

- Verify backend sets `csrf_access_token` cookie
- Check cookie domain and path settings
- Ensure `withCredentials: true` in API configuration

#### 2. Authentication Failures

**Problem**: 401 errors on authenticated requests
**Solution**:

- Check token refresh mechanism
- Verify cookie settings (HttpOnly, Secure, SameSite)
- Ensure proper CORS configuration

#### 3. Service Connection Issues

**Problem**: Network errors connecting to microservices
**Solution**:

- Verify environment variables are set correctly
- Check microservice health endpoints
- Validate network connectivity and firewall rules

#### 4. Development vs Production Differences

**Problem**: Works in development but fails in production
**Solution**:

- Check HTTPS requirements in production
- Verify production environment variables
- Ensure proper SSL certificate configuration

### Debug Tools

```javascript
// Debug helper for API calls
const debugApiCall = (serviceName, method, url, data = null) => {
  console.group(`🔍 ${serviceName} API Call`);
  console.log('Method:', method);
  console.log('URL:', url);
  if (data) console.log('Data:', data);
  console.log('Timestamp:', new Date().toISOString());
  console.groupEnd();
};

// Usage in services
const response = await api.get(url);
debugApiCall('AC Service', 'GET', url);
```

### Health Check Implementation

```javascript
// src/services/HealthService.js
import api from './api';

const checkServiceHealth = async (serviceName, baseUrl) => {
  try {
    const response = await api.get(`${baseUrl}/health`);
    return { service: serviceName, status: 'healthy', data: response.data };
  } catch (error) {
    return { service: serviceName, status: 'unhealthy', error: error.message };
  }
};

const checkAllServices = async () => {
  const services = [
    { name: 'AC Service', url: process.env.REACT_APP_AC_API_URL },
    { name: 'GS Service', url: process.env.REACT_APP_GS_API_URL },
    { name: 'Auth Service', url: process.env.REACT_APP_AUTH_API_URL },
    { name: 'Integrity Service', url: process.env.REACT_APP_INTEGRITY_API_URL },
  ];

  const healthChecks = await Promise.all(
    services.map((service) => checkServiceHealth(service.name, service.url))
  );

  return healthChecks;
};

export default { checkServiceHealth, checkAllServices };
```

### Performance Monitoring

```javascript
// src/utils/performanceMonitor.js
class PerformanceMonitor {
  static startTimer(operation) {
    const startTime = performance.now();
    return {
      end: () => {
        const endTime = performance.now();
        const duration = endTime - startTime;
        console.log(`⏱️ ${operation} took ${duration.toFixed(2)}ms`);
        return duration;
      },
    };
  }

  static async measureApiCall(serviceName, apiCall) {
    const timer = this.startTimer(`${serviceName} API Call`);
    try {
      const result = await apiCall();
      timer.end();
      return result;
    } catch (error) {
      timer.end();
      throw error;
    }
  }
}

// Usage
const principles = await PerformanceMonitor.measureApiCall('AC Service', () =>
  ACService.getPrinciples()
);
```

## Best Practices Summary

1. **Centralized API Configuration**: Use a single API instance with interceptors
2. **Environment Variables**: Always use environment variables for service URLs
3. **Error Handling**: Implement consistent error handling across all services
4. **Authentication**: Use HTTP-only cookies with CSRF protection
5. **Testing**: Mock services for unit tests, use integration tests for API calls
6. **Security**: Always validate inputs and handle sensitive data properly
7. **Monitoring**: Implement health checks and logging for production deployments
8. **Documentation**: Keep service interfaces documented and up-to-date
9. **Performance**: Monitor API call performance and implement caching where appropriate
10. **Resilience**: Implement retry logic and graceful degradation for service failures

## Quick Start Checklist

### For New Frontend Applications

- [ ] Set up centralized API instance with interceptors
- [ ] Configure environment variables for all microservices
- [ ] Implement authentication context and protected routes
- [ ] Create service modules for each microservice
- [ ] Add error handling and loading states to components
- [ ] Set up testing framework with service mocks
- [ ] Configure CORS for development and production
- [ ] Implement health checks for service monitoring
- [ ] Add performance monitoring and logging
- [ ] Document API integration patterns

### For Existing Applications

- [ ] Audit current API integration patterns
- [ ] Migrate to centralized API configuration
- [ ] Update authentication to use HTTP-only cookies
- [ ] Add CSRF protection to mutating requests
- [ ] Implement automatic token refresh
- [ ] Add comprehensive error handling
- [ ] Update tests to mock service dependencies
- [ ] Configure production environment variables
- [ ] Add health monitoring and alerting
- [ ] Update documentation and team training

This guide provides a complete foundation for integrating frontend applications with the ACGS-PGP microservices architecture. Follow these patterns for consistent, secure, and maintainable integrations.
