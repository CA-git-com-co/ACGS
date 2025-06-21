# ACGS-PGP Framework Testing Guide

This document outlines the comprehensive testing strategy for the ACGS-PGP
(Artificial Constitution Governance System - Prompt Governance Protocol) shared
component library.

## 🎯 Testing Philosophy

Our testing approach follows constitutional governance principles:

- **Transparency**: All tests are well-documented and self-explanatory
- **Reliability**: Comprehensive coverage ensures system stability
- **Accountability**: Tests validate compliance with governance requirements
- **Accessibility**: Testing includes accessibility validation for inclusive
  governance

## 📊 Coverage Targets

### Overall Coverage Goals (ACGS Standards)

- **Branches**: ≥80%
- **Functions**: ≥80%
- **Lines**: ≥80%
- **Statements**: ≥80%

### Critical Component Coverage

- **ComplianceChecker**: ≥90% (core governance functionality)
- **Services**: ≥85% (ACGS service integration)
- **Hooks**: ≥80% (shared logic components)

## 🧪 Test Types

### 1. Unit Tests (Jest + React Testing Library)

**Location**: `src/**/__tests__/**/*.test.{ts,tsx}`

**Purpose**: Test individual components and functions in isolation

**Key Features**:

- Component rendering and interaction
- Props validation with Zod schemas
- Hook behavior and state management
- Service function logic
- Error handling and edge cases

**Example**:

```bash
npm run test                    # Run all unit tests
npm run test:watch             # Run tests in watch mode
npm run test:coverage          # Run with coverage report
```

### 2. Integration Tests

**Location**: `src/__tests__/integration/**/*.test.{ts,tsx}`

**Purpose**: Test component interactions with services and contexts

**Key Features**:

- Service integration patterns
- Authentication flows
- Context provider behavior
- End-to-end component workflows
- Mock service responses

**Example**:

```bash
npm run test -- --testPathPattern=integration
```

### 3. End-to-End Tests (Playwright)

**Location**: `e2e/**/*.spec.ts`

**Purpose**: Test complete user workflows in browser environment

**Key Features**:

- Governance workflow validation
- Cross-browser compatibility
- Mobile responsiveness
- Accessibility compliance
- Real user interactions

**Example**:

```bash
npm run test:e2e              # Run E2E tests headless
npm run test:e2e:headed       # Run with browser UI
npm run test:e2e:ui           # Run with Playwright UI
npm run test:e2e:debug        # Debug mode
```

## 🏛️ ACGS-Specific Testing Patterns

### Constitutional Governance Testing

```typescript
// Test compliance validation
it('should validate constitutional compliance', async () => {
  const result = await validateCompliance(action, context, policy);
  expect(result).toBeCompliant();
  expect(result).toHaveValidationScore(90);
});

// Test service integration
it('should integrate with PGC service', () => {
  const component = render(<ComplianceChecker />);
  expect(component).toHaveServiceIntegration('PGC');
});
```

### Service Integration Testing

```typescript
// Mock ACGS services
jest.mock('../../services/ACService', () => ({
  getPrinciples: jest.fn().mockResolvedValue(mockPrinciples),
  createPrinciple: jest.fn().mockResolvedValue(mockPrinciple)
}));

// Test service calls
it('should call AC service correctly', async () => {
  await ACService.createPrinciple(principleData);
  expect(ACService.createPrinciple).toHaveBeenCalledWith(principleData);
});
```

### Authentication Testing

```typescript
// Test role-based access
it('should restrict access based on user role', () => {
  const { result } = renderHook(() => useAuthExtended(), {
    wrapper: ({ children }) => (
      <AuthProvider user={createMockUser({ role: 'user' })}>
        {children}
      </AuthProvider>
    )
  });

  expect(result.current.canPerformAction('admin_action')).toBe(false);
});
```

## 🔧 Test Configuration

### Jest Configuration (`jest.config.js`)

- **Environment**: jsdom for React component testing
- **Setup**: Custom matchers and mock services
- **Coverage**: Detailed thresholds for different component types
- **Transforms**: TypeScript and JSX support

### Playwright Configuration (`playwright.config.ts`)

- **Browsers**: Chrome, Firefox, Safari, Edge
- **Devices**: Desktop and mobile viewports
- **Reporters**: HTML, JSON, JUnit for CI integration
- **Global Setup**: Mock service configuration

## 📝 Writing Tests

### Component Test Structure

```typescript
describe('ComponentName', () => {
  // Setup and mocks
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render with default props', () => {
      // Test basic rendering
    });
  });

  describe('Interaction', () => {
    it('should handle user interactions', async () => {
      // Test user events
    });
  });

  describe('Props Validation', () => {
    it('should validate props with Zod', () => {
      // Test prop validation
    });
  });

  describe('ACGS Integration', () => {
    it('should integrate with services', () => {
      // Test service integration
    });
  });

  describe('Accessibility', () => {
    it('should be accessible', () => {
      // Test accessibility
    });
  });
});
```

### E2E Test Structure

```typescript
test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup page state
  });

  test('should complete user workflow', async ({ page }) => {
    // Test complete user journey
  });

  test('should work on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    // Test mobile experience
  });
});
```

## 🚀 Running Tests

### Development Workflow

```bash
# Start development with tests
npm run test:watch

# Run specific test file
npm test ComplianceChecker.test.tsx

# Run tests for specific component
npm test -- --testNamePattern="ComplianceChecker"

# Debug failing test
npm test -- --verbose --no-coverage
```

### CI/CD Pipeline

```bash
# Full test suite for CI
npm run test:all

# Coverage report for CI
npm run test:ci

# E2E tests for deployment validation
npm run test:e2e
```

### Coverage Analysis

```bash
# Generate and view coverage report
npm run test:coverage:open

# Check coverage for specific files
npm run test:coverage -- --collectCoverageFrom="src/components/ComplianceChecker.tsx"
```

## 🔍 Test Utilities

### Custom Matchers

```typescript
// Constitutional governance matchers
expect(result).toBeCompliant();
expect(result).toHaveValidationScore(90);
expect(component).toHaveServiceIntegration('PGC');
```

### Mock Factories

```typescript
// Create test data
const mockUser = createMockUser({ role: 'admin' });
const mockPrinciple = createMockPrinciple({ priority: 9 });
const mockPolicy = createMockPolicy({ status: 'active' });
const mockComplianceResult = createMockComplianceResult({ compliant: true });
```

### Service Mocks

```typescript
// Use predefined service mocks
mockServiceResponses.AC.getPrinciples();
mockServiceResponses.GS.synthesizePolicies(request);
mockServiceResponses.PGC.checkCompliance(action, context, policy);
```

## 📊 Test Reports

### Coverage Reports

- **HTML Report**: `coverage/lcov-report/index.html`
- **LCOV**: `coverage/lcov.info` (for CI integration)
- **JSON**: `coverage/coverage-final.json`

### E2E Reports

- **HTML Report**: `playwright-report/index.html`
- **JSON Results**: `test-results/results.json`
- **JUnit XML**: `test-results/results.xml`

## 🐛 Debugging Tests

### Unit Test Debugging

```bash
# Debug with Node.js inspector
node --inspect-brk node_modules/.bin/jest --runInBand

# Debug specific test
npm test -- --testNamePattern="specific test" --verbose
```

### E2E Test Debugging

```bash
# Debug mode with browser
npm run test:e2e:debug

# Headed mode to see browser
npm run test:e2e:headed

# Trace viewer for failed tests
npx playwright show-trace test-results/trace.zip
```

## ✅ Quality Gates

### Pre-commit Checks

- All tests must pass
- Coverage thresholds must be met
- No TypeScript errors
- ESLint and Prettier compliance

### CI/CD Requirements

- Unit test coverage ≥80%
- Integration tests pass
- E2E tests pass on all browsers
- Accessibility tests pass
- Performance benchmarks met

### Release Criteria

- All test suites pass
- Coverage reports generated
- No critical accessibility issues
- Cross-browser compatibility verified
- Mobile responsiveness validated

## 🔗 Integration with ACGS Services

### Service Testing Strategy

1. **Mock Services**: Use MSW for realistic API mocking
2. **Contract Testing**: Validate service interface compliance
3. **Integration Testing**: Test actual service communication
4. **Error Handling**: Validate service error scenarios

### Constitutional Compliance Testing

1. **Policy Validation**: Test compliance checking logic
2. **Governance Workflows**: Validate democratic processes
3. **Access Control**: Test role-based permissions
4. **Audit Trails**: Validate logging and transparency

---

_This testing strategy ensures the ACGS-PGP Framework maintains high quality
while supporting constitutional governance principles through comprehensive
validation and verification._
