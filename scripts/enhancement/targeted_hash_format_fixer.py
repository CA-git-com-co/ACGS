#!/usr/bin/env python3
"""
ACGS-2 Targeted Hash Format Fixer for PARTIAL Files
Constitutional Hash: cdd01ef066bc6cf2

Phase 8B: Targeted Hash Format Optimization
This script specifically targets the hash validation issue in PARTIAL files by:
- Adding HTML comment format for constitutional hash
- Ensuring proper hash validation compliance
- Converting PARTIAL files to GOOD status through targeted fixes

Target: Convert 200+ PARTIAL files to GOOD status by fixing hash format issues
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class TargetedHashFormatFixer:
    """Targeted fixer for hash format issues in PARTIAL files"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Track optimization statistics
        self.files_processed = 0
        self.files_fixed = 0
        self.partial_files_found = 0

    def load_partial_compliance_files(self) -> List[Dict]:
        """Load PARTIAL compliance files from latest report"""
        try:
            # Find the most recent compliance report
            reports_dir = self.project_root / "reports"
            compliance_reports = list(reports_dir.glob("constitutional_compliance_report_*.json"))
            
            if not compliance_reports:
                print("❌ No compliance reports found")
                return []
            
            latest_report = max(compliance_reports, key=lambda x: x.stat().st_mtime)
            print(f"📊 Loading PARTIAL compliance data from: {latest_report.name}")
            
            with open(latest_report, 'r') as f:
                report_data = json.load(f)
            
            partial_files = []
            for result in report_data.get("detailed_results", []):
                if result.get("compliance_level") == "PARTIAL":
                    partial_files.append(result)
            
            self.partial_files_found = len(partial_files)
            print(f"🎯 Found {self.partial_files_found} PARTIAL compliance files")
            
            return partial_files
            
        except Exception as e:
            print(f"❌ Error loading compliance data: {e}")
            return []

    def needs_hash_format_fix(self, file_data: Dict) -> bool:
        """Check if file needs hash format fix"""
        hash_validation = file_data.get("hash_validation", {})
        
        # Check if hash is present but comment format is missing
        has_hash = hash_validation.get("has_hash", False)
        has_comment_format = hash_validation.get("has_comment_format", False)
        
        return has_hash and not has_comment_format

    def fix_hash_format(self, content: str, file_path: str) -> str:
        """Add HTML comment format for constitutional hash"""
        
        # Check if HTML comment format already exists
        if re.search(r'<!--.*Constitutional Hash.*cdd01ef066bc6cf2.*-->', content, re.IGNORECASE):
            return content
        
        # Add HTML comment at the beginning of the file
        comment_line = f"<!-- Constitutional Hash: {self.constitutional_hash} -->\n"
        
        # If file starts with a heading, insert comment before it
        if content.strip().startswith('#'):
            return comment_line + content
        else:
            # Insert at the very beginning
            return comment_line + content

    def fix_partial_file(self, file_data: Dict) -> bool:
        """Fix hash format issue in a PARTIAL file"""
        try:
            file_path = file_data.get("file_path", "")
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                print(f"⚠️  File not found: {file_path}")
                return False
            
            # Skip archive and backup files
            if any(skip in file_path for skip in ["docs_consolidated_archive_", "docs_backup_", ".backup"]):
                print(f"⚠️  Skipping: {file_path} (archive/backup file)")
                return False
            
            # Check if this file needs hash format fix
            if not self.needs_hash_format_fix(file_data):
                print(f"⚠️  No hash format fix needed: {file_path}")
                return False
            
            # Read current content
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            original_content = content
            
            # Apply hash format fix
            fixed_content = self.fix_hash_format(content, file_path)
            
            # Check if fix was applied
            if fixed_content != original_content:
                # Backup original
                backup_path = full_path.with_suffix(full_path.suffix + '.backup')
                backup_path.write_text(original_content, encoding='utf-8')
                
                # Write fixed content
                full_path.write_text(fixed_content, encoding='utf-8')
                
                print(f"✅ Fixed hash format: {file_path}")
                return True
            else:
                print(f"⚠️  No changes needed: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error fixing {file_data.get('file_path', 'unknown')}: {e}")
            return False

    def run_targeted_hash_fix(self) -> Dict:
        """Execute targeted hash format fixing campaign"""
        print("🚀 Starting Phase 8B: Targeted Hash Format Fixing for PARTIAL Files")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print("Target: Fix hash format issues to convert PARTIAL files to GOOD status")
        
        # Load PARTIAL files
        partial_files = self.load_partial_compliance_files()
        if not partial_files:
            return {"success": False, "error": "No PARTIAL files found"}
        
        # Filter files that need hash format fixes
        files_needing_fix = [f for f in partial_files if self.needs_hash_format_fix(f)]
        
        print(f"🔧 Found {len(files_needing_fix)} files needing hash format fixes...")
        
        # Process each file that needs fixing
        for i, file_data in enumerate(files_needing_fix, 1):
            file_path = file_data.get("file_path", "")
            
            print(f"\n[{i}/{len(files_needing_fix)}] Processing: {file_path}")
            
            if self.fix_partial_file(file_data):
                self.files_fixed += 1
            
            self.files_processed += 1
            
            # Progress indicator
            if i % 25 == 0:
                progress = (i / len(files_needing_fix)) * 100
                success_rate = (self.files_fixed / self.files_processed) * 100
                print(f"  📊 Progress: {progress:.1f}% ({i}/{len(files_needing_fix)} files, {success_rate:.1f}% success rate)")
        
        # Calculate final results
        success_rate = (self.files_fixed / self.files_processed) * 100 if self.files_processed > 0 else 0
        target_met = self.files_fixed >= 200
        
        # Generate report
        report = {
            "phase": "Phase 8B: Targeted Hash Format Fixing",
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "partial_files_found": self.partial_files_found,
            "files_needing_fix": len(files_needing_fix),
            "files_processed": self.files_processed,
            "files_fixed": self.files_fixed,
            "success_rate": success_rate,
            "target_met": target_met,
            "target_threshold": 200
        }
        
        # Save report
        report_path = self.project_root / f"reports/phase8b_hash_format_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Phase 8B Hash Format Fixing Complete!")
        print(f"📊 Results:")
        print(f"  - PARTIAL files found: {self.partial_files_found}")
        print(f"  - Files needing fix: {len(files_needing_fix)}")
        print(f"  - Files processed: {self.files_processed}")
        print(f"  - Files fixed: {self.files_fixed}")
        print(f"  - Success rate: {success_rate:.1f}%")
        print(f"  - Target (200+ files): {'✅ MET' if target_met else '❌ NOT MET'}")
        print(f"  - Constitutional hash: {self.constitutional_hash}")
        print(f"📄 Fix report saved: {report_path}")
        
        return report

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ACGS-2 Targeted Hash Format Fixer")
    parser.add_argument("--project-root", required=True, help="Project root directory")
    parser.add_argument("--constitutional-hash", default="cdd01ef066bc6cf2", help="Constitutional hash")
    
    args = parser.parse_args()
    
    fixer = TargetedHashFormatFixer(args.project_root)
    result = fixer.run_targeted_hash_fix()
    
    if result.get("files_fixed", 0) > 0:
        print(f"\n🎉 Phase 8B: Targeted Hash Format Fixing Complete!")
        print(f"✅ {result.get('files_fixed', 0)} files fixed successfully!")
        print("\n🔄 Recommend running compliance validation to verify improvements.")
    else:
        print(f"\n🔄 Phase 8B completed with {result.get('files_fixed', 0)} files fixed.")
        print("📊 Review fix report for detailed analysis.")
