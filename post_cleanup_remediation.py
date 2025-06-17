#!/usr/bin/env python3
"""
ACGS-1 Post-Cleanup Remediation Script

This script addresses the issues found in the post-cleanup analysis:
1. Fix missing requirements.txt files for services
2. Consolidate environment configurations
3. Update documentation references
4. Validate service integration
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class PostCleanupRemediation:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.remediation_log = []
        
        # Service requirements mapping
        self.service_requirements = {
            "constitutional-ai": [
                "fastapi>=0.104.1",
                "uvicorn>=0.24.0",
                "pydantic>=2.5.0",
                "sqlalchemy>=2.0.0",
                "alembic>=1.13.0",
                "psycopg2-binary>=2.9.0",
                "python-multipart>=0.0.6",
                "python-jose[cryptography]>=3.3.0",
                "passlib[bcrypt]>=1.7.4",
                "httpx>=0.25.0"
            ],
            "governance-synthesis": [
                "fastapi>=0.104.1",
                "uvicorn>=0.24.0",
                "pydantic>=2.5.0",
                "openai>=1.3.0",
                "anthropic>=0.7.0",
                "httpx>=0.25.0",
                "langchain>=0.0.350",
                "langchain-openai>=0.0.2",
                "python-multipart>=0.0.6"
            ],
            "formal-verification": [
                "fastapi>=0.104.1",
                "uvicorn>=0.24.0",
                "pydantic>=2.5.0",
                "z3-solver>=4.12.0",
                "sympy>=1.12",
                "httpx>=0.25.0",
                "python-multipart>=0.0.6"
            ],
            "policy-governance": [
                "fastapi>=0.104.1",
                "uvicorn>=0.24.0",
                "pydantic>=2.5.0",
                "sqlalchemy>=2.0.0",
                "alembic>=1.13.0",
                "psycopg2-binary>=2.9.0",
                "httpx>=0.25.0",
                "python-multipart>=0.0.6",
                "redis>=5.0.0"
            ]
        }

    def log_action(self, action: str):
        """Log remediation actions."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {action}"
        self.remediation_log.append(log_entry)
        print(f"📝 {log_entry}")

    def create_missing_requirements_files(self):
        """Create missing requirements.txt files for services."""
        print("📦 Creating missing requirements.txt files...")
        
        services_core = self.project_root / "services" / "core"
        
        for service_name, requirements in self.service_requirements.items():
            service_path = services_core / service_name
            requirements_file = service_path / "requirements.txt"
            
            if service_path.exists() and not requirements_file.exists():
                # Create requirements.txt
                with open(requirements_file, 'w') as f:
                    f.write("# ACGS-1 Service Requirements\n")
                    f.write(f"# Generated for {service_name} service\n\n")
                    for req in requirements:
                        f.write(f"{req}\n")
                
                self.log_action(f"Created requirements.txt for {service_name}")
            elif requirements_file.exists():
                self.log_action(f"Requirements.txt already exists for {service_name}")

    def consolidate_environment_files(self):
        """Consolidate environment configuration files."""
        print("🔧 Consolidating environment files...")
        
        # Keep only essential environment files in root
        essential_env_files = [
            ".env",
            ".env.example", 
            ".env.production",
            ".env.staging"
        ]
        
        # Remove redundant environment files from root
        for env_file in self.project_root.glob(".env*"):
            if env_file.name not in essential_env_files:
                if env_file.is_file():
                    env_file.unlink()
                    self.log_action(f"Removed redundant env file: {env_file.name}")

    def update_documentation_references(self):
        """Update documentation to use correct service names."""
        print("📚 Updating documentation references...")
        
        # Mapping of old service names to new ones
        service_name_mapping = {
            "ac": "constitutional-ai",
            "ec": "evolutionary-computation", 
            "gs": "governance-synthesis",
            "pgc": "policy-governance",
            "constitutional_ai": "constitutional-ai",
            "evolutionary_computation": "evolutionary-computation",
            "formal_verification": "formal-verification",
            "governance_synthesis": "governance-synthesis",
            "policy_governance": "policy-governance",
            "self_evolving_ai": "self-evolving-ai"
        }
        
        # Files to update (excluding backups and analysis files)
        doc_files = []
        for pattern in ["*.md", "*.rst", "*.txt"]:
            for file_path in self.project_root.glob(pattern):
                # Skip backup directories and analysis files
                if "backup" not in str(file_path) and "analysis" not in str(file_path):
                    doc_files.append(file_path)
        
        updated_files = 0
        
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                
                # Update service references
                for old_name, new_name in service_name_mapping.items():
                    # Only replace if it's a clear service reference
                    patterns = [
                        f"services/core/{old_name}",
                        f"/{old_name}_service",
                        f" {old_name} service",
                        f"({old_name})",
                        f"`{old_name}`"
                    ]
                    
                    for pattern in patterns:
                        if old_name != new_name:  # Only replace if names are different
                            replacement = pattern.replace(old_name, new_name)
                            content = content.replace(pattern, replacement)
                
                # Write back if changed
                if content != original_content:
                    with open(doc_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated_files += 1
                    self.log_action(f"Updated service references in {doc_file.name}")
                    
            except Exception as e:
                self.log_action(f"Warning: Could not update {doc_file}: {e}")
        
        self.log_action(f"Updated {updated_files} documentation files")

    def validate_service_structure(self):
        """Validate that all services have proper structure."""
        print("✅ Validating service structure...")
        
        services_core = self.project_root / "services" / "core"
        required_services = [
            "constitutional-ai", "governance-synthesis", "formal-verification",
            "policy-governance", "evolutionary-computation", "self-evolving-ai", "acgs-pgp-v8"
        ]
        
        validation_results = {}
        
        for service_name in required_services:
            service_path = services_core / service_name
            
            validation = {
                "exists": service_path.exists(),
                "has_requirements": False,
                "has_main_app": False,
                "structure_valid": False
            }
            
            if validation["exists"]:
                # Check requirements
                req_file = service_path / "requirements.txt"
                validation["has_requirements"] = req_file.exists()
                
                # Check for main app structure
                app_indicators = [
                    service_path / "app",
                    service_path / "main.py",
                    service_path / "src"
                ]
                validation["has_main_app"] = any(p.exists() for p in app_indicators)
                
                validation["structure_valid"] = validation["has_requirements"] and validation["has_main_app"]
            
            validation_results[service_name] = validation
            
            status = "✅" if validation["structure_valid"] else "❌"
            self.log_action(f"Service validation {status} {service_name}")
        
        return validation_results

    def test_quantumagi_preservation(self):
        """Test that Quantumagi deployment is preserved."""
        print("⛓️ Testing Quantumagi preservation...")
        
        quantumagi_path = self.project_root / "blockchain" / "quantumagi-deployment"
        
        if not quantumagi_path.exists():
            self.log_action("ERROR: Quantumagi deployment directory missing!")
            return False
        
        critical_files = [
            "constitution_data.json",
            "governance_accounts.json",
            "initial_policies.json",
            "complete_deployment.sh"
        ]
        
        missing_files = []
        for file_name in critical_files:
            file_path = quantumagi_path / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_files:
            self.log_action(f"ERROR: Missing Quantumagi files: {missing_files}")
            return False
        
        # Check for constitutional hash
        constitution_file = quantumagi_path / "constitution_data.json"
        try:
            with open(constitution_file, 'r') as f:
                content = f.read()
                if "cdd01ef066bc6cf2" in content:
                    self.log_action("✅ Constitutional hash cdd01ef066bc6cf2 preserved")
                    return True
                else:
                    self.log_action("WARNING: Constitutional hash not found in constitution data")
                    return False
        except Exception as e:
            self.log_action(f"ERROR: Could not verify constitutional hash: {e}")
            return False

    def generate_remediation_report(self):
        """Generate remediation completion report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "remediation_type": "Post-Cleanup Remediation",
            "actions_performed": self.remediation_log,
            "summary": {
                "total_actions": len(self.remediation_log),
                "remediation_completed": True
            }
        }
        
        report_file = self.project_root / f"post_cleanup_remediation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log_action(f"Remediation report saved to {report_file}")
        return report

    def execute_remediation(self):
        """Execute complete post-cleanup remediation."""
        print("🚀 Starting post-cleanup remediation...")
        print("=" * 50)
        
        try:
            # Step 1: Create missing requirements files
            self.create_missing_requirements_files()
            
            # Step 2: Consolidate environment files
            self.consolidate_environment_files()
            
            # Step 3: Update documentation references
            self.update_documentation_references()
            
            # Step 4: Validate service structure
            validation_results = self.validate_service_structure()
            
            # Step 5: Test Quantumagi preservation
            quantumagi_ok = self.test_quantumagi_preservation()
            
            # Step 6: Generate report
            report = self.generate_remediation_report()
            
            # Summary
            valid_services = sum(1 for v in validation_results.values() if v["structure_valid"])
            total_services = len(validation_results)
            
            print("\n✅ Post-cleanup remediation completed!")
            print(f"📦 Services with valid structure: {valid_services}/{total_services}")
            print(f"⛓️ Quantumagi preservation: {'✅' if quantumagi_ok else '❌'}")
            print(f"📝 Total actions: {len(self.remediation_log)}")
            
            return valid_services == total_services and quantumagi_ok
            
        except Exception as e:
            self.log_action(f"ERROR during remediation: {str(e)}")
            print(f"❌ Remediation failed: {e}")
            return False

if __name__ == "__main__":
    remediation = PostCleanupRemediation()
    success = remediation.execute_remediation()
    exit(0 if success else 1)
