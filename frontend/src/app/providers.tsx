'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { SessionProvider } from 'next-auth/react';
import { ThemeProvider } from 'next-themes';
import { useState } from 'react';

import { ConstitutionalContextProvider } from '@/contexts/constitutional-context';
import { PersonalizationProvider } from '@/contexts/personalization-context';
import { ToastProvider } from '@/contexts/toast-context';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            gcTime: 10 * 60 * 1000, // 10 minutes
            retry: (failureCount, error) => {
              // Don't retry on 4xx errors
              if (error && 'status' in error && typeof error.status === 'number') {
                return error.status >= 500 && failureCount < 3;
              }
              return failureCount < 3;
            },
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <SessionProvider>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <ConstitutionalContextProvider>
            <PersonalizationProvider>
              <ToastProvider>
                {children}
                <ReactQueryDevtools initialIsOpen={false} />
              </ToastProvider>
            </PersonalizationProvider>
          </ConstitutionalContextProvider>
        </ThemeProvider>
      </SessionProvider>
    </QueryClientProvider>
  );
}