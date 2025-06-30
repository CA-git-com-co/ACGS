"""
Code Quality Guidelines for ACGS-2
Establishes consistent patterns and best practices.
"""

# Python Code Quality Standards

## Naming Conventions
- Use snake_case for variables, functions, and module names
- Use PascalCase for class names
- Use UPPER_CASE for constants
- Use descriptive names that clearly indicate purpose

## Function Design
- Keep functions small and focused (max 50 lines)
- Use type hints for all function parameters and return values
- Include comprehensive docstrings with Args, Returns, and Raises sections
- Limit function parameters to 5 or fewer

## Error Handling
- Use specific exception types rather than generic Exception
- Always include meaningful error messages
- Log errors with appropriate context
- Implement proper cleanup in finally blocks

## Documentation Standards
- All public classes and functions must have docstrings
- Use Google-style docstring format
- Include examples in docstrings for complex functions
- Keep README files up to date

## Import Organization
- Standard library imports first
- Third-party imports second
- Local application imports last
- Use absolute imports when possible

## Code Formatting
- Use Black for code formatting
- Line length limit of 88 characters
- Use meaningful variable names
- Add blank lines to separate logical sections

## Testing Standards
- Write tests for all public functions
- Use descriptive test names that explain what is being tested
- Follow AAA pattern: Arrange, Act, Assert
- Mock external dependencies

## Performance Considerations
- Use list comprehensions for simple transformations
- Prefer generators for large datasets
- Cache expensive computations
- Profile code before optimizing

## Security Best Practices
- Validate all inputs
- Use parameterized queries for database operations
- Never log sensitive information
- Use secure random number generation

## Example Code Structure

```python
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PolicyValidator:
    """Validates policy documents according to governance rules.
    
    This class provides comprehensive validation for policy documents,
    ensuring they meet all constitutional and governance requirements.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the policy validator.
        
        Args:
            config: Configuration dictionary containing validation rules
            
        Raises:
            ValueError: If config is invalid or missing required keys
        """
        self.config = config
        self._validate_config()
    
    def validate_policy(self, policy: Dict[str, Any]) -> ValidationResult:
        """Validate a policy document.
        
        Args:
            policy: Policy document to validate
            
        Returns:
            ValidationResult containing validation status and details
            
        Raises:
            PolicyValidationError: If policy format is invalid
            
        Example:
            >>> validator = PolicyValidator(config)
            >>> result = validator.validate_policy(policy_doc)
            >>> if result.is_valid:
            ...     print("Policy is valid")
        """
        try:
            # Validation logic here
            pass
        except Exception as e:
            logger.error(f"Policy validation failed: {e}")
            raise PolicyValidationError(f"Validation failed: {e}") from e
```

## Configuration Management
- Use environment variables for configuration
- Provide sensible defaults
- Validate configuration on startup
- Use configuration classes rather than dictionaries

## Logging Standards
- Use structured logging with JSON format
- Include correlation IDs for request tracing
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Never log sensitive data

## Database Patterns
- Use connection pooling
- Implement proper transaction management
- Use migrations for schema changes
- Index frequently queried columns

## API Design
- Use RESTful conventions
- Implement proper HTTP status codes
- Include comprehensive error responses
- Version APIs appropriately

## Monitoring and Observability
- Add metrics for key business operations
- Implement health checks
- Use distributed tracing
- Monitor error rates and latencies
