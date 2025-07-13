#!/usr/bin/env python3
"""
ACGS-2 Comprehensive Documentation Validation Tool
Constitutional Hash: cdd01ef066bc6cf2

This tool provides comprehensive validation of ACGS-2 documentation including:
- Constitutional compliance validation
- Broken link detection and repair
- Documentation quality assessment
- Performance metrics validation
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class DocumentationValidator:
    """Comprehensive documentation validation for ACGS-2."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Required critical files
        self.critical_files = [
            "docs/README.md",
            "docs/TECHNICAL_SPECIFICATIONS_2025.md", 
            "docs/integration/ACGS_XAI_INTEGRATION_GUIDE.md",
            "services/claude.md",
            "docs/api/claude.md",
            "infrastructure/claude.md",
            "config/claude.md",
            "tools/claude.md",
            "docs/architecture/claude.md",
            "docs/deployment/claude.md",
            "docs/security/claude.md",
            "docs/research/claude.md",
            "docs/training/claude.md"
        ]
        
        # Performance targets (enhanced for improved compliance)
        self.performance_targets = {
            "constitutional_compliance": 85.0,  # Enhanced minimum 85% compliance
            "broken_links_threshold": 100,     # Maximum 100 broken links
            "critical_files_coverage": 100.0,  # 100% critical files must exist
            "hash_coverage": 100.0             # 100% critical files must have hash
        }

    def validate_constitutional_compliance(self) -> Dict[str, any]:
        """Validate constitutional compliance using deployment tool."""
        print(f"🔍 Validating Constitutional Compliance")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print("-" * 50)
        
        result = {
            "status": "unknown",
            "compliance_rate": 0.0,
            "target_met": False,
            "details": {},
            "recommendations": []
        }
        
        try:
            # Check if deployment tool exists
            deploy_tool = self.project_root / "deploy_constitutional_hash.py"
            if not deploy_tool.exists():
                result["status"] = "error"
                result["details"]["error"] = "Constitutional hash deployment tool not found"
                result["recommendations"].append("Create deploy_constitutional_hash.py tool")
                return result
            
            # Run validation
            cmd = ["python3", str(deploy_tool), "--validate"]
            process = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if process.returncode == 0:
                output = process.stdout
                
                # Extract compliance rate
                for line in output.split('\n'):
                    if "Current compliance:" in line:
                        # Extract percentage
                        import re
                        match = re.search(r'(\d+\.?\d*)%', line)
                        if match:
                            result["compliance_rate"] = float(match.group(1))
                            break
                
                # Check if target met
                target = self.performance_targets["constitutional_compliance"]
                result["target_met"] = result["compliance_rate"] >= target
                result["status"] = "success" if result["target_met"] else "warning"
                
                result["details"]["output"] = output
                result["details"]["target"] = target
                
                if not result["target_met"]:
                    result["recommendations"].append(
                        f"Run: python3 deploy_constitutional_hash.py --target {target}"
                    )
                
                print(f"✅ Compliance Rate: {result['compliance_rate']:.1f}% (Target: {target}%)")
                
            else:
                result["status"] = "error"
                result["details"]["error"] = process.stderr
                result["recommendations"].append("Fix constitutional hash deployment tool errors")
                print(f"❌ Validation failed: {process.stderr}")
                
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            result["recommendations"].append("Check constitutional hash deployment tool")
            print(f"❌ Exception during validation: {e}")
        
        return result

    def validate_broken_links(self) -> Dict[str, any]:
        """Validate broken links using link checker tool."""
        print(f"\n🔗 Validating Internal Links")
        print("-" * 50)
        
        result = {
            "status": "unknown",
            "broken_count": 0,
            "threshold_met": False,
            "details": {},
            "recommendations": []
        }
        
        try:
            # Check if link checker tool exists
            link_tool = self.project_root / "fix_broken_links.py"
            if not link_tool.exists():
                result["status"] = "error"
                result["details"]["error"] = "Broken links checker tool not found"
                result["recommendations"].append("Create fix_broken_links.py tool")
                return result
            
            # Run analysis
            cmd = ["python3", str(link_tool), "--analyze-only"]
            process = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if process.returncode == 0:
                output = process.stdout
                
                # Extract broken link count
                for line in output.split('\n'):
                    if "Broken links:" in line:
                        import re
                        match = re.search(r'Broken links: (\d+)', line)
                        if match:
                            result["broken_count"] = int(match.group(1))
                            break
                
                # Check if threshold met
                threshold = self.performance_targets["broken_links_threshold"]
                result["threshold_met"] = result["broken_count"] <= threshold
                result["status"] = "success" if result["threshold_met"] else "warning"
                
                result["details"]["output"] = output
                result["details"]["threshold"] = threshold
                
                if not result["threshold_met"]:
                    result["recommendations"].append(
                        "Run: python3 fix_broken_links.py --create-missing"
                    )
                
                print(f"✅ Broken Links: {result['broken_count']} (Threshold: {threshold})")
                
            else:
                result["status"] = "error"
                result["details"]["error"] = process.stderr
                result["recommendations"].append("Fix broken links checker tool errors")
                print(f"❌ Link validation failed: {process.stderr}")
                
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            result["recommendations"].append("Check broken links checker tool")
            print(f"❌ Exception during link validation: {e}")
        
        return result

    def validate_critical_files(self) -> Dict[str, any]:
        """Validate presence of critical documentation files."""
        print(f"\n📋 Validating Critical Files")
        print("-" * 50)
        
        result = {
            "status": "unknown",
            "files_present": 0,
            "files_total": len(self.critical_files),
            "coverage_rate": 0.0,
            "target_met": False,
            "missing_files": [],
            "details": {},
            "recommendations": []
        }
        
        try:
            missing_files = []
            
            for file_path in self.critical_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    result["files_present"] += 1
                    print(f"✅ Found: {file_path}")
                else:
                    missing_files.append(file_path)
                    print(f"❌ Missing: {file_path}")
            
            result["missing_files"] = missing_files
            result["coverage_rate"] = (result["files_present"] / result["files_total"]) * 100
            
            target = self.performance_targets["critical_files_coverage"]
            result["target_met"] = result["coverage_rate"] >= target
            result["status"] = "success" if result["target_met"] else "warning"
            
            result["details"]["target"] = target
            
            if not result["target_met"]:
                result["recommendations"].append("Create missing critical documentation files")
                for missing_file in missing_files:
                    result["recommendations"].append(f"Create: {missing_file}")
            
            print(f"✅ Coverage: {result['coverage_rate']:.1f}% ({result['files_present']}/{result['files_total']})")
            
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            result["recommendations"].append("Check critical files validation")
            print(f"❌ Exception during critical files validation: {e}")
        
        return result

    def validate_hash_coverage(self) -> Dict[str, any]:
        """Validate constitutional hash presence in critical files."""
        print(f"\n🔒 Validating Constitutional Hash Coverage")
        print("-" * 50)
        
        result = {
            "status": "unknown",
            "files_with_hash": 0,
            "files_checked": 0,
            "coverage_rate": 0.0,
            "target_met": False,
            "missing_hash_files": [],
            "details": {},
            "recommendations": []
        }
        
        try:
            missing_hash_files = []
            
            for file_path in self.critical_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    result["files_checked"] += 1
                    
                    try:
                        content = full_path.read_text(encoding='utf-8', errors='ignore')
                        if self.constitutional_hash in content:
                            result["files_with_hash"] += 1
                            print(f"✅ Hash found in: {file_path}")
                        else:
                            missing_hash_files.append(file_path)
                            print(f"❌ Hash missing in: {file_path}")
                    except Exception as e:
                        print(f"⚠️ Error reading {file_path}: {e}")
            
            result["missing_hash_files"] = missing_hash_files
            
            if result["files_checked"] > 0:
                result["coverage_rate"] = (result["files_with_hash"] / result["files_checked"]) * 100
            
            target = self.performance_targets["hash_coverage"]
            result["target_met"] = result["coverage_rate"] >= target
            result["status"] = "success" if result["target_met"] else "warning"
            
            result["details"]["target"] = target
            
            if not result["target_met"]:
                result["recommendations"].append("Add constitutional hash to missing files")
                for missing_file in missing_hash_files:
                    result["recommendations"].append(f"Add hash to: {missing_file}")
            
            print(f"✅ Hash Coverage: {result['coverage_rate']:.1f}% ({result['files_with_hash']}/{result['files_checked']})")
            
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
            result["recommendations"].append("Check constitutional hash coverage validation")
            print(f"❌ Exception during hash coverage validation: {e}")
        
        return result

    def generate_validation_report(self, results: Dict[str, Dict]) -> Dict[str, any]:
        """Generate comprehensive validation report."""
        print(f"\n📊 ACGS-2 Documentation Validation Report")
        print("=" * 60)
        
        # Calculate overall status
        all_success = all(result["status"] == "success" for result in results.values())
        has_warnings = any(result["status"] == "warning" for result in results.values())
        has_errors = any(result["status"] == "error" for result in results.values())
        
        if has_errors:
            overall_status = "error"
            status_icon = "❌"
        elif has_warnings:
            overall_status = "warning"
            status_icon = "⚠️"
        else:
            overall_status = "success"
            status_icon = "✅"
        
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "constitutional_hash": self.constitutional_hash,
            "overall_status": overall_status,
            "validation_results": results,
            "summary": {
                "constitutional_compliance": results.get("constitutional_compliance", {}).get("compliance_rate", 0),
                "broken_links": results.get("broken_links", {}).get("broken_count", 0),
                "critical_files_coverage": results.get("critical_files", {}).get("coverage_rate", 0),
                "hash_coverage": results.get("hash_coverage", {}).get("coverage_rate", 0)
            },
            "recommendations": []
        }
        
        # Collect all recommendations
        for result in results.values():
            report["recommendations"].extend(result.get("recommendations", []))
        
        # Print summary
        print(f"{status_icon} Overall Status: {overall_status.upper()}")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Validation Time: {report['timestamp']}")
        print("")
        print("Summary:")
        print(f"- Constitutional Compliance: {report['summary']['constitutional_compliance']:.1f}%")
        print(f"- Broken Links: {report['summary']['broken_links']}")
        print(f"- Critical Files Coverage: {report['summary']['critical_files_coverage']:.1f}%")
        print(f"- Hash Coverage: {report['summary']['hash_coverage']:.1f}%")
        
        if report["recommendations"]:
            print(f"\nRecommendations ({len(report['recommendations'])}):")
            for i, rec in enumerate(report["recommendations"][:10], 1):
                print(f"{i:2d}. {rec}")
            if len(report["recommendations"]) > 10:
                print(f"    ... and {len(report['recommendations']) - 10} more")
        
        return report

    def run_full_validation(self) -> Dict[str, any]:
        """Run complete documentation validation."""
        print(f"🔍 ACGS-2 Comprehensive Documentation Validation")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print("=" * 60)
        
        results = {}
        
        # Run all validations
        results["constitutional_compliance"] = self.validate_constitutional_compliance()
        results["broken_links"] = self.validate_broken_links()
        results["critical_files"] = self.validate_critical_files()
        results["hash_coverage"] = self.validate_hash_coverage()
        
        # Generate comprehensive report
        report = self.generate_validation_report(results)
        
        return report

def main():
    """Main validation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive ACGS-2 documentation validation')
    parser.add_argument('--output', '-o', help='Output report to JSON file')
    parser.add_argument('--constitutional-only', action='store_true', help='Only validate constitutional compliance')
    parser.add_argument('--links-only', action='store_true', help='Only validate links')
    parser.add_argument('--files-only', action='store_true', help='Only validate critical files')
    parser.add_argument('--hash-only', action='store_true', help='Only validate hash coverage')
    
    args = parser.parse_args()
    
    validator = DocumentationValidator()
    
    # Run specific validation if requested
    if args.constitutional_only:
        result = validator.validate_constitutional_compliance()
        report = {"constitutional_compliance": result}
    elif args.links_only:
        result = validator.validate_broken_links()
        report = {"broken_links": result}
    elif args.files_only:
        result = validator.validate_critical_files()
        report = {"critical_files": result}
    elif args.hash_only:
        result = validator.validate_hash_coverage()
        report = {"hash_coverage": result}
    else:
        # Run full validation
        report = validator.run_full_validation()
    
    # Save report if requested
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(report, indent=2))
        print(f"\n💾 Report saved to: {output_path}")
    
    # Return appropriate exit code
    if "overall_status" in report:
        if report["overall_status"] == "error":
            return 1
        elif report["overall_status"] == "warning":
            return 0  # Warnings don't fail the validation
        else:
            return 0
    else:
        # Single validation result
        result = list(report.values())[0]
        return 1 if result["status"] == "error" else 0

if __name__ == "__main__":
    sys.exit(main())
