import React from 'react';
import { z } from 'zod';
import { Principle } from '../types/governance';
import { PrincipleSchema } from '../types/validation';
import { validateProps } from '../utils/propValidation';

/**
 * Props interface for PrincipleCard component
 *
 * @example
 * ```typescript
 * <PrincipleCard
 *   principle={{
 *     id: "PRIN-001",
 *     title: "Democratic Governance",
 *     content: "All policy changes must be approved through democratic voting",
 *     category: "governance",
 *     priority: 9
 *   }}
 *   onEdit={(principle) => console.log('Edit:', principle)}
 *   onDelete={(id) => console.log('Delete:', id)}
 *   className="mb-4"
 * />
 * ```
 */
interface PrincipleCardProps {
    /**
     * The principle object to display
     * Must contain all required principle fields
     */
    principle: Principle;
    /**
     * Optional callback when edit button is clicked
     * @param principle - The principle being edited
     */
    onEdit?: (principle: Principle) => void;
    /**
     * Optional callback when delete button is clicked
     * @param id - The ID of the principle being deleted
     */
    onDelete?: (id: string) => void;
    /**
     * Additional CSS classes to apply to the card
     * @default ''
     */
    className?: string;
}

/**
 * Zod schema for PrincipleCard props validation
 */
const PrincipleCardPropsSchema = z.object({
    principle: PrincipleSchema,
    onEdit: z.function()
        .args(PrincipleSchema)
        .returns(z.void())
        .optional(),
    onDelete: z.function()
        .args(z.string())
        .returns(z.void())
        .optional(),
    className: z.string().optional()
});

/**
 * PrincipleCard component for displaying constitutional principles
 *
 * This component renders a principle in a card format with optional
 * edit and delete actions. It includes comprehensive prop validation
 * and follows ACGS design patterns.
 *
 * @param props - Component props validated against PrincipleCardPropsSchema
 * @returns JSX element representing the principle card
 */
const PrincipleCard: React.FC<PrincipleCardProps> = (props) => {
    // Validate props in development mode
    const validatedProps = validateProps(
        PrincipleCardPropsSchema,
        props,
        'PrincipleCard'
    );

    const {
        principle,
        onEdit,
        onDelete,
        className = ''
    } = validatedProps;
    return (
        <div className={`principle-card border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow ${className}`}>
            <div className="principle-header mb-3">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {principle.title}
                </h3>
                <div className="principle-meta flex items-center gap-4 text-sm text-gray-600">
                    <span className="category">
                        Category: <span className="font-medium">{principle.category}</span>
                    </span>
                    <span className="priority">
                        Priority: <span className="font-medium">{principle.priority}</span>
                    </span>
                </div>
            </div>
            
            <div className="principle-content mb-4">
                <p className="text-gray-700 leading-relaxed">
                    {principle.content}
                </p>
            </div>
            
            {(onEdit || onDelete) && (
                <div className="principle-actions flex gap-2 pt-3 border-t border-gray-200">
                    {onEdit && (
                        <button 
                            onClick={() => onEdit(principle)}
                            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                        >
                            Edit
                        </button>
                    )}
                    {onDelete && (
                        <button 
                            onClick={() => onDelete(principle.id)}
                            className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                        >
                            Delete
                        </button>
                    )}
                </div>
            )}
        </div>
    );
};

export default PrincipleCard;
