module.exports = {
  // Test environment
  testEnvironment: 'jsdom',

  // Setup files
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],

  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],

  // Transform files
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
    '^.+\\.(js|jsx)$': 'babel-jest'
  },

  // Module name mapping for absolute imports and assets
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': 'jest-transform-stub'
  },

  // Test match patterns
  testMatch: ['<rootDir>/src/**/__tests__/**/*.(ts|tsx|js|jsx)', '<rootDir>/src/**/*.(test|spec).(ts|tsx|js|jsx)'],

  // Ignore patterns
  testPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/dist/',
    '<rootDir>/build/',
    '<rootDir>/storybook-static/'
  ],

  // Coverage configuration
  collectCoverage: false, // Enable with --coverage flag
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{ts,tsx}',
    '!src/**/*.test.{ts,tsx}',
    '!src/**/*.spec.{ts,tsx}',
    '!src/index.ts',
    '!src/setupTests.ts'
  ],

  // Coverage thresholds (ACGS quality standards)
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    },
    // Specific thresholds for critical components
    './src/components/ComplianceChecker.tsx': {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    },
    './src/services/': {
      branches: 85,
      functions: 85,
      lines: 85,
      statements: 85
    },
    './src/hooks/': {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },

  // Coverage reporters
  coverageReporters: ['text', 'text-summary', 'html', 'lcov', 'json'],

  // Coverage directory
  coverageDirectory: 'coverage',

  // Test timeout
  testTimeout: 10000,

  // Globals for TypeScript
  globals: {
    'ts-jest': {
      tsconfig: {
        jsx: 'react-jsx'
      }
    }
  },

  // Mock modules
  moduleNameMapping: {
    // Mock ACGS service URLs for testing
    '^@/services/(.*)$': '<rootDir>/src/services/$1',
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@/types/(.*)$': '<rootDir>/src/types/$1',
    '^@/utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@/contexts/(.*)$': '<rootDir>/src/contexts/$1'
  },

  // Clear mocks between tests
  clearMocks: true,

  // Restore mocks after each test
  restoreMocks: true,

  // Verbose output for debugging
  verbose: false,

  // Error on deprecated features
  errorOnDeprecated: true,

  // Notify mode for watch
  notify: false,

  // Watch plugins
  watchPlugins: ['jest-watch-typeahead/filename', 'jest-watch-typeahead/testname'],

  // Custom test environment options
  testEnvironmentOptions: {
    url: 'http://localhost:3000'
  },

  // Transform ignore patterns for node_modules
  transformIgnorePatterns: ['node_modules/(?!(axios|@testing-library)/)']
};
