// Main entry point for ACGS-PGP shared modules

// Services
export * from './services';

// Components
export * from './components';

// Contexts
export * from './contexts';

// Hooks
export * from './hooks';

// Utils
export * from './utils';

// Validation utilities
export * from './utils/propValidation';
export * from './types/validation';

// Types
export * from './types/governance';

// Styles and Theme
export { default as theme } from './styles/theme';
export * from './styles/theme';

// Pages
export { default as DashboardPage } from './pages/DashboardPage';
export { default as ACManagementPage } from './pages/AC/ACManagementPage';
export { default as LoginPage } from './pages/Auth/LoginPage';
