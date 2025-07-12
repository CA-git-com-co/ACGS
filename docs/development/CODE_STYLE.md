# ACGS-2 Code Style Guidelines

**Constitutional Hash:** `cdd01ef066bc6cf2`

## Overview

This document outlines the code style guidelines for ACGS-2 development to ensure consistency, maintainability, and constitutional compliance across all components.

## Python Code Style

### General Guidelines
- Follow PEP 8 standards
- Use type hints for all function parameters and return values
- Include comprehensive docstrings for all public functions and classes
- Maintain constitutional compliance in all code components

### Constitutional Compliance
- All modules must include constitutional hash validation
- Response objects must include `constitutional_hash: cdd01ef066bc6cf2`
- Error handling must preserve constitutional compliance

### Example Code Structure
```python
"""
Module docstring with constitutional compliance.
Constitutional Hash: cdd01ef066bc6cf2
"""

from typing import Dict, Optional
import structlog

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = structlog.get_logger(__name__)


class ExampleService:
    """Example service with constitutional compliance."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    async def process_request(self, data: Dict) -> Dict:
        """Process request with constitutional compliance."""
        try:
            # Process data
            result = {"status": "success", "data": data}
            
            # Add constitutional compliance
            result["constitutional_hash"] = CONSTITUTIONAL_HASH
            
            return result
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "constitutional_hash": CONSTITUTIONAL_HASH
            }
```

## Testing Standards

### Unit Test Requirements
- All tests must include constitutional compliance validation
- Use descriptive test names that explain the behavior being tested
- Include performance assertions where applicable
- Maintain >80% test coverage for operational services

### Example Test Structure
```python
def test_service_constitutional_compliance(self):
    """Test service maintains constitutional compliance."""
    service = ExampleService()
    result = service.process_request({"test": "data"})
    
    assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
    assert "status" in result
```

## Documentation Standards

### Docstring Format
- Use Google-style docstrings
- Include constitutional hash references
- Document all parameters and return values
- Include usage examples for complex functions

### File Headers
All Python files should include:
```python
"""
Brief module description.

Constitutional Hash: cdd01ef066bc6cf2
"""
```

## Performance Guidelines

### Optimization Requirements
- Target P99 latency <5ms for all operational services
- Implement proper connection pooling for database operations
- Use async/await for I/O operations
- Include performance monitoring and logging

### Constitutional Compliance Performance
- Constitutional hash validation should add <1ms overhead
- Cache validation results where appropriate
- Use efficient hash comparison algorithms

## Security Standards

### Input Validation
- Validate all input parameters
- Sanitize user-provided data
- Include constitutional compliance in validation responses

### Error Handling
- Never expose sensitive information in error messages
- Include constitutional hash in all error responses
- Log security events with appropriate detail

## Conclusion

Following these code style guidelines ensures consistency, maintainability, and constitutional compliance across the ACGS-2 codebase. All code must maintain the constitutional hash `cdd01ef066bc6cf2` and meet performance targets.

---

**Document Maintained By:** ACGS-2 Development Team  
**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Last Updated:** July 12, 2025
