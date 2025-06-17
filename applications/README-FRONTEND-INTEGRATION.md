# ACGS-PGP Frontend Microservices Integration

This repository contains comprehensive documentation and tools for integrating frontend applications with the ACGS-PGP (Artificial Constitution, Self-Synthesizing, Prompt Governance Compiler) microservices framework.

## 📋 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Access to ACGS-PGP microservices (AC, GS, PGC, Auth, Integrity)
- Basic understanding of React and modern JavaScript

### 1. Choose Your Frontend Application

This repository contains two frontend applications:

- **`governance-dashboard/`** - Modern React application with TypeScript
- **`legacy-applications/governance-dashboard/`** - Legacy React application for backward compatibility

### 2. Run the Setup Script

Navigate to your chosen frontend directory and run the setup script:

```bash
cd governance-dashboard  # or legacy-frontend
../scripts/setup-frontend-integration.sh
```

This script will:
- ✅ Check and install required dependencies
- ✅ Create environment configuration files
- ✅ Verify service structure
- ✅ Set up health check utilities
- ✅ Add helpful npm scripts

### 3. Configure Environment Variables

Update the `.env` file created by the setup script:

```bash
# Copy and customize the environment file
cp .env.example .env
# Edit .env with your specific microservice URLs
```

### 4. Verify Service Connectivity

Run the health check to ensure all microservices are accessible:

```bash
npm run health-check
```

## 📚 Documentation

### Core Documentation
- **[Frontend Microservices Integration Guide](docs/frontend-microservices-integration-guide.md)** - Comprehensive integration guide
- **[Deployment Guide](docs/deployment-guide.md)** - Production deployment instructions
- **[Implementation Plan](docs/implementation-plan.md)** - Development roadmap

### Key Integration Patterns

#### 1. Centralized API Configuration
```javascript
// src/services/api.js
import axios from 'axios';
import Cookies from 'js-cookie';

const api = axios.create({
    withCredentials: true,
});

// Automatic CSRF token handling
api.interceptors.request.use(config => {
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(config.method.toUpperCase())) {
        const csrfToken = Cookies.get('csrf_access_token');
        if (csrfToken) {
            config.headers['X-CSRF-Token'] = csrfToken;
        }
    }
    return config;
});
```

#### 2. Service Layer Pattern
```javascript
// src/services/ACService.js
import api from './api';

const API_URL_PREFIX = process.env.REACT_APP_AC_API_URL || 'http://localhost:8001/api/v1';

const getPrinciples = async () => {
    try {
        const response = await api.get(`${API_URL_PREFIX}/principles/`);
        return response.data;
    } catch (error) {
        console.error('Failed to fetch principles:', error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Failed to fetch principles');
    }
};
```

#### 3. Authentication Context
```javascript
// src/contexts/AuthContext.js
export const AuthProvider = ({ children }) => {
    const [currentUser, setCurrentUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    
    const login = async (username, password) => {
        const loginResponse = await AuthService.login(username, password);
        await verifyAuthStatus();
        return loginResponse;
    };
    
    // ... rest of context implementation
};
```

## 🏗️ Architecture Overview

### Microservices
- **AC Service** (Port 8001) - Constitutional principles management
- **GS Service** (Port 8003) - Policy synthesis and validation  
- **PGC Service** (Port 8004) - Runtime compliance checking
- **Auth Service** (Port 8002) - Authentication and authorization
- **Integrity Service** (Port 8006) - System integrity monitoring

### Frontend Applications
- **governance-dashboard** - Modern TypeScript React app
- **legacy-frontend** - Legacy JavaScript React app

### Security Features
- HTTP-only cookie authentication
- Automatic CSRF protection
- Token refresh handling
- Secure CORS configuration

## 🧪 Testing

### Run Tests
```bash
# Unit tests
npm test

# Integration tests
npm run integration-test

# Test coverage
npm run test:coverage
```

### Test Structure
```
src/
├── __tests__/
│   ├── services/           # Service layer tests
│   ├── components/         # Component tests
│   └── integration/        # Integration tests
└── utils/test/            # Test utilities and mocks
```

## 🚀 Development Workflow

### 1. Start Development Environment
```bash
# Install dependencies
npm install

# Start development server
npm start

# In another terminal, check service health
npm run health-check
```

### 2. Common Development Tasks

#### Adding a New Service Integration
1. Create service file in `src/services/`
2. Add environment variable for service URL
3. Implement service methods following the established pattern
4. Add tests for the service
5. Update documentation

#### Adding Authentication to a Component
```javascript
import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

const MyComponent = () => {
    const { currentUser, isAuthenticated } = useContext(AuthContext);
    
    if (!isAuthenticated) {
        return <div>Please log in</div>;
    }
    
    return <div>Welcome, {currentUser.username}!</div>;
};
```

## 🔧 Troubleshooting

### Common Issues

#### CSRF Token Missing
```
Error: CSRF token not found for mutating request
```
**Solution**: Verify backend sets `csrf_access_token` cookie and `withCredentials: true` is set.

#### 401 Authentication Errors
```
Error: 401 Unauthorized
```
**Solution**: Check token refresh mechanism and cookie settings.

#### Service Connection Issues
```
Error: Network Error
```
**Solution**: Verify environment variables and microservice availability.

### Debug Tools

#### Enable API Request Logging
```bash
# In .env file
REACT_APP_LOG_API_REQUESTS=true
REACT_APP_DEBUG_MODE=true
```

#### Health Check All Services
```bash
npm run health-check
```

## 📦 Production Deployment

### Environment Configuration
```bash
# Production environment variables
REACT_APP_AC_API_URL=https://api.governance.example.com/ac/v1
REACT_APP_GS_API_URL=https://api.governance.example.com/gs/v1
REACT_APP_AUTH_API_URL=https://auth.governance.example.com
REACT_APP_ENABLE_HTTPS_ONLY=true
REACT_APP_SECURE_COOKIES=true
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🤝 Contributing

### Development Guidelines
1. Follow the established service integration patterns
2. Add tests for new functionality
3. Update documentation for API changes
4. Use TypeScript for new components (governance-dashboard)
5. Maintain backward compatibility (legacy-frontend)

### Code Style
- Use ESLint and Prettier for code formatting
- Follow React best practices and hooks patterns
- Implement proper error handling and loading states
- Use environment variables for all configuration

## 📞 Support

### Resources
- [Integration Guide](docs/frontend-microservices-integration-guide.md) - Complete technical documentation
- [API Documentation](docs/api-documentation.md) - Microservice API reference
- [Troubleshooting Guide](docs/troubleshooting.md) - Common issues and solutions

### Getting Help
1. Check the troubleshooting section in the integration guide
2. Run `npm run health-check` to verify service connectivity
3. Review console logs for detailed error messages
4. Consult the API documentation for endpoint specifications

---

**Happy coding with ACGS-PGP! 🚀**
