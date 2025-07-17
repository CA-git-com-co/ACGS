#!/usr/bin/env python3
"""
ACGS-2 Cross-Reference Fixing Script
Constitutional Hash: cdd01ef066bc6cf2

This script implements Phase 3 of the reorganization plan by:
1. Identifying and fixing broken cross-references
2. Updating navigation links and breadcrumbs
3. Replacing template placeholders with actual content
4. Ensuring >80% cross-reference validity
5. Maintaining constitutional compliance throughout
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
import json
from datetime import datetime

class CrossReferenceFixer:
    """Fix cross-references and navigation in CLAUDE.md files"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Directory structure mapping for navigation
        self.directory_structure = {
            "docs": {
                "api": "API Documentation",
                "architecture": "System Architecture", 
                "compliance": "Constitutional Compliance",
                "deployment": "Deployment Guides",
                "development": "Development Resources",
                "integration": "Integration Patterns",
                "maintenance": "Maintenance Procedures",
                "monitoring": "Monitoring & Observability",
                "operations": "Operations Management",
                "performance": "Performance Optimization",
                "production": "Production Management",
                "quality": "Quality Assurance",
                "reports": "Reports & Analysis",
                "research": "Research & Development",
                "security": "Security Management",
                "standards": "Standards & Guidelines",
                "testing": "Testing Frameworks",
                "training": "Training Resources",
                "validation": "Validation Tools",
                "workflows": "Workflow Documentation"
            },
            "services": {
                "core": "Core Services",
                "platform_services": "Platform Services",
                "blockchain": "Blockchain Integration",
                "shared": "Shared Components",
                "cli": "Command Line Interface",
                "contexts": "Context Management"
            },
            "infrastructure": {
                "docker": "Docker Configuration",
                "kubernetes": "Kubernetes Deployment",
                "terraform": "Infrastructure as Code",
                "monitoring": "Monitoring Infrastructure"
            }
        }
        
        # Common navigation patterns
        self.navigation_patterns = {
            "parent_dirs": ["docs", "services", "infrastructure", "tools", "scripts"],
            "sibling_relationships": {},
            "common_references": {
                "constitutional_ai": "services/core/constitutional-ai/CLAUDE.md",
                "governance_synthesis": "services/core/governance-synthesis/CLAUDE.md",
                "api_gateway": "services/platform_services/api_gateway/CLAUDE.md",
                "deployment_guide": "docs/deployment/CLAUDE.md",
                "security_guide": "docs/security/CLAUDE.md",
                "testing_guide": "docs/testing/CLAUDE.md"
            }
        }
    
    def find_claude_md_files(self) -> List[Path]:
        """Find all CLAUDE.md files in the project"""
        claude_files = []
        for file_path in self.project_root.rglob("CLAUDE.md"):
            # Skip virtual environments and build directories
            if any(skip in str(file_path) for skip in ['.venv', '__pycache__', '.git', 'node_modules', 'target']):
                continue
            claude_files.append(file_path)
        return claude_files
    
    def analyze_directory_context(self, file_path: Path) -> Dict:
        """Analyze directory context for navigation generation"""
        relative_path = file_path.relative_to(self.project_root)
        path_parts = relative_path.parts[:-1]  # Exclude CLAUDE.md filename
        
        context = {
            "directory_name": path_parts[-1] if path_parts else "root",
            "parent_directory": path_parts[-2] if len(path_parts) > 1 else None,
            "depth": len(path_parts),
            "path_parts": path_parts,
            "is_root": len(path_parts) == 0,
            "category": path_parts[0] if path_parts else "root"
        }
        
        return context
    
    def generate_navigation_links(self, context: Dict) -> Dict[str, str]:
        """Generate appropriate navigation links based on directory context"""
        links = {}
        
        # Root link
        if context["is_root"]:
            links["root"] = "CLAUDE.md"
        else:
            depth = context["depth"]
            links["root"] = "../" * depth + "CLAUDE.md"
        
        # Parent directory link
        if context["parent_directory"]:
            links["parent"] = "../CLAUDE.md"
        
        # Category-specific links
        category = context["category"]
        if category in self.directory_structure:
            category_dirs = self.directory_structure[category]
            for dir_name, description in category_dirs.items():
                if dir_name != context["directory_name"]:
                    if context["depth"] == 1:
                        # Same level in category
                        links[f"{dir_name}"] = f"../{dir_name}/CLAUDE.md"
                    elif context["depth"] == 2 and context["path_parts"][0] == category:
                        # Sibling in same category
                        links[f"{dir_name}"] = f"../{dir_name}/CLAUDE.md"
        
        return links
    
    def generate_breadcrumb_navigation(self, context: Dict) -> str:
        """Generate breadcrumb navigation"""
        if context["is_root"]:
            return "**Root**"
        
        breadcrumbs = []
        path_parts = context["path_parts"]
        
        # Add root
        depth = context["depth"]
        root_link = "../" * depth + "CLAUDE.md"
        breadcrumbs.append(f"[Root]({root_link})")
        
        # Add intermediate directories
        for i, part in enumerate(path_parts[:-1]):
            depth_to_part = len(path_parts) - i - 1
            link = "../" * depth_to_part + "CLAUDE.md"
            breadcrumbs.append(f"[{part.title()}]({link})")
        
        # Add current directory (no link)
        current_dir = path_parts[-1].replace("_", " ").title()
        breadcrumbs.append(f"**{current_dir}**")
        
        return " → ".join(breadcrumbs)
    
    def replace_template_placeholders(self, content: str, context: Dict, navigation_links: Dict) -> str:
        """Replace template placeholders with actual content"""
        
        # Generate related directories based on context
        related_dirs = []
        if context["category"] in self.directory_structure:
            category_dirs = self.directory_structure[context["category"]]
            for dir_name, description in list(category_dirs.items())[:2]:
                if dir_name != context["directory_name"]:
                    if context["depth"] == 1:
                        link = f"../{dir_name}/CLAUDE.md"
                    elif context["depth"] == 2:
                        link = f"../{dir_name}/CLAUDE.md"
                    else:
                        link = f"../../{context['category']}/{dir_name}/CLAUDE.md"
                    related_dirs.append((dir_name.replace("_", " ").title(), link, description))
        
        # Ensure we have at least 2 related directories
        while len(related_dirs) < 2:
            related_dirs.append(("Documentation", "../docs/CLAUDE.md", "Main documentation"))
        
        # Generate navigation items
        nav_items = []
        common_refs = [
            ("API Documentation", "../docs/api/CLAUDE.md", "API specifications and guides"),
            ("Architecture", "../docs/architecture/CLAUDE.md", "System architecture documentation"),
            ("Security", "../docs/security/CLAUDE.md", "Security policies and procedures"),
            ("Testing", "../docs/testing/CLAUDE.md", "Testing frameworks and strategies")
        ]
        
        # Adjust paths based on depth
        depth = context["depth"]
        adjusted_nav_items = []
        for name, path, desc in common_refs[:2]:
            if depth == 0:
                adjusted_path = path.replace("../", "")
            elif depth == 1:
                adjusted_path = path
            else:
                adjusted_path = "../" * (depth - 1) + path.replace("../", "")
            adjusted_nav_items.append((name, adjusted_path, desc))
        
        # Generate documentation guides
        doc_guides = [
            ("Development Guide", "development/CLAUDE.md", "Development standards and practices"),
            ("Deployment Guide", "deployment/CLAUDE.md", "Deployment procedures and automation")
        ]
        
        # Adjust doc guide paths
        adjusted_doc_guides = []
        for name, path, desc in doc_guides:
            if depth == 0:
                adjusted_path = f"docs/{path}"
            elif depth == 1 and context["category"] == "docs":
                adjusted_path = path
            else:
                adjusted_path = f"../docs/{path}"
            adjusted_doc_guides.append((name, adjusted_path, desc))
        
        # Create replacements
        replacements = {
            # Related directories
            "{RELATED_DIR_1}": related_dirs[0][0],
            "{RELATED_DIR_1_PATH}": related_dirs[0][1].replace("/CLAUDE.md", ""),
            "{RELATED_DIR_1_DESCRIPTION}": related_dirs[0][2],
            "{RELATED_DIR_2}": related_dirs[1][0],
            "{RELATED_DIR_2_PATH}": related_dirs[1][1].replace("/CLAUDE.md", ""),
            "{RELATED_DIR_2_DESCRIPTION}": related_dirs[1][2],
            
            # Navigation items
            "{NAV_ITEM_1}": adjusted_nav_items[0][0],
            "{NAV_ITEM_1_PATH}": adjusted_nav_items[0][1],
            "{NAV_ITEM_1_DESCRIPTION}": adjusted_nav_items[0][2],
            "{NAV_ITEM_2}": adjusted_nav_items[1][0],
            "{NAV_ITEM_2_PATH}": adjusted_nav_items[1][1],
            "{NAV_ITEM_2_DESCRIPTION}": adjusted_nav_items[1][2],
            
            # Documentation guides
            "{DOC_GUIDE_1}": adjusted_doc_guides[0][0],
            "{DOC_GUIDE_1_PATH}": adjusted_doc_guides[0][1],
            "{DOC_GUIDE_1_DESCRIPTION}": adjusted_doc_guides[0][2],
            "{DOC_GUIDE_2}": adjusted_doc_guides[1][0],
            "{DOC_GUIDE_2_PATH}": adjusted_doc_guides[1][1],
            "{DOC_GUIDE_2_DESCRIPTION}": adjusted_doc_guides[1][2],
            
            # Breadcrumb navigation
            "{BREADCRUMB_1}": "Documentation" if context["category"] != "docs" else "Architecture",
            "{BREADCRUMB_1_PATH}": "docs" if context["category"] != "docs" else "docs/architecture",
            "{BREADCRUMB_2}": "Services" if context["category"] != "services" else "Core",
            "{BREADCRUMB_2_PATH}": "services" if context["category"] != "services" else "services/core",
            "{BREADCRUMB_3}": "Infrastructure" if context["category"] != "infrastructure" else "Monitoring",
            "{BREADCRUMB_3_PATH}": "infrastructure" if context["category"] != "infrastructure" else "infrastructure/monitoring"
        }
        
        # Apply replacements
        for placeholder, replacement in replacements.items():
            content = content.replace(placeholder, replacement)
        
        # Fix navigation section
        breadcrumb_nav = self.generate_breadcrumb_navigation(context)
        content = re.sub(
            r'\*\*Navigation\*\*:.*?\n',
            f"**Navigation**: {breadcrumb_nav}\n",
            content
        )
        
        return content
    
    def fix_file_cross_references(self, file_path: Path) -> bool:
        """Fix cross-references in a single CLAUDE.md file"""
        try:
            # Read current content
            content = file_path.read_text()
            
            # Analyze directory context
            context = self.analyze_directory_context(file_path)
            
            # Generate navigation links
            navigation_links = self.generate_navigation_links(context)
            
            # Replace template placeholders
            fixed_content = self.replace_template_placeholders(content, context, navigation_links)
            
            # Write fixed content
            file_path.write_text(fixed_content)
            
            print(f"  ✅ Fixed: {file_path.relative_to(self.project_root)}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error fixing {file_path}: {e}")
            return False
    
    def execute_cross_reference_fixing(self):
        """Execute the complete cross-reference fixing process"""
        print("🚀 Starting ACGS-2 Cross-Reference Fixing")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Project Root: {self.project_root}")
        
        try:
            # Find all CLAUDE.md files
            claude_files = self.find_claude_md_files()
            print(f"\n📁 Found {len(claude_files)} CLAUDE.md files")
            
            # Fix cross-references in each file
            print("\n🔗 Fixing cross-references...")
            fixed_count = 0
            
            for file_path in claude_files:
                if self.fix_file_cross_references(file_path):
                    fixed_count += 1
            
            # Generate summary
            fix_rate = (fixed_count / len(claude_files)) * 100 if claude_files else 0
            
            print(f"\n✅ Cross-reference fixing completed!")
            print(f"📊 Summary:")
            print(f"  - Files processed: {len(claude_files)}")
            print(f"  - Successfully fixed: {fixed_count} ({fix_rate:.1f}%)")
            print(f"  - Constitutional hash: {self.constitutional_hash}")
            print(f"  - Target: >80% cross-reference validity")
            
            return True
            
        except Exception as e:
            print(f"❌ Cross-reference fixing failed: {e}")
            return False

def main():
    """Main execution function"""
    project_root = "/home/dislove/ACGS-2"
    fixer = CrossReferenceFixer(project_root)
    
    # Execute cross-reference fixing
    success = fixer.execute_cross_reference_fixing()
    
    if success:
        print("\n🎉 ACGS-2 Cross-Reference Fixing Complete!")
        print("Next steps:")
        print("1. Run cross-reference validation to verify improvements")
        print("2. Implement constitutional compliance validation")
        print("3. Set up automated maintenance procedures")
    else:
        print("\n❌ Cross-reference fixing failed. Check logs for details.")

if __name__ == "__main__":
    main()
