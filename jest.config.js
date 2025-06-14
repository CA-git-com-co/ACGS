module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['@testing-library/jest-dom'],
  moduleNameMapper: {
    // If you have path aliases in tsconfig.json, you might need to map them here
    // For example, if @/hooks/* maps to hooks/*
    // "^@/hooks/(.*)$": "<rootDir>/hooks/$1",
  },
  // Automatically clear mock calls and instances between every test
  clearMocks: true,
};
