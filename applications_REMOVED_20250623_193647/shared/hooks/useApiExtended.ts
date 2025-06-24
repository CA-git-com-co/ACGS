import { useState, useCallback, useRef, useEffect } from 'react';
import { z } from 'zod';
import { useLoadingState, useMultipleLoadingStates } from './useLoadingState';
import { validateApiResponse } from '../utils/propValidation';
import { ApiResponseSchema } from '../types/validation';

/**
 * API hook configuration
 */
interface ApiConfig {
  /** Base URL for the API */
  baseUrl?: string;
  /** Default timeout in milliseconds */
  timeout?: number;
  /** Number of retry attempts */
  retryAttempts?: number;
  /** Retry delay in milliseconds */
  retryDelay?: number;
  /** Whether to cache responses */
  enableCache?: boolean;
  /** Cache TTL in milliseconds */
  cacheTtl?: number;
}

/**
 * API request options
 */
interface ApiRequestOptions {
  /** Request timeout */
  timeout?: number;
  /** Number of retries */
  retries?: number;
  /** Whether to use cache */
  useCache?: boolean;
  /** Custom headers */
  headers?: Record<string, string>;
  /** Validation schema for response */
  schema?: z.ZodSchema<any>;
}

/**
 * Cache entry interface
 */
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

/**
 * Enhanced API hook with caching, retries, and validation
 *
 * Provides a comprehensive API client with automatic retries,
 * response caching, validation, and loading state management.
 */
export const useApiExtended = (config: ApiConfig = {}) => {
  const {
    baseUrl = '',
    timeout = 30000,
    retryAttempts = 3,
    retryDelay = 1000,
    enableCache = true,
    cacheTtl = 300000 // 5 minutes
  } = config;

  // Cache storage
  const cache = useRef<Map<string, CacheEntry<any>>>(new Map());

  // Loading states for different operations
  const {
    states: loadingStates,
    startLoading,
    stopLoading,
    setError: setLoadingError,
    isAnyLoading
  } = useMultipleLoadingStates(['get', 'post', 'put', 'delete'], {
    timeout,
    retryAttempts,
    onTimeout: () => console.warn('API request timed out'),
    onError: error => console.error('API request failed:', error)
  });

  /**
   * Generate cache key for request
   */
  const getCacheKey = useCallback((url: string, options?: ApiRequestOptions): string => {
    const key = `${url}_${JSON.stringify(options?.headers || {})}_${options?.schema?.constructor.name || 'no-schema'}`;
    return btoa(key); // Base64 encode for safe key
  }, []);

  /**
   * Get cached response if valid
   */
  const getCachedResponse = useCallback(
    <T>(cacheKey: string): T | null => {
      if (!enableCache) return null;

      const entry = cache.current.get(cacheKey);
      if (!entry) return null;

      const isExpired = Date.now() - entry.timestamp > entry.ttl;
      if (isExpired) {
        cache.current.delete(cacheKey);
        return null;
      }

      return entry.data;
    },
    [enableCache]
  );

  /**
   * Cache response
   */
  const setCachedResponse = useCallback(
    <T>(cacheKey: string, data: T, ttl: number = cacheTtl): void => {
      if (!enableCache) return;

      cache.current.set(cacheKey, {
        data,
        timestamp: Date.now(),
        ttl
      });
    },
    [enableCache, cacheTtl]
  );

  /**
   * Clear cache
   */
  const clearCache = useCallback((pattern?: string): void => {
    if (pattern) {
      // Clear entries matching pattern
      for (const [key] of cache.current) {
        if (key.includes(pattern)) {
          cache.current.delete(key);
        }
      }
    } else {
      // Clear all cache
      cache.current.clear();
    }
  }, []);

  /**
   * Make HTTP request with retries and validation
   */
  const makeRequest = useCallback(
    async <T>(
      method: 'GET' | 'POST' | 'PUT' | 'DELETE',
      url: string,
      data?: any,
      options: ApiRequestOptions = {}
    ): Promise<T> => {
      const {
        timeout: requestTimeout = timeout,
        retries = retryAttempts,
        useCache = enableCache && method === 'GET',
        headers = {},
        schema
      } = options;

      const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
      const cacheKey = getCacheKey(fullUrl, options);

      // Check cache for GET requests
      if (useCache && method === 'GET') {
        const cachedResponse = getCachedResponse<T>(cacheKey);
        if (cachedResponse) {
          return cachedResponse;
        }
      }

      const operationKey = method.toLowerCase() as 'get' | 'post' | 'put' | 'delete';
      startLoading(operationKey);

      let lastError: Error | null = null;

      for (let attempt = 0; attempt <= retries; attempt++) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), requestTimeout);

          const requestOptions: RequestInit = {
            method,
            headers: {
              'Content-Type': 'application/json',
              ...headers
            },
            signal: controller.signal
          };

          if (data && method !== 'GET') {
            requestOptions.body = JSON.stringify(data);
          }

          const response = await fetch(fullUrl, requestOptions);
          clearTimeout(timeoutId);

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          const responseData = await response.json();

          // Validate response if schema provided
          let validatedData = responseData;
          if (schema) {
            validatedData = validateApiResponse(schema, responseData, fullUrl);
          }

          // Cache successful GET responses
          if (useCache && method === 'GET') {
            setCachedResponse(cacheKey, validatedData);
          }

          stopLoading(operationKey);
          return validatedData;
        } catch (error) {
          lastError = error as Error;

          // Don't retry on validation errors or client errors (4xx)
          if (
            error instanceof Error &&
            (error.message.includes('validation') || error.message.includes('HTTP 4'))
          ) {
            break;
          }

          // Wait before retry (except on last attempt)
          if (attempt < retries) {
            await new Promise(resolve => setTimeout(resolve, retryDelay * (attempt + 1)));
          }
        }
      }

      setLoadingError(operationKey, lastError || new Error('Request failed'));
      throw lastError || new Error('Request failed after retries');
    },
    [
      baseUrl,
      timeout,
      retryAttempts,
      retryDelay,
      enableCache,
      getCacheKey,
      getCachedResponse,
      setCachedResponse,
      startLoading,
      stopLoading,
      setLoadingError
    ]
  );

  /**
   * GET request
   */
  const get = useCallback(
    <T>(url: string, options?: ApiRequestOptions): Promise<T> => {
      return makeRequest<T>('GET', url, undefined, options);
    },
    [makeRequest]
  );

  /**
   * POST request
   */
  const post = useCallback(
    <T>(url: string, data?: any, options?: ApiRequestOptions): Promise<T> => {
      return makeRequest<T>('POST', url, data, options);
    },
    [makeRequest]
  );

  /**
   * PUT request
   */
  const put = useCallback(
    <T>(url: string, data?: any, options?: ApiRequestOptions): Promise<T> => {
      return makeRequest<T>('PUT', url, data, options);
    },
    [makeRequest]
  );

  /**
   * DELETE request
   */
  const del = useCallback(
    <T>(url: string, options?: ApiRequestOptions): Promise<T> => {
      return makeRequest<T>('DELETE', url, undefined, options);
    },
    [makeRequest]
  );

  /**
   * Upload file
   */
  const upload = useCallback(
    async <T>(url: string, file: File, options: ApiRequestOptions = {}): Promise<T> => {
      const formData = new FormData();
      formData.append('file', file);

      const { timeout: requestTimeout = timeout, headers = {} } = options;

      const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;

      startLoading('post');

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), requestTimeout);

        const response = await fetch(fullUrl, {
          method: 'POST',
          body: formData,
          headers: {
            // Don't set Content-Type for FormData, let browser set it
            ...headers
          },
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const responseData = await response.json();
        stopLoading('post');
        return responseData;
      } catch (error) {
        setLoadingError('post', error as Error);
        throw error;
      }
    },
    [baseUrl, timeout, startLoading, stopLoading, setLoadingError]
  );

  // Clean up cache on unmount
  useEffect(() => {
    return () => {
      cache.current.clear();
    };
  }, []);

  return {
    // HTTP methods
    get,
    post,
    put,
    delete: del,
    upload,

    // Loading states
    isLoading: isAnyLoading,
    loadingStates,

    // Cache management
    clearCache,
    getCacheSize: () => cache.current.size,

    // Configuration
    config: {
      baseUrl,
      timeout,
      retryAttempts,
      retryDelay,
      enableCache,
      cacheTtl
    }
  };
};

/**
 * Hook for service-specific API calls
 */
export const useServiceApi = (serviceName: string, serviceUrl?: string) => {
  const serviceUrls: Record<string, string> = {
    AC: process.env.REACT_APP_AC_API_URL || 'http://localhost:8001/api/v1',
    GS: process.env.REACT_APP_GS_API_URL || 'http://localhost:8003/api/v1',
    PGC: process.env.REACT_APP_PGC_API_URL || 'http://localhost:8005/api/v1',
    Auth: process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8002/auth',
    Integrity: process.env.REACT_APP_INTEGRITY_API_URL || 'http://localhost:8006/api/v1',
    FV: process.env.REACT_APP_FV_API_URL || 'http://localhost:8004/api/v1',
    EC: process.env.REACT_APP_EC_API_URL || 'http://localhost:8007/api/v1'
  };

  const baseUrl = serviceUrl || serviceUrls[serviceName] || '';

  return useApiExtended({
    baseUrl,
    timeout: 30000,
    retryAttempts: 3,
    enableCache: true,
    cacheTtl: 300000 // 5 minutes
  });
};

export default useApiExtended;
