// Shared hooks for ACGS-PGP Framework
export { useKeyboard } from './useKeyboard';
export { useLocalStorage } from './useLocalStorage';
export { useApi, useApiForm, usePaginatedApi } from './useApi';
export {
  useLoadingState,
  useAsyncOperation,
  useMultipleLoadingStates,
  useDebouncedLoading
} from './useLoadingState';

// Extended hooks
export {
  useAuthExtended,
  useRoleAccess,
  useProtectedAction
} from './useAuthExtended';

export {
  useApiExtended,
  useServiceApi
} from './useApiExtended';

// Re-export default
export { default as useApi } from './useApi';
