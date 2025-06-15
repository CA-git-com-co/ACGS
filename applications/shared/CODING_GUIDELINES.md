# ACGS-PGP Framework Coding Guidelines

This document outlines the coding standards and best practices for the ACGS-PGP (Artificial Constitution Governance System - Prompt Governance Protocol) shared component library.

## 🏛️ Constitutional Governance Principles

All code in this library should reflect the democratic and transparent values of the ACGS system:

- **Transparency**: Code should be self-documenting with clear naming and comprehensive comments
- **Accessibility**: All UI components must be accessible to users with disabilities
- **Reliability**: Robust error handling and graceful degradation
- **Accountability**: Comprehensive logging and audit trails for governance actions

## 📁 Project Structure

```
applications/shared/
├── components/           # Reusable UI components
│   ├── domains/         # Domain-organized components
│   ├── hoc/            # Higher-order components
│   └── *.stories.tsx   # Storybook stories
├── hooks/              # Custom React hooks
├── services/           # API service integrations
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
├── contexts/           # React contexts
└── styles/             # Global styles and themes
```

## 🎯 Naming Conventions

### Files and Directories
- **Components**: PascalCase (e.g., `ComplianceChecker.tsx`)
- **Hooks**: camelCase starting with "use" (e.g., `useAuthExtended.ts`)
- **Services**: PascalCase with "Service" suffix (e.g., `ACService.ts`)
- **Types**: camelCase (e.g., `governance.ts`)
- **Utilities**: camelCase (e.g., `propValidation.ts`)

### Variables and Functions
- **Variables**: camelCase (e.g., `activePolicies`, `isLoading`)
- **Functions**: camelCase with descriptive verbs (e.g., `validateCompliance`, `synthesizePolicies`)
- **Constants**: SCREAMING_SNAKE_CASE (e.g., `MAX_RETRY_ATTEMPTS`, `DEFAULT_TIMEOUT`)
- **Environment Variables**: SCREAMING_SNAKE_CASE with service prefix (e.g., `REACT_APP_AC_API_URL`)

### Components and Interfaces
- **React Components**: PascalCase (e.g., `PolicyCard`, `ComplianceChecker`)
- **Interfaces**: PascalCase with descriptive names (e.g., `ComplianceResult`, `PolicyRule`)
- **Types**: PascalCase (e.g., `ServiceType`, `LoadingState`)

## 🔧 TypeScript Guidelines

### Interface Definitions
```typescript
/**
 * Interface for constitutional principle data
 * 
 * @example
 * ```typescript
 * const principle: Principle = {
 *   id: "PRIN-001",
 *   title: "Democratic Governance",
 *   content: "All policy changes must be approved through democratic voting",
 *   category: "governance",
 *   priority: 9
 * };
 * ```
 */
interface Principle {
  /** Unique principle identifier */
  id: string;
  /** Principle title */
  title: string;
  /** Principle content/description */
  content: string;
  /** Principle category */
  category: string;
  /** Priority level (1-10, higher is more important) */
  priority: number;
  /** Creation timestamp */
  createdAt?: Date;
  /** Last update timestamp */
  updatedAt?: Date;
  /** Author identifier */
  author?: string;
}
```

### Function Documentation
```typescript
/**
 * Validates action compliance against governance policies
 * 
 * @param action - The action to validate
 * @param context - Action context including governance state
 * @param policy - The policy to check against
 * @returns Promise resolving to compliance result
 * 
 * @throws {Error} When PGC service is unavailable
 * 
 * @example
 * ```typescript
 * const result = await validateCompliance(
 *   "transfer 1000 tokens",
 *   { requiresGovernance: true, hasApproval: false },
 *   treasuryPolicy
 * );
 * ```
 */
async function validateCompliance(
  action: string,
  context: ActionContext,
  policy: Policy
): Promise<ComplianceResult> {
  // Implementation
}
```

## ⚛️ React Component Guidelines

### Component Structure
```typescript
import React from 'react';
import { z } from 'zod';
import { validateProps } from '../utils/propValidation';

// Props interface with comprehensive documentation
interface ComponentProps {
  /** Primary data for the component */
  data: SomeDataType;
  /** Optional callback for user interactions */
  onAction?: (result: ActionResult) => void;
  /** Additional CSS classes */
  className?: string;
}

// Zod schema for runtime validation
const ComponentPropsSchema = z.object({
  data: SomeDataSchema,
  onAction: z.function().optional(),
  className: z.string().optional()
});

/**
 * Component description with ACGS context
 * 
 * This component provides [functionality] for the constitutional governance
 * system, integrating with [relevant services] to [purpose].
 */
const MyComponent: React.FC<ComponentProps> = (props) => {
  // Validate props in development
  const validatedProps = validateProps(
    ComponentPropsSchema,
    props,
    'MyComponent'
  );

  const { data, onAction, className = '' } = validatedProps;

  // Component implementation
  return (
    <div className={`my-component ${className}`}>
      {/* Component content */}
    </div>
  );
};

export default MyComponent;
```

### Hook Guidelines
```typescript
import { useState, useCallback, useEffect } from 'react';

/**
 * Custom hook for [functionality] with ACGS integration
 * 
 * @param config - Hook configuration options
 * @returns Hook state and actions
 * 
 * @example
 * ```typescript
 * const { data, isLoading, error, refetch } = useMyHook({
 *   serviceUrl: 'http://localhost:8001/api/v1'
 * });
 * ```
 */
export const useMyHook = (config: HookConfig) => {
  const [state, setState] = useState(initialState);

  // Memoized callbacks
  const handleAction = useCallback(() => {
    // Implementation
  }, [dependencies]);

  // Effects
  useEffect(() => {
    // Side effects
  }, [dependencies]);

  return {
    // Return object
  };
};
```

## 🌐 Service Integration Patterns

### Service Client Structure
```typescript
import api from './api';
import { validateApiResponse } from '../utils/propValidation';

class ACService {
  private static readonly API_URL = process.env.REACT_APP_AC_API_URL || 'http://localhost:8001/api/v1';

  /**
   * Creates a new constitutional principle
   * 
   * @param principleData - Principle data to create
   * @returns Promise resolving to created principle
   */
  static async createPrinciple(principleData: PrincipleFormData): Promise<Principle> {
    try {
      const response = await api.post(`${this.API_URL}/principles/`, principleData);
      return validateApiResponse(PrincipleSchema, response.data, 'AC Service');
    } catch (error) {
      console.error('AC Service - Create principle failed:', error);
      throw error;
    }
  }
}

export default ACService;
```

### Error Handling Patterns
```typescript
// Service-specific error boundary usage
<ServiceErrorBoundary 
  serviceName="AC" 
  serviceUrl={process.env.REACT_APP_AC_API_URL}
>
  <PrincipleManager />
</ServiceErrorBoundary>

// Loading state management
const [loadingState, loadingActions] = useLoadingState({
  timeout: 30000,
  retryAttempts: 3,
  onTimeout: () => console.warn('AC Service timeout'),
  onError: (error) => console.error('AC Service error:', error)
});
```

## 🎨 Styling Guidelines

### CSS Classes
- Use descriptive, kebab-case class names
- Follow BEM methodology for complex components
- Use Tailwind CSS utilities for consistent spacing and colors
- Prefix custom classes with component name

```css
/* Component-specific styles */
.compliance-checker {
  /* Base styles */
}

.compliance-checker__form {
  /* Form styles */
}

.compliance-checker__result--compliant {
  /* Compliant state styles */
}
```

### Responsive Design
```typescript
// Mobile-first responsive classes
<div className="
  w-full 
  p-4 
  md:p-6 
  lg:p-8 
  grid 
  grid-cols-1 
  md:grid-cols-2 
  lg:grid-cols-3 
  gap-4 
  md:gap-6
">
```

## 🧪 Testing Guidelines

### Unit Test Structure
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ComplianceChecker } from '../ComplianceChecker';

describe('ComplianceChecker', () => {
  const mockProps = {
    activePolicies: mockPolicies,
    onComplianceCheck: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render compliance checker form', () => {
    render(<ComplianceChecker {...mockProps} />);
    
    expect(screen.getByText('PGC Compliance Checker')).toBeInTheDocument();
    expect(screen.getByLabelText('Action to Check')).toBeInTheDocument();
  });

  it('should handle compliance check submission', async () => {
    render(<ComplianceChecker {...mockProps} />);
    
    fireEvent.change(screen.getByLabelText('Action to Check'), {
      target: { value: 'test action' }
    });
    
    fireEvent.click(screen.getByText('Check Compliance'));
    
    await waitFor(() => {
      expect(mockProps.onComplianceCheck).toHaveBeenCalled();
    });
  });
});
```

## 📚 Documentation Standards

### Component Documentation
- Include comprehensive JSDoc comments
- Provide usage examples
- Document integration with ACGS services
- Include accessibility notes
- Document performance considerations

### Storybook Stories
```typescript
export default {
  title: 'Components/Governance/ComplianceChecker',
  component: ComplianceChecker,
  parameters: {
    docs: {
      description: {
        component: 'Comprehensive description of component purpose and ACGS integration'
      }
    }
  }
} as Meta;
```

## 🔒 Security Guidelines

### Input Validation
- Always validate props with Zod schemas
- Sanitize user inputs before API calls
- Use TypeScript for compile-time type safety
- Validate API responses before using data

### Authentication Integration
```typescript
// Use authentication hooks
const { isAuthenticated, hasRole, canPerformAction } = useAuthExtended();

// Protect sensitive operations
if (!canPerformAction('create_principle')) {
  return <UnauthorizedMessage />;
}
```

## 🚀 Performance Guidelines

### Code Splitting
```typescript
// Lazy load heavy components
const PolicyEditor = React.lazy(() => import('./PolicyEditor'));

// Use Suspense with loading fallback
<Suspense fallback={<PolicyEditorSkeleton />}>
  <PolicyEditor />
</Suspense>
```

### Memoization
```typescript
// Memoize expensive calculations
const expensiveValue = useMemo(() => {
  return calculateComplexValue(data);
}, [data]);

// Memoize callbacks
const handleSubmit = useCallback((formData) => {
  // Handle submission
}, [dependencies]);
```

## 🔄 Git Workflow

### Commit Messages
```
feat(compliance): add real-time policy validation

- Implement PGC service integration for live compliance checking
- Add loading states and error boundaries for service calls
- Include comprehensive test coverage for validation flows

Closes #123
```

### Branch Naming
- `feature/component-name` - New features
- `fix/issue-description` - Bug fixes
- `refactor/area-name` - Code refactoring
- `docs/section-name` - Documentation updates

## 📋 Code Review Checklist

- [ ] TypeScript interfaces are comprehensive and documented
- [ ] Components include prop validation with Zod
- [ ] Error boundaries are implemented for service integration
- [ ] Loading states are handled appropriately
- [ ] Accessibility requirements are met
- [ ] Tests achieve >80% coverage
- [ ] Storybook stories are comprehensive
- [ ] Performance considerations are addressed
- [ ] Security best practices are followed
- [ ] Documentation is complete and accurate

---

*These guidelines ensure that all code in the ACGS-PGP Framework maintains high quality, consistency, and alignment with constitutional governance principles.*
