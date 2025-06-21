import { z } from 'zod';
import { validateData } from '../types/validation';

/**
 * Prop validation utilities for React components
 *
 * Provides runtime prop validation using Zod schemas with development
 * warnings and production safety.
 */

/**
 * Development mode prop validator
 * @param schema - Zod schema to validate props against
 * @param props - Component props to validate
 * @param componentName - Name of the component for error reporting
 * @returns Validated props or original props with warnings
 */
export function validateProps<T>(
  schema: z.ZodSchema<T>,
  props: unknown,
  componentName: string = 'Component'
): T {
  // Only validate in development mode
  if (process.env.NODE_ENV === 'development') {
    const result = validateData(schema, props);

    if (!result.success) {
      console.group(`🚨 Prop validation failed for ${componentName}`);
      console.error('Invalid props:', props);
      console.error('Validation errors:');
      result.errors.forEach(error => console.error(`  - ${error}`));
      console.groupEnd();

      // In development, we still return the original props to avoid breaking the app
      // but with a warning that validation failed
      return props as T;
    }

    return result.data;
  }

  // In production, skip validation for performance
  return props as T;
}

/**
 * Higher-order component that adds prop validation
 * @param schema - Zod schema for prop validation
 * @param WrappedComponent - Component to wrap with validation
 * @returns Component with prop validation
 */
export function withPropValidation<P extends object>(
  schema: z.ZodSchema<P>,
  WrappedComponent: React.ComponentType<P>
) {
  const ValidatedComponent: React.FC<P> = props => {
    const validatedProps = validateProps(
      schema,
      props,
      WrappedComponent.displayName || WrappedComponent.name || 'Component'
    );

    return <WrappedComponent {...validatedProps} />;
  };

  ValidatedComponent.displayName = `withPropValidation(${WrappedComponent.displayName || WrappedComponent.name})`;

  return ValidatedComponent;
}

/**
 * Hook for validating props within a component
 * @param schema - Zod schema for validation
 * @param props - Props to validate
 * @param componentName - Component name for error reporting
 * @returns Validation result
 */
export function usePropValidation<T>(
  schema: z.ZodSchema<T>,
  props: unknown,
  componentName?: string
): { isValid: boolean; errors: string[]; data?: T } {
  const result = validateData(schema, props);

  if (result.success) {
    return {
      isValid: true,
      errors: [],
      data: result.data
    };
  }

  // Log errors in development
  if (process.env.NODE_ENV === 'development' && componentName) {
    console.warn(`Prop validation failed for ${componentName}:`, result.errors);
  }

  return {
    isValid: false,
    errors: result.errors
  };
}

/**
 * Validates API response data
 * @param schema - Zod schema for the expected response
 * @param response - API response to validate
 * @param endpoint - API endpoint for error reporting
 * @returns Validated response data
 */
export function validateApiResponse<T>(
  schema: z.ZodSchema<T>,
  response: unknown,
  endpoint?: string
): T {
  const result = validateData(schema, response);

  if (!result.success) {
    const errorMessage = `API response validation failed${endpoint ? ` for ${endpoint}` : ''}`;
    console.error(errorMessage, result.errors);

    // In development, log the full response for debugging
    if (process.env.NODE_ENV === 'development') {
      console.error('Invalid response:', response);
    }

    throw new Error(`${errorMessage}: ${result.errors.join(', ')}`);
  }

  return result.data;
}

/**
 * Form validation helper
 * @param schema - Zod schema for form data
 * @param formData - Form data to validate
 * @returns Validation result with field-specific errors
 */
export function validateFormData<T>(
  schema: z.ZodSchema<T>,
  formData: unknown
): {
  isValid: boolean;
  data?: T;
  errors: Record<string, string[]>;
  globalErrors: string[];
} {
  try {
    const validatedData = schema.parse(formData);
    return {
      isValid: true,
      data: validatedData,
      errors: {},
      globalErrors: []
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const fieldErrors: Record<string, string[]> = {};
      const globalErrors: string[] = [];

      error.errors.forEach(err => {
        if (err.path.length > 0) {
          const fieldPath = err.path.join('.');
          if (!fieldErrors[fieldPath]) {
            fieldErrors[fieldPath] = [];
          }
          fieldErrors[fieldPath].push(err.message);
        } else {
          globalErrors.push(err.message);
        }
      });

      return {
        isValid: false,
        errors: fieldErrors,
        globalErrors
      };
    }

    return {
      isValid: false,
      errors: {},
      globalErrors: ['Unknown validation error']
    };
  }
}

/**
 * Creates a type-safe prop validator function
 * @param schema - Zod schema
 * @returns Validator function
 */
export function createPropValidator<T>(schema: z.ZodSchema<T>) {
  return (props: unknown, componentName?: string): T => {
    return validateProps(schema, props, componentName);
  };
}

/**
 * Validates environment variables
 * @param schema - Zod schema for environment variables
 * @param env - Environment object (defaults to process.env)
 * @returns Validated environment variables
 */
export function validateEnv<T>(
  schema: z.ZodSchema<T>,
  env: Record<string, string | undefined> = process.env
): T {
  const result = validateData(schema, env);

  if (!result.success) {
    console.error('Environment validation failed:', result.errors);
    throw new Error(`Invalid environment configuration: ${result.errors.join(', ')}`);
  }

  return result.data;
}

/**
 * Type guard function generator
 * @param schema - Zod schema
 * @returns Type guard function
 */
export function createTypeGuard<T>(schema: z.ZodSchema<T>) {
  return (value: unknown): value is T => {
    try {
      schema.parse(value);
      return true;
    } catch {
      return false;
    }
  };
}

/**
 * Assertion function generator
 * @param schema - Zod schema
 * @returns Assertion function
 */
export function createAssertion<T>(schema: z.ZodSchema<T>) {
  return (value: unknown, message?: string): asserts value is T => {
    try {
      schema.parse(value);
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errorMessage =
          message || `Assertion failed: ${error.errors.map(e => e.message).join(', ')}`;
        throw new Error(errorMessage);
      }
      throw error;
    }
  };
}

/**
 * Safe parser that returns a result object instead of throwing
 * @param schema - Zod schema
 * @param data - Data to parse
 * @returns Parse result
 */
export function safeParse<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: T } | { success: false; error: z.ZodError } {
  try {
    const result = schema.parse(data);
    return { success: true, data: result };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false, error };
    }
    throw error;
  }
}

/**
 * Validates and transforms data with custom error handling
 * @param schema - Zod schema
 * @param data - Data to validate
 * @param onError - Custom error handler
 * @returns Validated data or result of error handler
 */
export function validateWithErrorHandler<T, E>(
  schema: z.ZodSchema<T>,
  data: unknown,
  onError: (errors: string[]) => E
): T | E {
  const result = validateData(schema, data);

  if (result.success) {
    return result.data;
  }

  return onError(result.errors);
}

/**
 * Batch validation for multiple values
 * @param schema - Zod schema
 * @param values - Array of values to validate
 * @returns Array of validation results
 */
export function batchValidate<T>(
  schema: z.ZodSchema<T>,
  values: unknown[]
): Array<
  { success: true; data: T; index: number } | { success: false; errors: string[]; index: number }
> {
  return values.map((value, index) => {
    const result = validateData(schema, value);
    return { ...result, index };
  });
}

// Export commonly used schemas for convenience
export {
  UserSchema,
  PrincipleSchema,
  PolicySchema,
  ComplianceResultSchema,
  LoadingPropsSchema,
  ErrorBoundaryPropsSchema,
  ServiceErrorBoundaryPropsSchema
} from '../types/validation';
