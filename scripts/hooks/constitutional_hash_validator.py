#!/usr/bin/env python3
"""
Constitutional Hash Validator Pre-commit Hook
Constitutional Hash: cdd01ef066bc6cf2

This script validates that documentation files contain the required constitutional hash.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Set


class ConstitutionalHashValidator:
    def __init__(self, required_hash: str):
        self.required_hash = required_hash
        self.hash_patterns = [
            rf"Constitutional Hash[:\s]+[`\"']?{re.escape(required_hash)}[`\"']?",
            rf"constitutional hash[:\s]+[`\"']?{re.escape(required_hash)}[`\"']?",
            rf"hash[:\s]+{re.escape(required_hash)}",
            rf"# Constitutional Hash: {re.escape(required_hash)}",
            rf"<!-- Constitutional Hash: {re.escape(required_hash)} -->",
        ]
        
        # Files that should be exempt from hash validation
        self.exempt_patterns = [
            r"\.pytest_cache/",
            r"__pycache__/",
            r"\.git/",
            r"node_modules/",
            r"\.venv/",
            r"venv/",
            r"build/",
            r"dist/",
            r"\.egg-info/",
            r"coverage\.xml",
            r"\.coverage",
            r"requirements.*\.txt",
            r"setup\.py",
            r"setup\.cfg",
            r"pyproject\.toml",
            r"\.gitignore",
            r"\.dockerignore",
            r"Dockerfile",
            r"docker-compose.*\.yml",
            r"\.env.*",
            r"LICENSE",
            r"CHANGELOG",
            r"\.pre-commit-config\.yaml",
        ]

    def is_exempt(self, file_path: Path) -> bool:
        """Check if a file is exempt from hash validation"""
        file_str = str(file_path)
        for pattern in self.exempt_patterns:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True
        return False

    def has_constitutional_hash(self, content: str) -> bool:
        """Check if content contains the required constitutional hash"""
        for pattern in self.hash_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                return True
        return False

    def validate_file(self, file_path: Path) -> bool:
        """Validate a single file for constitutional hash presence"""
        if self.is_exempt(file_path):
            return True
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip very small files (likely not documentation)
            if len(content.strip()) < 50:
                return True
                
            return self.has_constitutional_hash(content)
            
        except (UnicodeDecodeError, PermissionError):
            # Skip binary files or files we can't read
            return True
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False

    def validate_files(self, file_paths: List[str]) -> tuple[List[str], List[str]]:
        """Validate multiple files and return lists of valid and invalid files"""
        valid_files = []
        invalid_files = []
        
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            
            if not file_path.exists():
                continue
                
            if self.validate_file(file_path):
                valid_files.append(file_path_str)
            else:
                invalid_files.append(file_path_str)
                
        return valid_files, invalid_files

    def suggest_fix(self, file_path: str) -> str:
        """Suggest how to fix a file missing the constitutional hash"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.md':
            return f"""
Add one of these lines to your Markdown file:

**Constitutional Hash**: `{self.required_hash}`

or

# Constitutional Hash: {self.required_hash}
"""
        elif file_ext == '.py':
            return f"""
Add this comment to your Python file:

# Constitutional Hash: {self.required_hash}
"""
        elif file_ext in ['.yml', '.yaml']:
            return f"""
Add this comment to your YAML file:

# Constitutional Hash: {self.required_hash}
"""
        elif file_ext == '.json':
            return f"""
Add this comment to your JSON file (if comments are supported):

// Constitutional Hash: {self.required_hash}
"""
        else:
            return f"""
Add the constitutional hash {self.required_hash} to your file in an appropriate comment format.
"""


def main():
    parser = argparse.ArgumentParser(
        description="Validate constitutional hash presence in files"
    )
    parser.add_argument(
        "--hash",
        required=True,
        help="Required constitutional hash"
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
    
    validator = ConstitutionalHashValidator(args.hash)
    valid_files, invalid_files = validator.validate_files(args.files)
    
    if invalid_files:
        print(f"❌ Constitutional hash validation failed for {len(invalid_files)} files:")
        print(f"Required hash: {args.hash}")
        print()
        
        for file_path in invalid_files:
            print(f"  ❌ {file_path}")
            print(validator.suggest_fix(file_path))
        
        print(f"✅ {len(valid_files)} files passed validation")
        print()
        print("Constitutional compliance is required for all documentation files.")
        print("Please add the constitutional hash to the failing files and try again.")
        
        return 1
    else:
        print(f"✅ All {len(valid_files)} files passed constitutional hash validation")
        return 0


if __name__ == "__main__":
    sys.exit(main())
