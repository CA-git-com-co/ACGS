#!/usr/bin/env python3
"""
Academic Submission System Compiler

A comprehensive compilation system that handles:
1. LaTeX paper compilation with error handling and optimization
2. Python package building and distribution
3. Documentation generation
4. Asset optimization and validation
5. Deployment package creation

Usage:
    python compiler.py latex          # Compile LaTeX paper
    python compiler.py package        # Build Python package
    python compiler.py docs           # Generate documentation
    python compiler.py all            # Compile everything
    python compiler.py clean          # Clean build artifacts
    python compiler.py validate       # Validate compilation
"""

import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class CompilationType(Enum):
    """Types of compilation supported."""

    LATEX = "latex"
    PACKAGE = "package"
    DOCS = "docs"
    ALL = "all"
    CLEAN = "clean"
    VALIDATE = "validate"


@dataclass
class CompilationResult:
    """Result of a compilation operation."""

    success: bool
    compilation_type: str
    duration: float
    output_files: list[str]
    warnings: list[str]
    errors: list[str]
    log_file: str | None = None


class AcademicCompiler:
    """Main compiler class for the Academic Submission System."""

    def __init__(self, base_dir: str = "."):
        """Initialize the compiler with base directory."""
        self.base_dir = Path(base_dir).resolve()
        self.build_dir = self.base_dir / "build"
        self.dist_dir = self.base_dir / "dist"
        self.logs_dir = self.base_dir / "logs"

        # Create necessary directories
        for dir_path in [self.build_dir, self.dist_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)

        # Configuration
        self.latex_engine = "pdflatex"
        self.bibtex_engine = "bibtex"
        self.max_latex_runs = 4
        self.verbose = False

    def set_verbose(self, verbose: bool = True):
        """Enable or disable verbose output."""
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}"

        if self.verbose or level in ["ERROR", "WARNING"]:
            print(log_message)

        # Write to log file
        log_file = self.logs_dir / "compiler.log"
        with open(log_file, "a") as f:
            f.write(log_message + "\n")

    def run_command(
        self, cmd: list[str], cwd: Path | None = None, capture_output: bool = True
    ) -> tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        if cwd is None:
            cwd = self.base_dir

        self.log(f"Running command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                check=False,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            self.log("Command timed out", "ERROR")
            return 1, "", "Command timed out"
        except FileNotFoundError:
            self.log(f"Command not found: {cmd[0]}", "ERROR")
            return 1, "", f"Command not found: {cmd[0]}"

    def compile_latex(self) -> CompilationResult:
        """Compile LaTeX paper with full bibliography and cross-references."""
        self.log("Starting LaTeX compilation")
        start_time = time.time()

        main_tex = self.base_dir / "main.tex"
        if not main_tex.exists():
            error_msg = "main.tex not found"
            self.log(error_msg, "ERROR")
            return CompilationResult(
                success=False,
                compilation_type="latex",
                duration=0,
                output_files=[],
                warnings=[],
                errors=[error_msg],
            )

        warnings = []
        errors = []
        output_files = []

        # Step 1: First LaTeX run
        self.log("Running first LaTeX compilation")
        exit_code, stdout, stderr = self.run_command([self.latex_engine, "main.tex"])

        if exit_code != 0:
            errors.append(f"First LaTeX run failed: {stderr}")
            self.log(f"LaTeX compilation failed: {stderr}", "ERROR")
        else:
            self.log("First LaTeX run completed successfully")
            if "main.aux" in stdout or Path("main.aux").exists():
                output_files.append("main.aux")

        # Step 2: BibTeX run (if bibliography exists)
        bib_files = list(self.base_dir.glob("*.bib"))
        if bib_files and exit_code == 0:
            self.log("Running BibTeX compilation")
            exit_code, stdout, stderr = self.run_command([self.bibtex_engine, "main"])

            if exit_code != 0:
                warnings.append(f"BibTeX run had issues: {stderr}")
                self.log(f"BibTeX warning: {stderr}", "WARNING")
            else:
                self.log("BibTeX run completed successfully")
                if "main.bbl" in stdout or Path("main.bbl").exists():
                    output_files.append("main.bbl")

        # Step 3: Second LaTeX run (for bibliography)
        if exit_code == 0:
            self.log("Running second LaTeX compilation")
            exit_code, stdout, stderr = self.run_command(
                [self.latex_engine, "main.tex"]
            )

            if exit_code != 0:
                errors.append(f"Second LaTeX run failed: {stderr}")
                self.log(f"Second LaTeX run failed: {stderr}", "ERROR")
            else:
                self.log("Second LaTeX run completed successfully")

        # Step 4: Third LaTeX run (for cross-references)
        if exit_code == 0:
            self.log("Running final LaTeX compilation")
            exit_code, stdout, stderr = self.run_command(
                [self.latex_engine, "main.tex"]
            )

            if exit_code != 0:
                errors.append(f"Final LaTeX run failed: {stderr}")
                self.log(f"Final LaTeX run failed: {stderr}", "ERROR")
            else:
                self.log("Final LaTeX run completed successfully")
                if Path("main.pdf").exists():
                    output_files.append("main.pdf")

        # Check for warnings in log file
        log_file = Path("main.log")
        if log_file.exists():
            with open(log_file) as f:
                log_content = f.read()
                if "Warning" in log_content:
                    warnings.append("LaTeX warnings found in log file")
                if "Error" in log_content and exit_code == 0:
                    warnings.append("LaTeX errors found but compilation succeeded")

        duration = time.time() - start_time
        success = exit_code == 0 and Path("main.pdf").exists()

        if success:
            self.log(f"LaTeX compilation completed successfully in {duration:.2f}s")
        else:
            self.log(f"LaTeX compilation failed after {duration:.2f}s", "ERROR")

        return CompilationResult(
            success=success,
            compilation_type="latex",
            duration=duration,
            output_files=output_files,
            warnings=warnings,
            errors=errors,
            log_file="main.log" if log_file.exists() else None,
        )

    def build_package(self) -> CompilationResult:
        """Build Python package distribution."""
        self.log("Starting Python package build")
        start_time = time.time()

        warnings = []
        errors = []
        output_files = []

        # Check if setup.py exists
        setup_py = self.base_dir / "setup.py"
        if not setup_py.exists():
            error_msg = "setup.py not found"
            self.log(error_msg, "ERROR")
            return CompilationResult(
                success=False,
                compilation_type="package",
                duration=0,
                output_files=[],
                warnings=[],
                errors=[error_msg],
            )

        # Clean previous builds
        for dir_name in ["build", "dist", "*.egg-info"]:
            for path in self.base_dir.glob(dir_name):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                    self.log(f"Cleaned {path}")

        # Build source distribution
        self.log("Building source distribution")
        exit_code, stdout, stderr = self.run_command(
            [sys.executable, "setup.py", "sdist"]
        )

        if exit_code != 0:
            errors.append(f"Source distribution build failed: {stderr}")
            self.log(f"sdist failed: {stderr}", "ERROR")
        else:
            self.log("Source distribution built successfully")
            # Find generated files
            for tar_file in self.base_dir.glob("dist/*.tar.gz"):
                output_files.append(str(tar_file.relative_to(self.base_dir)))

        # Build wheel distribution
        if exit_code == 0:
            self.log("Building wheel distribution")
            exit_code, stdout, stderr = self.run_command(
                [sys.executable, "setup.py", "bdist_wheel"]
            )

            if exit_code != 0:
                warnings.append(f"Wheel build had issues: {stderr}")
                self.log(f"bdist_wheel warning: {stderr}", "WARNING")
            else:
                self.log("Wheel distribution built successfully")
                # Find generated files
                for whl_file in self.base_dir.glob("dist/*.whl"):
                    output_files.append(str(whl_file.relative_to(self.base_dir)))

        # Validate distributions
        if output_files:
            self.log("Validating distributions with twine")
            exit_code, stdout, stderr = self.run_command(
                [sys.executable, "-m", "twine", "check", "dist/*"]
            )

            if exit_code != 0:
                warnings.append(f"Distribution validation issues: {stderr}")
                self.log(f"twine check warning: {stderr}", "WARNING")
            else:
                self.log("Distribution validation passed")

        duration = time.time() - start_time
        success = len(output_files) > 0 and len(errors) == 0

        if success:
            self.log(f"Package build completed successfully in {duration:.2f}s")
        else:
            self.log(f"Package build failed after {duration:.2f}s", "ERROR")

        return CompilationResult(
            success=success,
            compilation_type="package",
            duration=duration,
            output_files=output_files,
            warnings=warnings,
            errors=errors,
        )

    def generate_docs(self) -> CompilationResult:
        """Generate documentation."""
        self.log("Starting documentation generation")
        start_time = time.time()

        warnings = []
        errors = []
        output_files = []

        # Check if docs directory exists
        docs_dir = self.base_dir / "docs"
        if not docs_dir.exists():
            error_msg = "docs directory not found"
            self.log(error_msg, "ERROR")
            return CompilationResult(
                success=False,
                compilation_type="docs",
                duration=0,
                output_files=[],
                warnings=[],
                errors=[error_msg],
            )

        # Count markdown files
        md_files = list(docs_dir.rglob("*.md"))
        self.log(f"Found {len(md_files)} markdown files")

        for md_file in md_files:
            output_files.append(str(md_file.relative_to(self.base_dir)))

        # Validate markdown files
        for md_file in md_files:
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()
                    if len(content.strip()) == 0:
                        warnings.append(f"Empty documentation file: {md_file}")
                    elif len(content) < 100:
                        warnings.append(f"Very short documentation file: {md_file}")
            except Exception as e:
                errors.append(f"Error reading {md_file}: {e}")

        # Check for required documentation files
        required_docs = [
            "README.md",
            "USER_GUIDE.md",
            "API_REFERENCE.md",
            "TUTORIAL.md",
        ]

        for req_doc in required_docs:
            if not any(req_doc in str(md_file) for md_file in md_files):
                warnings.append(f"Missing required documentation: {req_doc}")

        duration = time.time() - start_time
        success = len(errors) == 0 and len(output_files) > 0

        if success:
            self.log(f"Documentation generation completed in {duration:.2f}s")
        else:
            self.log(f"Documentation generation failed after {duration:.2f}s", "ERROR")

        return CompilationResult(
            success=success,
            compilation_type="docs",
            duration=duration,
            output_files=output_files,
            warnings=warnings,
            errors=errors,
        )

    def clean_build_artifacts(self) -> CompilationResult:
        """Clean all build artifacts."""
        self.log("Starting cleanup of build artifacts")
        start_time = time.time()

        cleaned_files = []
        errors = []

        # LaTeX artifacts
        latex_extensions = [
            "*.aux",
            "*.bbl",
            "*.blg",
            "*.fdb_latexmk",
            "*.fls",
            "*.log",
            "*.out",
            "*.toc",
            "*.lof",
            "*.lot",
            "*.synctex.gz",
        ]

        for pattern in latex_extensions:
            for file_path in self.base_dir.glob(pattern):
                try:
                    file_path.unlink()
                    cleaned_files.append(str(file_path.relative_to(self.base_dir)))
                    self.log(f"Removed {file_path}")
                except Exception as e:
                    errors.append(f"Failed to remove {file_path}: {e}")

        # Python artifacts
        python_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.egg-info",
            "build",
            "dist",
            ".pytest_cache",
            ".mypy_cache",
            ".coverage",
            "htmlcov",
        ]

        for pattern in python_patterns:
            for path in self.base_dir.glob(pattern):
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    cleaned_files.append(str(path.relative_to(self.base_dir)))
                    self.log(f"Removed {path}")
                except Exception as e:
                    errors.append(f"Failed to remove {path}: {e}")

        duration = time.time() - start_time
        success = len(errors) == 0

        self.log(
            f"Cleanup completed in {duration:.2f}s, removed {len(cleaned_files)} items"
        )

        return CompilationResult(
            success=success,
            compilation_type="clean",
            duration=duration,
            output_files=cleaned_files,
            warnings=[],
            errors=errors,
        )

    def validate_compilation(self) -> CompilationResult:
        """Validate that all compilation outputs are correct."""
        self.log("Starting compilation validation")
        start_time = time.time()

        warnings = []
        errors = []
        validated_files = []

        # Check LaTeX output
        pdf_file = self.base_dir / "main.pdf"
        if pdf_file.exists():
            validated_files.append("main.pdf")
            # Check PDF file size
            pdf_size = pdf_file.stat().st_size
            if pdf_size < 1000:  # Less than 1KB
                warnings.append("PDF file is very small, may be corrupted")
            elif pdf_size > 50 * 1024 * 1024:  # More than 50MB
                warnings.append("PDF file is very large")
            self.log(f"PDF file size: {pdf_size / 1024:.1f} KB")
        else:
            errors.append("main.pdf not found")

        # Check Python package
        dist_files = list(self.base_dir.glob("dist/*"))
        if dist_files:
            for dist_file in dist_files:
                validated_files.append(str(dist_file.relative_to(self.base_dir)))
            self.log(f"Found {len(dist_files)} distribution files")
        else:
            warnings.append("No Python distribution files found")

        # Check documentation
        docs_dir = self.base_dir / "docs"
        if docs_dir.exists():
            doc_files = list(docs_dir.rglob("*.md"))
            for doc_file in doc_files:
                validated_files.append(str(doc_file.relative_to(self.base_dir)))
            self.log(f"Found {len(doc_files)} documentation files")
        else:
            warnings.append("Documentation directory not found")

        # Run basic tests if available
        if (self.base_dir / "tests").exists():
            self.log("Running basic validation tests")
            exit_code, stdout, stderr = self.run_command(
                [sys.executable, "-m", "pytest", "tests/", "-x", "--tb=short"]
            )

            if exit_code != 0:
                warnings.append(f"Some tests failed: {stderr}")
            else:
                self.log("Basic tests passed")

        duration = time.time() - start_time
        success = len(errors) == 0

        if success:
            self.log(f"Validation completed successfully in {duration:.2f}s")
        else:
            self.log(f"Validation found issues after {duration:.2f}s", "ERROR")

        return CompilationResult(
            success=success,
            compilation_type="validate",
            duration=duration,
            output_files=validated_files,
            warnings=warnings,
            errors=errors,
        )

    def compile_all(self) -> dict[str, CompilationResult]:
        """Compile everything in the correct order."""
        self.log("Starting complete compilation")

        results = {}

        # Step 1: Clean previous builds
        results["clean"] = self.clean_build_artifacts()

        # Step 2: Compile LaTeX
        results["latex"] = self.compile_latex()

        # Step 3: Build Python package
        results["package"] = self.build_package()

        # Step 4: Generate documentation
        results["docs"] = self.generate_docs()

        # Step 5: Validate everything
        results["validate"] = self.validate_compilation()

        # Summary
        total_duration = sum(result.duration for result in results.values())
        successful_steps = sum(1 for result in results.values() if result.success)
        total_steps = len(results)

        self.log(f"Complete compilation finished in {total_duration:.2f}s")
        self.log(f"Successful steps: {successful_steps}/{total_steps}")

        return results

    def generate_report(self, results: dict[str, CompilationResult]) -> str:
        """Generate a compilation report."""
        report_lines = [
            "# Academic Submission System Compilation Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
        ]

        total_duration = sum(result.duration for result in results.values())
        successful_steps = sum(1 for result in results.values() if result.success)
        total_steps = len(results)

        report_lines.extend(
            [
                f"- **Total Duration**: {total_duration:.2f} seconds",
                f"- **Successful Steps**: {successful_steps}/{total_steps}",
                f"- **Overall Status**: {'✅ SUCCESS' if successful_steps == total_steps else '❌ PARTIAL FAILURE'}",
                "",
            ]
        )

        for step_name, result in results.items():
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            report_lines.extend(
                [
                    f"## {step_name.title()} Compilation",
                    f"- **Status**: {status}",
                    f"- **Duration**: {result.duration:.2f} seconds",
                    f"- **Output Files**: {len(result.output_files)}",
                    f"- **Warnings**: {len(result.warnings)}",
                    f"- **Errors**: {len(result.errors)}",
                    "",
                ]
            )

            if result.output_files:
                report_lines.append("**Output Files:**")
                for file_path in result.output_files:
                    report_lines.append(f"- {file_path}")
                report_lines.append("")

            if result.warnings:
                report_lines.append("**Warnings:**")
                for warning in result.warnings:
                    report_lines.append(f"- {warning}")
                report_lines.append("")

            if result.errors:
                report_lines.append("**Errors:**")
                for error in result.errors:
                    report_lines.append(f"- {error}")
                report_lines.append("")

        return "\n".join(report_lines)


def main():
    """Main entry point for the compiler."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Academic Submission System Compiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compiler.py latex          # Compile LaTeX paper
  python compiler.py package        # Build Python package  
  python compiler.py docs           # Generate documentation
  python compiler.py all            # Compile everything
  python compiler.py clean          # Clean build artifacts
  python compiler.py validate       # Validate compilation
        """,
    )

    parser.add_argument(
        "action",
        choices=["latex", "package", "docs", "all", "clean", "validate"],
        help="Compilation action to perform",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--report", "-r", action="store_true", help="Generate compilation report"
    )

    args = parser.parse_args()

    # Initialize compiler
    compiler = AcademicCompiler()
    compiler.set_verbose(args.verbose)

    # Perform compilation
    if args.action == "latex":
        result = compiler.compile_latex()
        results = {"latex": result}
    elif args.action == "package":
        result = compiler.build_package()
        results = {"package": result}
    elif args.action == "docs":
        result = compiler.generate_docs()
        results = {"docs": result}
    elif args.action == "clean":
        result = compiler.clean_build_artifacts()
        results = {"clean": result}
    elif args.action == "validate":
        result = compiler.validate_compilation()
        results = {"validate": result}
    elif args.action == "all":
        results = compiler.compile_all()

    # Generate report if requested
    if args.report:
        report = compiler.generate_report(results)
        report_file = Path("compilation_report.md")
        with open(report_file, "w") as f:
            f.write(report)
        print(f"Compilation report saved to {report_file}")

    # Exit with appropriate code
    all_successful = all(result.success for result in results.values())
    sys.exit(0 if all_successful else 1)


if __name__ == "__main__":
    main()
