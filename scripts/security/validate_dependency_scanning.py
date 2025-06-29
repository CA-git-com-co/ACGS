#!/usr/bin/env python3
"""
Dependency Vulnerability Scanning Validation Script

This script validates that dependency scanning is properly configured
and working across all supported languages in the ACGS-PGP project.

Usage:
    python3 scripts/security/validate_dependency_scanning.py
    python3 scripts/security/validate_dependency_scanning.py --verbose
    python3 scripts/security/validate_dependency_scanning.py --check-tools
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class DependencyScanningValidator:
    """Validates dependency vulnerability scanning setup."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.project_root = Path(__file__).parent.parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validation_results": {},
            "recommendations": [],
            "overall_status": "unknown"
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with optional verbosity control."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, command: List[str], cwd: Path = None) -> Tuple[bool, str, str]:
        """Run a command and return success status, stdout, stderr."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def check_workflow_files(self) -> Dict[str, bool]:
        """Check if required workflow files exist and are properly configured."""
        self.log("Checking GitHub workflow files...")
        
        workflow_dir = self.project_root / ".github" / "workflows"
        required_workflows = {
            "dependency-monitoring.yml": "Daily dependency monitoring",
            "security-scanning.yml": "Comprehensive security scanning",
            "ci.yml": "Main CI pipeline with security integration"
        }
        
        results = {}
        for workflow_file, description in required_workflows.items():
            workflow_path = workflow_dir / workflow_file
            exists = workflow_path.exists()
            results[workflow_file] = exists
            
            if exists:
                self.log(f"✅ Found {description}: {workflow_file}")
                # Check if workflow contains dependency scanning
                content = workflow_path.read_text()
                has_scanning = any(keyword in content.lower() for keyword in 
                                 ["pip-audit", "npm audit", "cargo audit", "safety"])
                if has_scanning:
                    self.log(f"   ✅ Contains dependency scanning commands")
                else:
                    self.log(f"   ⚠️ May not contain dependency scanning", "WARNING")
            else:
                self.log(f"❌ Missing {description}: {workflow_file}", "ERROR")
        
        return results
    
    def check_python_scanning_tools(self) -> Dict[str, bool]:
        """Check Python dependency scanning tools availability."""
        self.log("Checking Python dependency scanning tools...")
        
        tools = {
            "pip-audit": "pip-audit --version",
            "safety": "safety --version"
        }
        
        results = {}
        for tool, version_command in tools.items():
            success, stdout, stderr = self.run_command(version_command.split())
            results[tool] = success
            
            if success:
                version = stdout.strip().split('\n')[0] if stdout else "unknown"
                self.log(f"✅ {tool} available: {version}")
            else:
                self.log(f"❌ {tool} not available: {stderr}", "WARNING")
                self.results["recommendations"].append(f"Install {tool}: pip install {tool}")
        
        return results
    
    def check_nodejs_scanning_tools(self) -> Dict[str, bool]:
        """Check Node.js dependency scanning tools availability."""
        self.log("Checking Node.js dependency scanning tools...")
        
        # Check if npm is available
        npm_available, npm_stdout, npm_stderr = self.run_command(["npm", "--version"])
        
        results = {"npm": npm_available}
        
        if npm_available:
            version = npm_stdout.strip()
            self.log(f"✅ npm available: {version}")
            
            # Check for package.json files
            package_files = list(self.project_root.rglob("package.json"))
            package_files = [f for f in package_files if "node_modules" not in str(f)]
            
            if package_files:
                self.log(f"✅ Found {len(package_files)} package.json files")
                results["package_files"] = True
            else:
                self.log("⚠️ No package.json files found", "WARNING")
                results["package_files"] = False
        else:
            self.log(f"❌ npm not available: {npm_stderr}", "WARNING")
            results["package_files"] = False
        
        return results
    
    def check_rust_scanning_tools(self) -> Dict[str, bool]:
        """Check Rust dependency scanning tools availability."""
        self.log("Checking Rust dependency scanning tools...")
        
        tools = {
            "cargo": "cargo --version",
            "cargo-audit": "cargo audit --version",
            "cargo-deny": "cargo deny --version"
        }
        
        results = {}
        for tool, version_command in tools.items():
            success, stdout, stderr = self.run_command(version_command.split())
            results[tool] = success
            
            if success:
                version = stdout.strip().split('\n')[0] if stdout else "unknown"
                self.log(f"✅ {tool} available: {version}")
            else:
                self.log(f"❌ {tool} not available: {stderr}", "WARNING")
                if tool == "cargo-audit":
                    self.results["recommendations"].append("Install cargo-audit: cargo install cargo-audit")
                elif tool == "cargo-deny":
                    self.results["recommendations"].append("Install cargo-deny: cargo install cargo-deny")
        
        # Check for Rust projects
        cargo_files = list(self.project_root.rglob("Cargo.toml"))
        if cargo_files:
            self.log(f"✅ Found {len(cargo_files)} Cargo.toml files")
            results["cargo_projects"] = True
        else:
            self.log("⚠️ No Cargo.toml files found", "WARNING")
            results["cargo_projects"] = False
        
        return results
    
    def validate_scanning_configuration(self) -> bool:
        """Validate overall scanning configuration."""
        self.log("Validating dependency scanning configuration...")
        
        # Check workflow files
        workflow_results = self.check_workflow_files()
        self.results["validation_results"]["workflows"] = workflow_results
        
        # Check scanning tools
        python_results = self.check_python_scanning_tools()
        nodejs_results = self.check_nodejs_scanning_tools()
        rust_results = self.check_rust_scanning_tools()
        
        self.results["validation_results"]["python_tools"] = python_results
        self.results["validation_results"]["nodejs_tools"] = nodejs_results
        self.results["validation_results"]["rust_tools"] = rust_results
        
        # Determine overall status
        critical_workflows = ["dependency-monitoring.yml", "security-scanning.yml"]
        workflows_ok = all(workflow_results.get(w, False) for w in critical_workflows)
        
        python_ok = python_results.get("pip-audit", False) or python_results.get("safety", False)
        nodejs_ok = nodejs_results.get("npm", False)
        rust_ok = rust_results.get("cargo", False)
        
        if workflows_ok and python_ok and nodejs_ok and rust_ok:
            self.results["overall_status"] = "excellent"
            self.log("✅ Dependency scanning configuration is excellent!")
        elif workflows_ok and (python_ok or nodejs_ok or rust_ok):
            self.results["overall_status"] = "good"
            self.log("✅ Dependency scanning configuration is good")
        else:
            self.results["overall_status"] = "needs_improvement"
            self.log("⚠️ Dependency scanning configuration needs improvement", "WARNING")
        
        return self.results["overall_status"] in ["excellent", "good"]
    
    def generate_report(self) -> str:
        """Generate a comprehensive validation report."""
        report_path = self.project_root / "reports" / "dependency_scanning_validation.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.log(f"📊 Validation report saved to: {report_path}")
        return str(report_path)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate dependency vulnerability scanning setup")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--check-tools", action="store_true", help="Only check tool availability")
    
    args = parser.parse_args()
    
    validator = DependencyScanningValidator(verbose=args.verbose)
    
    print("🔍 ACGS-PGP Dependency Scanning Validation")
    print("=" * 50)
    
    if args.check_tools:
        # Only check tools
        validator.check_python_scanning_tools()
        validator.check_nodejs_scanning_tools()
        validator.check_rust_scanning_tools()
    else:
        # Full validation
        success = validator.validate_scanning_configuration()
        report_path = validator.generate_report()
        
        print("\n📋 Validation Summary:")
        print(f"Overall Status: {validator.results['overall_status'].upper()}")
        
        if validator.results["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in validator.results["recommendations"]:
                print(f"  - {rec}")
        
        print(f"\n📊 Detailed report: {report_path}")
        
        if not success:
            print("\n⚠️ Some issues found. Please review the recommendations above.")
            sys.exit(1)
        else:
            print("\n✅ Dependency scanning is properly configured!")


if __name__ == "__main__":
    main()
