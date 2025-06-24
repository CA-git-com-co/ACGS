/**
 * Unified Error Handling Utility for ACGS-PGP Framework
 *
 * Provides consistent error handling patterns across all services
 * with standardized logging and error message formatting.
 */

/**
 * Standard error handler for API service calls
 * @param {Error} error - The error object from axios
 * @param {string} operation - Description of the operation that failed
 * @param {Object} options - Additional options for error handling
 * @returns {never} - Always throws an error
 */
export const handleServiceError = (error, operation, options = {}) => {
  const { logLevel = 'error', includeStack = false, customMessage = null } = options;

  // Extract error details
  const errorData = error.response?.data;
  const errorMessage = error.response?.data?.message || error.message;
  const statusCode = error.response?.status;
  const statusText = error.response?.statusText;

  // Create standardized error message
  const baseMessage = customMessage || `${operation} failed`;
  const detailedMessage = errorData?.detail || errorMessage || 'Unknown error occurred';

  // Log error with consistent format
  const logMessage = `🚨 ${operation} failed:`;
  const logDetails = {
    message: detailedMessage,
    status: statusCode,
    statusText: statusText,
    url: error.config?.url,
    method: error.config?.method?.toUpperCase(),
    ...(includeStack && { stack: error.stack }),
  };

  if (logLevel === 'error') {
    console.error(logMessage, logDetails);
  } else if (logLevel === 'warn') {
    console.warn(logMessage, logDetails);
  }

  // Create and throw standardized error
  const serviceError = new Error(baseMessage);
  serviceError.originalError = error;
  serviceError.statusCode = statusCode;
  serviceError.details = errorData;
  serviceError.operation = operation;

  // Preserve original error data if it exists (for backend validation errors)
  if (errorData && typeof errorData === 'object') {
    throw errorData;
  }

  throw serviceError;
};

/**
 * Wrapper for service API calls with automatic error handling
 * @param {Function} apiCall - The API call function
 * @param {string} operation - Description of the operation
 * @param {Object} options - Error handling options
 * @returns {Promise} - The result of the API call
 */
export const withErrorHandling = async (apiCall, operation, options = {}) => {
  try {
    const response = await apiCall();
    return response.data || response;
  } catch (error) {
    handleServiceError(error, operation, options);
  }
};

/**
 * Performance monitoring wrapper for API calls
 * @param {Function} apiCall - The API call function
 * @param {string} operation - Description of the operation
 * @returns {Promise} - The result with performance metrics
 */
export const withPerformanceMonitoring = async (apiCall, operation) => {
  const startTime = performance.now();

  try {
    const result = await apiCall();
    const endTime = performance.now();
    const duration = endTime - startTime;

    console.log(`⏱️ ${operation} completed in ${duration.toFixed(2)}ms`);

    return result;
  } catch (error) {
    const endTime = performance.now();
    const duration = endTime - startTime;

    console.error(`⏱️ ${operation} failed after ${duration.toFixed(2)}ms`);
    throw error;
  }
};

/**
 * Combined wrapper for API calls with error handling and performance monitoring
 * @param {Function} apiCall - The API call function
 * @param {string} operation - Description of the operation
 * @param {Object} options - Error handling options
 * @returns {Promise} - The result of the API call
 */
export const serviceCall = async (apiCall, operation, options = {}) => {
  const { enablePerformanceMonitoring = true, ...errorOptions } = options;

  const wrappedCall = () => withErrorHandling(apiCall, operation, errorOptions);

  if (enablePerformanceMonitoring) {
    return withPerformanceMonitoring(wrappedCall, operation);
  }

  return wrappedCall();
};

export default {
  handleServiceError,
  withErrorHandling,
  withPerformanceMonitoring,
  serviceCall,
};
