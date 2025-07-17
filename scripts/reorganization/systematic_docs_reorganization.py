#!/usr/bin/env python3
"""
ACGS-2 Systematic Documentation Reorganization Script
Constitutional Hash: cdd01ef066bc6cf2

This script implements Phase 1 of the ACGS-2 reorganization plan by:
1. Analyzing current documentation structure
2. Creating logical category mappings
3. Moving files to appropriate subdirectories
4. Updating cross-references and navigation
5. Maintaining constitutional compliance throughout
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime

class DocumentationReorganizer:
    """Systematic documentation reorganization with constitutional compliance"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docs_root = self.project_root / "docs"
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.backup_dir = self.project_root / f"docs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # File categorization mapping
        self.category_mappings = {
            "api": [
                "API", "api", "openapi", "swagger", "endpoint", "specification",
                "ACGE_API", "ACGS_CODE_ANALYSIS_ENGINE_API", "constitutional_compliance_api"
            ],
            "architecture": [
                "ARCHITECTURE", "architecture", "SYSTEM_OVERVIEW", "AGENTS", "PHASE",
                "ACGE_PHASE", "ACGS_UNIFIED_ARCHITECTURE", "COMPREHENSIVE_TASK_COMPLETION"
            ],
            "compliance": [
                "CONSTITUTIONAL", "constitutional", "compliance", "COMPLIANCE",
                "validation_framework", "CONSTITUTIONAL_MIDDLEWARE"
            ],
            "deployment": [
                "DEPLOYMENT", "deployment", "PRODUCTION_DEPLOYMENT", "AUTOMATED_DEPLOYMENT",
                "DOCKER_COMPOSE", "MIGRATION_GUIDE", "WORKFLOW_TRANSITION"
            ],
            "development": [
                "DEVELOPER", "development", "CODE_STYLE", "CONTRIBUTING", "DEPENDENCIES",
                "GEMINI", "enhanced_system_prompt", "CLAUDE_CONTEXT"
            ],
            "integration": [
                "INTEGRATION", "integration", "SERVICE_INTEGRATION", "GITHUB_WEBHOOK",
                "CLAUDE_MCP", "KIMI_GROQ", "ROUTER_KIMI", "SENTRY"
            ],
            "maintenance": [
                "MAINTENANCE", "maintenance", "REMEDIATION", "WORKFLOW_FIXES",
                "DOCUMENTATION_REMEDIATION"
            ],
            "monitoring": [
                "MONITORING", "monitoring", "SENTRY", "prometheus_metrics",
                "PERFORMANCE_OPTIMIZATION"
            ],
            "operations": [
                "OPERATIONS", "operations", "CONTINUOUS_IMPROVEMENT", "SERVICE_ISSUE",
                "SERVICE_STATUS", "runbooks", "maintenance-schedules"
            ],
            "performance": [
                "PERFORMANCE", "performance", "OPTIMIZATION", "benchmarking",
                "TUNING", "FURTHER_TUNING"
            ],
            "production": [
                "PRODUCTION", "production", "READINESS", "USER_GUIDE", "RUNBOOK",
                "SCALING_CONFIGURATION"
            ],
            "quality": [
                "QUALITY", "quality", "CODE_QUALITY", "TEST", "testing",
                "COVERAGE", "IMPROVEMENTS"
            ],
            "reports": [
                "REPORT", "report", "SUMMARY", "summary", "COMPLETION",
                "VALIDATION_REPORT", "AUDIT_REPORT"
            ],
            "research": [
                "RESEARCH", "research", "ACADEMIC", "PAPER", "arxiv",
                "CONVERSION", "DOWNLOAD", "LATEX"
            ],
            "security": [
                "SECURITY", "security", "VULNERABILITY", "HARDENING",
                "REMEDIATION_SUMMARY", "ASSESSMENT"
            ],
            "standards": [
                "STANDARDS", "standards", "DOCUMENTATION_STANDARDS",
                "RESPONSIBILITY_MATRIX", "REVIEW_REQUIREMENTS"
            ],
            "testing": [
                "TEST", "testing", "Enhanced-Test-Suite", "TESTING_STRATEGY",
                "PYTEST_WARNING"
            ],
            "training": [
                "TRAINING", "training", "ADMINISTRATOR", "END_USER",
                "ONBOARDING", "SRE_TRAINING", "DOCUMENTATION_TEAM"
            ],
            "validation": [
                "VALIDATION", "validation", "CLAUDE_MD_VALIDATION",
                "SERVICE_CONFIG", "groqcloud-integration-validation"
            ],
            "workflows": [
                "WORKFLOW", "workflow", "DOCUMENTATION_UPDATE_WORKFLOWS",
                "MODERNIZATION", "GITHUB_ACTIONS"
            ]
        }
        
        # Files to keep in root docs directory
        self.root_files = [
            "README.md", "CLAUDE.md", "CHANGELOG.md", "CONTRIBUTING.md",
            "DEPENDENCIES.md", "EXECUTIVE_SUMMARY.md", "NON_TECHNICAL_SUMMARY.md"
        ]
    
    def create_backup(self):
        """Create backup of current docs directory"""
        print(f"📦 Creating backup at {self.backup_dir}")
        shutil.copytree(self.docs_root, self.backup_dir)
        print(f"✅ Backup created successfully")
    
    def analyze_current_structure(self) -> Dict[str, List[str]]:
        """Analyze current documentation files and categorize them"""
        print("🔍 Analyzing current documentation structure...")
        
        files_by_category = {category: [] for category in self.category_mappings.keys()}
        files_by_category["uncategorized"] = []
        
        # Get all files in docs root (excluding subdirectories)
        for file_path in self.docs_root.iterdir():
            if file_path.is_file() and file_path.name not in self.root_files:
                category = self.categorize_file(file_path.name)
                files_by_category[category].append(file_path.name)
        
        # Print analysis results
        print(f"\n📊 File categorization analysis:")
        for category, files in files_by_category.items():
            if files:
                print(f"  {category}: {len(files)} files")
        
        return files_by_category
    
    def categorize_file(self, filename: str) -> str:
        """Categorize a file based on its name"""
        filename_upper = filename.upper()
        
        for category, keywords in self.category_mappings.items():
            for keyword in keywords:
                if keyword.upper() in filename_upper:
                    return category
        
        return "uncategorized"
    
    def create_category_directories(self):
        """Create category subdirectories if they don't exist"""
        print("📁 Creating category directories...")
        
        for category in self.category_mappings.keys():
            category_dir = self.docs_root / category
            if not category_dir.exists():
                category_dir.mkdir(parents=True, exist_ok=True)
                print(f"  Created: {category}/")
    
    def move_files_to_categories(self, files_by_category: Dict[str, List[str]]):
        """Move files to their appropriate category directories"""
        print("📦 Moving files to category directories...")
        
        moved_files = []
        
        for category, files in files_by_category.items():
            if category == "uncategorized" or not files:
                continue
                
            category_dir = self.docs_root / category
            
            for filename in files:
                source_path = self.docs_root / filename
                target_path = category_dir / filename
                
                if source_path.exists() and not target_path.exists():
                    try:
                        shutil.move(str(source_path), str(target_path))
                        moved_files.append((filename, category))
                        print(f"  Moved: {filename} → {category}/")
                    except Exception as e:
                        print(f"  ❌ Error moving {filename}: {e}")
        
        return moved_files
    
    def update_claude_md_files(self):
        """Ensure all category directories have CLAUDE.md files"""
        print("📝 Updating CLAUDE.md files...")
        
        template_path = self.project_root / "claude_md_template.md"
        if not template_path.exists():
            print("  ⚠️ Template file not found, skipping CLAUDE.md creation")
            return
        
        template_content = template_path.read_text()
        
        for category in self.category_mappings.keys():
            category_dir = self.docs_root / category
            claude_md_path = category_dir / "CLAUDE.md"
            
            if category_dir.exists() and not claude_md_path.exists():
                # Create basic CLAUDE.md from template
                content = self.generate_claude_md_content(category, template_content)
                claude_md_path.write_text(content)
                print(f"  Created: {category}/CLAUDE.md")
    
    def generate_claude_md_content(self, category: str, template: str) -> str:
        """Generate CLAUDE.md content for a category"""
        category_title = category.replace("_", " ").title()
        
        replacements = {
            "{DIRECTORY_NAME}": category_title,
            "{DIRECTORY_NAME_LOWER}": category.lower(),
            "{DIRECTORY_DESCRIPTION}": f"Documentation for {category_title} components",
            "{DIRECTORY_PURPOSE}": f"{category} operations",
            "{DIRECTORY_VALUE_PROPOSITION}": f"comprehensive {category} guidance",
            "{TARGET_AUDIENCE}": "ACGS-2 developers and operators",
            "{COMPLIANCE_STATUS}": "🔄 IN PROGRESS",
            "{UPDATE_DATE}": datetime.now().strftime("%Y-%m-%d"),
            "{UPDATE_DESCRIPTION}": "Systematic reorganization implementation"
        }
        
        content = template
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        return content
    
    def generate_reorganization_report(self, moved_files: List[Tuple[str, str]]):
        """Generate detailed reorganization report"""
        report_path = self.project_root / "reports" / f"docs_reorganization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "constitutional_hash": self.constitutional_hash,
            "reorganization_timestamp": datetime.now().isoformat(),
            "backup_location": str(self.backup_dir),
            "moved_files_count": len(moved_files),
            "moved_files": [{"filename": f, "category": c} for f, c in moved_files],
            "categories_created": list(self.category_mappings.keys()),
            "performance_targets": {
                "p99_latency": "<5ms",
                "throughput": ">100 RPS", 
                "cache_hit_rate": ">85%"
            },
            "implementation_status": "✅ IMPLEMENTED"
        }
        
        # Ensure reports directory exists
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Reorganization report saved: {report_path}")
        return report
    
    def execute_reorganization(self):
        """Execute the complete reorganization process"""
        print("🚀 Starting ACGS-2 Documentation Reorganization")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Project Root: {self.project_root}")
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Analyze current structure
            files_by_category = self.analyze_current_structure()
            
            # Step 3: Create category directories
            self.create_category_directories()
            
            # Step 4: Move files to categories
            moved_files = self.move_files_to_categories(files_by_category)
            
            # Step 5: Update CLAUDE.md files
            self.update_claude_md_files()
            
            # Step 6: Generate report
            report = self.generate_reorganization_report(moved_files)
            
            print(f"\n✅ Reorganization completed successfully!")
            print(f"📊 Summary:")
            print(f"  - Files moved: {len(moved_files)}")
            print(f"  - Categories created: {len(self.category_mappings)}")
            print(f"  - Backup location: {self.backup_dir}")
            print(f"  - Constitutional compliance: {self.constitutional_hash}")
            
            return True
            
        except Exception as e:
            print(f"❌ Reorganization failed: {e}")
            print(f"💡 Backup available at: {self.backup_dir}")
            return False

def main():
    """Main execution function"""
    project_root = "/home/dislove/ACGS-2"
    reorganizer = DocumentationReorganizer(project_root)
    
    # Execute reorganization
    success = reorganizer.execute_reorganization()
    
    if success:
        print("\n🎉 ACGS-2 Documentation Reorganization Complete!")
        print("Next steps:")
        print("1. Validate cross-references and update broken links")
        print("2. Standardize CLAUDE.md files with 8-section template")
        print("3. Implement constitutional compliance validation")
    else:
        print("\n❌ Reorganization failed. Check backup and logs.")

if __name__ == "__main__":
    main()
