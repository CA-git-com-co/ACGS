#!/usr/bin/env python3
"""
Fix pattern extraction test issues
Constitutional Hash: cdd01ef066bc6cf2
"""

import re
from pathlib import Path

def fix_pattern_tests():
    """Fix the pattern extraction test file."""
    test_file = Path("tests/validation/test_pattern_extraction.py")
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Fix all patch.object calls for relative_to
    pattern = r'with patch\.object\(\s*test_file,\s*"relative_to",\s*return_value=Path\("([^"]+)"\)\s*\):\s*references = analyzer\._extract_cross_references\(\s*test_file,\s*([^,]+),\s*([^)]+)\s*\)'
    
    def replacement(match):
        path_value = match.group(1)
        content_var = match.group(2)
        lines_var = match.group(3)
        return f'''# Use a mock file path instead of patching relative_to
            mock_file = Mock()
            mock_file.relative_to.return_value = Path("{path_value}")
            references = analyzer._extract_cross_references(
                mock_file, {content_var}, {lines_var}
            )'''
    
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix the complex_pattern_registry fixture issue
    fixture_pattern = r'def test_extraction_benchmark\(self, benchmark, complex_pattern_registry\):'
    content = re.sub(fixture_pattern, 'def test_extraction_benchmark(self, benchmark):', content)
    
    # Add the missing fixture
    fixture_def = '''    @pytest.fixture
    def complex_pattern_registry(self):
        """Complex pattern registry for edge case testing."""
        return {
            "version": "1.0",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "categories": {
                "markdown_links": {"base_confidence": 0.8},
                "code_references": {"base_confidence": 0.9},
                "configuration_references": {"base_confidence": 0.7},
                "edge_cases": {"base_confidence": 0.6},
            },
            "patterns": [
                {
                    "name": "markdown_link",
                    "category": "markdown_links",
                    "regex": r"\\[([^\\]]*)\\]\\(([^)]+)\\)",
                    "capture_groups": {"text": 1, "url": 2},
                    "reference_type": "direct",
                    "exclusions": [r"^https?://", r"^mailto:"],
                },
            ],
        }

'''
    
    # Insert the fixture before the test class
    class_pattern = r'class TestPatternExtractionEdgeCases:'
    content = re.sub(class_pattern, fixture_def + 'class TestPatternExtractionEdgeCases:', content)
    
    with open(test_file, 'w') as f:
        f.write(content)
    
    print("✅ Fixed pattern extraction test issues")

if __name__ == "__main__":
    fix_pattern_tests()
