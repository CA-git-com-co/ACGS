#!/usr/bin/env python3
"""
ACGS-PGP Constitutional Compliance Enforcer
Validates and enforces constitutional hash compliance across the entire codebase.
Constitutional Hash: cdd01ef066bc6cf2
"""

import argparse
import hashlib
import json
import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constitutional compliance configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
HASH_PATTERN = re.compile(r'["\']?(?:constitutional_hash|CONSTITUTIONAL_HASH)["\']?\s*[:=]\s*["\']?([a-f0-9]{16})["\']?', re.IGNORECASE)


@dataclass
class ComplianceViolation:
    """Represents a constitutional compliance violation."""
    file_path: Path
    line_number: int
    violation_type: str
    expected_hash: str
    found_hash: Optional[str]
    severity: str  # critical, high, medium, low
    message: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "file": str(self.file_path),
            "line": self.line_number,
            "type": self.violation_type,
            "expected": self.expected_hash,
            "found": self.found_hash,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass
class ComplianceReport:
    """Constitutional compliance report."""
    timestamp: str
    constitutional_hash: str
    files_scanned: int
    files_compliant: int
    violations: List[ComplianceViolation]
    services_validated: List[str]
    overall_compliance_score: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "constitutional_hash": self.constitutional_hash,
            "files_scanned": self.files_scanned,
            "files_compliant": self.files_compliant,
            "violations": [v.to_dict() for v in self.violations],
            "services_validated": self.services_validated,
            "overall_compliance_score": self.overall_compliance_score,
        }


class ConstitutionalComplianceEnforcer:
    """Enforces constitutional compliance across ACGS-PGP."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.violations: List[ComplianceViolation] = []
        self.files_scanned = 0
        self.files_compliant = 0
        self.services_validated: Set[str] = set()
        
        # File patterns that must contain constitutional hash
        self.required_patterns = {
            "main.py": "critical",
            "app.py": "critical",
            "__init__.py": "high",
            "config.py": "high",
            "settings.py": "high",
            "*_service.py": "high",
            "*_engine.py": "high",
            "middleware.py": "medium",
        }
        
        # Files/directories to skip
        self.skip_patterns = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            "venv",
            ".venv",
            "migrations",
            "tests",
            "test_*.py",
            "*_test.py",
        }
        
    def scan_codebase(self) -> ComplianceReport:
        """Scan entire codebase for constitutional compliance."""
        logger.info(f"Starting constitutional compliance scan from {self.project_root}")
        
        # Scan all relevant files
        for file_path in self._find_files_to_scan():
            self._scan_file(file_path)
            
        # Check service configurations
        self._validate_service_configurations()
        
        # Check CI/CD configurations
        self._validate_cicd_configurations()
        
        # Check documentation
        self._validate_documentation()
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score()
        
        # Generate report
        report = ComplianceReport(
            timestamp=datetime.utcnow().isoformat(),
            constitutional_hash=CONSTITUTIONAL_HASH,
            files_scanned=self.files_scanned,
            files_compliant=self.files_compliant,
            violations=self.violations,
            services_validated=list(self.services_validated),
            overall_compliance_score=compliance_score,
        )
        
        return report
        
    def _find_files_to_scan(self) -> List[Path]:
        """Find all files that need scanning."""
        files_to_scan = []
        
        # Common file extensions to scan
        extensions = {".py", ".yaml", ".yml", ".json", ".toml", ".md", ".rst"}
        
        for ext in extensions:
            for file_path in self.project_root.rglob(f"*{ext}"):
                # Skip if in skip patterns
                if any(pattern in str(file_path) for pattern in self.skip_patterns):
                    continue
                    
                # Skip if file name matches skip pattern
                if any(file_path.name == pattern or 
                      (pattern.startswith("*") and file_path.name.endswith(pattern[1:])) or
                      (pattern.endswith("*") and file_path.name.startswith(pattern[:-1]))
                      for pattern in self.skip_patterns):
                    continue
                    
                files_to_scan.append(file_path)
                
        return files_to_scan
        
    def _scan_file(self, file_path: Path) -> None:
        """Scan a single file for compliance."""
        self.files_scanned += 1
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check if file requires constitutional hash
            severity = self._get_required_severity(file_path)
            
            # Find all hash references
            hash_matches = list(HASH_PATTERN.finditer(content))
            
            if severity:
                # File requires hash
                if not hash_matches:
                    self.violations.append(ComplianceViolation(
                        file_path=file_path,
                        line_number=0,
                        violation_type="missing_hash",
                        expected_hash=CONSTITUTIONAL_HASH,
                        found_hash=None,
                        severity=severity,
                        message=f"Required constitutional hash not found in {file_path.name}"
                    ))
                else:
                    # Validate all found hashes
                    file_compliant = True
                    for match in hash_matches:
                        found_hash = match.group(1)
                        if found_hash != CONSTITUTIONAL_HASH:
                            line_number = content[:match.start()].count('\n') + 1
                            self.violations.append(ComplianceViolation(
                                file_path=file_path,
                                line_number=line_number,
                                violation_type="incorrect_hash",
                                expected_hash=CONSTITUTIONAL_HASH,
                                found_hash=found_hash,
                                severity=severity,
                                message=f"Incorrect constitutional hash found"
                            ))
                            file_compliant = False
                            
                    if file_compliant:
                        self.files_compliant += 1
            else:
                # File doesn't require hash, but check if it has incorrect hash
                for match in hash_matches:
                    found_hash = match.group(1)
                    if found_hash != CONSTITUTIONAL_HASH:
                        line_number = content[:match.start()].count('\n') + 1
                        self.violations.append(ComplianceViolation(
                            file_path=file_path,
                            line_number=line_number,
                            violation_type="incorrect_hash",
                            expected_hash=CONSTITUTIONAL_HASH,
                            found_hash=found_hash,
                            severity="low",
                            message=f"Incorrect constitutional hash found in optional file"
                        ))
                    else:
                        self.files_compliant += 1
                        
            # Additional checks for specific file types
            if file_path.suffix == ".py":
                self._check_python_compliance(file_path, content)
            elif file_path.suffix in [".yaml", ".yml"]:
                self._check_yaml_compliance(file_path, content)
                
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
            
    def _get_required_severity(self, file_path: Path) -> Optional[str]:
        """Determine if file requires constitutional hash and its severity."""
        file_name = file_path.name
        
        for pattern, severity in self.required_patterns.items():
            if pattern.startswith("*") and file_name.endswith(pattern[1:]):
                return severity
            elif pattern.endswith("*") and file_name.startswith(pattern[:-1]):
                return severity
            elif file_name == pattern:
                return severity
                
        # Check if it's a main service file
        if "services" in file_path.parts and file_name in ["main.py", "app.py"]:
            return "critical"
            
        return None
        
    def _check_python_compliance(self, file_path: Path, content: str) -> None:
        """Additional compliance checks for Python files."""
        # Check for middleware without hash validation
        if "middleware" in content and "@app.middleware" in content:
            if "constitutional" not in content.lower():
                self.violations.append(ComplianceViolation(
                    file_path=file_path,
                    line_number=0,
                    violation_type="missing_validation",
                    expected_hash=CONSTITUTIONAL_HASH,
                    found_hash=None,
                    severity="medium",
                    message="Middleware missing constitutional validation"
                ))
                
        # Check for API endpoints without proper headers
        if "@app." in content and any(method in content for method in ["get(", "post(", "put(", "delete("]):
            if "X-Constitutional-Hash" not in content:
                self.violations.append(ComplianceViolation(
                    file_path=file_path,
                    line_number=0,
                    violation_type="missing_header",
                    expected_hash=CONSTITUTIONAL_HASH,
                    found_hash=None,
                    severity="medium",
                    message="API endpoints missing constitutional hash header"
                ))
                
    def _check_yaml_compliance(self, file_path: Path, content: str) -> None:
        """Additional compliance checks for YAML files."""
        try:
            data = yaml.safe_load(content)
            
            # Check Docker Compose files
            if "docker-compose" in file_path.name and isinstance(data, dict):
                services = data.get("services", {})
                for service_name, service_config in services.items():
                    env_vars = service_config.get("environment", {})
                    if isinstance(env_vars, dict) and "CONSTITUTIONAL_HASH" not in env_vars:
                        self.violations.append(ComplianceViolation(
                            file_path=file_path,
                            line_number=0,
                            violation_type="missing_env_var",
                            expected_hash=CONSTITUTIONAL_HASH,
                            found_hash=None,
                            severity="high",
                            message=f"Service '{service_name}' missing CONSTITUTIONAL_HASH env var"
                        ))
                        
        except yaml.YAMLError:
            pass  # Skip invalid YAML files
            
    def _validate_service_configurations(self) -> None:
        """Validate service-specific configurations."""
        services_dir = self.project_root / "services"
        if not services_dir.exists():
            return
            
        for service_dir in services_dir.rglob("*"):
            if service_dir.is_dir() and (service_dir / "main.py").exists():
                service_name = service_dir.name
                self.services_validated.add(service_name)
                
                # Check for required files
                required_files = {
                    "requirements.txt": "medium",
                    "Dockerfile": "high",
                    "README.md": "low",
                }
                
                for file_name, severity in required_files.items():
                    file_path = service_dir / file_name
                    if not file_path.exists():
                        self.violations.append(ComplianceViolation(
                            file_path=service_dir,
                            line_number=0,
                            violation_type="missing_required_file",
                            expected_hash=CONSTITUTIONAL_HASH,
                            found_hash=None,
                            severity=severity,
                            message=f"Service '{service_name}' missing {file_name}"
                        ))
                        
    def _validate_cicd_configurations(self) -> None:
        """Validate CI/CD pipeline configurations."""
        workflows_dir = self.project_root / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.yml"):
                try:
                    content = workflow_file.read_text()
                    data = yaml.safe_load(content)
                    
                    # Check for constitutional validation step
                    if isinstance(data, dict) and "jobs" in data:
                        has_validation = False
                        for job_name, job_config in data["jobs"].items():
                            if isinstance(job_config, dict) and "steps" in job_config:
                                for step in job_config["steps"]:
                                    if isinstance(step, dict) and "constitutional" in str(step).lower():
                                        has_validation = True
                                        break
                                        
                        if not has_validation:
                            self.violations.append(ComplianceViolation(
                                file_path=workflow_file,
                                line_number=0,
                                violation_type="missing_ci_validation",
                                expected_hash=CONSTITUTIONAL_HASH,
                                found_hash=None,
                                severity="high",
                                message="CI/CD workflow missing constitutional validation step"
                            ))
                            
                except Exception as e:
                    logger.error(f"Error validating workflow {workflow_file}: {e}")
                    
    def _validate_documentation(self) -> None:
        """Validate documentation contains constitutional hash."""
        doc_files = ["README.md", "CONTRIBUTING.md", "ARCHITECTURE.md"]
        
        for doc_name in doc_files:
            doc_path = self.project_root / doc_name
            if doc_path.exists():
                content = doc_path.read_text()
                if CONSTITUTIONAL_HASH not in content:
                    self.violations.append(ComplianceViolation(
                        file_path=doc_path,
                        line_number=0,
                        violation_type="missing_doc_reference",
                        expected_hash=CONSTITUTIONAL_HASH,
                        found_hash=None,
                        severity="low",
                        message=f"{doc_name} missing constitutional hash reference"
                    ))
                    
    def _calculate_compliance_score(self) -> float:
        """Calculate overall compliance score."""
        if self.files_scanned == 0:
            return 0.0
            
        # Base score from file compliance
        file_score = (self.files_compliant / self.files_scanned) * 100
        
        # Deduct for violations based on severity
        severity_penalties = {
            "critical": 10.0,
            "high": 5.0,
            "medium": 2.0,
            "low": 0.5,
        }
        
        total_penalty = sum(
            severity_penalties.get(v.severity, 0) 
            for v in self.violations
        )
        
        # Calculate final score
        score = max(0, file_score - total_penalty)
        
        return round(score, 2)
        
    def fix_violations(self, auto_fix: bool = False) -> int:
        """Attempt to fix violations automatically."""
        if not auto_fix:
            logger.info("Auto-fix not enabled. Run with --auto-fix to fix violations.")
            return 0
            
        fixed_count = 0
        
        for violation in self.violations:
            if violation.violation_type == "incorrect_hash":
                try:
                    # Read file
                    content = violation.file_path.read_text()
                    
                    # Replace incorrect hash
                    new_content = content.replace(
                        violation.found_hash,
                        CONSTITUTIONAL_HASH
                    )
                    
                    # Write back
                    violation.file_path.write_text(new_content)
                    fixed_count += 1
                    logger.info(f"Fixed incorrect hash in {violation.file_path}")
                    
                except Exception as e:
                    logger.error(f"Failed to fix {violation.file_path}: {e}")
                    
            elif violation.violation_type == "missing_hash" and violation.file_path.suffix == ".py":
                try:
                    # Read file
                    content = violation.file_path.read_text()
                    
                    # Add hash as constant after imports
                    lines = content.split('\n')
                    insert_index = 0
                    
                    # Find location after imports
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith(('import', 'from', '#')):
                            insert_index = i
                            break
                            
                    # Insert constitutional hash
                    lines.insert(insert_index, f'\n# Constitutional compliance\nCONSTITUTIONAL_HASH = "{CONSTITUTIONAL_HASH}"\n')
                    
                    # Write back
                    violation.file_path.write_text('\n'.join(lines))
                    fixed_count += 1
                    logger.info(f"Added constitutional hash to {violation.file_path}")
                    
                except Exception as e:
                    logger.error(f"Failed to fix {violation.file_path}: {e}")
                    
        return fixed_count
        
    def generate_report(self, report: ComplianceReport) -> str:
        """Generate human-readable compliance report."""
        lines = [
            f"# Constitutional Compliance Report",
            f"Generated: {report.timestamp}",
            f"Constitutional Hash: {report.constitutional_hash}",
            "",
            f"## Summary",
            f"- Files Scanned: {report.files_scanned}",
            f"- Files Compliant: {report.files_compliant}",
            f"- Violations Found: {len(report.violations)}",
            f"- Services Validated: {len(report.services_validated)}",
            f"- **Overall Compliance Score: {report.overall_compliance_score:.1f}%**",
            "",
        ]
        
        if report.violations:
            # Group violations by severity
            by_severity = {"critical": [], "high": [], "medium": [], "low": []}
            for violation in report.violations:
                by_severity[violation.severity].append(violation)
                
            lines.extend([
                "## Violations by Severity",
                "",
            ])
            
            for severity in ["critical", "high", "medium", "low"]:
                violations = by_severity[severity]
                if violations:
                    lines.extend([
                        f"### {severity.upper()} ({len(violations)} violations)",
                        "",
                    ])
                    
                    for v in violations[:10]:  # Show first 10
                        lines.append(
                            f"- `{v.file_path}:{v.line_number}` - {v.message}"
                        )
                        
                    if len(violations) > 10:
                        lines.append(f"- ... and {len(violations) - 10} more")
                        
                    lines.append("")
                    
        else:
            lines.extend([
                "## Status",
                "✅ **No violations found!** The codebase is fully compliant.",
                "",
            ])
            
        if report.services_validated:
            lines.extend([
                "## Services Validated",
                "",
                *[f"- {service}" for service in sorted(report.services_validated)],
                "",
            ])
            
        # Add recommendations
        lines.extend([
            "## Recommendations",
            "",
        ])
        
        if report.overall_compliance_score < 100:
            lines.extend([
                "1. Run with `--auto-fix` to automatically fix correctable violations",
                "2. Add constitutional hash validation to all middleware",
                "3. Include hash in CI/CD pipeline checks",
                "4. Document constitutional requirements in README",
                "",
            ])
        else:
            lines.extend([
                "1. Continue monitoring compliance in CI/CD",
                "2. Add pre-commit hooks for automatic validation",
                "3. Regular compliance audits",
                "",
            ])
            
        return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ACGS-PGP Constitutional Compliance Enforcer"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("constitutional-compliance-report.json"),
        help="Output file for JSON report",
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Automatically fix correctable violations",
    )
    parser.add_argument(
        "--fail-on-violation",
        action="store_true",
        help="Exit with error code if violations found",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=95.0,
        help="Minimum compliance score required",
    )
    
    args = parser.parse_args()
    
    # Initialize enforcer
    enforcer = ConstitutionalComplianceEnforcer(args.project_root)
    
    # Scan codebase
    logger.info("Starting constitutional compliance scan...")
    report = enforcer.scan_codebase()
    
    # Auto-fix if requested
    if args.auto_fix and report.violations:
        logger.info("Attempting to auto-fix violations...")
        fixed_count = enforcer.fix_violations(auto_fix=True)
        logger.info(f"Fixed {fixed_count} violations")
        
        # Re-scan after fixes
        enforcer = ConstitutionalComplianceEnforcer(args.project_root)
        report = enforcer.scan_codebase()
        
    # Save JSON report
    with open(args.output, 'w') as f:
        json.dump(report.to_dict(), f, indent=2)
    logger.info(f"JSON report saved to {args.output}")
    
    # Generate and print markdown report
    markdown_report = enforcer.generate_report(report)
    print("\n" + markdown_report)
    
    # Save markdown report
    md_output = args.output.with_suffix('.md')
    with open(md_output, 'w') as f:
        f.write(markdown_report)
    logger.info(f"Markdown report saved to {md_output}")
    
    # Check compliance
    if report.overall_compliance_score < args.min_score:
        logger.error(
            f"Compliance score {report.overall_compliance_score:.1f}% "
            f"is below minimum {args.min_score}%"
        )
        if args.fail_on_violation:
            sys.exit(1)
    else:
        logger.info(
            f"✅ Compliance score {report.overall_compliance_score:.1f}% "
            f"meets requirement"
        )
        
    if args.fail_on_violation and report.violations:
        logger.error(f"Found {len(report.violations)} compliance violations")
        sys.exit(1)


if __name__ == "__main__":
    main()