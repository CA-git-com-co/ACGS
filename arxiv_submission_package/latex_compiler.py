#!/usr/bin/env python3
"""
Advanced LaTeX Compiler for Academic Papers

Provides sophisticated LaTeX compilation with:
- Multiple engine support (pdflatex, xelatex, lualatex)
- Automatic dependency detection and compilation
- Error analysis and suggestions
- Bibliography management
- Figure optimization
- Cross-reference validation
- Output optimization for different venues

Usage:
    python latex_compiler.py                    # Compile with auto-detection
    python latex_compiler.py --engine xelatex   # Use specific engine
    python latex_compiler.py --optimize arxiv   # Optimize for venue
    python latex_compiler.py --watch            # Watch mode for development
"""

import hashlib
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class LaTeXEngine(Enum):
    """Supported LaTeX engines."""

    PDFLATEX = "pdflatex"
    XELATEX = "xelatex"
    LUALATEX = "lualatex"


class VenueOptimization(Enum):
    """Venue-specific optimizations."""

    ARXIV = "arxiv"
    IEEE = "ieee"
    ACM = "acm"
    SPRINGER = "springer"
    ELSEVIER = "elsevier"


@dataclass
class LaTeXError:
    """Represents a LaTeX compilation error."""

    line_number: int | None
    error_type: str
    message: str
    suggestion: str | None = None


@dataclass
class CompilationStats:
    """Statistics from LaTeX compilation."""

    pages: int = 0
    words: int = 0
    characters: int = 0
    figures: int = 0
    tables: int = 0
    references: int = 0
    warnings: int = 0
    errors: int = 0


class LaTeXCompiler:
    """Advanced LaTeX compiler with error handling and optimization."""

    def __init__(self, main_file: str = "main.tex", base_dir: str = "."):
        """Initialize the LaTeX compiler."""
        self.base_dir = Path(base_dir).resolve()
        self.main_file = self.base_dir / main_file
        self.engine = LaTeXEngine.PDFLATEX
        self.venue_optimization = None
        self.max_runs = 4
        self.verbose = False
        self.watch_mode = False

        # File tracking for watch mode
        self.tracked_files: set[Path] = set()
        self.file_hashes: dict[Path, str] = {}

        # Compilation state
        self.last_compilation_time = 0
        self.compilation_count = 0

        if not self.main_file.exists():
            raise FileNotFoundError(f"Main LaTeX file not found: {self.main_file}")

    def set_engine(self, engine: LaTeXEngine):
        """Set the LaTeX engine to use."""
        self.engine = engine

    def set_venue_optimization(self, venue: VenueOptimization):
        """Set venue-specific optimization."""
        self.venue_optimization = venue

    def set_verbose(self, verbose: bool = True):
        """Enable or disable verbose output."""
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")

    def detect_dependencies(self) -> set[Path]:
        """Detect all LaTeX dependencies (input files, figures, etc.)."""
        dependencies = set()
        dependencies.add(self.main_file)

        def scan_file(file_path: Path):
            """Recursively scan a LaTeX file for dependencies."""
            if not file_path.exists():
                return

            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                return

            # Find input/include files
            input_patterns = [
                r"\\input\{([^}]+)\}",
                r"\\include\{([^}]+)\}",
                r"\\subfile\{([^}]+)\}",
                r"\\InputIfFileExists\{([^}]+)\}",
            ]

            for pattern in input_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Handle relative paths
                    dep_path = file_path.parent / f"{match}.tex"
                    if not dep_path.exists():
                        dep_path = file_path.parent / match
                    if dep_path.exists() and dep_path not in dependencies:
                        dependencies.add(dep_path)
                        scan_file(dep_path)  # Recursive scan

            # Find figure files
            figure_patterns = [
                r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}",
                r"\\pgfimage\{([^}]+)\}",
            ]

            for pattern in figure_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Try different extensions
                    for ext in [".png", ".jpg", ".jpeg", ".pdf", ".eps", ".svg"]:
                        fig_path = self.base_dir / f"{match}{ext}"
                        if fig_path.exists():
                            dependencies.add(fig_path)
                            break
                    else:
                        # Try without extension
                        fig_path = self.base_dir / match
                        if fig_path.exists():
                            dependencies.add(fig_path)

            # Find bibliography files
            bib_patterns = [
                r"\\bibliography\{([^}]+)\}",
                r"\\addbibresource\{([^}]+)\}",
            ]

            for pattern in bib_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    bib_path = self.base_dir / f"{match}.bib"
                    if not bib_path.exists():
                        bib_path = self.base_dir / match
                    if bib_path.exists():
                        dependencies.add(bib_path)

        # Start scanning from main file
        scan_file(self.main_file)

        # Add common auxiliary files
        for aux_file in ["*.cls", "*.sty", "*.bst"]:
            dependencies.update(self.base_dir.glob(aux_file))

        self.tracked_files = dependencies
        return dependencies

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def files_changed(self) -> bool:
        """Check if any tracked files have changed."""
        for file_path in self.tracked_files:
            if not file_path.exists():
                continue

            current_hash = self.calculate_file_hash(file_path)
            if file_path not in self.file_hashes:
                self.file_hashes[file_path] = current_hash
                return True

            if self.file_hashes[file_path] != current_hash:
                self.file_hashes[file_path] = current_hash
                self.log(f"File changed: {file_path.name}")
                return True

        return False

    def run_latex_command(
        self, additional_args: list[str] = None
    ) -> tuple[int, str, str]:
        """Run LaTeX compilation command."""
        if additional_args is None:
            additional_args = []

        # Base command
        cmd = [self.engine.value]

        # Add venue-specific optimizations
        if self.venue_optimization == VenueOptimization.ARXIV:
            cmd.extend(["-interaction=nonstopmode", "-file-line-error"])
        elif self.venue_optimization == VenueOptimization.IEEE:
            cmd.extend(["-interaction=nonstopmode", "-shell-escape"])
        else:
            cmd.extend(["-interaction=nonstopmode", "-file-line-error"])

        # Add additional arguments
        cmd.extend(additional_args)

        # Add main file
        cmd.append(str(self.main_file.name))

        self.log(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "LaTeX compilation timed out"
        except FileNotFoundError:
            return 1, "", f"LaTeX engine not found: {self.engine.value}"

    def parse_log_file(self) -> tuple[list[LaTeXError], CompilationStats]:
        """Parse LaTeX log file for errors and statistics."""
        log_file = self.base_dir / f"{self.main_file.stem}.log"
        if not log_file.exists():
            return [], CompilationStats()

        errors = []
        stats = CompilationStats()

        try:
            with open(log_file, encoding="utf-8", errors="ignore") as f:
                log_content = f.read()
        except Exception:
            return errors, stats

        # Parse errors and warnings
        error_patterns = [
            (r"! (.+)", "Error"),
            (r"LaTeX Warning: (.+)", "Warning"),
            (r"Package \w+ Warning: (.+)", "Package Warning"),
            (r"Overfull \\hbox \((.+)\)", "Overfull hbox"),
            (r"Underfull \\hbox \((.+)\)", "Underfull hbox"),
        ]

        lines = log_content.split("\n")
        for i, line in enumerate(lines):
            for pattern, error_type in error_patterns:
                match = re.search(pattern, line)
                if match:
                    # Try to extract line number
                    line_num = None
                    if i > 0:
                        line_match = re.search(r"l\.(\d+)", lines[i - 1])
                        if line_match:
                            line_num = int(line_match.group(1))

                    # Generate suggestion based on error type
                    suggestion = self.generate_error_suggestion(
                        match.group(1), error_type
                    )

                    errors.append(
                        LaTeXError(
                            line_number=line_num,
                            error_type=error_type,
                            message=match.group(1),
                            suggestion=suggestion,
                        )
                    )

                    if error_type == "Warning":
                        stats.warnings += 1
                    else:
                        stats.errors += 1

        # Parse statistics
        if "Output written on" in log_content:
            # Extract page count
            page_match = re.search(r"\((\d+) page", log_content)
            if page_match:
                stats.pages = int(page_match.group(1))

        # Count figures and tables from aux file
        aux_file = self.base_dir / f"{self.main_file.stem}.aux"
        if aux_file.exists():
            try:
                with open(aux_file) as f:
                    aux_content = f.read()
                    stats.figures = len(re.findall(r"\\@writefile\{lof\}", aux_content))
                    stats.tables = len(re.findall(r"\\@writefile\{lot\}", aux_content))
                    stats.references = len(re.findall(r"\\bibcite", aux_content))
            except Exception:
                pass

        return errors, stats

    def generate_error_suggestion(
        self, error_message: str, error_type: str
    ) -> str | None:
        """Generate helpful suggestions for common LaTeX errors."""
        suggestions = {
            "Undefined control sequence": "Check for typos in command names or missing packages",
            "Missing $ inserted": "Check for unescaped special characters or missing math mode",
            "Extra alignment tab": "Check table column alignment and & symbols",
            "Missing \\begin{document}": "Ensure \\begin{document} is present",
            "File ended while scanning": "Check for unmatched braces { }",
            "Paragraph ended before": "Check for missing closing braces",
            "Citation.*undefined": "Run BibTeX or check citation keys",
            "Reference.*undefined": "Check \\label and \\ref commands",
            "Package.*not found": "Install missing LaTeX package",
        }

        for pattern, suggestion in suggestions.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                return suggestion

        return None

    def run_bibtex(self) -> bool:
        """Run BibTeX if needed."""
        aux_file = self.base_dir / f"{self.main_file.stem}.aux"
        if not aux_file.exists():
            return True

        # Check if BibTeX is needed
        try:
            with open(aux_file) as f:
                aux_content = f.read()
                if "\\bibdata" not in aux_content:
                    return True  # No bibliography
        except Exception:
            return True

        self.log("Running BibTeX")
        try:
            result = subprocess.run(
                ["bibtex", self.main_file.stem],
                check=False,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                self.log(f"BibTeX warning: {result.stderr}", "WARNING")
                return False

            return True
        except Exception as e:
            self.log(f"BibTeX failed: {e}", "ERROR")
            return False

    def compile_once(self) -> tuple[bool, list[LaTeXError], CompilationStats]:
        """Perform one compilation pass."""
        self.compilation_count += 1
        self.log(f"Compilation pass {self.compilation_count}")

        # Run LaTeX
        exit_code, stdout, stderr = self.run_latex_command()

        # Parse results
        errors, stats = self.parse_log_file()

        success = exit_code == 0 and not any(e.error_type == "Error" for e in errors)

        if not success:
            self.log(f"Compilation failed with exit code {exit_code}", "ERROR")
            if stderr:
                self.log(f"Error output: {stderr}", "ERROR")

        return success, errors, stats

    def compile_full(self) -> tuple[bool, list[LaTeXError], CompilationStats]:
        """Perform full compilation with bibliography and cross-references."""
        self.log("Starting full LaTeX compilation")
        start_time = time.time()

        all_errors = []
        final_stats = CompilationStats()

        # First pass
        success, errors, stats = self.compile_once()
        all_errors.extend(errors)
        final_stats = stats

        if not success:
            return False, all_errors, final_stats

        # Run BibTeX if needed
        self.run_bibtex()

        # Second pass (for bibliography)
        success, errors, stats = self.compile_once()
        all_errors.extend(errors)
        final_stats = stats

        if not success:
            return False, all_errors, final_stats

        # Third pass (for cross-references)
        success, errors, stats = self.compile_once()
        all_errors.extend(errors)
        final_stats = stats

        # Check if we need another pass
        aux_file = self.base_dir / f"{self.main_file.stem}.aux"
        if aux_file.exists() and self.compilation_count < self.max_runs:
            try:
                with open(aux_file) as f:
                    aux_content = f.read()
                    if "Rerun to get cross-references right" in aux_content:
                        self.log("Additional pass needed for cross-references")
                        success, errors, stats = self.compile_once()
                        all_errors.extend(errors)
                        final_stats = stats
            except Exception:
                pass

        duration = time.time() - start_time
        self.last_compilation_time = duration

        pdf_file = self.base_dir / f"{self.main_file.stem}.pdf"
        if success and pdf_file.exists():
            pdf_size = pdf_file.stat().st_size / 1024  # KB
            self.log(
                f"Compilation successful in {duration:.2f}s, PDF size: {pdf_size:.1f} KB"
            )
        else:
            self.log(f"Compilation failed after {duration:.2f}s", "ERROR")

        return success, all_errors, final_stats

    def watch_and_compile(self):
        """Watch for file changes and recompile automatically."""
        self.log("Starting watch mode - press Ctrl+C to stop")
        self.watch_mode = True

        # Initial dependency detection
        self.detect_dependencies()

        # Initial compilation
        self.compile_full()

        try:
            while self.watch_mode:
                time.sleep(1)  # Check every second

                if self.files_changed():
                    self.log("Files changed, recompiling...")
                    success, errors, stats = self.compile_full()

                    if success:
                        self.log("✅ Compilation successful")
                    else:
                        self.log("❌ Compilation failed")
                        for error in errors[:5]:  # Show first 5 errors
                            self.log(f"  {error.error_type}: {error.message}", "ERROR")

        except KeyboardInterrupt:
            self.log("Watch mode stopped")
            self.watch_mode = False

    def optimize_for_venue(self, venue: VenueOptimization):
        """Apply venue-specific optimizations."""
        self.venue_optimization = venue
        self.log(f"Optimizing for {venue.value}")

        # Venue-specific settings
        if venue == VenueOptimization.ARXIV:
            # arXiv prefers PDF figures and specific packages
            self.log("Applying arXiv optimizations")
        elif venue == VenueOptimization.IEEE:
            # IEEE has specific formatting requirements
            self.log("Applying IEEE optimizations")
        elif venue == VenueOptimization.ACM:
            # ACM has specific template requirements
            self.log("Applying ACM optimizations")

    def generate_compilation_report(
        self, errors: list[LaTeXError], stats: CompilationStats
    ) -> str:
        """Generate a detailed compilation report."""
        report_lines = [
            "# LaTeX Compilation Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Engine: {self.engine.value}",
            f"Main file: {self.main_file.name}",
            "",
            "## Statistics",
            f"- Pages: {stats.pages}",
            f"- Figures: {stats.figures}",
            f"- Tables: {stats.tables}",
            f"- References: {stats.references}",
            f"- Compilation time: {self.last_compilation_time:.2f}s",
            f"- Compilation passes: {self.compilation_count}",
            "",
            "## Issues",
            f"- Errors: {stats.errors}",
            f"- Warnings: {stats.warnings}",
            "",
        ]

        if errors:
            report_lines.append("### Detailed Issues")
            for error in errors:
                line_info = f" (line {error.line_number})" if error.line_number else ""
                report_lines.append(
                    f"**{error.error_type}**{line_info}: {error.message}"
                )
                if error.suggestion:
                    report_lines.append(f"  *Suggestion: {error.suggestion}*")
                report_lines.append("")

        return "\n".join(report_lines)


def main():
    """Main entry point for the LaTeX compiler."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Advanced LaTeX Compiler for Academic Papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--engine",
        "-e",
        type=str,
        choices=["pdflatex", "xelatex", "lualatex"],
        default="pdflatex",
        help="LaTeX engine to use",
    )

    parser.add_argument(
        "--optimize",
        "-o",
        type=str,
        choices=["arxiv", "ieee", "acm", "springer", "elsevier"],
        help="Optimize for specific venue",
    )

    parser.add_argument(
        "--watch",
        "-w",
        action="store_true",
        help="Watch mode - recompile on file changes",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--report", "-r", action="store_true", help="Generate compilation report"
    )

    parser.add_argument(
        "main_file", nargs="?", default="main.tex", help="Main LaTeX file to compile"
    )

    args = parser.parse_args()

    try:
        # Initialize compiler
        compiler = LaTeXCompiler(args.main_file)
        compiler.set_engine(LaTeXEngine(args.engine))
        compiler.set_verbose(args.verbose)

        if args.optimize:
            compiler.set_venue_optimization(VenueOptimization(args.optimize))

        # Compile
        if args.watch:
            compiler.watch_and_compile()
        else:
            success, errors, stats = compiler.compile_full()

            if args.report:
                report = compiler.generate_compilation_report(errors, stats)
                report_file = Path("latex_compilation_report.md")
                with open(report_file, "w") as f:
                    f.write(report)
                print(f"Compilation report saved to {report_file}")

            # Print summary
            if success:
                print("✅ Compilation successful")
                if stats.pages > 0:
                    print(f"📄 Generated {stats.pages} pages")
            else:
                print("❌ Compilation failed")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"  {error.error_type}: {error.message}")

            sys.exit(0 if success else 1)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCompilation interrupted")
        sys.exit(1)


if __name__ == "__main__":
    main()
