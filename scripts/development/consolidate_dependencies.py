#!/usr/bin/env python3
"""
ACGS Dependency Consolidation Script
Constitutional Hash: cdd01ef066bc6cf2

This script consolidates dependencies across the ACGS project.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set

class DependencyConsolidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.shared_req_dir = project_root / "services" / "shared" / "requirements"
        
    def create_shared_requirements(self):
        """Create shared requirements directory and files."""
        print("Creating shared requirements directory...")
        self.shared_req_dir.mkdir(parents=True, exist_ok=True)
        
        # Create requirements-base.txt
        base_requirements = '''# ACGS Base Requirements
# Constitutional Hash: cdd01ef066bc6cf2
# Core dependencies for all ACGS services

# Web Framework
fastapi>=0.115.6
uvicorn[standard]>=0.34.0
pydantic>=2.10.5
pydantic-settings>=2.7.1

# Database and Storage
asyncpg>=0.29.0
sqlalchemy[asyncio]>=2.0.23
alembic>=1.13.0
aioredis>=2.0.1

# HTTP and Networking
httpx>=0.28.1
aiohttp>=3.9.0

# Security and Authentication
cryptography>=45.0.4
pyjwt[crypto]>=2.10.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.20

# Configuration and Environment
python-dotenv>=1.0.0

# Monitoring and Observability
prometheus-client>=0.19.0
structlog>=23.2.0

# Core Utilities
requests>=2.32.4
urllib3>=2.5.0
certifi>=2025.6.15
tenacity>=8.2.3
'''
        
        with open(self.shared_req_dir / "requirements-base.txt", "w") as f:
            f.write(base_requirements)
        
        # Create requirements-test.txt
        test_requirements = '''# ACGS Test Requirements
# Constitutional Hash: cdd01ef066bc6cf2
-r requirements-base.txt

# Testing Framework
pytest>=7.4.3
pytest-asyncio>=0.21.1
pytest-cov>=4.1.0
pytest-mock>=3.14.1
pytest-benchmark>=4.0.0
fakeredis>=2.18.0
factory-boy>=3.3.0
faker>=19.0.0
'''
        
        with open(self.shared_req_dir / "requirements-test.txt", "w") as f:
            f.write(test_requirements)
        
        # Create requirements-dev.txt
        dev_requirements = '''# ACGS Development Requirements
# Constitutional Hash: cdd01ef066bc6cf2
-r requirements-test.txt

# Code Quality
black>=23.11.0
isort>=5.12.0
ruff>=0.1.6
mypy>=1.7.0
pre-commit>=3.4.0

# Security
bandit>=1.7.5
safety>=2.3.0
'''
        
        with open(self.shared_req_dir / "requirements-dev.txt", "w") as f:
            f.write(dev_requirements)
        
        print("✓ Created shared requirements files")
    
    def backup_existing_files(self):
        """Backup existing requirements files."""
        backup_dir = self.project_root / "requirements_backup"
        backup_dir.mkdir(exist_ok=True)
        
        print("Backing up existing requirements files...")
        
        req_files = list(self.project_root.rglob("requirements*.txt"))
        for req_file in req_files:
            if "requirements_backup" not in str(req_file):
                rel_path = req_file.relative_to(self.project_root)
                backup_path = backup_dir / rel_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(req_file, backup_path)
        
        print(f"✓ Backed up {len(req_files)} requirements files to {backup_dir}")
    
    def update_service_requirements(self):
        """Update service requirements files to use shared base."""
        print("Updating service requirements files...")
        
        # Service-specific dependencies
        service_deps = {
            "code-analysis": ["scikit-learn>=1.3.0", "numpy>=1.24.0"],
            "formal-verification": ["z3-solver>=4.12.6.0"],
            "governance-engine": ["numpy>=1.24.0", "scipy>=1.11.0"],
            "api_gateway": ["slowapi>=0.1.9"],
            "evolutionary-computation": [],
            "constitutional-core": [],
            "authentication": [],
            "integrity": [],
            "audit_aggregator": []
        }
        
        services_dir = self.project_root / "services"
        
        for service_type in ["core", "platform_services"]:
            service_type_dir = services_dir / service_type
            if not service_type_dir.exists():
                continue
                
            for service_dir in service_type_dir.iterdir():
                if service_dir.is_dir():
                    req_file = service_dir / "config/environments/requirements.txt"
                    if req_file.exists():
                        self.update_single_service_requirements(req_file, service_dir.name, service_deps)
    
    def update_single_service_requirements(self, req_file: Path, service_name: str, service_deps: Dict):
        """Update a single service's requirements file."""
        relative_path = "../shared/requirements/requirements-base.txt"
        
        content = f'''# {service_name.title()} Service Requirements
# Constitutional Hash: cdd01ef066bc6cf2
-r {relative_path}

'''
        
        # Add service-specific dependencies
        if service_name in service_deps:
            specific_deps = service_deps[service_name]
            if specific_deps:
                content += "# Service-specific dependencies\n"
                for dep in specific_deps:
                    content += f"{dep}\n"
        
        with open(req_file, "w") as f:
            f.write(content)
        
        print(f"✓ Updated {req_file}")
    
    def update_test_requirements(self):
        """Update test requirements files."""
        print("Updating test requirements files...")
        
        test_dirs = [
            "tests/load_testing",
            "tests/security", 
            "tests/compliance"
        ]
        
        for test_dir in test_dirs:
            req_file = self.project_root / test_dir / "config/environments/requirements.txt"
            if req_file.exists():
                relative_path = "../../services/shared/requirements/requirements-test.txt"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
                
                content = f'''# {test_dir.replace("/", " ").title()} Requirements
# Constitutional Hash: cdd01ef066bc6cf2
-r {relative_path}

# Additional test-specific dependencies
'''
                
                # Add specific dependencies for load testing
                if "load_testing" in test_dir:
                    content += "locust>=2.17.0\n"
                    content += "gevent>=23.7.0\n"
                    content += "pandas>=2.0.0\n"
                    content += "matplotlib>=3.7.0\n"
                    content += "seaborn>=0.12.0\n"
                
                with open(req_file, "w") as f:
                    f.write(content)
                
                print(f"✓ Updated {req_file}")
    
    def update_tools_requirements(self):
        """Update tools requirements."""
        print("Updating tools requirements...")
        
        tools_req = self.project_root / "tools" / "config/environments/requirements.txt"
        if tools_req.exists():
            relative_path = "../services/shared/requirements/requirements-dev.txt"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
            
            content = f'''# Tools Requirements
# Constitutional Hash: cdd01ef066bc6cf2
-r {relative_path}

# Tool-specific dependencies
alembic>=1.13.0
psycopg2-binary>=2.9.10
markupsafe>=3.0.2
'''
            
            with open(tools_req, "w") as f:
                f.write(content)
            
            print(f"✓ Updated {tools_req}")
    
    def update_pyproject_toml(self):
        """Update config/environments/pyproject.toml to reflect consolidated dependencies."""
        print("Updating config/environments/pyproject.toml...")
        
        pyproject_file = self.project_root / "config/environments/pyproject.toml"
        if not pyproject_file.exists():
            return
        
        # Read current content
        with open(pyproject_file, "r") as f:
            content = f.read()
        
        # Update dependencies section to match our base requirements
        updated_deps = '''# Core runtime dependencies - essential for all services
dependencies = [
    # Core Web Framework
    "fastapi>=0.115.6",
    "uvicorn[standard]>=0.34.0",
    "pydantic>=2.10.5",
    "pydantic-settings>=2.7.1",
    
    # Database and Storage
    "asyncpg>=0.29.0",
    "sqlalchemy[asyncio]>=2.0.23",
    "alembic>=1.13.0",
    "aioredis>=2.0.1",
    
    # HTTP and Networking
    "httpx>=0.28.1",
    "aiohttp>=3.9.0",
    "aiofiles>=23.0.0",
    
    # Security and Authentication
    "cryptography>=45.0.4",
    "pyjwt[crypto]>=2.10.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.20",
    
    # Configuration and Environment
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0.1",
    "click>=8.1.7",
    "rich>=13.6.0",
    "typer>=0.9.0",
    
    # Monitoring and Observability
    "prometheus-client>=0.19.0",
    "opentelemetry-api>=1.34.1",
    "opentelemetry-sdk>=1.34.1",
    "opentelemetry-instrumentation-fastapi>=0.42b0",
    
    # Core Utilities
    "requests>=2.32.4",
    "urllib3>=2.5.0",
    "certifi>=2025.6.15",
    "tenacity>=8.2.3",
    
    # Additional Performance and Utilities
    "cachetools>=5.3.2",
    "orjson>=3.9.10",
    "msgpack>=1.0.7",
    
    # Async Support  
    "anyio>=4.1.0",
    "websockets>=12.0",
    
    # Validation and Parsing
    "email-validator>=2.1.0",
    "python-dateutil>=2.8.2",
    "pytz>=2023.3",
    
    # Monitoring Extensions
    "prometheus-fastapi-instrumentator>=6.1.0", 
    "structlog>=23.2.0",
]'''
        
        # Replace the dependencies section
        import re
        pattern = r'dependencies = \[(.*?)\]'
        content = re.sub(pattern, updated_deps, content, flags=re.DOTALL)
        
        with open(pyproject_file, "w") as f:
            f.write(content)
        
        print("✓ Updated config/environments/pyproject.toml")
    
    def create_validation_script(self):
        """Create a script to validate the consolidation."""
        script_path = self.project_root / "scripts" / "validate_dependencies.py"
        
        validation_script = '''#!/usr/bin/env python3
"""
Dependency Validation Script
Constitutional Hash: cdd01ef066bc6cf2
"""

import subprocess
import sys
from pathlib import Path

def validate_requirements():
    """Validate that all requirements files are valid."""
    print("Validating requirements files...")
    
    req_files = list(Path(".").rglob("requirements*.txt"))
    
    for req_file in req_files:
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--dry-run", "-r", str(req_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ {req_file}: {result.stderr}")
            else:
                print(f"✅ {req_file}: Valid")
                
        except Exception as e:
            print(f"❌ {req_file}: {e}")

if __name__ == "__main__":
    validate_requirements()
'''
        
        with open(script_path, "w") as f:
            f.write(validation_script)
        
        # Make it executable
        script_path.chmod(0o755)
        
        print(f"✓ Created validation script at {script_path}")
    
    def run_consolidation(self):
        """Run the complete consolidation process."""
        print("Starting ACGS dependency consolidation...")
        print("Constitutional Hash: cdd01ef066bc6cf2")
        print("=" * 50)
        
        # Step 1: Backup existing files
        self.backup_existing_files()
        
        # Step 2: Create shared requirements
        self.create_shared_requirements()
        
        # Step 3: Update service requirements
        self.update_service_requirements()
        
        # Step 4: Update test requirements
        self.update_test_requirements()
        
        # Step 5: Update tools requirements
        self.update_tools_requirements()
        
        # Step 6: Update config/environments/pyproject.toml
        self.update_pyproject_toml()
        
        # Step 7: Create validation script
        self.create_validation_script()
        
        print("\n" + "=" * 50)
        print("DEPENDENCY CONSOLIDATION COMPLETE")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Review the updated requirements files")
        print("2. Run 'python scripts/validate_dependencies.py' to validate")
        print("3. Test services individually")
        print("4. Update CI/CD pipelines")
        print("5. Update documentation")
        print("\nBackup files are in: requirements_backup/")

if __name__ == "__main__":
    consolidator = DependencyConsolidator(Path("/home/dislove/ACGS-2"))
    consolidator.run_consolidation()