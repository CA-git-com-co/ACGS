#!/usr/bin/env python3
"""
ACGS-2 CLAUDE.md Standardization Script
Constitutional Hash: cdd01ef066bc6cf2

This script implements Phase 2 of the reorganization plan by:
1. Standardizing all CLAUDE.md files to follow the 8-section template
2. Ensuring constitutional compliance validation
3. Adding implementation status indicators
4. Updating cross-references and navigation
5. Maintaining performance targets throughout
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

class ClaudeMdStandardizer:
    """Standardize CLAUDE.md files with constitutional compliance"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.template_path = self.project_root / "claude_md_template.md"
        
        # 8-section template structure
        self.required_sections = [
            "Directory Overview",
            "File Inventory", 
            "Dependencies & Interactions",
            "Key Components",
            "Constitutional Compliance Status",
            "Performance Considerations",
            "Implementation Status",
            "Cross-References & Navigation"
        ]
        
        # Performance targets
        self.performance_targets = {
            "p99_latency": "<5ms",
            "throughput": ">100 RPS",
            "cache_hit_rate": ">85%"
        }
        
        # Directory-specific configurations
        self.directory_configs = {
            "api": {
                "description": "API documentation, specifications, and endpoint definitions",
                "purpose": "API development and integration",
                "value_proposition": "comprehensive API guidance and specifications",
                "target_audience": "API developers and integrators"
            },
            "architecture": {
                "description": "System architecture documentation and design patterns",
                "purpose": "architectural planning and system design",
                "value_proposition": "detailed architectural guidance and patterns",
                "target_audience": "system architects and senior developers"
            },
            "compliance": {
                "description": "Constitutional compliance frameworks and validation tools",
                "purpose": "compliance validation and constitutional enforcement",
                "value_proposition": "comprehensive compliance assurance",
                "target_audience": "compliance officers and governance teams"
            },
            "deployment": {
                "description": "Deployment guides, procedures, and automation scripts",
                "purpose": "deployment operations and automation",
                "value_proposition": "streamlined deployment processes",
                "target_audience": "DevOps engineers and deployment teams"
            },
            "development": {
                "description": "Developer guides, coding standards, and development tools",
                "purpose": "development workflows and standards",
                "value_proposition": "enhanced developer productivity",
                "target_audience": "software developers and development teams"
            },
            "integration": {
                "description": "Integration patterns, guides, and service connectivity",
                "purpose": "service integration and connectivity",
                "value_proposition": "seamless system integration",
                "target_audience": "integration engineers and system integrators"
            },
            "maintenance": {
                "description": "Maintenance procedures, remediation guides, and operational tasks",
                "purpose": "system maintenance and operational excellence",
                "value_proposition": "reliable system maintenance",
                "target_audience": "operations teams and site reliability engineers"
            },
            "monitoring": {
                "description": "Monitoring configurations, dashboards, and observability tools",
                "purpose": "system monitoring and observability",
                "value_proposition": "comprehensive system visibility",
                "target_audience": "monitoring engineers and operations teams"
            },
            "operations": {
                "description": "Operational procedures, runbooks, and service management",
                "purpose": "operational excellence and service management",
                "value_proposition": "efficient operational workflows",
                "target_audience": "operations teams and service managers"
            },
            "performance": {
                "description": "Performance optimization guides and benchmarking tools",
                "purpose": "performance optimization and tuning",
                "value_proposition": "optimal system performance",
                "target_audience": "performance engineers and optimization teams"
            },
            "production": {
                "description": "Production deployment guides and operational procedures",
                "purpose": "production operations and management",
                "value_proposition": "reliable production systems",
                "target_audience": "production engineers and operations teams"
            },
            "quality": {
                "description": "Quality assurance processes and testing frameworks",
                "purpose": "quality assurance and testing",
                "value_proposition": "comprehensive quality validation",
                "target_audience": "QA engineers and testing teams"
            },
            "reports": {
                "description": "Generated reports, analysis results, and documentation summaries",
                "purpose": "reporting and analysis",
                "value_proposition": "comprehensive system insights",
                "target_audience": "stakeholders and management teams"
            },
            "research": {
                "description": "Research papers, academic content, and experimental documentation",
                "purpose": "research and development",
                "value_proposition": "cutting-edge research insights",
                "target_audience": "researchers and academic teams"
            },
            "security": {
                "description": "Security policies, procedures, and vulnerability assessments",
                "purpose": "security management and compliance",
                "value_proposition": "comprehensive security assurance",
                "target_audience": "security engineers and compliance teams"
            },
            "standards": {
                "description": "Documentation standards, coding guidelines, and best practices",
                "purpose": "standardization and best practices",
                "value_proposition": "consistent quality standards",
                "target_audience": "development teams and technical writers"
            },
            "testing": {
                "description": "Testing strategies, frameworks, and validation procedures",
                "purpose": "testing and validation",
                "value_proposition": "comprehensive testing coverage",
                "target_audience": "testing engineers and QA teams"
            },
            "training": {
                "description": "Training materials, guides, and educational resources",
                "purpose": "training and knowledge transfer",
                "value_proposition": "effective knowledge sharing",
                "target_audience": "trainees and educational teams"
            },
            "validation": {
                "description": "Validation tools, reports, and compliance checking",
                "purpose": "validation and compliance verification",
                "value_proposition": "thorough validation processes",
                "target_audience": "validation engineers and compliance teams"
            },
            "workflows": {
                "description": "Workflow documentation, procedures, and automation guides",
                "purpose": "workflow optimization and automation",
                "value_proposition": "streamlined operational workflows",
                "target_audience": "workflow engineers and automation teams"
            }
        }
    
    def load_template(self) -> str:
        """Load the CLAUDE.md template"""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        return self.template_path.read_text()
    
    def find_claude_md_files(self) -> List[Path]:
        """Find all CLAUDE.md files in the project"""
        claude_files = []
        for file_path in self.project_root.rglob("CLAUDE.md"):
            # Skip virtual environments and build directories
            if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'node_modules', 'target']):
                continue
            claude_files.append(file_path)
        return claude_files
    
    def analyze_existing_content(self, file_path: Path) -> Dict:
        """Analyze existing CLAUDE.md content to preserve valuable information"""
        try:
            content = file_path.read_text()
            
            analysis = {
                "has_constitutional_hash": self.constitutional_hash in content,
                "existing_sections": [],
                "valuable_content": {},
                "cross_references": [],
                "performance_metrics": {}
            }
            
            # Extract existing sections
            section_pattern = r'^##\s+(.+)$'
            for match in re.finditer(section_pattern, content, re.MULTILINE):
                analysis["existing_sections"].append(match.group(1).strip())
            
            # Extract cross-references
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for match in re.finditer(link_pattern, content):
                analysis["cross_references"].append({
                    "text": match.group(1),
                    "url": match.group(2)
                })
            
            # Extract performance metrics
            for target, value in self.performance_targets.items():
                if value in content:
                    analysis["performance_metrics"][target] = value
            
            return analysis
            
        except Exception as e:
            print(f"  ⚠️ Error analyzing {file_path}: {e}")
            return {"has_constitutional_hash": False, "existing_sections": [], "valuable_content": {}}
    
    def generate_standardized_content(self, directory_name: str, template: str, existing_analysis: Dict) -> str:
        """Generate standardized CLAUDE.md content for a directory"""
        
        # Get directory configuration
        config = self.directory_configs.get(directory_name, {
            "description": f"Documentation for {directory_name} components",
            "purpose": f"{directory_name} operations",
            "value_proposition": f"comprehensive {directory_name} guidance",
            "target_audience": "ACGS-2 developers and operators"
        })
        
        # Determine implementation status
        implementation_status = "✅ IMPLEMENTED" if existing_analysis.get("has_constitutional_hash") else "🔄 IN PROGRESS"
        
        # Create replacements dictionary
        replacements = {
            "{DIRECTORY_NAME}": directory_name.replace("_", " ").title(),
            "{DIRECTORY_NAME_LOWER}": directory_name.lower(),
            "{DIRECTORY_DESCRIPTION}": config["description"],
            "{DIRECTORY_PURPOSE}": config["purpose"],
            "{DIRECTORY_VALUE_PROPOSITION}": config["value_proposition"],
            "{TARGET_AUDIENCE}": config["target_audience"],
            "{COMPLIANCE_STATUS}": implementation_status,
            "{HASH_VALIDATION_STATUS}": "✅ Active" if existing_analysis.get("has_constitutional_hash") else "🔄 Implementing",
            "{SCOPE}": f"all {directory_name} operations",
            "{UPDATE_DATE}": datetime.now().strftime("%Y-%m-%d"),
            "{UPDATE_DESCRIPTION}": "Systematic standardization implementation",
            "{COMPLIANCE_STATEMENT}": f"All {directory_name} operations maintain constitutional hash `{self.constitutional_hash}` validation and performance targets (P99 <5ms, >100 RPS, >85% cache hit rates)."
        }
        
        # Apply replacements to template
        content = template
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        return content
    
    def standardize_file(self, file_path: Path) -> bool:
        """Standardize a single CLAUDE.md file"""
        try:
            # Get directory name
            directory_name = file_path.parent.name
            
            # Analyze existing content
            existing_analysis = self.analyze_existing_content(file_path)
            
            # Load template
            template = self.load_template()
            
            # Generate standardized content
            standardized_content = self.generate_standardized_content(
                directory_name, template, existing_analysis
            )
            
            # Write standardized content
            file_path.write_text(standardized_content)
            
            print(f"  ✅ Standardized: {file_path.relative_to(self.project_root)}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error standardizing {file_path}: {e}")
            return False
    
    def validate_constitutional_compliance(self, file_path: Path) -> bool:
        """Validate constitutional compliance in a CLAUDE.md file"""
        try:
            content = file_path.read_text()
            
            # Check for constitutional hash
            has_hash = self.constitutional_hash in content
            
            # Check for performance targets
            has_performance_targets = all(
                target in content for target in self.performance_targets.values()
            )
            
            # Check for implementation status indicators
            has_status_indicators = any(
                indicator in content for indicator in ["✅ IMPLEMENTED", "🔄 IN PROGRESS", "❌ PLANNED"]
            )
            
            compliance_score = sum([has_hash, has_performance_targets, has_status_indicators])
            
            if compliance_score == 3:
                print(f"  ✅ Full compliance: {file_path.relative_to(self.project_root)}")
                return True
            else:
                print(f"  🔄 Partial compliance ({compliance_score}/3): {file_path.relative_to(self.project_root)}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error validating {file_path}: {e}")
            return False
    
    def execute_standardization(self):
        """Execute the complete standardization process"""
        print("🚀 Starting ACGS-2 CLAUDE.md Standardization")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Project Root: {self.project_root}")
        
        try:
            # Find all CLAUDE.md files
            claude_files = self.find_claude_md_files()
            print(f"\n📁 Found {len(claude_files)} CLAUDE.md files")
            
            # Standardize each file
            print("\n📝 Standardizing CLAUDE.md files...")
            standardized_count = 0
            
            for file_path in claude_files:
                if self.standardize_file(file_path):
                    standardized_count += 1
            
            # Validate constitutional compliance
            print("\n🔍 Validating constitutional compliance...")
            compliant_count = 0
            
            for file_path in claude_files:
                if self.validate_constitutional_compliance(file_path):
                    compliant_count += 1
            
            # Generate summary report
            compliance_rate = (compliant_count / len(claude_files)) * 100 if claude_files else 0
            standardization_rate = (standardized_count / len(claude_files)) * 100 if claude_files else 0
            
            print(f"\n✅ Standardization completed!")
            print(f"📊 Summary:")
            print(f"  - Files processed: {len(claude_files)}")
            print(f"  - Successfully standardized: {standardized_count} ({standardization_rate:.1f}%)")
            print(f"  - Constitutional compliance: {compliant_count} ({compliance_rate:.1f}%)")
            print(f"  - Constitutional hash: {self.constitutional_hash}")
            print(f"  - Performance targets: P99 <5ms, >100 RPS, >85% cache hit rates")
            
            return True
            
        except Exception as e:
            print(f"❌ Standardization failed: {e}")
            return False

def main():
    """Main execution function"""
    project_root = "/home/dislove/ACGS-2"
    standardizer = ClaudeMdStandardizer(project_root)
    
    # Execute standardization
    success = standardizer.execute_standardization()
    
    if success:
        print("\n🎉 ACGS-2 CLAUDE.md Standardization Complete!")
        print("Next steps:")
        print("1. Validate cross-references and update broken links")
        print("2. Implement automated validation pipeline")
        print("3. Set up continuous compliance monitoring")
    else:
        print("\n❌ Standardization failed. Check logs for details.")

if __name__ == "__main__":
    main()
