import { useState, useEffect, useCallback } from 'react';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
}

/**
 * Custom hook for API calls with loading, error, and data state management
 */
export const useApi = <T = any>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseApiOptions = {}
) => {
  const { immediate = false, onSuccess, onError } = options;

  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null
  });

  const execute = useCallback(
    async (...args: any[]) => {
      setState(prev => ({ ...prev, loading: true, error: null }));

      try {
        const result = await apiFunction(...args);
        setState({ data: result, loading: false, error: null });
        onSuccess?.(result);
        return result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'An error occurred';
        setState({ data: null, loading: false, error: errorMessage });
        onError?.(errorMessage);
        throw error;
      }
    },
    [apiFunction, onSuccess, onError]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return {
    ...state,
    execute,
    reset
  };
};

/**
 * Hook for managing form submission with API calls
 */
export const useApiForm = <T = any>(
  submitFunction: (data: any) => Promise<T>,
  options: UseApiOptions = {}
) => {
  const { onSuccess, onError } = options;

  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null
  });

  const submit = useCallback(
    async (formData: any) => {
      setState(prev => ({ ...prev, loading: true, error: null }));

      try {
        const result = await submitFunction(formData);
        setState({ data: result, loading: false, error: null });
        onSuccess?.(result);
        return result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Submission failed';
        setState(prev => ({ ...prev, loading: false, error: errorMessage }));
        onError?.(errorMessage);
        throw error;
      }
    },
    [submitFunction, onSuccess, onError]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    submit,
    reset,
    isSubmitting: state.loading
  };
};

/**
 * Hook for paginated API calls
 */
export const usePaginatedApi = <T = any>(
  apiFunction: (
    page: number,
    limit: number,
    ...args: any[]
  ) => Promise<{ data: T[]; total: number; page: number; limit: number }>,
  initialLimit: number = 10
) => {
  const [state, setState] = useState({
    data: [] as T[],
    loading: false,
    error: null as string | null,
    page: 1,
    limit: initialLimit,
    total: 0,
    hasMore: false
  });

  const fetchPage = useCallback(
    async (page: number, ...args: any[]) => {
      setState(prev => ({ ...prev, loading: true, error: null }));

      try {
        const result = await apiFunction(page, state.limit, ...args);
        setState(prev => ({
          ...prev,
          data: page === 1 ? result.data : [...prev.data, ...result.data],
          loading: false,
          page: result.page,
          total: result.total,
          hasMore: result.data.length === state.limit && page * state.limit < result.total
        }));
        return result;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch data';
        setState(prev => ({ ...prev, loading: false, error: errorMessage }));
        throw error;
      }
    },
    [apiFunction, state.limit]
  );

  const loadMore = useCallback(
    (...args: any[]) => {
      if (!state.loading && state.hasMore) {
        return fetchPage(state.page + 1, ...args);
      }
    },
    [fetchPage, state.loading, state.hasMore, state.page]
  );

  const refresh = useCallback(
    (...args: any[]) => {
      return fetchPage(1, ...args);
    },
    [fetchPage]
  );

  const reset = useCallback(() => {
    setState({
      data: [],
      loading: false,
      error: null,
      page: 1,
      limit: initialLimit,
      total: 0,
      hasMore: false
    });
  }, [initialLimit]);

  return {
    ...state,
    fetchPage,
    loadMore,
    refresh,
    reset
  };
};

export default useApi;
