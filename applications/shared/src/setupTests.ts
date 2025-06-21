// Jest setup for ACGS-PGP Framework testing
import '@testing-library/jest-dom';

// Mock environment variables for ACGS services
process.env.REACT_APP_AC_API_URL = 'http://localhost:8001/api/v1';
process.env.REACT_APP_GS_API_URL = 'http://localhost:8003/api/v1';
process.env.REACT_APP_PGC_API_URL = 'http://localhost:8005/api/v1';
process.env.REACT_APP_AUTH_API_URL = 'http://localhost:8002/auth';
process.env.REACT_APP_INTEGRITY_API_URL = 'http://localhost:8006/api/v1';
process.env.REACT_APP_FV_API_URL = 'http://localhost:8004/api/v1';
process.env.REACT_APP_EC_API_URL = 'http://localhost:8007/api/v1';

// Mock fetch for API calls
global.fetch = jest.fn();

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
    origin: 'http://localhost:3000',
    pathname: '/',
    search: '',
    hash: '',
    reload: jest.fn(),
    assign: jest.fn()
  },
  writable: true
});

// Mock window.alert
global.alert = jest.fn();

// Mock window.confirm
global.confirm = jest.fn(() => true);

// Mock console methods to reduce noise in tests
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  console.error = (...args: any[]) => {
    // Suppress React error boundary warnings in tests
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };

  console.warn = (...args: any[]) => {
    // Suppress specific warnings that are expected in tests
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('componentWillReceiveProps') || args[0].includes('componentWillUpdate'))
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
  console.warn = originalWarn;
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn()
  }))
});

// Mock scrollTo
window.scrollTo = jest.fn();

// Mock requestAnimationFrame
global.requestAnimationFrame = (callback: FrameRequestCallback) => {
  return setTimeout(callback, 0);
};

global.cancelAnimationFrame = (id: number) => {
  clearTimeout(id);
};

// Custom matchers for ACGS testing
expect.extend({
  toBeCompliant(received: any) {
    const pass = received && received.compliant === true;
    if (pass) {
      return {
        message: () => `expected ${received} not to be compliant`,
        pass: true
      };
    } else {
      return {
        message: () => `expected ${received} to be compliant`,
        pass: false
      };
    }
  },

  toHaveValidationScore(received: any, expected: number) {
    const pass =
      received &&
      typeof received.validationScore === 'number' &&
      received.validationScore >= expected;
    if (pass) {
      return {
        message: () => `expected ${received.validationScore} not to be >= ${expected}`,
        pass: true
      };
    } else {
      return {
        message: () => `expected ${received.validationScore} to be >= ${expected}`,
        pass: false
      };
    }
  },

  toHaveServiceIntegration(received: any, serviceName: string) {
    const serviceUrls = {
      AC: process.env.REACT_APP_AC_API_URL,
      GS: process.env.REACT_APP_GS_API_URL,
      PGC: process.env.REACT_APP_PGC_API_URL,
      Auth: process.env.REACT_APP_AUTH_API_URL,
      Integrity: process.env.REACT_APP_INTEGRITY_API_URL,
      FV: process.env.REACT_APP_FV_API_URL,
      EC: process.env.REACT_APP_EC_API_URL
    };

    const expectedUrl = serviceUrls[serviceName as keyof typeof serviceUrls];
    const pass = received && received.includes && received.includes(expectedUrl);

    if (pass) {
      return {
        message: () => `expected ${received} not to include ${serviceName} service URL`,
        pass: true
      };
    } else {
      return {
        message: () =>
          `expected ${received} to include ${serviceName} service URL (${expectedUrl})`,
        pass: false
      };
    }
  }
});

// Extend Jest matchers type definitions
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeCompliant(): R;
      toHaveValidationScore(score: number): R;
      toHaveServiceIntegration(serviceName: string): R;
    }
  }
}

// Global test utilities
export const createMockUser = (overrides = {}) => ({
  id: 'user-123',
  username: 'testuser',
  email: 'test@acgs.dev',
  role: 'user',
  createdAt: new Date('2024-01-01'),
  ...overrides
});

export const createMockPrinciple = (overrides = {}) => ({
  id: 'PRIN-001',
  title: 'Test Principle',
  content: 'This is a test constitutional principle',
  category: 'governance',
  priority: 5,
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date('2024-01-01'),
  author: 'test-author',
  ...overrides
});

export const createMockPolicy = (overrides = {}) => ({
  id: 'POL-001',
  name: 'Test Policy',
  description: 'This is a test governance policy',
  rules: [
    {
      id: 'R1',
      condition: 'test.condition === true',
      action: 'ALLOW'
    }
  ],
  validationScore: 85,
  complianceComplexity: 30,
  status: 'active' as const,
  category: 'test',
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date('2024-01-01'),
  author: 'test-author',
  ...overrides
});

export const createMockComplianceResult = (overrides = {}) => ({
  compliant: true,
  confidenceScore: 95,
  violationReasons: undefined,
  ...overrides
});

// Mock service responses
export const mockServiceResponses = {
  AC: {
    getPrinciples: () => Promise.resolve({ principles: [createMockPrinciple()] }),
    createPrinciple: (data: any) => Promise.resolve(createMockPrinciple(data)),
    updatePrinciple: (id: string, data: any) =>
      Promise.resolve(createMockPrinciple({ id, ...data })),
    deletePrinciple: (id: string) => Promise.resolve({ success: true })
  },
  GS: {
    synthesizePolicies: (data: any) =>
      Promise.resolve({
        policies: [createMockPolicy()],
        validationScore: 90,
        complianceComplexity: 25
      })
  },
  PGC: {
    checkCompliance: (action: string, context: any, policy: any) =>
      Promise.resolve(createMockComplianceResult())
  },
  Auth: {
    login: (username: string, password: string) =>
      Promise.resolve({
        user: createMockUser({ username }),
        token: 'mock-token'
      }),
    logout: () => Promise.resolve({ success: true }),
    refreshToken: () => Promise.resolve({ token: 'new-mock-token' })
  }
};

// Reset all mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
  (fetch as jest.Mock).mockClear();
});
