import React, { useState, useCallback } from 'react';
import { z } from 'zod';
import { validateProps, validateFormData } from '../utils/propValidation';
import { LoadingButton } from './LoadingStates';

/**
 * Form field configuration interface
 */
interface FormField {
    /** Field name/key */
    name: string;
    /** Field label */
    label: string;
    /** Field type */
    type: 'text' | 'email' | 'password' | 'number' | 'textarea' | 'select';
    /** Whether field is required */
    required?: boolean;
    /** Placeholder text */
    placeholder?: string;
    /** Options for select fields */
    options?: Array<{ value: string; label: string }>;
    /** Field validation schema */
    validation?: z.ZodSchema<any>;
}

/**
 * Props interface for ValidatedForm component
 * 
 * @example
 * ```typescript
 * const userFormFields: FormField[] = [
 *   {
 *     name: 'username',
 *     label: 'Username',
 *     type: 'text',
 *     required: true,
 *     validation: z.string().min(3, 'Username must be at least 3 characters')
 *   },
 *   {
 *     name: 'email',
 *     label: 'Email',
 *     type: 'email',
 *     required: true,
 *     validation: z.string().email('Invalid email format')
 *   }
 * ];
 * 
 * <ValidatedForm
 *   fields={userFormFields}
 *   onSubmit={(data) => console.log('Form data:', data)}
 *   submitLabel="Create User"
 *   isLoading={false}
 * />
 * ```
 */
interface ValidatedFormProps {
    /** 
     * Array of form field configurations
     * Each field defines its type, validation, and display properties
     */
    fields: FormField[];
    /** 
     * Callback when form is submitted with valid data
     * @param data - Validated form data
     */
    onSubmit: (data: Record<string, any>) => void | Promise<void>;
    /** 
     * Optional callback when form is cancelled
     */
    onCancel?: () => void;
    /** 
     * Initial form data
     * @default {}
     */
    initialData?: Record<string, any>;
    /** 
     * Submit button label
     * @default 'Submit'
     */
    submitLabel?: string;
    /** 
     * Cancel button label
     * @default 'Cancel'
     */
    cancelLabel?: string;
    /** 
     * Loading state for form submission
     * @default false
     */
    isLoading?: boolean;
    /** 
     * Additional CSS classes to apply to the form
     * @default ''
     */
    className?: string;
}

/**
 * Zod schema for ValidatedForm props validation
 */
const ValidatedFormPropsSchema = z.object({
    fields: z.array(z.object({
        name: z.string().min(1, 'Field name is required'),
        label: z.string().min(1, 'Field label is required'),
        type: z.enum(['text', 'email', 'password', 'number', 'textarea', 'select']),
        required: z.boolean().optional(),
        placeholder: z.string().optional(),
        options: z.array(z.object({
            value: z.string(),
            label: z.string()
        })).optional(),
        validation: z.any().optional()
    })).min(1, 'At least one field is required'),
    onSubmit: z.function().args(z.record(z.any())).returns(z.union([z.void(), z.promise(z.void())])),
    onCancel: z.function().args().returns(z.void()).optional(),
    initialData: z.record(z.any()).optional(),
    submitLabel: z.string().optional(),
    cancelLabel: z.string().optional(),
    isLoading: z.boolean().optional(),
    className: z.string().optional()
});

/**
 * ValidatedForm component for creating dynamic forms with validation
 * 
 * This component generates forms based on field configurations and provides
 * comprehensive validation using Zod schemas. It includes error handling,
 * loading states, and follows ACGS design patterns.
 * 
 * @param props - Component props validated against ValidatedFormPropsSchema
 * @returns JSX element representing the validated form
 */
const ValidatedForm: React.FC<ValidatedFormProps> = (props) => {
    // Validate props in development mode
    const validatedProps = validateProps(
        ValidatedFormPropsSchema,
        props,
        'ValidatedForm'
    );

    const {
        fields,
        onSubmit,
        onCancel,
        initialData = {},
        submitLabel = 'Submit',
        cancelLabel = 'Cancel',
        isLoading = false,
        className = ''
    } = validatedProps;

    // Form state
    const [formData, setFormData] = useState<Record<string, any>>(initialData);
    const [errors, setErrors] = useState<Record<string, string[]>>({});
    const [globalErrors, setGlobalErrors] = useState<string[]>([]);

    /**
     * Handle field value changes
     */
    const handleFieldChange = useCallback((fieldName: string, value: any) => {
        setFormData(prev => ({ ...prev, [fieldName]: value }));
        
        // Clear field-specific errors when user starts typing
        if (errors[fieldName]) {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[fieldName];
                return newErrors;
            });
        }
    }, [errors]);

    /**
     * Validate form data using field schemas
     */
    const validateForm = useCallback(() => {
        const fieldErrors: Record<string, string[]> = {};
        let hasErrors = false;

        fields.forEach(field => {
            if (field.validation) {
                const fieldValue = formData[field.name];
                
                try {
                    field.validation.parse(fieldValue);
                } catch (error) {
                    if (error instanceof z.ZodError) {
                        fieldErrors[field.name] = error.errors.map(e => e.message);
                        hasErrors = true;
                    }
                }
            } else if (field.required && (!formData[field.name] || formData[field.name] === '')) {
                fieldErrors[field.name] = [`${field.label} is required`];
                hasErrors = true;
            }
        });

        setErrors(fieldErrors);
        return !hasErrors;
    }, [fields, formData]);

    /**
     * Handle form submission
     */
    const handleSubmit = useCallback(async (e: React.FormEvent) => {
        e.preventDefault();
        
        setGlobalErrors([]);
        
        if (!validateForm()) {
            return;
        }

        try {
            await onSubmit(formData);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Form submission failed';
            setGlobalErrors([errorMessage]);
        }
    }, [formData, validateForm, onSubmit]);

    /**
     * Render form field based on type
     */
    const renderField = (field: FormField) => {
        const fieldValue = formData[field.name] || '';
        const fieldErrors = errors[field.name] || [];
        const hasError = fieldErrors.length > 0;

        const baseInputClasses = `w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            hasError ? 'border-red-300 focus:border-red-500' : 'border-gray-300 focus:border-blue-500'
        }`;

        switch (field.type) {
            case 'textarea':
                return (
                    <textarea
                        id={field.name}
                        name={field.name}
                        value={fieldValue}
                        onChange={(e) => handleFieldChange(field.name, e.target.value)}
                        placeholder={field.placeholder}
                        required={field.required}
                        rows={4}
                        className={baseInputClasses}
                    />
                );

            case 'select':
                return (
                    <select
                        id={field.name}
                        name={field.name}
                        value={fieldValue}
                        onChange={(e) => handleFieldChange(field.name, e.target.value)}
                        required={field.required}
                        className={baseInputClasses}
                    >
                        <option value="">Select {field.label}</option>
                        {field.options?.map(option => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                );

            case 'number':
                return (
                    <input
                        type="number"
                        id={field.name}
                        name={field.name}
                        value={fieldValue}
                        onChange={(e) => handleFieldChange(field.name, parseFloat(e.target.value) || 0)}
                        placeholder={field.placeholder}
                        required={field.required}
                        className={baseInputClasses}
                    />
                );

            default:
                return (
                    <input
                        type={field.type}
                        id={field.name}
                        name={field.name}
                        value={fieldValue}
                        onChange={(e) => handleFieldChange(field.name, e.target.value)}
                        placeholder={field.placeholder}
                        required={field.required}
                        className={baseInputClasses}
                    />
                );
        }
    };

    return (
        <form onSubmit={handleSubmit} className={`validated-form space-y-6 ${className}`}>
            {/* Global errors */}
            {globalErrors.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                    <div className="flex">
                        <svg className="h-5 w-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div>
                            <h3 className="text-sm font-medium text-red-800">Form submission failed</h3>
                            <ul className="mt-1 text-sm text-red-700">
                                {globalErrors.map((error, index) => (
                                    <li key={index}>• {error}</li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            )}

            {/* Form fields */}
            {fields.map(field => (
                <div key={field.name} className="form-field">
                    <label htmlFor={field.name} className="block text-sm font-medium text-gray-700 mb-1">
                        {field.label}
                        {field.required && <span className="text-red-500 ml-1">*</span>}
                    </label>
                    
                    {renderField(field)}
                    
                    {/* Field errors */}
                    {errors[field.name] && (
                        <div className="mt-1 text-sm text-red-600">
                            {errors[field.name].map((error, index) => (
                                <div key={index}>• {error}</div>
                            ))}
                        </div>
                    )}
                </div>
            ))}

            {/* Form actions */}
            <div className="form-actions flex gap-3 pt-4">
                <LoadingButton
                    type="submit"
                    isLoading={isLoading}
                    disabled={isLoading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                    loadingText="Submitting..."
                >
                    {submitLabel}
                </LoadingButton>
                
                {onCancel && (
                    <button
                        type="button"
                        onClick={onCancel}
                        disabled={isLoading}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50"
                    >
                        {cancelLabel}
                    </button>
                )}
            </div>
        </form>
    );
};

export default ValidatedForm;
