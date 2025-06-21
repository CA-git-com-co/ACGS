import React from 'react';
import { z } from 'zod';
import { Policy } from '../types/governance';
import { PolicySchema } from '../types/validation';
import { validateProps } from '../utils/propValidation';
import { LoadingButton } from './LoadingStates';

/**
 * Props interface for PolicyCard component
 *
 * @example
 * ```typescript
 * <PolicyCard
 *   policy={{
 *     id: "POL-001",
 *     name: "Treasury Protection",
 *     description: "Protects treasury funds from unauthorized access",
 *     rules: [{ id: "R1", condition: "amount > limit", action: "DENY" }],
 *     validationScore: 95,
 *     complianceComplexity: 30,
 *     status: "active",
 *     category: "financial",
 *     createdAt: new Date(),
 *     updatedAt: new Date(),
 *     author: "system"
 *   }}
 *   onActivate={(id) => console.log('Activate:', id)}
 *   onDeactivate={(id) => console.log('Deactivate:', id)}
 *   onEdit={(policy) => console.log('Edit:', policy)}
 *   isLoading={false}
 *   className="mb-4"
 * />
 * ```
 */
interface PolicyCardProps {
  /**
   * The policy object to display
   * Must contain all required policy fields
   */
  policy: Policy;
  /**
   * Optional callback when activate button is clicked
   * @param id - The ID of the policy being activated
   */
  onActivate?: (id: string) => void;
  /**
   * Optional callback when deactivate button is clicked
   * @param id - The ID of the policy being deactivated
   */
  onDeactivate?: (id: string) => void;
  /**
   * Optional callback when edit button is clicked
   * @param policy - The policy being edited
   */
  onEdit?: (policy: Policy) => void;
  /**
   * Loading state for async operations
   * @default false
   */
  isLoading?: boolean;
  /**
   * Additional CSS classes to apply to the card
   * @default ''
   */
  className?: string;
}

/**
 * Zod schema for PolicyCard props validation
 */
const PolicyCardPropsSchema = z.object({
  policy: PolicySchema,
  onActivate: z.function().args(z.string()).returns(z.void()).optional(),
  onDeactivate: z.function().args(z.string()).returns(z.void()).optional(),
  onEdit: z.function().args(PolicySchema).returns(z.void()).optional(),
  isLoading: z.boolean().optional(),
  className: z.string().optional()
});

/**
 * PolicyCard component for displaying governance policies
 *
 * This component renders a policy in a card format with status indicators,
 * validation scores, and action buttons. It includes comprehensive prop
 * validation and follows ACGS design patterns.
 *
 * @param props - Component props validated against PolicyCardPropsSchema
 * @returns JSX element representing the policy card
 */
const PolicyCard: React.FC<PolicyCardProps> = props => {
  // Validate props in development mode
  const validatedProps = validateProps(PolicyCardPropsSchema, props, 'PolicyCard');

  const {
    policy,
    onActivate,
    onDeactivate,
    onEdit,
    isLoading = false,
    className = ''
  } = validatedProps;

  /**
   * Get status color classes based on policy status
   */
  const getStatusColor = (status: Policy['status']): string => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'draft':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'archived':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  /**
   * Get validation score color based on score value
   */
  const getScoreColor = (score: number): string => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  /**
   * Get complexity color based on complexity value
   */
  const getComplexityColor = (complexity: number): string => {
    if (complexity <= 30) return 'text-green-600';
    if (complexity <= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div
      className={`policy-card border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow bg-white ${className}`}
    >
      {/* Header */}
      <div className="policy-header mb-4">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-semibold text-gray-900">{policy.name}</h3>
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(policy.status)}`}
          >
            {policy.status.toUpperCase()}
          </span>
        </div>

        <div className="policy-meta flex items-center gap-4 text-sm text-gray-600 mb-2">
          <span className="policy-id">ID: {policy.id}</span>
          <span className="policy-category">
            Category: <span className="font-medium">{policy.category}</span>
          </span>
          <span className="policy-author">
            Author: <span className="font-medium">{policy.author}</span>
          </span>
        </div>

        <p className="text-gray-700 text-sm leading-relaxed">{policy.description}</p>
      </div>

      {/* Metrics */}
      <div className="policy-metrics grid grid-cols-2 gap-4 mb-4 p-3 bg-gray-50 rounded-md">
        <div className="metric">
          <span className="text-xs text-gray-500 block">Validation Score</span>
          <span className={`text-lg font-semibold ${getScoreColor(policy.validationScore)}`}>
            {policy.validationScore}%
          </span>
        </div>
        <div className="metric">
          <span className="text-xs text-gray-500 block">Complexity</span>
          <span
            className={`text-lg font-semibold ${getComplexityColor(policy.complianceComplexity)}`}
          >
            {policy.complianceComplexity}%
          </span>
        </div>
      </div>

      {/* Rules */}
      <div className="policy-rules mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Rules ({policy.rules.length})</h4>
        <div className="space-y-2 max-h-32 overflow-y-auto">
          {policy.rules.map(rule => (
            <div key={rule.id} className="rule bg-blue-50 p-2 rounded text-xs">
              <div className="rule-condition mb-1">
                <span className="font-medium text-blue-800">Condition:</span>
                <span className="text-blue-700 ml-1">{rule.condition}</span>
              </div>
              <div className="rule-action">
                <span className="font-medium text-blue-800">Action:</span>
                <span className="text-blue-700 ml-1">{rule.action}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      {(onActivate || onDeactivate || onEdit) && (
        <div className="policy-actions flex gap-2 pt-4 border-t border-gray-200">
          {onEdit && (
            <LoadingButton
              onClick={() => onEdit(policy)}
              isLoading={isLoading}
              disabled={isLoading}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
            >
              Edit
            </LoadingButton>
          )}

          {policy.status === 'draft' && onActivate && (
            <LoadingButton
              onClick={() => onActivate(policy.id)}
              isLoading={isLoading}
              disabled={isLoading}
              className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
              loadingText="Activating..."
            >
              Activate
            </LoadingButton>
          )}

          {policy.status === 'active' && onDeactivate && (
            <LoadingButton
              onClick={() => onDeactivate(policy.id)}
              isLoading={isLoading}
              disabled={isLoading}
              className="px-3 py-1 text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700"
              loadingText="Deactivating..."
            >
              Deactivate
            </LoadingButton>
          )}
        </div>
      )}

      {/* Timestamps */}
      <div className="policy-timestamps mt-4 pt-3 border-t border-gray-100 text-xs text-gray-500">
        <div className="flex justify-between">
          <span>Created: {policy.createdAt.toLocaleDateString()}</span>
          <span>Updated: {policy.updatedAt.toLocaleDateString()}</span>
        </div>
      </div>
    </div>
  );
};

export default PolicyCard;
