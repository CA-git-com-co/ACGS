// Constitutional Hash: cdd01ef066bc6cf2

import '@testing-library/jest-dom';
import { CONSTITUTIONAL_HASH } from '@/types';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
  }),
  usePathname: () => '/test',
  useSearchParams: () => new URLSearchParams(),
}));

// Mock Next.js image
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => props,
}));

// Mock environment variables
process.env.NEXT_PUBLIC_CONSTITUTIONAL_HASH = CONSTITUTIONAL_HASH;
process.env.NEXT_PUBLIC_API_BASE_URL = 'http://localhost:8010';
process.env.NEXT_PUBLIC_GRAPHQL_URL = 'http://localhost:8010/graphql';
process.env.NEXT_PUBLIC_WS_URL = 'ws://localhost:8010/ws';

// Mock fetch
global.fetch = jest.fn();

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
  },
  writable: true,
});

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
});