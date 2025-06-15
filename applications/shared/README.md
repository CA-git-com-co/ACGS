# ACGS-PGP Shared Module

This directory contains shared components, services, types, and contexts for the ACGS-PGP Framework applications.

## Structure

```
shared/
├── components/          # Shared UI components
│   ├── PrincipleCard.tsx
│   ├── ProtectedRoute.tsx
│   └── index.ts
├── contexts/            # React context providers
│   ├── AuthContext.tsx
│   └── index.ts
├── services/            # API communication modules
│   ├── api.js
│   ├── ACService.js
│   ├── GSService.js
│   ├── AuthService.js
│   └── index.js
├── types/               # TypeScript interfaces and types
│   └── governance.ts
├── hooks/               # Custom React hooks
│   ├── useKeyboard.ts
│   └── useLocalStorage.ts
├── package.json
├── tsconfig.json
└── index.ts
```

## Usage

### In governance-dashboard or legacy-frontend

```javascript
// Import services
import { ACService, GSService, AuthService } from '@acgs/shared/services';

// Import components
import { PrincipleCard, ProtectedRoute } from '@acgs/shared/components';

// Import contexts
import { AuthProvider, useAuth } from '@acgs/shared/contexts';

// Import types
import { Principle, Policy, ComplianceResult } from '@acgs/shared/types/governance';
```

### Services

#### ACService (Artificial Constitution)
- `getPrinciples()` - Fetch all principles
- `getPrincipleById(id)` - Fetch principle by ID
- `createPrinciple(principleData)` - Create new principle
- `updatePrinciple(id, principleData)` - Update existing principle
- `deletePrinciple(id)` - Delete principle

#### GSService (Self-Synthesizing Engine)
- `synthesizePolicies(synthesisRequestData)` - Synthesize policies from principles
- `analyzeAmendmentImpact(amendmentData)` - Analyze amendment impact
- `validateSemanticConsistency(validationData)` - Validate semantic consistency
- `detectPolicyConflicts(conflictData)` - Detect policy conflicts

#### AuthService
- `login(username, password)` - User login
- `register(username, email, password)` - User registration
- `logout()` - User logout
- `getUserProfile()` - Get current user profile
- `refreshToken()` - Refresh authentication token

### Components

#### PrincipleCard
```tsx
<PrincipleCard 
  principle={principle}
  onEdit={(principle) => handleEdit(principle)}
  onDelete={(id) => handleDelete(id)}
/>
```

#### ProtectedRoute
```tsx
<ProtectedRoute requiredRole="admin">
  <AdminPanel />
</ProtectedRoute>
```

### Authentication Context

```tsx
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

function Dashboard() {
  const { currentUser, isAuthenticated, logout } = useAuth();
  
  return (
    <div>
      <h1>Welcome, {currentUser?.username}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

## Environment Variables

The shared services use the following environment variables:

- `REACT_APP_AC_API_URL` - AC Service URL (default: http://localhost:8001/api/v1)
- `REACT_APP_GS_API_URL` - GS Service URL (default: http://localhost:8003/api/v1)
- `REACT_APP_AUTH_API_URL` - Auth Service URL (default: http://localhost:8002/auth)

## Development

### Building
```bash
npm run build
```

### Type Checking
```bash
npm run type-check
```

## Framework Integration

This shared module implements the core patterns for the ACGS-PGP Framework:

1. **Artificial Constitution (AC)** - Principle management through ACService
2. **Self-Synthesizing (GS) Engine** - Policy synthesis through GSService  
3. **Prompt Governance Compiler (PGC)** - Compliance validation (mocked in components)

All services include proper error handling, CSRF protection, and authentication token management.
