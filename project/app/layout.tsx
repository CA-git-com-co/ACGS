import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ClientProviders } from '@/components/providers/ClientProviders';
import { SkipLink } from '@/components/ui/skip-link';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'ACGS - Autonomous Constitutional Governance System',
  description: 'Unified platform for constitutional governance and policy management',
  keywords: ['governance', 'constitutional', 'policy', 'blockchain', 'democracy'],
  authors: [{ name: 'ACGS Team', url: 'https://acgs.ai' }],
  creator: 'ACGS Team',
  publisher: 'ACGS',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
  },
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        {/* Skip navigation links for accessibility */}
        <SkipLink href="#main-content">Skip to main content</SkipLink>
        <SkipLink href="#navigation">Skip to navigation</SkipLink>

        <ClientProviders>
          {/* Main layout structure with proper landmarks */}
          <div className="min-h-screen bg-background">{children}</div>
        </ClientProviders>
      </body>
    </html>
  );
}
