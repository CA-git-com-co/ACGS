import { Inter, JetBrains_Mono } from 'next/font/google';
import { Providers } from './providers';
import { ConstitutionalCompliance } from '@/components/constitutional/constitutional-compliance';
import { MainNavigation } from '@/components/navigation/MainNavigation';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { Toaster } from '@/components/ui/toast';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
});

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

export const metadata = {
  title: 'ACGS-2 Constitutional AI Governance System',
  description: 'Modern frontend for ACGS-2 Constitutional AI Governance System with custom experience enhancement',
  keywords: ['constitutional-ai', 'governance', 'ai-safety', 'compliance'],
  authors: [{ name: 'ACGS-2 Team' }],
  creator: 'ACGS-2 Team',
  publisher: 'ACGS-2 Team',

  robots: {
    index: false,
    follow: false,
    nocache: true,
    googleBot: {
      index: false,
      follow: false,
      noimageindex: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
  other: {
    'constitutional-hash': 'cdd01ef066bc6cf2',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="constitutional-hash" content="cdd01ef066bc6cf2" />
        <meta name="theme-color" content="#0ea5e9" />
        <meta name="msapplication-TileColor" content="#0ea5e9" />
        <meta name="color-scheme" content="light dark" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}
        suppressHydrationWarning
      >
        <Providers>
          <ErrorBoundary showDetails={process.env.NODE_ENV === 'development'}>
            <ConstitutionalCompliance>
              <div className="relative flex min-h-screen bg-background">
                <MainNavigation />
                <div className="flex-1 flex flex-col">
                  <main className="flex-1 overflow-auto">
                    <ErrorBoundary maxRetries={2}>
                      {children}
                    </ErrorBoundary>
                  </main>
                </div>
              </div>
            </ConstitutionalCompliance>
          </ErrorBoundary>
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}