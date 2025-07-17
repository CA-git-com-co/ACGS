import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ErrorBoundary, APIErrorBoundary, RealTimeErrorBoundary } from '../ErrorBoundary';

// Mock the config
vi.mock('@/config', () => ({
  CONFIG: {
    constitutional: {
      hash: 'cdd01ef066bc6cf2',
    },
    features: {
      enableAuditLogging: true,
    },
  },
}));

// Mock fetch for error reporting
global.fetch = vi.fn();

// Component that throws an error
const ThrowError = ({ shouldThrow = true }: { shouldThrow?: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error message');
  }
  return <div>No error</div>;
};

// Component that throws an error after render
const ThrowErrorAfterEffect = () => {
  React.useEffect(() => {
    throw new Error('Effect error');
  }, []);
  return <div>Component rendered</div>;
};

describe('ErrorBoundary', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock console.error to avoid noise in tests
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Basic Error Boundary', () => {
    it('should catch and display errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByText('An unexpected error occurred while rendering this component')).toBeInTheDocument();
    });

    it('should display error message', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Error: Test error message')).toBeInTheDocument();
    });

    it('should display constitutional hash', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Constitutional Hash: cdd01ef066bc6cf2')).toBeInTheDocument();
    });

    it('should display error ID', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      const errorIdElement = screen.getByText(/Error ID:/);
      expect(errorIdElement).toBeInTheDocument();
    });

    it('should call onError callback when provided', () => {
      const onErrorMock = vi.fn();
      
      render(
        <ErrorBoundary onError={onErrorMock}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(onErrorMock).toHaveBeenCalledWith(
        expect.any(Error),
        expect.any(Object),
        expect.any(String)
      );
    });

    it('should render children when no error', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('No error')).toBeInTheDocument();
    });
  });

  describe('Error Boundary with Retry', () => {
    it('should show retry button', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    it('should retry on button click', async () => {
      const TestComponent = () => {
        const [shouldThrow, setShouldThrow] = React.useState(true);
        
        React.useEffect(() => {
          const timer = setTimeout(() => {
            setShouldThrow(false);
          }, 100);
          return () => clearTimeout(timer);
        }, []);

        return <ThrowError shouldThrow={shouldThrow} />;
      };

      render(
        <ErrorBoundary>
          <TestComponent />
        </ErrorBoundary>
      );

      // Initially should show error
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      
      // Click retry
      fireEvent.click(screen.getByText('Try Again'));
      
      // Should eventually show success
      await waitFor(() => {
        expect(screen.getByText('No error')).toBeInTheDocument();
      });
    });

    it('should track retry count', () => {
      render(
        <ErrorBoundary maxRetries={3}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Retry 0/3')).toBeInTheDocument();
    });

    it('should disable retry button after max retries', () => {
      render(
        <ErrorBoundary maxRetries={1}>
          <ThrowError />
        </ErrorBoundary>
      );

      const retryButton = screen.getByText('Try Again');
      
      // First retry
      fireEvent.click(retryButton);
      
      // Should still be enabled after first retry
      expect(retryButton).not.toBeDisabled();
      
      // Second retry (should reach max)
      fireEvent.click(retryButton);
      
      // Should be disabled after max retries
      expect(retryButton).toBeDisabled();
    });
  });

  describe('Error Boundary with Custom Fallback', () => {
    it('should render custom fallback', () => {
      const customFallback = (error: Error, retry: () => void) => (
        <div>
          <h2>Custom Error</h2>
          <p>{error.message}</p>
          <button onClick={retry}>Custom Retry</button>
        </div>
      );

      render(
        <ErrorBoundary fallback={customFallback}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Custom Error')).toBeInTheDocument();
      expect(screen.getByText('Test error message')).toBeInTheDocument();
      expect(screen.getByText('Custom Retry')).toBeInTheDocument();
    });
  });

  describe('Error Boundary with Details', () => {
    it('should show details when enabled', () => {
      render(
        <ErrorBoundary showDetails={true}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Stack Trace')).toBeInTheDocument();
      expect(screen.getByText('Component Stack')).toBeInTheDocument();
    });

    it('should hide details by default', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.queryByText('Stack Trace')).not.toBeInTheDocument();
    });
  });

  describe('Error Reporting', () => {
    it('should report errors when audit logging is enabled', async () => {
      const fetchMock = vi.mocked(fetch);
      fetchMock.mockResolvedValueOnce(new Response('OK'));

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      await waitFor(() => {
        expect(fetchMock).toHaveBeenCalledWith('/api/errors', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Constitutional-Hash': 'cdd01ef066bc6cf2',
          },
          body: expect.stringContaining('Test error message'),
        });
      });
    });

    it('should handle error reporting failures gracefully', async () => {
      const fetchMock = vi.mocked(fetch);
      fetchMock.mockRejectedValueOnce(new Error('Network error'));

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(
          'Failed to report error:',
          expect.any(Error)
        );
      });
    });
  });

  describe('Specialized Error Boundaries', () => {
    it('should render API error boundary with custom fallback', () => {
      render(
        <APIErrorBoundary>
          <ThrowError />
        </APIErrorBoundary>
      );

      expect(screen.getByText('API Error')).toBeInTheDocument();
      expect(screen.getByText('Failed to communicate with the server. Please check your connection.')).toBeInTheDocument();
    });

    it('should render real-time error boundary', () => {
      render(
        <RealTimeErrorBoundary>
          <ThrowError />
        </RealTimeErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });
  });

  describe('Reload Functionality', () => {
    it('should show reload button', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Reload Page')).toBeInTheDocument();
    });

    it('should trigger reload on button click', () => {
      const mockReload = vi.fn();
      Object.defineProperty(window, 'location', {
        value: { reload: mockReload },
        writable: true,
      });

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      fireEvent.click(screen.getByText('Reload Page'));
      expect(mockReload).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      // Check for proper headings
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      
      // Check for proper button roles
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /reload page/i })).toBeInTheDocument();
    });
  });
});