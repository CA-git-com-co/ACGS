# Breaking Changes and Migration Guide

## ACGS-PGP Legacy Frontend Deprecation

**Version**: 1.0  
**Date**: 2025-06-15  
**Scope**: Complete guide for migrating from legacy-frontend to shared architecture  
**Audience**: Developers, DevOps, and System Administrators

---

## Overview

This guide documents all breaking changes introduced during the legacy-frontend deprecation and provides step-by-step migration instructions for each affected component and service.

---

## Breaking Changes Summary

### 🔴 CRITICAL BREAKING CHANGES

#### 1. App Entry Point Consolidation

**Change**: Removal of `App.js` in favor of single `App.tsx` entry point  
**Impact**: Build configuration and import paths  
**Timeline**: Day 11 of migration

#### 2. Quantumagi Dashboard Component

**Change**: Migration from `QuantumagiDashboard.jsx` to shared blockchain components  
**Impact**: Solana wallet integration and blockchain functionality  
**Timeline**: Day 9 of migration (CRITICAL)

#### 3. Constitutional Council Dashboard

**Change**: Migration from `ConstitutionalCouncilDashboard.js` to shared dashboard  
**Impact**: Governance workflows and real-time monitoring  
**Timeline**: Day 7 of migration

### 🟡 HIGH IMPACT BREAKING CHANGES

#### 4. Service Architecture Changes

**Change**: Migration from legacy services to shared service architecture  
**Impact**: API contracts and service integration patterns  
**Timeline**: Days 5-6 of migration

#### 5. Styling System Migration

**Change**: Removal of legacy CSS files in favor of shared theme system  
**Impact**: Component styling and visual consistency  
**Timeline**: Day 2 of migration

#### 6. Error Handling Migration

**Change**: Migration from `errorHandler.js` to shared error boundaries  
**Impact**: Error reporting and recovery mechanisms  
**Timeline**: Day 8 of migration

---

## Migration Instructions

### 1. App Entry Point Migration

#### Before (Legacy):

```javascript
// App.js
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>{/* Legacy routing */}</Router>
    </AuthProvider>
  );
}
```

#### After (Shared):

```typescript
// App.tsx
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from '@acgs/shared/contexts/AuthContext';
import { Layout } from '@acgs/shared/components';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          {/* Modern routing with shared components */}
        </Layout>
      </Router>
    </AuthProvider>
  );
};
```

#### Migration Steps:

1. Update imports to use shared components
2. Convert to TypeScript if needed
3. Update routing configuration
4. Test application initialization
5. Remove legacy App.js file

### 2. Service Migration

#### Before (Legacy):

```javascript
// services/PublicConsultationService.js
import api from './api';

class PublicConsultationService {
  async getProposals() {
    const response = await api.get('/proposals');
    return response.data;
  }
}
```

#### After (Shared):

```javascript
// Using shared service
import { PublicConsultationService } from '@acgs/shared/services';

// Service now available through shared package
const proposals = await PublicConsultationService.getProposals();
```

#### Migration Steps:

1. Identify legacy service usage
2. Update imports to shared services
3. Verify API contract compatibility
4. Test service functionality
5. Remove legacy service files

### 3. Component Migration

#### Before (Legacy):

```javascript
// components/ConstitutionalCouncilDashboard.js
import React, { useState, useEffect } from 'react';
import ACService from '../services/ACService';

const ConstitutionalCouncilDashboard = () => {
  const [principles, setPrinciples] = useState([]);

  useEffect(() => {
    ACService.getPrinciples().then(setPrinciples);
  }, []);

  return <div className="dashboard">{/* Legacy dashboard implementation */}</div>;
};
```

#### After (Shared):

```typescript
// Using shared component
import { ConstitutionalDashboard } from '@acgs/shared/components/dashboard';

const Dashboard: React.FC = () => {
  return <ConstitutionalDashboard />;
};
```

#### Migration Steps:

1. Identify component functionality
2. Map to shared component equivalent
3. Update imports and usage
4. Test component functionality
5. Remove legacy component files

### 4. Styling Migration

#### Before (Legacy):

```css
/* App.css */
.dashboard {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
}

.nav-links {
  display: flex;
  gap: 16px;
}
```

#### After (Shared):

```typescript
// Using shared theme
import { useTheme } from '@acgs/shared/styles/theme';

const Dashboard: React.FC = () => {
  const theme = useTheme();

  return (
    <div style={{
      backgroundColor: theme.colors.background.secondary,
      padding: theme.spacing.lg,
      borderRadius: theme.borderRadius.md
    }}>
      {/* Component content */}
    </div>
  );
};
```

#### Migration Steps:

1. Audit legacy CSS usage
2. Map styles to shared theme tokens
3. Update component styling
4. Test visual consistency
5. Remove legacy CSS files

---

## Feature Flag Implementation

### Setup Feature Flags

```typescript
// Feature flag configuration
import { FeatureFlagProvider } from '@acgs/shared/utils/featureFlags';

const featureFlags = {
  useSharedDashboard: process.env.REACT_APP_USE_SHARED_DASHBOARD === 'true',
  useSharedServices: process.env.REACT_APP_USE_SHARED_SERVICES === 'true',
  useQuantumagiShared: process.env.REACT_APP_USE_QUANTUMAGI_SHARED === 'true'
};

export const App: React.FC = () => {
  return (
    <FeatureFlagProvider flags={featureFlags}>
      {/* App content */}
    </FeatureFlagProvider>
  );
};
```

### Using Feature Flags

```typescript
// Component with feature flag
import { useFeatureFlag } from '@acgs/shared/utils/featureFlags';
import LegacyDashboard from './LegacyDashboard';
import { SharedDashboard } from '@acgs/shared/components';

const Dashboard: React.FC = () => {
  const useSharedDashboard = useFeatureFlag('useSharedDashboard');

  return useSharedDashboard ? <SharedDashboard /> : <LegacyDashboard />;
};
```

---

## Testing and Validation

### Component Testing

```typescript
// Test both legacy and shared components
import { render, screen } from '@testing-library/react';
import { Dashboard } from './Dashboard';
import { FeatureFlagProvider } from '@acgs/shared/utils/featureFlags';

describe('Dashboard Migration', () => {
  it('renders legacy dashboard when flag is disabled', () => {
    render(
      <FeatureFlagProvider flags={{ useSharedDashboard: false }}>
        <Dashboard />
      </FeatureFlagProvider>
    );
    expect(screen.getByTestId('legacy-dashboard')).toBeInTheDocument();
  });

  it('renders shared dashboard when flag is enabled', () => {
    render(
      <FeatureFlagProvider flags={{ useSharedDashboard: true }}>
        <Dashboard />
      </FeatureFlagProvider>
    );
    expect(screen.getByTestId('shared-dashboard')).toBeInTheDocument();
  });
});
```

### Service Testing

```typescript
// Test service migration
import { PublicConsultationService } from '@acgs/shared/services';

describe('Service Migration', () => {
  it('maintains API contract compatibility', async () => {
    const proposals = await PublicConsultationService.getProposals();
    expect(proposals).toHaveProperty('data');
    expect(Array.isArray(proposals.data)).toBe(true);
  });
});
```

---

## Rollback Procedures

### Emergency Rollback

1. **Immediate Rollback via Feature Flags**

   ```bash
   # Disable shared components
   export REACT_APP_USE_SHARED_DASHBOARD=false
   export REACT_APP_USE_SHARED_SERVICES=false
   export REACT_APP_USE_QUANTUMAGI_SHARED=false

   # Restart application
   npm restart
   ```

2. **Git Rollback**

   ```bash
   # Rollback to previous stable commit
   git revert <migration-commit-hash>
   git push origin main
   ```

3. **Service Rollback**
   ```bash
   # Restore legacy service endpoints
   kubectl rollout undo deployment/legacy-frontend
   ```

### Validation After Rollback

1. Test all governance workflows
2. Verify Quantumagi Solana functionality
3. Check service connectivity
4. Validate user authentication
5. Monitor system performance

---

## Common Issues and Solutions

### Issue 1: Import Path Errors

**Problem**: Module not found errors after migration  
**Solution**: Update import paths to use @acgs/shared package

```typescript
// Before
import AuthService from './services/AuthService';

// After
import { AuthService } from '@acgs/shared/services';
```

### Issue 2: Styling Inconsistencies

**Problem**: Visual differences after CSS migration  
**Solution**: Map legacy styles to shared theme tokens

```typescript
// Use theme tokens instead of hardcoded values
const theme = useTheme();
const styles = {
  backgroundColor: theme.colors.background.primary, // Instead of '#ffffff'
  padding: theme.spacing.md, // Instead of '16px'
};
```

### Issue 3: Service API Incompatibility

**Problem**: Different API contracts between legacy and shared services  
**Solution**: Implement adapter pattern for backward compatibility

```typescript
// Service adapter
class LegacyServiceAdapter {
  async getProposals() {
    const result = await SharedService.getProposals();
    // Transform data to match legacy format
    return { data: result.proposals };
  }
}
```

---

## Support and Resources

### Documentation

- [Shared Components Documentation](../shared/README.md)
- [Service Integration Guide](./service-integration-guide.md)
- [Testing Guidelines](../shared/TESTING.md)

### Emergency Contacts

- **Development Team**: dev-team@acgs.org
- **DevOps Team**: devops@acgs.org
- **System Administrator**: sysadmin@acgs.org

### Monitoring and Alerts

- **Application Monitoring**: Grafana Dashboard
- **Error Tracking**: Sentry Integration
- **Performance Monitoring**: New Relic APM

---

**Migration Guide Version**: 1.0  
**Last Updated**: 2025-06-15  
**Next Review**: After Phase 3 completion
