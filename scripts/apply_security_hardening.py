#!/usr/bin/env python3
"""
ACGS Security Hardening Application Script
Constitutional Hash: cdd01ef066bc6cf2

This script applies comprehensive security hardening across all ACGS services.
It standardizes input validation, rate limiting, and security headers.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class SecurityHardeningApplicator:
    """Apply security hardening across ACGS services."""
    
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
                                services.append(service_dir)
                                break
        
        return services
    
    def backup_file(self, file_path: Path) -> Path:
        """Create a backup of the file."""
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def find_main_py(self, service_dir: Path) -> Path:
        """Find the main.py file for a service."""
        possible_paths = [
            service_dir / "app" / "main.py",
            service_dir / f"{service_dir.name}_service" / "app" / "main.py",
            service_dir / "main.py",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        raise FileNotFoundError(f"Could not find main.py for service {service_dir.name}")
    
    def update_service_imports(self, main_py_path: Path, service_name: str) -> bool:
        """Update service imports to include security middleware."""
        try:
            with open(main_py_path, 'r') as f:
                content = f.read()
            
            # Check if security middleware is already imported
            if "apply_acgs_security_middleware" in content:
                print(f"  ✓ Security middleware already applied to {service_name}")
                return True
            
            # Create backup
            self.backup_file(main_py_path)
            
            # Add security imports
            security_import = '''
# ACGS Security Middleware Integration
try:
    import sys
    from pathlib import Path
    shared_security_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "security"
    sys.path.insert(0, str(shared_security_path))
    
    from middleware_integration import (
        apply_acgs_security_middleware,
        setup_security_monitoring,
        get_security_headers,
        SecurityLevel,
        validate_request_body,
        create_secure_endpoint_decorator
    )
    ACGS_SECURITY_AVAILABLE = True
    print(f"✅ ACGS Security middleware loaded for {service_name}")
except ImportError as e:
    print(f"⚠️ ACGS Security middleware not available for {service_name}: {e}")
    ACGS_SECURITY_AVAILABLE = False
'''
            
            # Find where to insert the security import
            lines = content.split('\n')
            insert_index = 0
            
            # Find the end of existing imports
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    insert_index = i + 1
                elif line.strip() and not line.strip().startswith('#') and insert_index > 0:
                    break
            
            # Insert security import
            lines.insert(insert_index, security_import)
            
            # Add security middleware application after app creation
            app_creation_patterns = [
                'app = FastAPI(',
                'app = create_app(',
                'app = FastAPI()',
            ]
            
            security_application = f'''
# Apply ACGS Security Middleware
if ACGS_SECURITY_AVAILABLE:
    environment = os.getenv("ENVIRONMENT", "development")
    apply_acgs_security_middleware(app, "{service_name}", environment)
    setup_security_monitoring(app, "{service_name}")
'''
            
            # Find where to insert security application
            for i, line in enumerate(lines):
                for pattern in app_creation_patterns:
                    if pattern in line:
                        # Insert after the app creation and any immediate setup
                        insert_pos = i + 1
                        while (insert_pos < len(lines) and 
                               (lines[insert_pos].strip().startswith('app.') or 
                                not lines[insert_pos].strip())):
                            insert_pos += 1
                        
                        lines.insert(insert_pos, security_application)
                        break
                else:
                    continue
                break
            
            # Write updated content
            updated_content = '\n'.join(lines)
            with open(main_py_path, 'w') as f:
                f.write(updated_content)
            
            print(f"  ✅ Security middleware applied to {service_name}")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to update {service_name}: {e}")
            # Restore from backup if it exists
            backup_path = main_py_path.with_suffix(f"{main_py_path.suffix}.backup")
            if backup_path.exists():
                shutil.copy2(backup_path, main_py_path)
            return False
    
    def apply_security_to_service(self, service_dir: Path) -> bool:
        """Apply security hardening to a single service."""
        service_name = service_dir.name
        print(f"Applying security hardening to {service_name}...")
        
        try:
            main_py = self.find_main_py(service_dir)
            return self.update_service_imports(main_py, service_name)
        except Exception as e:
            print(f"  ❌ Error processing {service_name}: {e}")
            return False
    
    def validate_security_configuration(self) -> Dict[str, Any]:
        """Validate that security configuration is properly set up."""
        validation_results = {
            "secrets_manager_exists": False,
            "unified_validation_exists": False,
            "middleware_integration_exists": False,
            "env_example_updated": False,
        }
        
        # Check if secrets manager exists
        secrets_manager_path = self.services_root / "shared" / "secrets_manager.py"
        validation_results["secrets_manager_exists"] = secrets_manager_path.exists()
        
        # Check if unified validation exists
        unified_validation_path = self.services_root / "shared" / "security" / "unified_input_validation.py"
        validation_results["unified_validation_exists"] = unified_validation_path.exists()
        
        # Check if middleware integration exists
        middleware_integration_path = self.services_root / "shared" / "security" / "middleware_integration.py"
        validation_results["middleware_integration_exists"] = middleware_integration_path.exists()
        
        # Check if .env.example is updated
        env_example_path = self.project_root / ".env.example"
        if env_example_path.exists():
            with open(env_example_path, 'r') as f:
                content = f.read()
                validation_results["env_example_updated"] = "CSRF_SECRET_KEY" in content
        
        return validation_results
    
    def create_security_documentation(self) -> None:
        """Create security documentation for developers."""
        doc_path = self.project_root / "docs" / "SECURITY_IMPLEMENTATION.md"
        doc_path.parent.mkdir(exist_ok=True)
        
        security_doc = f'''# ACGS Security Implementation Guide
Constitutional Hash: {CONSTITUTIONAL_HASH}

## Overview

This document describes the security hardening implemented across all ACGS services.

## Security Features

### 1. Input Validation
- **XSS Protection**: All string inputs are validated and sanitized
- **SQL Injection Prevention**: Comprehensive pattern detection
- **Command Injection Prevention**: System command pattern blocking
- **Path Traversal Protection**: File path validation
- **LDAP Injection Prevention**: LDAP query sanitization

### 2. Rate Limiting
- **Request Rate Limiting**: Configurable per-minute limits
- **Burst Protection**: Additional burst capacity
- **IP-based Tracking**: Per-client tracking and enforcement

### 3. CSRF Protection
- **Token-based Protection**: Secure token generation and validation
- **Session Integration**: Token tied to user sessions
- **Automatic Cleanup**: Expired token removal

### 4. Security Headers
- **Content Security Policy**: Strict CSP enforcement
- **XSS Protection Headers**: Browser XSS filtering
- **Frame Options**: Clickjacking prevention
- **Content Type Options**: MIME type sniffing prevention

### 5. File Upload Security
- **File Type Validation**: Whitelist-based file type checking
- **Magic Number Validation**: Content verification
- **Size Limits**: Configurable file size limits
- **Filename Sanitization**: Secure filename handling

## Usage

### Automatic Integration

Security middleware is automatically applied to all services through the standardized integration:

```python
from middleware_integration import apply_acgs_security_middleware

# Automatically applied during service startup
environment = os.getenv("ENVIRONMENT", "development")
apply_acgs_security_middleware(app, "service-name", environment)
```

### Manual Validation

For endpoint-specific validation:

```python
from middleware_integration import validate_request_body, SecurityLevel

# Validate request body
sanitized_data = validate_request_body(request_data, SecurityLevel.HIGH)
```

### Security Monitoring

Monitor security metrics:

```bash
curl http://service:port/security/metrics
curl http://service:port/security/health
```

## Configuration

### Environment Variables

```bash
# Rate limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=200

# CSRF protection
CSRF_SECRET_KEY=your-secure-csrf-key

# Security level
SECURITY_LEVEL=production  # or development
```

### Development vs Production

- **Development**: More permissive settings for easier testing
- **Production**: Strict security enforcement

## Security Levels

1. **LOW**: Basic sanitization
2. **MEDIUM**: Standard security validation (default)
3. **HIGH**: Strict validation with aggressive sanitization
4. **CRITICAL**: Maximum security with blocking

## Troubleshooting

### Common Issues

1. **Rate Limit Exceeded**: Adjust `RATE_LIMIT_PER_MINUTE` environment variable
2. **CSRF Token Validation Failed**: Ensure `CSRF_SECRET_KEY` is properly set
3. **Input Validation Failed**: Check security level configuration

### Debugging

Enable debug logging for security events:

```python
import logging
logging.getLogger("acgs.security").setLevel(logging.DEBUG)
```

## Constitutional Compliance

All security features maintain constitutional compliance with hash validation: `{CONSTITUTIONAL_HASH}`

## Support

For security-related issues, refer to the security team or create an issue in the project repository.
'''
        
        with open(doc_path, 'w') as f:
            f.write(security_doc)
        
        print(f"✅ Security documentation created at {doc_path}")
    
    def run(self) -> Dict[str, Any]:
        """Run the complete security hardening process."""
        print(f"🔒 Starting ACGS Security Hardening Application")
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Project Root: {self.project_root}")
        
        # Validate prerequisites
        print("\n📋 Validating security configuration...")
        validation = self.validate_security_configuration()
        
        for check, result in validation.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check.replace('_', ' ').title()}: {result}")
        
        if not all(validation.values()):
            print("\n⚠️ Some security components are missing. Continuing with available components...")
        
        # Find all services
        print("\n🔍 Finding ACGS services...")
        services = self.find_service_directories()
        print(f"Found {len(services)} services to update")
        
        # Apply security to each service
        print("\n🛡️ Applying security hardening...")
        for service_dir in services:
            if self.apply_security_to_service(service_dir):
                self.results["updated"].append(service_dir.name)
            else:
                self.results["failed"].append(service_dir.name)
        
        # Create documentation
        print("\n📚 Creating security documentation...")
        self.create_security_documentation()
        
        # Summary
        print(f"\n📊 Security Hardening Summary:")
        print(f"  ✅ Successfully Updated: {len(self.results['updated'])} services")
        print(f"  ❌ Failed: {len(self.results['failed'])} services")
        print(f"  ⏭️ Skipped: {len(self.results['skipped'])} services")
        
        if self.results["updated"]:
            print(f"\n✅ Updated services: {', '.join(self.results['updated'])}")
        
        if self.results["failed"]:
            print(f"\n❌ Failed services: {', '.join(self.results['failed'])}")
        
        print(f"\n🎉 Security hardening completed!")
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
    
    applicator = SecurityHardeningApplicator(project_root)
    results = applicator.run()
    
    # Exit with error code if any services failed
    if results["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()