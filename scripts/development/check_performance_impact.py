#!/usr/bin/env python3
"""
ACGS-PGP Performance Impact Checker
Analyzes code changes for potential performance impacts before commit.
Constitutional Hash: cdd01ef066bc6cf2
"""

import ast
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Performance impact patterns to check
PERFORMANCE_PATTERNS = {
    "nested_loops": {
        "pattern": r"for\s+.*\s+in\s+.*:\s*\n\s*for\s+.*\s+in\s+.*:",
        "severity": "high",
        "message": "Nested loops detected - O(n²) complexity",
    },
    "n_plus_one_query": {
        "pattern": r"for\s+.*\s+in\s+.*:\s*\n.*\.(get|filter|select|query)\(",
        "severity": "high",
        "message": "Potential N+1 query pattern detected",
    },
    "sync_in_async": {
        "pattern": r"async\s+def.*\n(?:.*\n)*?\s+(?!await)[a-zA-Z_]+\.(get|post|put|delete|query|execute)\(",
        "severity": "medium",
        "message": "Synchronous operation in async function",
    },
    "large_memory_allocation": {
        "pattern": r"(\[\]\s*\*\s*[0-9]{6,}|list\(range\([0-9]{6,}\)\))",
        "severity": "medium",
        "message": "Large memory allocation detected",
    },
    "unbounded_cache": {
        "pattern": r"@(cache|lru_cache|cached)\s*\((?!.*maxsize)",
        "severity": "medium",
        "message": "Unbounded cache detected - potential memory leak",
    },
    "no_pagination": {
        "pattern": r"\.(all\(\)|fetchall\(\))\s*(?!.*limit|offset|paginate)",
        "severity": "medium",
        "message": "Fetching all records without pagination",
    },
    "blocking_io": {
        "pattern": r"(time\.sleep|requests\.|urllib\.|open\(|file\()",
        "severity": "low",
        "message": "Blocking I/O operation detected",
    },
}


# AST-based checks
class PerformanceAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze performance issues in Python code."""

    def __init__(self):
        self.issues: List[Tuple[int, str, str]] = []
        self.in_async_function = False
        self.loop_depth = 0

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function context."""
        prev_async = self.in_async_function
        self.in_async_function = True
        self.generic_visit(node)
        self.in_async_function = prev_async

    def visit_For(self, node: ast.For) -> None:
        """Track loop depth for nested loop detection."""
        self.loop_depth += 1
        if self.loop_depth > 2:
            self.issues.append(
                (
                    node.lineno,
                    "high",
                    f"Deeply nested loops ({self.loop_depth} levels) - O(n^{self.loop_depth}) complexity",
                )
            )
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_Call(self, node: ast.Call) -> None:
        """Check for performance-impacting function calls."""
        # Check for list comprehensions that could be generators
        if isinstance(node.func, ast.Name):
            if node.func.id == "list" and len(node.args) == 1:
                if isinstance(node.args[0], ast.GeneratorExp):
                    self.issues.append(
                        (
                            node.lineno,
                            "low",
                            "Consider using generator instead of list() for large datasets",
                        )
                    )

        # Check for synchronous HTTP calls in async context
        if self.in_async_function:
            if isinstance(node.func, ast.Attribute):
                if hasattr(node.func.value, "id") and node.func.value.id == "requests":
                    self.issues.append(
                        (
                            node.lineno,
                            "high",
                            "Synchronous HTTP call in async function - use aiohttp instead",
                        )
                    )

        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Check for inefficient list comprehensions."""
        # Check if list comprehension is used where generator would be better
        parent = getattr(node, "parent", None)
        if parent and isinstance(parent, ast.Call):
            if hasattr(parent.func, "id") and parent.func.id in (
                "sum",
                "any",
                "all",
                "min",
                "max",
            ):
                self.issues.append(
                    (
                        node.lineno,
                        "low",
                        f"Use generator expression instead of list comprehension with {parent.func.id}()",
                    )
                )
        self.generic_visit(node)


def check_file_performance(filepath: Path) -> List[Dict[str, Any]]:
    """Check a single file for performance issues."""
    issues = []

    try:
        content = filepath.read_text()

        # Skip if file is too small to have performance issues
        if len(content) < 100:
            return issues

        # Regex-based pattern matching
        for pattern_name, pattern_info in PERFORMANCE_PATTERNS.items():
            matches = re.finditer(
                pattern_info["pattern"], content, re.MULTILINE | re.IGNORECASE
            )
            for match in matches:
                line_num = content[: match.start()].count("\n") + 1
                issues.append(
                    {
                        "file": str(filepath),
                        "line": line_num,
                        "severity": pattern_info["severity"],
                        "message": pattern_info["message"],
                        "pattern": pattern_name,
                    }
                )

        # AST-based analysis for Python files
        if filepath.suffix == ".py":
            try:
                tree = ast.parse(content)
                analyzer = PerformanceAnalyzer()
                analyzer.visit(tree)

                for line, severity, message in analyzer.issues:
                    issues.append(
                        {
                            "file": str(filepath),
                            "line": line,
                            "severity": severity,
                            "message": message,
                            "pattern": "ast_analysis",
                        }
                    )
            except SyntaxError:
                # Skip files with syntax errors
                pass

    except Exception as e:
        print(f"Error analyzing {filepath}: {e}", file=sys.stderr)

    return issues


def check_constitutional_compliance(issues: List[Dict[str, Any]]) -> bool:
    """Ensure performance checks align with constitutional requirements."""
    # Constitutional hash validation
    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

    # Check if any high-severity issues violate response time requirements
    high_severity_count = sum(1 for issue in issues if issue["severity"] == "high")

    # P99 ≤2s requirement means we can't have too many high-severity issues
    if high_severity_count > 3:
        print(f"\n⚠️  Constitutional Compliance Warning (Hash: {CONSTITUTIONAL_HASH})")
        print(
            f"Too many high-severity performance issues ({high_severity_count}) may violate P99 ≤2s requirement"
        )
        return False

    return True


def main():
    """Main entry point for performance impact checker."""
    if len(sys.argv) < 2:
        print("No files provided for performance analysis")
        return 0

    all_issues = []

    for filepath_str in sys.argv[1:]:
        filepath = Path(filepath_str)
        if filepath.exists() and filepath.is_file():
            issues = check_file_performance(filepath)
            all_issues.extend(issues)

    if not all_issues:
        print("✅ No performance issues detected")
        return 0

    # Group issues by severity
    issues_by_severity = {"high": [], "medium": [], "low": []}
    for issue in all_issues:
        issues_by_severity[issue["severity"]].append(issue)

    # Display issues
    print("\n🔍 Performance Impact Analysis Results")
    print("=" * 60)

    for severity in ["high", "medium", "low"]:
        if issues_by_severity[severity]:
            print(
                f"\n{severity.upper()} severity issues ({len(issues_by_severity[severity])})"
            )
            print("-" * 40)
            for issue in issues_by_severity[severity]:
                print(f"{issue['file']}:{issue['line']} - {issue['message']}")

    # Check constitutional compliance
    if not check_constitutional_compliance(all_issues):
        print("\n❌ Performance issues may violate constitutional requirements")
        return 1

    # Fail if high-severity issues found
    if issues_by_severity["high"]:
        print(
            f"\n❌ Found {len(issues_by_severity['high'])} high-severity performance issues"
        )
        return 1

    print(f"\n⚠️  Found {len(all_issues)} performance warnings - please review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
