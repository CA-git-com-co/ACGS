import * as React from 'react';
import { cn } from '@/lib/utils';

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  helperText?: string;
  label?: string;
  constitutional?: boolean;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, helperText, label, constitutional, ...props }, ref) => {
    const id = props.id || props.name;
    
    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={id}
            className={cn(
              'block text-sm font-medium text-foreground mb-1',
              constitutional && 'text-constitutional-700'
            )}
          >
            {label}
          </label>
        )}
        <input
          type={type}
          className={cn(
            'flex h-10 w-full rounded-lg border border-input bg-transparent px-4 py-2.5 text-sm shadow-resend transition-all duration-200 file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:shadow-resend-md disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-destructive focus-visible:ring-destructive',
            constitutional && 'border-constitutional-300 focus-visible:ring-constitutional-500',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="mt-1 text-xs text-destructive">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-xs text-muted-foreground">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };