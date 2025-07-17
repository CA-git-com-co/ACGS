/**
 * Enhanced API Client for ACGS-2 Frontend
 * Constitutional Hash: cdd01ef066bc6cf2
 */

import { CONFIG } from '@/config';
import type { APIResponse, APIError as APIErrorType } from '@/types';

// Enhanced error types with better context
export interface APIErrorDetail {
  code: string;
  message: string;
  field?: string;
  context?: Record<string, unknown>;
}

export interface APIErrorContext {
  endpoint: string;
  method: string;
  requestId: string;
  timestamp: string;
  userAgent?: string;
  constitutionalHash: string;
}

export class APIError extends Error {
  public readonly context: APIErrorContext;
  
  constructor(
    message: string,
    public readonly status: number,
    public readonly errors: APIErrorDetail[] = [],
    context: Partial<APIErrorContext> = {}
  ) {
    super(message);
    this.name = 'APIError';
    
    this.context = {
      endpoint: context.endpoint || 'unknown',
      method: context.method || 'unknown',
      requestId: context.requestId || createRequestId(),
      timestamp: context.timestamp || new Date().toISOString(),
      userAgent: context.userAgent || (typeof window !== 'undefined' ? window.navigator.userAgent : 'unknown'),
      constitutionalHash: CONFIG.constitutional.hash,
    };
  }

  // Helper methods for error type checking
  isNetworkError(): boolean {
    return this.status === 0;
  }

  isClientError(): boolean {
    return this.status >= 400 && this.status < 500;
  }

  isServerError(): boolean {
    return this.status >= 500;
  }

  isConstitutionalError(): boolean {
    return this.errors.some(error => error.code.includes('CONSTITUTIONAL'));
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      status: this.status,
      errors: this.errors,
      context: this.context,
    };
  }
}

export class APIClient {
  private baseURL: string;
  private headers: Record<string, string>;
  private requestQueue: Map<string, AbortController> = new Map();

  constructor(baseURL: string = CONFIG.api.baseUrl) {
    this.baseURL = baseURL;
    this.headers = {
      'Content-Type': 'application/json',
      'X-Constitutional-Hash': CONFIG.constitutional.hash,
      'X-Client-Version': '1.0.0',
    };
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    const requestId = createRequestId();
    const startTime = performance.now();
    const method = options.method || 'GET';
    const url = `${this.baseURL}${endpoint}`;

    // Create abort controller for request cancellation
    const controller = new AbortController();
    this.requestQueue.set(requestId, controller);

    const config: RequestInit = {
      ...options,
      signal: controller.signal,
      headers: {
        ...this.headers,
        'X-Request-ID': requestId,
        ...options.headers,
      },
    };

    try {
      // Apply timeout using AbortController and setTimeout
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, CONFIG.api.timeout);

      const response = await fetch(url, config);
      clearTimeout(timeoutId);
      
      const endTime = performance.now();
      const duration = endTime - startTime;

      // Log performance metrics
      this.logPerformanceMetrics(endpoint, method, duration, response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData.errors || [],
          {
            endpoint,
            method,
            requestId,
            timestamp: new Date().toISOString(),
          }
        );
      }

      const data = await response.json();
      
      // Validate constitutional hash in response
      if (CONFIG.constitutional.validationEnabled && 
          data.constitutionalCompliance?.hash !== CONFIG.constitutional.hash) {
        throw new APIError(
          'Constitutional hash mismatch in response',
          400,
          [{ code: 'CONSTITUTIONAL_HASH_MISMATCH', message: 'Invalid constitutional hash' }],
          { endpoint, method, requestId }
        );
      }

      return data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      // Handle fetch errors (network, timeout, etc.)
      const errorMessage = error instanceof Error ? error.message : 'Network error';
      const status = error instanceof Error && error.name === 'AbortError' ? 408 : 0;
      
      throw new APIError(
        errorMessage,
        status,
        [],
        { endpoint, method, requestId }
      );
    } finally {
      // Clean up request from queue
      this.requestQueue.delete(requestId);
    }
  }

  private logPerformanceMetrics(endpoint: string, method: string, duration: number, status: number) {
    if (CONFIG.features.enablePerformanceMonitoring) {
      const metrics = {
        endpoint,
        method,
        duration,
        status,
        timestamp: new Date().toISOString(),
        constitutionalHash: CONFIG.constitutional.hash,
      };

      // Log to console in development
      if (process.env.NODE_ENV === 'development') {
        console.log('API Performance:', metrics);
      }

      // Send to analytics service if available
      if (typeof window !== 'undefined' && (window as any).analytics) {
        (window as any).analytics.track('api_request', metrics);
      }
    }
  }

  // Enhanced retry mechanism with exponential backoff
  private async withRetry<T>(
    fn: () => Promise<T>,
    maxAttempts: number = CONFIG.api.retryAttempts,
    baseDelay: number = 1000
  ): Promise<T> {
    let lastError: Error;
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        
        // Don't retry on client errors (4xx) except for specific cases
        if (error instanceof APIError && error.isClientError() && error.status !== 429) {
          throw error;
        }
        
        if (attempt === maxAttempts) {
          throw lastError;
        }
        
        // Exponential backoff with jitter
        const delay = baseDelay * Math.pow(2, attempt - 1) + Math.random() * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError!;
  }

  async get<T>(endpoint: string, params?: Record<string, any>, options?: { retry?: boolean }): Promise<APIResponse<T>> {
    const searchParams = params ? new URLSearchParams(params).toString() : '';
    const url = searchParams ? `${endpoint}?${searchParams}` : endpoint;
    
    const requestFn = () => this.request<T>(url, { method: 'GET' });
    
    return options?.retry !== false ? this.withRetry(requestFn) : requestFn();
  }

  async post<T>(endpoint: string, data?: any, options?: { retry?: boolean }): Promise<APIResponse<T>> {
    const requestFn = () => this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
    
    return options?.retry !== false ? this.withRetry(requestFn) : requestFn();
  }

  async put<T>(endpoint: string, data?: any, options?: { retry?: boolean }): Promise<APIResponse<T>> {
    const requestFn = () => this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
    
    return options?.retry !== false ? this.withRetry(requestFn) : requestFn();
  }

  async delete<T>(endpoint: string, options?: { retry?: boolean }): Promise<APIResponse<T>> {
    const requestFn = () => this.request<T>(endpoint, { method: 'DELETE' });
    
    return options?.retry !== false ? this.withRetry(requestFn) : requestFn();
  }

  async patch<T>(endpoint: string, data?: any, options?: { retry?: boolean }): Promise<APIResponse<T>> {
    const requestFn = () => this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
    
    return options?.retry !== false ? this.withRetry(requestFn) : requestFn();
  }

  // Request cancellation methods
  cancelRequest(requestId: string): void {
    const controller = this.requestQueue.get(requestId);
    if (controller) {
      controller.abort();
      this.requestQueue.delete(requestId);
    }
  }

  cancelAllRequests(): void {
    this.requestQueue.forEach(controller => controller.abort());
    this.requestQueue.clear();
  }

  // Health check method
  async healthCheck(): Promise<{ status: string; timestamp: string; constitutionalHash: string }> {
    try {
      const response = await this.get<{ status: string }>('/health', undefined, { retry: false });
      return {
        status: response.data.status,
        timestamp: new Date().toISOString(),
        constitutionalHash: CONFIG.constitutional.hash,
      };
    } catch (error) {
      return {
        status: 'error',
        timestamp: new Date().toISOString(),
        constitutionalHash: CONFIG.constitutional.hash,
      };
    }
  }

  setAuthToken(token: string) {
    this.headers['Authorization'] = `Bearer ${token}`;
  }

  removeAuthToken() {
    delete this.headers['Authorization'];
  }

  setTenantId(tenantId: string) {
    this.headers['X-Tenant-ID'] = tenantId;
  }

  setRequestId(requestId: string) {
    this.headers['X-Request-ID'] = requestId;
  }
}

// GraphQL Client
export class GraphQLClient {
  private client: APIClient;

  constructor(baseURL: string = CONFIG.api.graphqlUrl) {
    this.client = new APIClient(baseURL);
  }

  async query<T>(
    query: string,
    variables?: Record<string, any>
  ): Promise<APIResponse<T>> {
    return this.client.post<T>('', {
      query,
      variables,
    });
  }

  async mutation<T>(
    mutation: string,
    variables?: Record<string, any>
  ): Promise<APIResponse<T>> {
    return this.client.post<T>('', {
      query: mutation,
      variables,
    });
  }

  setAuthToken(token: string) {
    this.client.setAuthToken(token);
  }
}

// WebSocket Client
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, ((data: any) => void)[]> = new Map();

  constructor(private url: string) {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          this.reconnectAttempts = 0;
          
          // Send constitutional hash for validation
          this.send('auth', { constitutionalHash: CONFIG.constitutional.hash });
          
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            // Validate constitutional hash
            if (data.constitutionalCompliance?.hash !== CONFIG.constitutional.hash) {
              console.error('Constitutional hash mismatch in WebSocket message');
              return;
            }

            // Emit to listeners
            const listeners = this.listeners.get(data.type) || [];
            listeners.forEach(listener => listener(data));
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = () => {
          this.handleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        this.connect().catch(console.error);
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  send(type: string, data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type,
        data,
        constitutionalCompliance: {
          hash: CONFIG.constitutional.hash,
          timestamp: new Date().toISOString(),
        },
      }));
    }
  }

  subscribe(type: string, listener: (data: any) => void) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type)!.push(listener);

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(type) || [];
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
  }
}

// Singleton instances with enhanced configuration
export const apiClient = new APIClient(CONFIG.api.baseUrl);
export const graphqlClient = new GraphQLClient(CONFIG.api.graphqlUrl);
export const wsClient = new WebSocketClient(CONFIG.api.wsUrl);

// Utility functions
export const withRetry = async <T>(
  fn: () => Promise<T>,
  maxAttempts = CONFIG.api.retryAttempts,
  delay = 1000
): Promise<T> => {
  let lastError: Error;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt === maxAttempts) {
        throw lastError;
      }
      
      // Exponential backoff with jitter
      const backoffDelay = delay * Math.pow(2, attempt - 1) + Math.random() * 1000;
      await new Promise(resolve => setTimeout(resolve, backoffDelay));
    }
  }
  
  throw lastError!;
};

export const createRequestId = (): string => {
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
};

// Performance monitoring helper
export const measureApiPerformance = <T>(
  operation: string,
  fn: () => Promise<T>
): Promise<T> => {
  const startTime = performance.now();
  
  return fn().then(
    result => {
      if (CONFIG.features.enablePerformanceMonitoring) {
        const duration = performance.now() - startTime;
        console.log(`API Operation "${operation}" completed in ${duration.toFixed(2)}ms`);
      }
      return result;
    },
    error => {
      if (CONFIG.features.enablePerformanceMonitoring) {
        const duration = performance.now() - startTime;
        console.log(`API Operation "${operation}" failed after ${duration.toFixed(2)}ms:`, error);
      }
      throw error;
    }
  );
};

// Constitutional compliance helper
export const validateConstitutionalResponse = (response: any): boolean => {
  if (!CONFIG.constitutional.validationEnabled) {
    return true;
  }
  
  return response?.constitutionalCompliance?.hash === CONFIG.constitutional.hash;
};

// Batch request helper
export const batchRequests = async <T>(
  requests: Array<() => Promise<T>>,
  concurrency: number = 3
): Promise<T[]> => {
  const results: T[] = [];
  
  for (let i = 0; i < requests.length; i += concurrency) {
    const batch = requests.slice(i, i + concurrency);
    const batchResults = await Promise.all(batch.map(request => request()));
    results.push(...batchResults);
  }
  
  return results;
};