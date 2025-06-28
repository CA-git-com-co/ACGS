'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface SkipLinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string;
  children: React.ReactNode;
}

const SkipLink = React.forwardRef<HTMLAnchorElement, SkipLinkProps>(
  ({ className, href, children, ...props }, ref) => {
    return (
      <a
        ref={ref}
        href={href}
        className={cn(
          // Position skip link off-screen by default
          'sr-only absolute -top-40 left-6 z-[9999] bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium',
          // Show skip link when focused
          'focus:not-sr-only focus:top-6',
          // Ensure proper focus styles
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          className
        )}
        {...props}
      >
        {children}
      </a>
    );
  }
);
SkipLink.displayName = 'SkipLink';

export { SkipLink };
