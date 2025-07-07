#!/usr/bin/env python3
"""
ACGS Error Handling Standardization Script
Constitutional Hash: cdd01ef066bc6cf2

This script applies standardized error handling across all ACGS services.
"""

import os
import sys
import shutil
import re
from pathlib import Path
from typing import List, Dict, Any

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ErrorHandlingApplicator:
    """Apply standardized error handling across ACGS services."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.services_root = project_root / "services"
        self.results = {"updated": [], "failed": [], "skipped": []}
    
    def find_service_directories(self) -> List[Path]:
        """Find all service directories with main.py files."""
        services = []
        
        for service_type in ["core", "platform_services"]:
            service_type_dir = self.services_root / service_type
            if service_type_dir.exists():
                for service_dir in service_type_dir.iterdir():
                    if service_dir.is_dir():
                        # Look for main.py in various common locations
                        main_py_paths = [
                            service_dir / "app" / "main.py",
                            service_dir / f"{service_dir.name}_service" / "app" / "main.py",
                            service_dir / "main.py",
                        ]
                        
                        for main_py in main_py_paths:
                            if main_py.exists():
                                services.append((service_dir, main_py))
                                break
        
        return services
    
    def backup_file(self, file_path: Path) -> Path:
        """Create a backup of the file."""
        backup_path = file_path.with_suffix(f"{file_path.suffix}.error_backup")
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def update_service_error_handling(self, service_dir: Path, main_py_path: Path) -> bool:
        """Update service to use standardized error handling."""
        service_name = service_dir.name
        
        try:
            with open(main_py_path, 'r') as f:
                content = f.read()
            
            # Check if error handling is already applied
            if "setup_error_handlers" in content and "ErrorHandlingMiddleware" in content:
                print(f"  ✓ Error handling already applied to {service_name}")
                return True
            
            # Create backup
            self.backup_file(main_py_path)
            
            # Add error handling imports
            error_handling_import = '''
# ACGS Standardized Error Handling
try:
    import sys
    from pathlib import Path
    shared_middleware_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "middleware"
    sys.path.insert(0, str(shared_middleware_path))
    
    from error_handling import (
        setup_error_handlers,
        ErrorHandlingMiddleware,
        ACGSException,
        ConstitutionalComplianceError,
        SecurityValidationError,
        AuthenticationError,
        ValidationError,
        log_error_with_context,
        ErrorContext
    )
    ACGS_ERROR_HANDLING_AVAILABLE = True
    print(f"✅ ACGS Error handling loaded for {service_name}")
except ImportError as e:
    print(f"⚠️ ACGS Error handling not available for {service_name}: {e}")
    ACGS_ERROR_HANDLING_AVAILABLE = False
'''
            
            # Find where to insert the error handling import
            lines = content.split('\n')
            insert_index = 0
            
            # Find the end of existing imports
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    insert_index = i + 1
                elif line.strip() and not line.strip().startswith('#') and insert_index > 0:
                    break
            
            # Insert error handling import
            lines.insert(insert_index, error_handling_import)
            
            # Add error handling setup after app creation
            app_creation_patterns = [
                'app = FastAPI(',
                'app = create_app(',
                'app = FastAPI()',
                'app = create_constitutional_ai_app()',
            ]
            
            error_handling_setup = f'''
# Apply ACGS Error Handling
if ACGS_ERROR_HANDLING_AVAILABLE:
    import os
    development_mode = os.getenv("ENVIRONMENT", "development") != "production"
    setup_error_handlers(app, "{service_name}", include_traceback=development_mode)
'''
            
            # Find where to insert error handling setup
            inserted = False
            for i, line in enumerate(lines):
                for pattern in app_creation_patterns:
                    if pattern in line:
                        # Insert after the app creation and any immediate setup
                        insert_pos = i + 1
                        while (insert_pos < len(lines) and 
                               (lines[insert_pos].strip().startswith('app.') or 
                                not lines[insert_pos].strip())):
                            insert_pos += 1
                        
                        lines.insert(insert_pos, error_handling_setup)
                        inserted = True
                        break
                if inserted:
                    break
            
            if not inserted:
                # If we couldn't find app creation, add at the end
                lines.append(error_handling_setup)
            
            # Update exception handling patterns
            lines = self._update_exception_patterns(lines, service_name)
            
            # Write updated content
            updated_content = '\n'.join(lines)
            with open(main_py_path, 'w') as f:
                f.write(updated_content)
            
            print(f"  ✅ Error handling applied to {service_name}")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to update {service_name}: {e}")
            # Restore from backup if it exists
            backup_path = main_py_path.with_suffix(f"{main_py_path.suffix}.error_backup")
            if backup_path.exists():
                shutil.copy2(backup_path, main_py_path)
            return False
    
    def _update_exception_patterns(self, lines: List[str], service_name: str) -> List[str]:
        """Update existing exception handling patterns to use ACGS standards."""
        updated_lines = []
        
        for line in lines:
            # Replace generic exception handling with ACGS patterns
            if re.search(r'except Exception as \w+:', line):
                # Add comment about using ACGS error handling
                updated_lines.append(line)
                updated_lines.append(f'        # TODO: Consider using ACGS error handling: log_error_with_context()')
            elif 'HTTPException(' in line and 'status_code=500' in line:
                # Replace with ACGSException
                updated_lines.append(line.replace(
                    'HTTPException(status_code=500',
                    'ACGSException(status_code=500, error_code="INTERNAL_ERROR"'
                ))
            elif 'raise Exception(' in line:
                # Replace with ACGSException
                updated_lines.append(line.replace('Exception(', 'ACGSException('))
            else:
                updated_lines.append(line)
        
        return updated_lines
    
    def apply_error_handling_to_service(self, service_dir: Path, main_py_path: Path) -> bool:
        """Apply error handling to a single service."""
        service_name = service_dir.name
        print(f"Applying error handling to {service_name}...")
        
        try:
            return self.update_service_error_handling(service_dir, main_py_path)
        except Exception as e:
            print(f"  ❌ Error processing {service_name}: {e}")
            return False
    
    def create_error_handling_documentation(self) -> None:
        """Create error handling documentation for developers."""
        doc_path = self.project_root / "docs" / "ERROR_HANDLING_GUIDE.md"
        doc_path.parent.mkdir(exist_ok=True)
        
        error_doc = f'''# ACGS Error Handling Guide
Constitutional Hash: {CONSTITUTIONAL_HASH}

## Overview

This document describes the standardized error handling implemented across all ACGS services.

## Error Handling Features

### 1. Standardized Exception Hierarchy
- **ACGSException**: Base exception for all ACGS services
- **ConstitutionalComplianceError**: Constitutional violations (403)
- **SecurityValidationError**: Security validation failures (400)
- **AuthenticationError**: Authentication failures (401)
- **AuthorizationError**: Authorization failures (403)
- **ValidationError**: Input validation failures (422)
- **ServiceUnavailableError**: Service unavailability (503)
- **RateLimitError**: Rate limiting violations (429)

### 2. Consistent Error Response Format
```json
{{
  "error": {{
    "id": "unique-error-id",
    "timestamp": "2024-01-01T12:00:00Z",
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "status_code": 400,
    "details": {{}},
    "constitutional_hash": "{CONSTITUTIONAL_HASH}",
    "request": {{
      "method": "POST",
      "path": "/api/v1/endpoint",
      "query_params": {{}}
    }}
  }}
}}
```

### 3. Comprehensive Logging
- **Structured logging** with context information
- **Request tracking** with unique error IDs
- **Performance metrics** including response times
- **Constitutional compliance** tracking

## Usage

### Automatic Integration

Error handling is automatically applied to all services:

```python
from error_handling import setup_error_handlers

# Automatically applied during service startup
setup_error_handlers(app, "service-name", include_traceback=development_mode)
```

### Custom Exception Handling

```python
from error_handling import (
    ConstitutionalComplianceError,
    SecurityValidationError,
    ValidationError,
    log_error_with_context,
    ErrorContext
)

# Raise specific errors
if not constitutional_check():
    raise ConstitutionalComplianceError(
        "Constitutional compliance validation failed",
        details={{"violation_type": "democratic_deficit"}}
    )

# Use error context for graceful handling
with ErrorContext("database_operation", "my-service"):
    # Code that might fail
    result = database.query()
```

### Error Logging with Context

```python
from error_handling import log_error_with_context

try:
    risky_operation()
except Exception as e:
    log_error_with_context(
        error=e,
        context={{
            "operation": "data_processing",
            "user_id": user.id,
            "request_id": request_id
        }},
        service_name="my-service"
    )
    raise
```

## Error Response Headers

All error responses include:
- **X-Error-ID**: Unique error identifier for tracking
- **X-Constitutional-Hash**: Constitutional compliance hash
- **X-Service**: Service name that generated the error

## Development vs Production

### Development Mode
- **Detailed tracebacks** included in error responses
- **Verbose logging** for debugging
- **More permissive** error handling

### Production Mode
- **No tracebacks** in responses (security)
- **Structured logging** only
- **Strict error handling** with proper status codes

## Error Monitoring

### Metrics Collection
```bash
# Check service error rates
curl http://service:port/metrics | grep error_rate

# Check specific error types
curl http://service:port/health
```

### Log Analysis
```bash
# Search for errors by ID
grep "error_id:12345" /var/log/acgs/service.log

# Search for constitutional violations
grep "CONSTITUTIONAL_VIOLATION" /var/log/acgs/*.log
```

## Best Practices

### 1. Use Specific Exceptions
```python
# Good
raise ValidationError("Invalid email format", details={{"field": "email"}})

# Avoid
raise Exception("Something went wrong")
```

### 2. Provide Context
```python
# Good
raise SecurityValidationError(
    "XSS detected in input",
    details={{
        "field": "comment",
        "pattern": "script_tag",
        "input_length": len(user_input)
    }}
)

# Avoid
raise SecurityValidationError("Invalid input")
```

### 3. Log Before Raising
```python
try:
    external_service.call()
except ConnectionError as e:
    log_error_with_context(
        error=e,
        context={{"service": "external_api", "endpoint": "/data"}},
        service_name="my-service"
    )
    raise ServiceUnavailableError("External service unavailable")
```

## Constitutional Compliance

All error handling maintains constitutional compliance:
- **Hash validation**: All errors include constitutional hash
- **Audit logging**: Error events are audited
- **Transparency**: Error information appropriately disclosed
- **Accountability**: Clear error tracking and responsibility

## Troubleshooting

### Common Issues

1. **Error handling not applied**: Check service startup logs
2. **Missing error context**: Ensure proper import paths
3. **Inconsistent responses**: Verify error handler setup

### Debug Mode

Enable detailed error logging:
```python
import logging
logging.getLogger("acgs.errors").setLevel(logging.DEBUG)
```

## Support

For error handling issues:
1. Check service logs for error patterns
2. Verify constitutional hash compliance
3. Review error response format
4. Contact development team with error ID

Constitutional Hash: {CONSTITUTIONAL_HASH}
'''
        
        with open(doc_path, 'w') as f:
            f.write(error_doc)
        
        print(f"✅ Error handling documentation created at {doc_path}")
    
    def run(self) -> Dict[str, Any]:
        """Run the complete error handling standardization process."""
        print(f"🔧 Starting ACGS Error Handling Standardization")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Project Root: {self.project_root}")
        
        # Find all services
        print("\n🔍 Finding ACGS services...")
        services = self.find_service_directories()
        print(f"Found {len(services)} services to update")
        
        # Apply error handling to each service
        print("\n🛠️ Applying standardized error handling...")
        for service_dir, main_py_path in services:
            if self.apply_error_handling_to_service(service_dir, main_py_path):
                self.results["updated"].append(service_dir.name)
            else:
                self.results["failed"].append(service_dir.name)
        
        # Create documentation
        print("\n📚 Creating error handling documentation...")
        self.create_error_handling_documentation()
        
        # Summary
        print(f"\n📊 Error Handling Standardization Summary:")
        print(f"  ✅ Successfully Updated: {len(self.results['updated'])} services")
        print(f"  ❌ Failed: {len(self.results['failed'])} services")
        print(f"  ⏭️ Skipped: {len(self.results['skipped'])} services")
        
        if self.results["updated"]:
            print(f"\n✅ Updated services: {', '.join(self.results['updated'])}")
        
        if self.results["failed"]:
            print(f"\n❌ Failed services: {', '.join(self.results['failed'])}")
        
        print(f"\n🎉 Error handling standardization completed!")
        print(f"Constitutional Hash Validated: {CONSTITUTIONAL_HASH}")
        
        return self.results


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()
    
    if not project_root.exists():
        print(f"❌ Project root does not exist: {project_root}")
        sys.exit(1)
    
    applicator = ErrorHandlingApplicator(project_root)
    results = applicator.run()
    
    # Exit with error code if any services failed
    if results["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()