import React from 'react'; // Added React import for JSX
import { renderHook, waitFor } from '@testing-library/react';
import { usePrinciples } from './usePrinciples'; // Assuming this path is correct from the test file's location
import { SWRConfig } from 'swr';

// Mocking fetch
global.fetch = jest.fn();

const mockPrinciples = [
  { id: '1', title: 'Principle 1' },
  { id: '2', title: 'Principle 2' },
];

// Wrapper to provide SWRConfig cache to the hook. This helps reset cache between tests.
const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <SWRConfig value={{ provider: () => new Map() }}>
      {children}
    </SWRConfig>
  );
};


describe('usePrinciples Hook', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
    // Reset SWR cache if needed, though AllTheProviders should handle this for each renderHook
  });

  it('should return loading initially, then data on success', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPrinciples,
    });

    const { result } = renderHook(() => usePrinciples(), { wrapper: AllTheProviders });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.principles).toBeUndefined();
    expect(result.current.isError).toBeUndefined();

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.principles).toEqual(mockPrinciples);
    expect(result.current.isError).toBeUndefined(); // isError should remain undefined on success
  });

  it('should return an error if fetch fails due to network or server error (res.ok is false)', async () => {
    const errorResponse = { message: 'Server Error' };
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => errorResponse, // Optional: if your fetcher tries to parse error.info
      text: async () => 'Server Error' // Optional: if your fetcher tries to parse error.info as text
    });

    const { result } = renderHook(() => usePrinciples(), { wrapper: AllTheProviders });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isError).toBeInstanceOf(Error);
    expect(result.current.isError.message).toBe('An error occurred while fetching the data.');
    expect(result.current.principles).toBeUndefined();
  });

  it('should return an error if JSON parsing fails', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => { throw new SyntaxError("Unexpected token < in JSON at position 0"); },
      // SWR fetcher might try to call .text() if .json() fails, or it might depend on the exact fetcher implementation.
      // For this test, we assume the error from .json() is what gets caught and propagated.
    });

    const { result } = renderHook(() => usePrinciples(), { wrapper: AllTheProviders });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.isError).toBeInstanceOf(Error);
    // The exact error message might depend on how SWR and the fetcher handle it.
    // The hook itself wraps it in 'Failed to parse JSON response.'
    expect(result.current.isError.message).toBe('Failed to parse JSON response.');
    expect(result.current.principles).toBeUndefined();
  });

  it('should handle initial loading state correctly', () => {
    // This test focuses on the synchronous part of the initial render
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPrinciples,
    });

    const { result } = renderHook(() => usePrinciples(), { wrapper: AllTheProviders });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.principles).toBeUndefined();
    expect(result.current.isError).toBeUndefined();
    // No await waitFor here, we are just checking the state before any async operation completes
  });
});
