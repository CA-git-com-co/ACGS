#!/usr/bin/env python3
"""
Comprehensive Documentation Validation Script
Constitutional Hash: cdd01ef066bc6cf2

This script provides comprehensive validation of ACGS-2 documentation including:
- CLAUDE.md file structure validation
- Cross-reference validation
- Constitutional compliance checking
- Documentation quality metrics
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

class DocumentationValidator:
    """Comprehensive documentation validator for ACGS-2"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.results = {
            "claude_md_validation": {},
            "cross_reference_validation": {},
            "constitutional_compliance": {},
            "quality_metrics": {},
            "overall_status": "unknown"
        }
    
    def validate_claude_md_files(self) -> bool:
        """Validate CLAUDE.md file structure and content"""
        print("🔍 Validating CLAUDE.md files...")
        
        try:
            # Run the CLAUDE.md validator
            result = subprocess.run([
                sys.executable, 
                str(self.project_root / "claude_md_validator.py"),
                str(self.project_root)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ CLAUDE.md validation passed")
                self.results["claude_md_validation"]["status"] = "passed"
                
                # Extract metrics from output
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if "files valid" in line:
                        self.results["claude_md_validation"]["summary"] = line.strip()
                        break
                
                return True
            else:
                print(f"❌ CLAUDE.md validation failed: {result.stderr}")
                self.results["claude_md_validation"]["status"] = "failed"
                self.results["claude_md_validation"]["error"] = result.stderr
                return False
                
        except Exception as e:
            print(f"❌ Error running CLAUDE.md validation: {e}")
            self.results["claude_md_validation"]["status"] = "error"
            self.results["claude_md_validation"]["error"] = str(e)
            return False
    
    def validate_cross_references(self) -> bool:
        """Validate cross-references between documentation files"""
        print("🔗 Validating cross-references...")
        
        try:
            # Run the cross-reference validator
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "claude_md_cross_reference_validator.py"),
                str(self.project_root)
            ], capture_output=True, text=True, timeout=300)
            
            # Extract link validity percentage
            output_lines = result.stdout.split('\n')
            link_validity = None
            
            for line in output_lines:
                if "Link validity:" in line:
                    # Extract percentage
                    parts = line.split("Link validity:")
                    if len(parts) > 1:
                        validity_part = parts[1].strip()
                        if "%" in validity_part:
                            link_validity = float(validity_part.split("%")[0].strip().split("(")[0])
                            break
            
            if link_validity is not None:
                self.results["cross_reference_validation"]["link_validity"] = link_validity
                
                # Set threshold (60% for now, targeting 80%)
                threshold = 60.0
                if link_validity >= threshold:
                    print(f"✅ Cross-reference validation passed: {link_validity}% >= {threshold}%")
                    self.results["cross_reference_validation"]["status"] = "passed"
                    return True
                else:
                    print(f"❌ Cross-reference validation failed: {link_validity}% < {threshold}%")
                    self.results["cross_reference_validation"]["status"] = "failed"
                    return False
            else:
                print("❌ Could not extract link validity percentage")
                self.results["cross_reference_validation"]["status"] = "error"
                return False
                
        except Exception as e:
            print(f"❌ Error running cross-reference validation: {e}")
            self.results["cross_reference_validation"]["status"] = "error"
            self.results["cross_reference_validation"]["error"] = str(e)
            return False
    
    def validate_constitutional_compliance(self) -> bool:
        """Validate constitutional compliance across documentation"""
        print("🏛️ Validating constitutional compliance...")
        
        try:
            # Find all markdown files
            md_files = list(self.project_root.rglob("*.md"))
            
            # Filter out excluded directories
            excluded_dirs = {'.venv', '__pycache__', '.git', 'node_modules'}
            md_files = [f for f in md_files if not any(excluded in str(f) for excluded in excluded_dirs)]
            
            total_files = len(md_files)
            compliant_files = 0
            
            for md_file in md_files:
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if self.constitutional_hash in content:
                            compliant_files += 1
                except Exception:
                    continue
            
            compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 0
            
            self.results["constitutional_compliance"]["total_files"] = total_files
            self.results["constitutional_compliance"]["compliant_files"] = compliant_files
            self.results["constitutional_compliance"]["compliance_rate"] = compliance_rate
            
            # Target 80% compliance
            target_compliance = 80.0
            if compliance_rate >= target_compliance:
                print(f"✅ Constitutional compliance passed: {compliance_rate:.1f}% >= {target_compliance}%")
                self.results["constitutional_compliance"]["status"] = "passed"
                return True
            else:
                print(f"❌ Constitutional compliance failed: {compliance_rate:.1f}% < {target_compliance}%")
                self.results["constitutional_compliance"]["status"] = "failed"
                return False
                
        except Exception as e:
            print(f"❌ Error validating constitutional compliance: {e}")
            self.results["constitutional_compliance"]["status"] = "error"
            self.results["constitutional_compliance"]["error"] = str(e)
            return False
    
    def generate_quality_metrics(self) -> Dict:
        """Generate documentation quality metrics"""
        print("📊 Generating quality metrics...")
        
        try:
            # Count CLAUDE.md files
            claude_files = list(self.project_root.rglob("CLAUDE.md"))
            claude_files = [f for f in claude_files if not any(excluded in str(f) for excluded in {'.venv', '__pycache__', '.git', 'node_modules'})]
            
            # Count total markdown files
            md_files = list(self.project_root.rglob("*.md"))
            md_files = [f for f in md_files if not any(excluded in str(f) for excluded in {'.venv', '__pycache__', '.git', 'node_modules'})]
            
            # Count directories
            all_dirs = [d for d in self.project_root.rglob("*") if d.is_dir()]
            all_dirs = [d for d in all_dirs if not any(excluded in str(d) for excluded in {'.venv', '__pycache__', '.git', 'node_modules'})]
            
            metrics = {
                "claude_md_files": len(claude_files),
                "total_md_files": len(md_files),
                "total_directories": len(all_dirs),
                "documentation_coverage": (len(claude_files) / len(all_dirs) * 100) if all_dirs else 0
            }
            
            self.results["quality_metrics"] = metrics
            
            print(f"📈 Quality Metrics:")
            print(f"   - CLAUDE.md files: {metrics['claude_md_files']}")
            print(f"   - Total markdown files: {metrics['total_md_files']}")
            print(f"   - Documentation coverage: {metrics['documentation_coverage']:.1f}%")
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error generating quality metrics: {e}")
            self.results["quality_metrics"]["error"] = str(e)
            return {}
    
    def run_full_validation(self) -> bool:
        """Run complete validation suite"""
        print("🚀 Starting comprehensive documentation validation...")
        print(f"📁 Project root: {self.project_root}")
        print(f"🏛️ Constitutional hash: {self.constitutional_hash}")
        print("=" * 60)
        
        # Run all validations
        claude_md_valid = self.validate_claude_md_files()
        cross_ref_valid = self.validate_cross_references()
        constitutional_valid = self.validate_constitutional_compliance()
        self.generate_quality_metrics()
        
        # Determine overall status
        all_passed = claude_md_valid and cross_ref_valid and constitutional_valid
        
        if all_passed:
            self.results["overall_status"] = "passed"
            print("\n✅ All documentation validation checks passed!")
        else:
            self.results["overall_status"] = "failed"
            print("\n❌ Some documentation validation checks failed!")
        
        # Save results
        results_file = self.project_root / "documentation_validation_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Results saved to: {results_file}")
        
        return all_passed

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="ACGS-2 Documentation Validation")
    parser.add_argument("project_root", help="Path to project root directory")
    parser.add_argument("--claude-md-only", action="store_true", help="Only validate CLAUDE.md files")
    parser.add_argument("--cross-ref-only", action="store_true", help="Only validate cross-references")
    parser.add_argument("--constitutional-only", action="store_true", help="Only validate constitutional compliance")
    
    args = parser.parse_args()
    
    validator = DocumentationValidator(args.project_root)
    
    if args.claude_md_only:
        success = validator.validate_claude_md_files()
    elif args.cross_ref_only:
        success = validator.validate_cross_references()
    elif args.constitutional_only:
        success = validator.validate_constitutional_compliance()
    else:
        success = validator.run_full_validation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
