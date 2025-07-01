#!/usr/bin/env python3
"""
Academic Submission System Build Script

Orchestrates the complete build process including:
- LaTeX paper compilation
- Python package building
- Documentation generation
- Testing and validation
- Deployment preparation

Usage:
    python build.py                    # Full build
    python build.py --quick            # Quick build (no tests)
    python build.py --latex-only       # LaTeX only
    python build.py --package-only     # Package only
    python build.py --release          # Release build with all checks
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class BuildConfig:
    """Build configuration settings."""

    latex_engine: str = "pdflatex"
    venue_optimization: str | None = None
    run_tests: bool = True
    run_linting: bool = True
    generate_docs: bool = True
    create_package: bool = True
    verbose: bool = False
    clean_first: bool = True


@dataclass
class BuildResult:
    """Result of a build step."""

    step_name: str
    success: bool
    duration: float
    output_files: list[str]
    warnings: list[str]
    errors: list[str]


class BuildOrchestrator:
    """Orchestrates the complete build process."""

    def __init__(self, config: BuildConfig):
        """Initialize the build orchestrator."""
        self.config = config
        self.base_dir = Path().resolve()
        self.build_dir = self.base_dir / "build"
        self.results: list[BuildResult] = []
        self.start_time = time.time()

        # Ensure build directory exists
        self.build_dir.mkdir(exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        if self.config.verbose or level in ["ERROR", "WARNING"]:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")

    def run_command(self, cmd: list[str], step_name: str) -> BuildResult:
        """Run a command and track the result."""
        self.log(f"Starting {step_name}")
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            duration = time.time() - start_time
            success = result.returncode == 0

            # Parse output for files, warnings, errors
            output_files = []
            warnings = []
            errors = []

            if result.stdout:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "warning" in line.lower():
                        warnings.append(line.strip())
                    elif "error" in line.lower():
                        errors.append(line.strip())
                    elif any(ext in line for ext in [".pdf", ".tar.gz", ".whl", ".md"]):
                        output_files.append(line.strip())

            if result.stderr and not success:
                errors.extend(result.stderr.split("\n"))

            build_result = BuildResult(
                step_name=step_name,
                success=success,
                duration=duration,
                output_files=output_files,
                warnings=warnings,
                errors=errors,
            )

            self.results.append(build_result)

            if success:
                self.log(f"✅ {step_name} completed in {duration:.2f}s")
            else:
                self.log(f"❌ {step_name} failed after {duration:.2f}s", "ERROR")
                if errors:
                    for error in errors[:3]:  # Show first 3 errors
                        self.log(f"  {error}", "ERROR")

            return build_result

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            build_result = BuildResult(
                step_name=step_name,
                success=False,
                duration=duration,
                output_files=[],
                warnings=[],
                errors=[f"{step_name} timed out after {duration:.0f}s"],
            )
            self.results.append(build_result)
            self.log(f"❌ {step_name} timed out", "ERROR")
            return build_result

        except Exception as e:
            duration = time.time() - start_time
            build_result = BuildResult(
                step_name=step_name,
                success=False,
                duration=duration,
                output_files=[],
                warnings=[],
                errors=[str(e)],
            )
            self.results.append(build_result)
            self.log(f"❌ {step_name} failed: {e}", "ERROR")
            return build_result

    def clean_build_artifacts(self) -> BuildResult:
        """Clean previous build artifacts."""
        if not self.config.clean_first:
            return BuildResult("clean", True, 0, [], [], [])

        return self.run_command(
            [sys.executable, "compiler.py", "clean"], "Clean Build Artifacts"
        )

    def compile_latex(self) -> BuildResult:
        """Compile LaTeX paper."""
        cmd = [sys.executable, "latex_compiler.py"]

        if self.config.venue_optimization:
            cmd.extend(["--optimize", self.config.venue_optimization])

        if self.config.verbose:
            cmd.append("--verbose")

        return self.run_command(cmd, "LaTeX Compilation")

    def run_tests(self) -> BuildResult:
        """Run test suite."""
        if not self.config.run_tests:
            return BuildResult("tests", True, 0, [], [], [])

        return self.run_command(
            [sys.executable, "-m", "pytest", "tests/unit/", "-x", "--tb=short"],
            "Unit Tests",
        )

    def run_linting(self) -> BuildResult:
        """Run code linting."""
        if not self.config.run_linting:
            return BuildResult("linting", True, 0, [], [], [])

        return self.run_command(
            ["flake8", "quality_assurance", "cli", "web", "--count", "--statistics"],
            "Code Linting",
        )

    def build_package(self) -> BuildResult:
        """Build Python package."""
        if not self.config.create_package:
            return BuildResult("package", True, 0, [], [], [])

        return self.run_command(
            [sys.executable, "compiler.py", "package"], "Package Build"
        )

    def generate_documentation(self) -> BuildResult:
        """Generate documentation."""
        if not self.config.generate_docs:
            return BuildResult("docs", True, 0, [], [], [])

        return self.run_command(
            [sys.executable, "compiler.py", "docs"], "Documentation Generation"
        )

    def validate_build(self) -> BuildResult:
        """Validate the complete build."""
        return self.run_command(
            [sys.executable, "compiler.py", "validate"], "Build Validation"
        )

    def run_full_build(self) -> dict[str, BuildResult]:
        """Run the complete build process."""
        self.log("🚀 Starting Academic Submission System build")

        build_steps = [
            ("clean", self.clean_build_artifacts),
            ("latex", self.compile_latex),
            ("tests", self.run_tests),
            ("linting", self.run_linting),
            ("package", self.build_package),
            ("docs", self.generate_documentation),
            ("validate", self.validate_build),
        ]

        results = {}

        for step_name, step_function in build_steps:
            result = step_function()
            results[step_name] = result

            # Stop on critical failures (except for linting and tests in quick mode)
            if not result.success:
                if step_name in ["latex", "package"] or (
                    step_name in ["tests", "linting"] and not self.config.run_tests
                ):
                    self.log(
                        f"❌ Critical step {step_name} failed, stopping build", "ERROR"
                    )
                    break
                self.log(
                    f"⚠️ Non-critical step {step_name} failed, continuing", "WARNING"
                )

        total_duration = time.time() - self.start_time
        successful_steps = sum(1 for r in results.values() if r.success)
        total_steps = len(results)

        self.log(f"🏁 Build completed in {total_duration:.2f}s")
        self.log(f"📊 Success rate: {successful_steps}/{total_steps} steps")

        if successful_steps == total_steps:
            self.log("✅ Build successful!")
        else:
            self.log("❌ Build completed with issues", "WARNING")

        return results

    def generate_build_report(self, results: dict[str, BuildResult]) -> str:
        """Generate a comprehensive build report."""
        total_duration = time.time() - self.start_time
        successful_steps = sum(1 for r in results.values() if r.success)
        total_steps = len(results)

        report_lines = [
            "# Academic Submission System Build Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Build Configuration",
            f"- LaTeX Engine: {self.config.latex_engine}",
            f"- Venue Optimization: {self.config.venue_optimization or 'None'}",
            f"- Run Tests: {self.config.run_tests}",
            f"- Run Linting: {self.config.run_linting}",
            f"- Generate Docs: {self.config.generate_docs}",
            f"- Create Package: {self.config.create_package}",
            "",
            "## Build Summary",
            f"- **Total Duration**: {total_duration:.2f} seconds",
            f"- **Successful Steps**: {successful_steps}/{total_steps}",
            f"- **Overall Status**: {'✅ SUCCESS' if successful_steps == total_steps else '❌ PARTIAL FAILURE'}",
            "",
        ]

        # Step details
        for step_name, result in results.items():
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            report_lines.extend(
                [
                    f"### {step_name.title()}",
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
                for file_path in result.output_files[:10]:  # Limit to 10 files
                    report_lines.append(f"- {file_path}")
                if len(result.output_files) > 10:
                    report_lines.append(
                        f"- ... and {len(result.output_files) - 10} more"
                    )
                report_lines.append("")

            if result.warnings:
                report_lines.append("**Warnings:**")
                for warning in result.warnings[:5]:  # Limit to 5 warnings
                    report_lines.append(f"- {warning}")
                if len(result.warnings) > 5:
                    report_lines.append(f"- ... and {len(result.warnings) - 5} more")
                report_lines.append("")

            if result.errors:
                report_lines.append("**Errors:**")
                for error in result.errors[:5]:  # Limit to 5 errors
                    report_lines.append(f"- {error}")
                if len(result.errors) > 5:
                    report_lines.append(f"- ... and {len(result.errors) - 5} more")
                report_lines.append("")

        # Build artifacts summary
        all_output_files = []
        for result in results.values():
            all_output_files.extend(result.output_files)

        if all_output_files:
            report_lines.extend(["## Build Artifacts", ""])

            # Group by type
            pdfs = [f for f in all_output_files if f.endswith(".pdf")]
            packages = [f for f in all_output_files if f.endswith((".tar.gz", ".whl"))]
            docs = [f for f in all_output_files if f.endswith(".md")]

            if pdfs:
                report_lines.append("**PDF Documents:**")
                for pdf in pdfs:
                    report_lines.append(f"- {pdf}")
                report_lines.append("")

            if packages:
                report_lines.append("**Python Packages:**")
                for pkg in packages:
                    report_lines.append(f"- {pkg}")
                report_lines.append("")

            if docs:
                report_lines.append("**Documentation:**")
                for doc in docs[:5]:  # Limit to 5 docs
                    report_lines.append(f"- {doc}")
                if len(docs) > 5:
                    report_lines.append(f"- ... and {len(docs) - 5} more")
                report_lines.append("")

        return "\n".join(report_lines)

    def save_build_metadata(self, results: dict[str, BuildResult]):
        """Save build metadata as JSON."""
        metadata = {
            "build_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_duration": time.time() - self.start_time,
            "config": asdict(self.config),
            "results": {name: asdict(result) for name, result in results.items()},
            "success": all(r.success for r in results.values()),
        }

        metadata_file = self.build_dir / "build_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        self.log(f"Build metadata saved to {metadata_file}")


def main():
    """Main entry point for the build script."""
    parser = argparse.ArgumentParser(
        description="Academic Submission System Build Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Quick build (skip tests and linting)",
    )

    parser.add_argument("--latex-only", action="store_true", help="Compile LaTeX only")

    parser.add_argument(
        "--package-only", action="store_true", help="Build Python package only"
    )

    parser.add_argument(
        "--release", action="store_true", help="Release build with all checks"
    )

    parser.add_argument(
        "--engine",
        choices=["pdflatex", "xelatex", "lualatex"],
        default="pdflatex",
        help="LaTeX engine to use",
    )

    parser.add_argument(
        "--venue", choices=["arxiv", "ieee", "acm"], help="Optimize for specific venue"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--no-clean", action="store_true", help="Don't clean before building"
    )

    parser.add_argument(
        "--report", "-r", action="store_true", help="Generate build report"
    )

    args = parser.parse_args()

    # Configure build
    config = BuildConfig(
        latex_engine=args.engine,
        venue_optimization=args.venue,
        run_tests=not args.quick and not args.latex_only,
        run_linting=not args.quick and not args.latex_only,
        generate_docs=not args.latex_only and not args.package_only,
        create_package=not args.latex_only,
        verbose=args.verbose,
        clean_first=not args.no_clean,
    )

    if args.release:
        config.run_tests = True
        config.run_linting = True
        config.generate_docs = True
        config.create_package = True

    # Run build
    orchestrator = BuildOrchestrator(config)

    if args.latex_only:
        result = orchestrator.compile_latex()
        results = {"latex": result}
    elif args.package_only:
        result = orchestrator.build_package()
        results = {"package": result}
    else:
        results = orchestrator.run_full_build()

    # Generate report if requested
    if args.report:
        report = orchestrator.generate_build_report(results)
        report_file = Path("build_report.md")
        with open(report_file, "w") as f:
            f.write(report)
        print(f"Build report saved to {report_file}")

    # Save metadata
    orchestrator.save_build_metadata(results)

    # Exit with appropriate code
    all_successful = all(result.success for result in results.values())
    sys.exit(0 if all_successful else 1)


if __name__ == "__main__":
    main()
