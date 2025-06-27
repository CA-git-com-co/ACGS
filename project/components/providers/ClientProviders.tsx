'use client';

import { SessionProvider } from 'next-auth/react';
import { QueryProvider } from '@/components/providers/QueryProvider';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import { FeatureFlagProvider } from '@/lib/feature-flags/provider';
import { Toaster } from '@/components/ui/sonner';

export function ClientProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
      <SessionProvider>
        <QueryProvider>
          <FeatureFlagProvider>
            <div className="min-h-screen bg-background">{children}</div>
            <Toaster richColors position="top-right" />
          </FeatureFlagProvider>
        </QueryProvider>
      </SessionProvider>
    </ThemeProvider>
  );
}
