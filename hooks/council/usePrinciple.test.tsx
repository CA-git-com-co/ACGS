import React from 'react';
import { renderHook, waitFor } from '@testing-library/react';
import { usePrinciple } from './usePrinciple'; // Adjust path if your structure differs
import { SWRConfig } from 'swr';

// Mocking fetch
global.fetch = jest.fn();

const mockPrinciple = { id: '1', title: 'Principle 1', content: 'Details for principle 1' };

// Wrapper to provide SWRConfig cache to the hook.
// eslint-disable-next-line react/prop-types
const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
      {children}
    </SWRConfig>
  );
};

describe('usePrinciple Hook', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  it('should return loading initially, then data on success with a valid ID', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPrinciple,
    });

    const { result } = renderHook(() => usePrinciple('1'), { wrapper: AllTheProviders });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.principle).toBeUndefined();
    expect(result.current.isError).toBeUndefined();

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.principle).toEqual(mockPrinciple);
    expect(result.current.isError).toBeUndefined();
  });

  it('should return an error if fetch fails with a valid ID', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ message: 'Server Error' }), // Optional error details
      text: async () => 'Server Error'
    });

    const { result } = renderHook(() => usePrinciple('1'), { wrapper: AllTheProviders });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.isError).toBeInstanceOf(Error);
    expect(result.current.isError?.message).toBe('An error occurred while fetching the data.');
    expect(result.current.principle).toBeUndefined();
  });

  it('should not fetch if principleId is null', () => {
    const { result } = renderHook(() => usePrinciple(null), { wrapper: AllTheProviders });

    expect(fetch).not.toHaveBeenCalled();
    // For a null key, SWR's isLoading is typically false, data and error undefined.
    expect(result.current.isLoading).toBe(false);
    expect(result.current.principle).toBeUndefined();
    expect(result.current.isError).toBeUndefined();
  });

  it('should not fetch if principleId is undefined', () => {
    // Pass undefined explicitly to the hook call
    const { result } = renderHook(() => usePrinciple(undefined as string | null | undefined), { wrapper: AllTheProviders });


    expect(fetch).not.toHaveBeenCalled();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.principle).toBeUndefined();
    expect(result.current.isError).toBeUndefined();
  });

  it('should return an error if JSON parsing fails with a valid ID', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => { throw new SyntaxError("Unexpected token < in JSON at position 0"); },
    });

    const { result } = renderHook(() => usePrinciple('1'), { wrapper: AllTheProviders });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.isError).toBeInstanceOf(Error);
    expect(result.current.isError?.message).toBe('Failed to parse JSON response.');
    expect(result.current.principle).toBeUndefined();
  });

  // Test case for when ID changes from null to valid
  it('should fetch when principleId changes from null to a valid ID', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPrinciple,
    });

    const { result, rerender } = renderHook(({ id }) => usePrinciple(id), {
      initialProps: { id: null as string | null },
      wrapper: AllTheProviders,
    });

    // Initial state with null ID
    expect(fetch).not.toHaveBeenCalled();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.principle).toBeUndefined();

    // Rerender with a valid ID
    rerender({ id: '1' });

    // Now it should be loading
    expect(result.current.isLoading).toBe(true);
    expect(fetch).toHaveBeenCalledWith('/api/principles/1');

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.principle).toEqual(mockPrinciple);
    expect(result.current.isError).toBeUndefined();
  });
});
