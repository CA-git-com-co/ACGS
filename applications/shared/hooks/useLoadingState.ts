import { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Loading state configuration
 */
interface LoadingConfig {
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
  onTimeout?: () => void;
  onError?: (error: Error) => void;
  onSuccess?: () => void;
}

/**
 * Loading state return type
 */
interface LoadingState {
  isLoading: boolean;
  error: Error | null;
  isTimeout: boolean;
  retryCount: number;
  progress: number;
}

/**
 * Loading state actions
 */
interface LoadingActions {
  startLoading: () => void;
  stopLoading: () => void;
  setError: (error: Error | null) => void;
  retry: () => Promise<void>;
  reset: () => void;
  setProgress: (progress: number) => void;
}

/**
 * Async operation wrapper type
 */
type AsyncOperation<T> = () => Promise<T>;

/**
 * Custom hook for managing loading states with timeout and retry functionality
 */
export const useLoadingState = (config: LoadingConfig = {}): [LoadingState, LoadingActions] => {
  const {
    timeout = 30000, // 30 seconds default
    retryAttempts = 3,
    retryDelay = 1000,
    onTimeout,
    onError,
    onSuccess
  } = config;

  const [state, setState] = useState<LoadingState>({
    isLoading: false,
    error: null,
    isTimeout: false,
    retryCount: 0,
    progress: 0
  });

  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastOperationRef = useRef<AsyncOperation<any> | null>(null);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const startLoading = useCallback(() => {
    setState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
      isTimeout: false,
      progress: 0
    }));

    // Set timeout
    if (timeout > 0) {
      timeoutRef.current = setTimeout(() => {
        setState(prev => ({
          ...prev,
          isLoading: false,
          isTimeout: true
        }));
        if (onTimeout) {
          onTimeout();
        }
      }, timeout);
    }
  }, [timeout, onTimeout]);

  const stopLoading = useCallback(() => {
    setState(prev => ({
      ...prev,
      isLoading: false
    }));

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    if (onSuccess) {
      onSuccess();
    }
  }, [onSuccess]);

  const setError = useCallback((error: Error | null) => {
    setState(prev => ({
      ...prev,
      isLoading: false,
      error
    }));

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    if (error && onError) {
      onError(error);
    }
  }, [onError]);

  const setProgress = useCallback((progress: number) => {
    setState(prev => ({
      ...prev,
      progress: Math.min(Math.max(progress, 0), 100)
    }));
  }, []);

  const retry = useCallback(async () => {
    if (state.retryCount >= retryAttempts || !lastOperationRef.current) {
      return;
    }

    setState(prev => ({
      ...prev,
      retryCount: prev.retryCount + 1,
      error: null,
      isTimeout: false
    }));

    // Wait for retry delay
    if (retryDelay > 0) {
      await new Promise(resolve => setTimeout(resolve, retryDelay));
    }

    try {
      startLoading();
      await lastOperationRef.current();
      stopLoading();
    } catch (error) {
      setError(error as Error);
    }
  }, [state.retryCount, retryAttempts, retryDelay, startLoading, stopLoading, setError]);

  const reset = useCallback(() => {
    setState({
      isLoading: false,
      error: null,
      isTimeout: false,
      retryCount: 0,
      progress: 0
    });

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    lastOperationRef.current = null;
  }, []);

  const actions: LoadingActions = {
    startLoading,
    stopLoading,
    setError,
    retry,
    reset,
    setProgress
  };

  return [state, actions];
};

/**
 * Custom hook for wrapping async operations with loading state
 */
export const useAsyncOperation = <T>(
  operation: AsyncOperation<T>,
  config: LoadingConfig = {}
) => {
  const [loadingState, actions] = useLoadingState(config);

  const execute = useCallback(async (): Promise<T | null> => {
    // Store the operation for retry functionality
    (actions as any).lastOperationRef = { current: operation };

    try {
      actions.startLoading();
      const result = await operation();
      actions.stopLoading();
      return result;
    } catch (error) {
      actions.setError(error as Error);
      return null;
    }
  }, [operation, actions]);

  const executeWithRetry = useCallback(async (): Promise<T | null> => {
    let result = await execute();
    
    // Auto-retry on failure if configured
    while (result === null && loadingState.retryCount < (config.retryAttempts || 3) && !loadingState.isTimeout) {
      await actions.retry();
      result = await execute();
    }
    
    return result;
  }, [execute, actions, loadingState.retryCount, loadingState.isTimeout, config.retryAttempts]);

  return {
    ...loadingState,
    execute,
    executeWithRetry,
    retry: actions.retry,
    reset: actions.reset,
    setProgress: actions.setProgress
  };
};

/**
 * Custom hook for managing multiple loading states
 */
export const useMultipleLoadingStates = (keys: string[], config: LoadingConfig = {}) => {
  const [states, setStates] = useState<Record<string, LoadingState>>(() =>
    keys.reduce((acc, key) => ({
      ...acc,
      [key]: {
        isLoading: false,
        error: null,
        isTimeout: false,
        retryCount: 0,
        progress: 0
      }
    }), {})
  );

  const updateState = useCallback((key: string, updates: Partial<LoadingState>) => {
    setStates(prev => ({
      ...prev,
      [key]: { ...prev[key], ...updates }
    }));
  }, []);

  const startLoading = useCallback((key: string) => {
    updateState(key, { isLoading: true, error: null, isTimeout: false, progress: 0 });
  }, [updateState]);

  const stopLoading = useCallback((key: string) => {
    updateState(key, { isLoading: false });
  }, [updateState]);

  const setError = useCallback((key: string, error: Error | null) => {
    updateState(key, { isLoading: false, error });
  }, [updateState]);

  const setProgress = useCallback((key: string, progress: number) => {
    updateState(key, { progress: Math.min(Math.max(progress, 0), 100) });
  }, [updateState]);

  const reset = useCallback((key: string) => {
    updateState(key, {
      isLoading: false,
      error: null,
      isTimeout: false,
      retryCount: 0,
      progress: 0
    });
  }, [updateState]);

  const resetAll = useCallback(() => {
    keys.forEach(key => reset(key));
  }, [keys, reset]);

  const isAnyLoading = Object.values(states).some(state => state.isLoading);
  const hasAnyError = Object.values(states).some(state => state.error);
  const isAnyTimeout = Object.values(states).some(state => state.isTimeout);

  return {
    states,
    startLoading,
    stopLoading,
    setError,
    setProgress,
    reset,
    resetAll,
    isAnyLoading,
    hasAnyError,
    isAnyTimeout
  };
};

/**
 * Custom hook for debounced loading state
 */
export const useDebouncedLoading = (delay: number = 300) => {
  const [isLoading, setIsLoading] = useState(false);
  const [debouncedLoading, setDebouncedLoading] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      setDebouncedLoading(isLoading);
    }, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isLoading, delay]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    isLoading: debouncedLoading,
    setLoading: setIsLoading
  };
};

export type { LoadingConfig, LoadingState, LoadingActions, AsyncOperation };
