#!/usr/bin/env python3
"""
Performance Targets Validator Pre-commit Hook
Constitutional Hash: cdd01ef066bc6cf2

This script validates that documentation files contain required performance targets.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Set


class PerformanceTargetsValidator:
    def __init__(self, require_targets: bool = False):
        self.require_targets = require_targets
        
        # Required performance targets
        self.required_targets = {
            "p99_latency": {
                "patterns": [
                    r"P99.*<5ms",
                    r"P99.*latency.*<5ms",
                    r"99th percentile.*<5ms",
                ],
                "description": "P99 Latency: <5ms"
            },
            "throughput": {
                "patterns": [
                    r"Throughput.*>100\s*RPS",
                    r">100\s*RPS",
                    r"requests per second.*>100",
                ],
                "description": "Throughput: >100 RPS"
            },
            "cache_hit_rate": {
                "patterns": [
                    r"Cache Hit Rate.*>85%",
                    r"cache.*hit.*>85%",
                    r"cache.*efficiency.*>85%",
                ],
                "description": "Cache Hit Rate: >85%"
            }
        }
        
        # Files that should contain performance targets
        self.target_file_patterns = [
            r"README\.md$",
            r"PERFORMANCE\.md$",
            r"ARCHITECTURE\.md$",
            r"IMPLEMENTATION.*\.md$",
            r"GUIDE\.md$",
            r"services/.*/.*\.md$",
            r"docs/.*/.*\.md$",
            r"infrastructure/.*/.*\.md$",
        ]
        
        # Files exempt from performance target requirements
        self.exempt_patterns = [
            r"\.pytest_cache/",
            r"__pycache__/",
            r"\.git/",
            r"CHANGELOG",
            r"LICENSE",
            r"CONTRIBUTING",
            r"CODE_OF_CONDUCT",
            r"\.github/",
            r"archive/",
            r"docs_consolidated_archive",
        ]

    def is_exempt(self, file_path: Path) -> bool:
        """Check if a file is exempt from performance target validation"""
        file_str = str(file_path)
        for pattern in self.exempt_patterns:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True
        return False

    def should_have_targets(self, file_path: Path) -> bool:
        """Check if a file should contain performance targets"""
        if self.is_exempt(file_path):
            return False
            
        file_str = str(file_path)
        for pattern in self.target_file_patterns:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True
        return False

    def check_performance_targets(self, content: str) -> Dict[str, bool]:
        """Check which performance targets are present in content"""
        results = {}
        
        for target_name, target_info in self.required_targets.items():
            found = False
            for pattern in target_info["patterns"]:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    found = True
                    break
            results[target_name] = found
            
        return results

    def validate_file(self, file_path: Path) -> tuple[bool, Dict[str, bool], List[str]]:
        """Validate a single file for performance targets"""
        if not self.should_have_targets(file_path):
            return True, {}, []
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip very small files
            if len(content.strip()) < 100:
                return True, {}, []
            
            target_results = self.check_performance_targets(content)
            missing_targets = []
            
            for target_name, found in target_results.items():
                if not found:
                    missing_targets.append(self.required_targets[target_name]["description"])
            
            is_valid = len(missing_targets) == 0 or not self.require_targets
            
            return is_valid, target_results, missing_targets
            
        except (UnicodeDecodeError, PermissionError):
            return True, {}, []
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False, {}, []

    def validate_files(self, file_paths: List[str]) -> tuple[List[str], List[tuple[str, List[str]]]]:
        """Validate multiple files and return results"""
        valid_files = []
        invalid_files = []
        
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            
            if not file_path.exists():
                continue
                
            is_valid, target_results, missing_targets = self.validate_file(file_path)
            
            if is_valid:
                valid_files.append(file_path_str)
            else:
                invalid_files.append((file_path_str, missing_targets))
                
        return valid_files, invalid_files

    def suggest_fix(self, missing_targets: List[str]) -> str:
        """Suggest how to add missing performance targets"""
        return f"""
Add a Performance Requirements section with these targets:

## Performance Requirements

### ACGS-2 Performance Targets
{chr(10).join(f"- **{target}**" for target in missing_targets)}
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

### Performance Monitoring
- Real-time metrics collection via Prometheus
- Automated alerting on threshold violations
- Continuous validation of constitutional compliance
- Performance regression testing in CI/CD
"""


def main():
    parser = argparse.ArgumentParser(
        description="Validate performance targets in documentation files"
    )
    parser.add_argument(
        "--require-targets",
        action="store_true",
        help="Require performance targets in applicable files"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to validate"
    )
    
    args = parser.parse_args()
    
    if not args.files:
        print("No files to validate")
        return 0
    
    validator = PerformanceTargetsValidator(require_targets=args.require_targets)
    valid_files, invalid_files = validator.validate_files(args.files)
    
    if invalid_files and args.require_targets:
        print(f"❌ Performance targets validation failed for {len(invalid_files)} files:")
        print()
        
        for file_path, missing_targets in invalid_files:
            print(f"  ❌ {file_path}")
            print(f"    Missing targets: {', '.join(missing_targets)}")
            print(validator.suggest_fix(missing_targets))
        
        print(f"✅ {len(valid_files)} files passed validation")
        print()
        print("Performance targets are required for documentation files.")
        print("Please add the missing targets and try again.")
        
        return 1
    else:
        if args.require_targets:
            print(f"✅ All {len(valid_files)} files passed performance targets validation")
        else:
            print(f"ℹ️  Performance targets check completed (not required)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
