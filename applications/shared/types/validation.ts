import { z } from 'zod';

/**
 * Zod validation schemas for ACGS-PGP Framework types
 *
 * These schemas provide runtime validation for component props,
 * API responses, and form data to ensure type safety and data integrity.
 */

// Base validation schemas
export const IdSchema = z.string().min(1, 'ID is required');
export const EmailSchema = z.string().email('Invalid email format');
export const UrlSchema = z.string().url('Invalid URL format');
export const DateSchema = z
  .union([z.string(), z.date()])
  .transform(val => (typeof val === 'string' ? new Date(val) : val));

// User and Authentication schemas
export const UserSchema = z.object({
  /** Unique user identifier */
  id: IdSchema,
  /** Username for authentication */
  username: z.string().min(3, 'Username must be at least 3 characters'),
  /** User email address (optional) */
  email: EmailSchema.optional(),
  /** User role in the system */
  role: z.enum(['admin', 'user', 'moderator', 'viewer']),
  /** Account creation timestamp */
  createdAt: DateSchema.optional()
});

export const AuthContextSchema = z.object({
  /** Currently authenticated user */
  currentUser: UserSchema.nullable(),
  /** Authentication status */
  isAuthenticated: z.boolean(),
  /** Loading state for auth operations */
  isLoading: z.boolean(),
  /** Login function */
  login: z.function().args(z.string(), z.string()).returns(z.promise(z.void())),
  /** Logout function */
  logout: z.function().args().returns(z.promise(z.void())),
  /** Token refresh function */
  refreshToken: z.function().args().returns(z.promise(z.void()))
});

// Principle schemas for AC Service
export const PrincipleSchema = z.object({
  /** Unique principle identifier */
  id: IdSchema,
  /** Principle title */
  title: z.string().min(1, 'Title is required').max(200, 'Title too long'),
  /** Principle content/description */
  content: z.string().min(10, 'Content must be at least 10 characters'),
  /** Principle category */
  category: z.string().min(1, 'Category is required'),
  /** Priority level (1-10, higher is more important) */
  priority: z.number().int().min(1).max(10),
  /** Creation timestamp */
  createdAt: DateSchema.optional(),
  /** Last update timestamp */
  updatedAt: DateSchema.optional(),
  /** Author identifier */
  author: z.string().optional()
});

// Policy schemas for GS Service
export const PolicyRuleSchema = z.object({
  /** Rule identifier */
  id: IdSchema,
  /** Condition that triggers the rule */
  condition: z.string().min(1, 'Condition is required'),
  /** Action to take when condition is met */
  action: z.string().min(1, 'Action is required')
});

export const PolicySchema = z.object({
  /** Unique policy identifier */
  id: IdSchema,
  /** Policy name */
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  /** Policy description */
  description: z.string().min(10, 'Description must be at least 10 characters'),
  /** Policy rules */
  rules: z.array(PolicyRuleSchema).min(1, 'At least one rule is required'),
  /** Validation score (0-100) */
  validationScore: z.number().min(0).max(100),
  /** Compliance complexity score (0-100) */
  complianceComplexity: z.number().min(0).max(100),
  /** Policy status */
  status: z.enum(['draft', 'active', 'archived']),
  /** Policy category */
  category: z.string().min(1, 'Category is required'),
  /** Creation timestamp */
  createdAt: DateSchema,
  /** Last update timestamp */
  updatedAt: DateSchema,
  /** Author identifier */
  author: z.string().min(1, 'Author is required')
});

export const ActivePolicySchema = z.object({
  /** Policy identifier */
  id: IdSchema,
  /** Policy name */
  name: z.string().min(1, 'Name is required'),
  /** Policy rules */
  rules: z.array(PolicyRuleSchema)
});

// Compliance schemas for PGC Service
export const ComplianceResultSchema = z.object({
  /** Whether the action is compliant */
  compliant: z.boolean(),
  /** Confidence score (0-100) */
  confidenceScore: z.number().min(0).max(100),
  /** Reasons for violation (if any) */
  violationReasons: z.array(z.string()).optional()
});

// Amendment schemas
export const AmendmentVoteSchema = z.object({
  /** Vote identifier */
  id: IdSchema,
  /** Amendment being voted on */
  amendmentId: IdSchema,
  /** User casting the vote */
  userId: IdSchema,
  /** Vote choice */
  vote: z.enum(['yes', 'no', 'abstain']),
  /** Optional comment */
  comment: z.string().optional(),
  /** Vote timestamp */
  createdAt: DateSchema
});

export const AmendmentSchema = z.object({
  /** Amendment identifier */
  id: IdSchema,
  /** Amendment title */
  title: z.string().min(1, 'Title is required').max(200, 'Title too long'),
  /** Amendment description */
  description: z.string().min(10, 'Description must be at least 10 characters'),
  /** Proposer identifier */
  proposer: z.string().min(1, 'Proposer is required'),
  /** Amendment status */
  status: z.enum(['pending', 'voting', 'approved', 'rejected']),
  /** Voting deadline */
  votingDeadline: DateSchema.optional(),
  /** Creation timestamp */
  createdAt: DateSchema,
  /** Votes cast */
  votes: z.array(AmendmentVoteSchema).optional()
});

// Synthesis schemas for GS Engine
export const SynthesisRequestSchema = z.object({
  /** Principles to synthesize from */
  principles: z
    .array(
      z.object({
        id: IdSchema
      })
    )
    .min(1, 'At least one principle is required')
});

export const SynthesisResultSchema = z.object({
  /** Generated policies */
  policies: z.array(PolicySchema),
  /** Overall validation score */
  validationScore: z.number().min(0).max(100),
  /** Overall compliance complexity */
  complianceComplexity: z.number().min(0).max(100)
});

// Component prop validation schemas
export const LoadingPropsSchema = z.object({
  /** Loading spinner size */
  size: z.enum(['sm', 'md', 'lg', 'xl']).optional(),
  /** Loading spinner color */
  color: z.enum(['blue', 'green', 'yellow', 'red', 'gray', 'indigo']).optional(),
  /** Additional CSS classes */
  className: z.string().optional()
});

export const ErrorBoundaryPropsSchema = z.object({
  /** Child components */
  children: z.any(),
  /** Custom fallback component */
  fallback: z.any().optional(),
  /** Error handler callback */
  onError: z.function().args(z.any(), z.any()).returns(z.void()).optional(),
  /** Show detailed error information */
  showDetails: z.boolean().optional(),
  /** Component name for error reporting */
  componentName: z.string().optional(),
  /** Additional CSS classes */
  className: z.string().optional()
});

export const ServiceErrorBoundaryPropsSchema = ErrorBoundaryPropsSchema.extend({
  /** Service name */
  serviceName: z.enum(['AC', 'GS', 'PGC', 'Auth', 'Integrity', 'FV', 'EC']),
  /** Service URL */
  serviceUrl: z.string().optional(),
  /** Service-specific error handler */
  onServiceError: z.function().args(z.any(), z.string()).returns(z.void()).optional(),
  /** Number of retry attempts */
  retryAttempts: z.number().int().min(0).max(10).optional()
});

// API Response schemas
export const ApiResponseSchema = z.object({
  /** Response data */
  data: z.any().optional(),
  /** Success status */
  success: z.boolean(),
  /** Error message */
  message: z.string().optional(),
  /** Error details */
  errors: z.array(z.string()).optional(),
  /** Response metadata */
  meta: z
    .object({
      /** Total count for paginated responses */
      total: z.number().optional(),
      /** Current page */
      page: z.number().optional(),
      /** Items per page */
      limit: z.number().optional()
    })
    .optional()
});

// Export type inference helpers
export type User = z.infer<typeof UserSchema>;
export type AuthContext = z.infer<typeof AuthContextSchema>;
export type Principle = z.infer<typeof PrincipleSchema>;
export type Policy = z.infer<typeof PolicySchema>;
export type PolicyRule = z.infer<typeof PolicyRuleSchema>;
export type ActivePolicy = z.infer<typeof ActivePolicySchema>;
export type ComplianceResult = z.infer<typeof ComplianceResultSchema>;
export type Amendment = z.infer<typeof AmendmentSchema>;
export type AmendmentVote = z.infer<typeof AmendmentVoteSchema>;
export type SynthesisRequest = z.infer<typeof SynthesisRequestSchema>;
export type SynthesisResult = z.infer<typeof SynthesisResultSchema>;
export type LoadingProps = z.infer<typeof LoadingPropsSchema>;
export type ErrorBoundaryProps = z.infer<typeof ErrorBoundaryPropsSchema>;
export type ServiceErrorBoundaryProps = z.infer<typeof ServiceErrorBoundaryPropsSchema>;
export type ApiResponse<T = any> = z.infer<typeof ApiResponseSchema> & { data?: T };

/**
 * Validation helper functions
 */

/**
 * Validates data against a Zod schema and returns typed result
 * @param schema - Zod schema to validate against
 * @param data - Data to validate
 * @returns Validation result with typed data or errors
 */
export function validateData<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: T } | { success: false; errors: string[] } {
  try {
    const validatedData = schema.parse(data);
    return { success: true, data: validatedData };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        errors: error.errors.map(err => `${err.path.join('.')}: ${err.message}`)
      };
    }
    return {
      success: false,
      errors: ['Unknown validation error']
    };
  }
}

/**
 * Safe validation that returns undefined on error
 * @param schema - Zod schema to validate against
 * @param data - Data to validate
 * @returns Validated data or undefined
 */
export function safeValidate<T>(schema: z.ZodSchema<T>, data: unknown): T | undefined {
  try {
    return schema.parse(data);
  } catch {
    return undefined;
  }
}

/**
 * Partial validation for form data
 * @param schema - Zod schema to validate against
 * @param data - Partial data to validate
 * @returns Validation result
 */
export function validatePartial<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: Partial<T> } | { success: false; errors: string[] } {
  try {
    const partialSchema = schema.partial();
    const validatedData = partialSchema.parse(data);
    return { success: true, data: validatedData };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        errors: error.errors.map(err => `${err.path.join('.')}: ${err.message}`)
      };
    }
    return {
      success: false,
      errors: ['Unknown validation error']
    };
  }
}
