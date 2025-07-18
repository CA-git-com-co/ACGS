#!/usr/bin/env python3
"""
ACGS-2 Constitutional Hash Deployment Tool
Constitutional Hash: cdd01ef066bc6cf2

This tool systematically deploys the constitutional hash to all documentation files
to achieve 80% constitutional compliance target within the ACGS-2 repository.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Set
import subprocess
import time

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
HASH_COMMENT = f"<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->"

class ConstitutionalHashDeployer:
    """Deploy constitutional hash to documentation files."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.hash_comment = HASH_COMMENT
        
        # File patterns to include
        self.include_patterns = [
            "**/*.md",
            "**/*.rst", 
            "**/*.txt"
        ]
        
        # Exclude patterns to avoid (refined for enhanced compliance)
        self.exclude_patterns = [
            "**/node_modules/**",
            "**/venv/**",
            "**/.venv/**",
            "**/target/**",
            "**/.git/**",
            "**/build/**",
            "**/dist/**",
            "**/vendor/**",
            "**/__pycache__/**",
            "**/site-packages/**",
            "**/dist-info/**",
            "**/egg-info/**",
            # Exclude specific third-party cache files but allow ACGS-2 README files
            "**/.pytest_cache/**/CACHEDIR.TAG",
            "**/.pytest_cache/**/v/**",
            # Exclude specific virtual environment patterns
            "**/lib/python*/site-packages/**",
            "**/include/python*/**",
            "**/bin/activate*",
            "**/pyvenv.cfg"
        ]
        
        # Priority file categories
        self.critical_files = [
            "README.md",
            "TECHNICAL_SPECIFICATIONS_2025.md",
            "ACGS_XAI_INTEGRATION_GUIDE.md",
            "claude.md"
        ]
        
        self.high_priority_dirs = [
            ".claude/commands",
            "services",
            "docs",
            "config",
            "infrastructure",
            "tools",
            "scripts",
            "reports",
            "reorganization-tools",
            "database"
        ]

        # Additional file categories for enhanced compliance
        self.enhanced_compliance_files = [
            "CHANGELOG.md",
            "CODE_OF_CONDUCT.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "config/environments/requirements.txt",
            "requirements_dev.txt"
        ]

    def find_documentation_files(self) -> List[Path]:
        """Find all documentation files in the project."""
        files = []
        for pattern in self.include_patterns:
            for file_path in self.project_root.rglob(pattern):
                # Check if file should be excluded
                should_exclude = False
                for exclude_pattern in self.exclude_patterns:
                    if file_path.match(exclude_pattern):
                        should_exclude = True
                        break
                
                if not should_exclude and file_path.is_file():
                    files.append(file_path)
        
        return sorted(files)

    def check_constitutional_compliance(self, file_path: Path) -> bool:
        """Check if file contains constitutional hash."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            return self.constitutional_hash in content
        except Exception:
            return False

    def add_constitutional_hash(self, file_path: Path, dry_run: bool = False) -> bool:
        """Add constitutional hash to file if missing."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Skip if already has hash
            if self.constitutional_hash in content:
                return True
            
            # Determine insertion strategy based on file type
            lines = content.split('\n')
            
            # For markdown files, add after any existing front matter
            if file_path.suffix.lower() == '.md':
                insert_line = 0
                
                # Check for YAML front matter
                if lines and lines[0].strip() == '---':
                    for i, line in enumerate(lines[1:], 1):
                        if line.strip() == '---':
                            insert_line = i + 1
                            break
                
                # Insert hash comment
                if insert_line < len(lines):
                    lines.insert(insert_line, '')
                    lines.insert(insert_line, self.hash_comment)
                else:
                    lines.insert(0, self.hash_comment)
                    lines.insert(1, '')
            
            # For other file types, add at the beginning
            else:
                lines.insert(0, self.hash_comment)
                lines.insert(1, '')
            
            new_content = '\n'.join(lines)
            
            if not dry_run:
                file_path.write_text(new_content, encoding='utf-8')
                print(f"✅ Added hash to: {file_path.relative_to(self.project_root)}")
            else:
                print(f"🔍 Would add hash to: {file_path.relative_to(self.project_root)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False

    def categorize_files(self, files: List[Path]) -> Tuple[List[Path], List[Path], List[Path]]:
        """Categorize files by priority."""
        critical = []
        high_priority = []
        standard = []
        
        for file_path in files:
            file_str = str(file_path)
            file_name = file_path.name

            # Check if critical file
            if any(cf in file_str for cf in self.critical_files):
                critical.append(file_path)
            # Check if enhanced compliance file (specific filenames)
            elif any(ecf == file_name for ecf in self.enhanced_compliance_files):
                high_priority.append(file_path)
            # Check if in high priority directory
            elif any(hpd in file_str for hpd in self.high_priority_dirs):
                high_priority.append(file_path)
            else:
                standard.append(file_path)
        
        return critical, high_priority, standard

    def deploy_constitutional_hash(self, dry_run: bool = False, target_compliance: float = 80.0) -> Tuple[float, int, int]:
        """Deploy constitutional hash to achieve target compliance."""
        print(f"🔍 ACGS-2 Constitutional Hash Deployment")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Target Compliance: {target_compliance}%")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE DEPLOYMENT'}")
        print("=" * 60)
        
        # Find all documentation files
        files = self.find_documentation_files()
        print(f"📁 Found {len(files)} documentation files")
        
        # Check current compliance
        compliant_files = 0
        for file_path in files:
            if self.check_constitutional_compliance(file_path):
                compliant_files += 1
        
        initial_compliance = (compliant_files / len(files) * 100) if files else 0
        print(f"📊 Current compliance: {initial_compliance:.1f}% ({compliant_files}/{len(files)})")
        
        # Categorize files by priority
        critical, high_priority, standard = self.categorize_files(files)
        print(f"📋 File categories:")
        print(f"   Critical: {len(critical)} files")
        print(f"   High Priority: {len(high_priority)} files") 
        print(f"   Standard: {len(standard)} files")
        
        # Deploy hash by priority
        files_updated = 0
        
        # Phase 1: Critical files
        print(f"\n🔴 Phase 1: Processing critical files...")
        for file_path in critical:
            if not self.check_constitutional_compliance(file_path):
                if self.add_constitutional_hash(file_path, dry_run):
                    files_updated += 1
        
        # Phase 2: High priority files
        print(f"\n🟡 Phase 2: Processing high priority files...")
        for file_path in high_priority:
            if not self.check_constitutional_compliance(file_path):
                if self.add_constitutional_hash(file_path, dry_run):
                    files_updated += 1
        
        # Phase 3: Standard files (if needed to reach target)
        current_compliant = compliant_files + files_updated
        current_compliance = (current_compliant / len(files) * 100) if files else 0
        
        if current_compliance < target_compliance:
            print(f"\n🟢 Phase 3: Processing standard files to reach {target_compliance}% target...")
            files_needed = int((target_compliance / 100 * len(files)) - current_compliant)
            
            processed = 0
            for file_path in standard:
                if processed >= files_needed:
                    break
                    
                if not self.check_constitutional_compliance(file_path):
                    if self.add_constitutional_hash(file_path, dry_run):
                        files_updated += 1
                        processed += 1
        
        # Calculate final compliance
        final_compliant = compliant_files + files_updated
        final_compliance = (final_compliant / len(files) * 100) if files else 0
        
        print(f"\n" + "=" * 60)
        print(f"📊 DEPLOYMENT SUMMARY")
        print(f"=" * 60)
        print(f"Initial Compliance: {initial_compliance:.1f}% ({compliant_files}/{len(files)})")
        print(f"Files Updated: {files_updated}")
        print(f"Final Compliance: {final_compliance:.1f}% ({final_compliant}/{len(files)})")
        print(f"Target Achieved: {'✅ YES' if final_compliance >= target_compliance else '❌ NO'}")
        
        return final_compliance, files_updated, len(files)

    def validate_deployment(self) -> Tuple[float, List[str]]:
        """Validate constitutional hash deployment."""
        files = self.find_documentation_files()
        compliant_files = 0
        non_compliant = []
        
        for file_path in files:
            if self.check_constitutional_compliance(file_path):
                compliant_files += 1
            else:
                non_compliant.append(str(file_path.relative_to(self.project_root)))
        
        compliance_rate = (compliant_files / len(files) * 100) if files else 0
        return compliance_rate, non_compliant

def main():
    """Main deployment function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy constitutional hash to ACGS-2 documentation')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--target', type=float, default=80.0, help='Target compliance percentage (default: 80.0)')
    parser.add_argument('--validate', action='store_true', help='Validate current deployment status')
    
    args = parser.parse_args()
    
    deployer = ConstitutionalHashDeployer()
    
    if args.validate:
        print("🔍 Validating constitutional hash deployment...")
        compliance, non_compliant = deployer.validate_deployment()
        print(f"📊 Current compliance: {compliance:.1f}%")
        
        if non_compliant:
            print(f"📋 Non-compliant files ({len(non_compliant)}):")
            for file_path in non_compliant[:20]:  # Show first 20
                print(f"   - {file_path}")
            if len(non_compliant) > 20:
                print(f"   ... and {len(non_compliant) - 20} more")
        
        return 0 if compliance >= args.target else 1
    
    # Deploy constitutional hash
    final_compliance, files_updated, total_files = deployer.deploy_constitutional_hash(
        dry_run=args.dry_run,
        target_compliance=args.target
    )
    
    # Return success if target achieved
    return 0 if final_compliance >= args.target else 1

if __name__ == "__main__":
    sys.exit(main())
