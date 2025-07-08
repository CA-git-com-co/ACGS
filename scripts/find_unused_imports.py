#!/usr/bin/env python3
"""Find unused imports in Python files."""

import ast
import os
from collections import defaultdict
from pathlib import Path


class UnusedImportFinder(ast.NodeVisitor):
    def __init__(self):
        self.imports = {}  # name -> (module, alias, lineno)
        self.used_names = set()
        self.star_imports = []  # List of star imports (module, lineno)

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = (alias.name, alias.asname, node.lineno)

    def visit_ImportFrom(self, node):
        if node.module is None:
            return
        for alias in node.names:
            if alias.name == "*":
                self.star_imports.append((node.module, node.lineno))
            else:
                name = alias.asname if alias.asname else alias.name
                self.imports[name] = (
                    f"{node.module}.{alias.name}",
                    alias.asname,
                    node.lineno,
                )

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
            # Also check for module.attribute access
            parts = node.id.split(".")
            if parts:
                self.used_names.add(parts[0])

    def visit_Attribute(self, node):
        # Handle cases like module.submodule.function
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        self.generic_visit(node)

    def get_unused_imports(self):
        unused = []
        for name, (module, alias, lineno) in self.imports.items():
            if name not in self.used_names:
                # Check if it's used as part of a larger expression
                if not any(used.startswith(name + ".") for used in self.used_names):
                    unused.append((name, module, alias, lineno))
        return unused


def analyze_file(
    filepath: Path,
) -> tuple[list[tuple[str, str, str, int]], list[tuple[str, int]]]:
    """Analyze a Python file for unused imports."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        finder = UnusedImportFinder()
        finder.visit(tree)

        return finder.get_unused_imports(), finder.star_imports
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return [], []


def find_dead_code(filepath: Path) -> dict[str, list[tuple[str, int]]]:
    """Find potentially dead code (unused functions, classes, variables)."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        # Track definitions and usages
        definitions = {
            "functions": {},  # name -> lineno
            "classes": {},  # name -> lineno
            "variables": {},  # name -> lineno
        }

        used_names = set()

        class DeadCodeFinder(ast.NodeVisitor):
            def __init__(self):
                self.in_function = False
                self.in_class = False
                self.current_scope = []

            def visit_FunctionDef(self, node):
                if not self.in_function and not node.name.startswith("_"):
                    definitions["functions"][node.name] = node.lineno
                old_in_function = self.in_function
                self.in_function = True
                self.generic_visit(node)
                self.in_function = old_in_function

            def visit_AsyncFunctionDef(self, node):
                if not self.in_function and not node.name.startswith("_"):
                    definitions["functions"][node.name] = node.lineno
                old_in_function = self.in_function
                self.in_function = True
                self.generic_visit(node)
                self.in_function = old_in_function

            def visit_ClassDef(self, node):
                if not self.in_class:
                    definitions["classes"][node.name] = node.lineno
                old_in_class = self.in_class
                self.in_class = True
                self.generic_visit(node)
                self.in_class = old_in_class

            def visit_Assign(self, node):
                # Only track module-level assignments
                if not self.in_function and not self.in_class:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if not target.id.startswith("_") and target.id.isupper():
                                definitions["variables"][target.id] = node.lineno
                self.generic_visit(node)

            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
                self.generic_visit(node)

            def visit_Attribute(self, node):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
                self.generic_visit(node)

        finder = DeadCodeFinder()
        finder.visit(tree)

        # Find unused definitions
        dead_code = defaultdict(list)

        for func_name, lineno in definitions["functions"].items():
            if func_name not in used_names and func_name != "main":
                dead_code["functions"].append((func_name, lineno))

        for class_name, lineno in definitions["classes"].items():
            if class_name not in used_names:
                dead_code["classes"].append((class_name, lineno))

        for var_name, lineno in definitions["variables"].items():
            if var_name not in used_names:
                dead_code["variables"].append((var_name, lineno))

        return dict(dead_code)

    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return {}


def main():
    # Focus on services/core and services/shared
    directories = ["services/core", "services/shared"]

    total_files = 0
    files_with_issues = 0

    for directory in directories:
        if not os.path.exists(directory):
            continue

        print(f"\n{'=' * 80}")
        print(f"Analyzing {directory}")
        print(f"{'=' * 80}\n")

        for root, dirs, files in os.walk(directory):
            # Skip __pycache__ and migration directories
            dirs[:] = [
                d for d in dirs if d not in ["__pycache__", ".pytest_cache", "alembic"]
            ]

            for file in files:
                if file.endswith(".py"):
                    filepath = Path(root) / file
                    total_files += 1

                    unused_imports, star_imports = analyze_file(filepath)
                    dead_code = find_dead_code(filepath)

                    if unused_imports or star_imports or dead_code:
                        files_with_issues += 1
                        print(f"\n{filepath}")
                        print("-" * len(str(filepath)))

                        if unused_imports:
                            print("\nUnused imports:")
                            for name, module, alias, lineno in unused_imports:
                                if alias:
                                    print(f"  Line {lineno}: {module} as {alias}")
                                else:
                                    print(f"  Line {lineno}: {name} (from {module})")

                        if star_imports:
                            print("\nStar imports (avoid these):")
                            for module, lineno in star_imports:
                                print(f"  Line {lineno}: from {module} import *")

                        if dead_code:
                            if dead_code.get("functions"):
                                print("\nPotentially unused functions:")
                                for name, lineno in dead_code["functions"]:
                                    print(f"  Line {lineno}: def {name}(...)")

                            if dead_code.get("classes"):
                                print("\nPotentially unused classes:")
                                for name, lineno in dead_code["classes"]:
                                    print(f"  Line {lineno}: class {name}")

                            if dead_code.get("variables"):
                                print("\nPotentially unused variables:")
                                for name, lineno in dead_code["variables"]:
                                    print(f"  Line {lineno}: {name}")

    print(f"\n{'=' * 80}")
    print(f"Summary: Found issues in {files_with_issues}/{total_files} files")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
