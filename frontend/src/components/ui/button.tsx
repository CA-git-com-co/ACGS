import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground shadow-resend hover:bg-primary/90 hover:shadow-resend-md',
        destructive: 'bg-destructive text-destructive-foreground shadow-resend hover:bg-destructive/90 hover:shadow-resend-md',
        outline: 'border border-input bg-background shadow-resend hover:bg-accent hover:text-accent-foreground hover:shadow-resend-md',
        secondary: 'bg-secondary text-secondary-foreground shadow-resend hover:bg-secondary/80 hover:shadow-resend-md',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
        constitutional: 'bg-constitutional-600 text-white shadow-resend hover:bg-constitutional-700 hover:shadow-resend-md',
        governance: 'bg-governance-600 text-white shadow-resend hover:bg-governance-700 hover:shadow-resend-md',
        success: 'bg-success-600 text-white shadow-resend hover:bg-success-700 hover:shadow-resend-md',
        warning: 'bg-warning-600 text-white shadow-resend hover:bg-warning-700 hover:shadow-resend-md',
        error: 'bg-error-600 text-white shadow-resend hover:bg-error-700 hover:shadow-resend-md',
        resend: 'bg-resend-500 text-white shadow-resend hover:bg-resend-600 hover:shadow-resend-md',
      },
      size: {
        default: 'h-10 px-6 py-2.5',
        sm: 'h-8 rounded-lg px-4 text-xs',
        lg: 'h-12 rounded-lg px-8 text-base',
        icon: 'h-10 w-10',
        xs: 'h-7 rounded-md px-3 text-xs',
        xl: 'h-14 rounded-lg px-12 text-lg',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  constitutional?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, loading, icon, constitutional, children, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    
    // Apply constitutional variant if constitutional prop is true
    const finalVariant = constitutional ? 'constitutional' : variant;
    
    return (
      <Comp
        className={cn(buttonVariants({ variant: finalVariant, size, className }))}
        ref={ref}
        disabled={loading || props.disabled}
        {...props}
      >
        {loading && (
          <svg
            className="mr-2 h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {icon && !loading && <span className="mr-2">{icon}</span>}
        {children}
      </Comp>
    );
  }
);

Button.displayName = 'Button';

export { Button, buttonVariants };