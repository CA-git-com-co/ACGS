#!/usr/bin/env python3
"""
Documentation Compliance Validator Pre-commit Hook
Constitutional Hash: cdd01ef066bc6cf2

This script validates documentation files for comprehensive compliance requirements.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple


class DocumentationComplianceValidator:
    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Implementation status indicators
        self.status_indicators = [
            "✅ IMPLEMENTED",
            "🔄 IN PROGRESS", 
            "❌ PLANNED"
        ]
        
        # Required sections for comprehensive documentation
        self.required_sections = {
            "README.md": [
                "Overview",
                "Performance",  # Matches "Performance Metrics", "Performance Targets", etc.
                "Implementation Status"
            ],
            "IMPLEMENTATION_GUIDE.md": [
                "Architecture",
                "Performance",
                "Implementation Status"
            ],
            "ARCHITECTURE.md": [
                "Overview",
                "Components",
                "Performance"
            ]
        }
        
        # Files exempt from full compliance checking
        self.exempt_patterns = [
            r"\.pytest_cache/",
            r"__pycache__/",
            r"\.git/",
            r"CHANGELOG",
            r"LICENSE",
            r"\.github/",
            r"archive/",
            r"docs_consolidated_archive",
        ]

    def is_exempt(self, file_path: Path) -> bool:
        """Check if a file is exempt from compliance validation"""
        file_str = str(file_path)
        for pattern in self.exempt_patterns:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True
        return False

    def check_constitutional_hash(self, content: str) -> bool:
        """Check if content contains constitutional hash"""
        patterns = [
            rf"Constitutional Hash[:\s]+[`\"']?{re.escape(self.constitutional_hash)}[`\"']?",
            rf"constitutional hash[:\s]+[`\"']?{re.escape(self.constitutional_hash)}[`\"']?",
            rf"# Constitutional Hash: {re.escape(self.constitutional_hash)}",
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                return True
        return False

    def check_status_indicators(self, content: str) -> bool:
        """Check if content contains implementation status indicators"""
        for indicator in self.status_indicators:
            if indicator in content:
                return True
        return False

    def check_performance_targets(self, content: str) -> bool:
        """Check if content contains performance targets"""
        patterns = [
            r"P99.*<5ms",
            r"Throughput.*>100\s*RPS",
            r"Cache Hit Rate.*>85%",
            r"Performance Requirements",
            r"Performance Targets"
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                return True
        return False

    def check_required_sections(self, content: str, file_name: str) -> List[str]:
        """Check for required sections based on file type"""
        missing_sections = []

        if file_name in self.required_sections:
            for section in self.required_sections[file_name]:
                # Look for section headers (more flexible matching)
                pattern = rf"^#+\s*.*{re.escape(section)}"
                if not re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    missing_sections.append(section)

        return missing_sections

    def validate_file(self, file_path: Path) -> Tuple[bool, Dict[str, any]]:
        """Validate a single documentation file"""
        if self.is_exempt(file_path):
            return True, {"exempt": True}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip very small files
            if len(content.strip()) < 50:
                return True, {"too_small": True}
            
            file_name = file_path.name
            
            # Check various compliance aspects
            has_hash = self.check_constitutional_hash(content)
            has_status = self.check_status_indicators(content)
            has_performance = self.check_performance_targets(content)
            missing_sections = self.check_required_sections(content, file_name)
            
            # Determine if file is compliant
            is_compliant = (
                has_hash and 
                (has_status or len(content) < 500) and  # Small files don't need status
                (has_performance or not file_name.startswith(('README', 'IMPLEMENTATION', 'ARCHITECTURE'))) and
                len(missing_sections) == 0
            )
            
            validation_result = {
                "has_constitutional_hash": has_hash,
                "has_status_indicators": has_status,
                "has_performance_targets": has_performance,
                "missing_sections": missing_sections,
                "file_size": len(content),
                "is_compliant": is_compliant
            }
            
            return is_compliant, validation_result
            
        except (UnicodeDecodeError, PermissionError):
            return True, {"unreadable": True}
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False, {"error": str(e)}

    def validate_files(self, file_paths: List[str]) -> Tuple[List[str], List[Tuple[str, Dict]]]:
        """Validate multiple files"""
        valid_files = []
        invalid_files = []
        
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            
            if not file_path.exists() or not file_path.suffix.lower() in ['.md', '.rst']:
                continue
                
            is_valid, validation_result = self.validate_file(file_path)
            
            if is_valid:
                valid_files.append(file_path_str)
            else:
                invalid_files.append((file_path_str, validation_result))
                
        return valid_files, invalid_files

    def suggest_fixes(self, validation_result: Dict) -> str:
        """Suggest fixes for compliance issues"""
        suggestions = []
        
        if not validation_result.get("has_constitutional_hash", True):
            suggestions.append(f"Add constitutional hash: **Constitutional Hash**: `{self.constitutional_hash}`")
        
        if not validation_result.get("has_status_indicators", True) and validation_result.get("file_size", 0) > 500:
            suggestions.append("Add implementation status indicators (✅ 🔄 ❌)")
        
        if not validation_result.get("has_performance_targets", True):
            suggestions.append("Add performance requirements section with P99 <5ms, >100 RPS, >85% cache hit targets")
        
        missing_sections = validation_result.get("missing_sections", [])
        if missing_sections:
            suggestions.append(f"Add missing sections: {', '.join(missing_sections)}")
        
        if suggestions:
            return "\n    " + "\n    ".join(f"• {suggestion}" for suggestion in suggestions)
        else:
            return "\n    • No specific suggestions available"


def main():
    parser = argparse.ArgumentParser(
        description="Validate documentation compliance"
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
    
    validator = DocumentationComplianceValidator()
    valid_files, invalid_files = validator.validate_files(args.files)
    
    if invalid_files:
        print(f"❌ Documentation compliance failed for {len(invalid_files)} files:")
        print()
        
        for file_path, validation_result in invalid_files:
            print(f"  ❌ {file_path}")
            print(f"    Issues found:{validator.suggest_fixes(validation_result)}")
            print()
        
        print(f"✅ {len(valid_files)} files passed validation")
        print()
        print("Documentation compliance is required for all documentation files.")
        print("Please address the issues above and try again.")
        
        return 1
    else:
        print(f"✅ All {len(valid_files)} documentation files passed compliance validation")
        return 0


if __name__ == "__main__":
    sys.exit(main())
