#!/usr/bin/env python3
"""
Validation script for the modular ACGS-PGP Enhanced LaTeX research paper.
Checks compilation, cross-references, typography, and content quality.
"""

import os
import subprocess
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple

class LaTeXValidator:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.main_file = "ACGS-PGP-Enhanced-Main.tex"
        self.modular_files = [
            "preamble.tex",
            "01-introduction.tex",
            "02-related-work.tex", 
            "03-methods.tex",
            "04-results.tex",
            "05-discussion.tex",
            "06-future-work.tex",
            "07-conclusion.tex",
            "08-appendix.tex"
        ]
        self.required_figures = [
            "service_health.png",
            "scaling_validation.png", 
            "stability_analysis.png",
            "performance_comparison.png"
        ]
        
    def check_file_existence(self) -> Dict[str, bool]:
        """Check if all required files exist."""
        results = {}
        
        # Check main file
        results[self.main_file] = (self.base_dir / self.main_file).exists()
        
        # Check modular files
        for file in self.modular_files:
            results[file] = (self.base_dir / file).exists()
            
        # Check bibliography
        results["references.bib"] = (self.base_dir / "references.bib").exists()
        
        # Check figures
        for fig in self.required_figures:
            results[fig] = (self.base_dir / fig).exists()
            
        return results
    
    def compile_latex(self) -> Tuple[bool, str]:
        """Compile the main LaTeX document."""
        try:
            # First pass
            result1 = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", self.main_file],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Bibliography
            subprocess.run(
                ["bibtex", self.main_file.replace(".tex", "")],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Second pass
            result2 = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", self.main_file],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Third pass for cross-references
            result3 = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", self.main_file],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return result3.returncode == 0, result3.stdout + result3.stderr
            
        except subprocess.TimeoutExpired:
            return False, "Compilation timeout"
        except Exception as e:
            return False, str(e)
    
    def check_typography_warnings(self) -> List[str]:
        """Check for typography warnings in compilation output."""
        success, output = self.compile_latex()
        if not success:
            return ["Compilation failed"]
            
        warnings = []
        
        # Check for underfull/overfull boxes
        underfull_pattern = r"Underfull \\[hv]box.*badness (\d+)"
        overfull_pattern = r"Overfull \\[hv]box.*too wide"
        
        for line in output.split('\n'):
            if re.search(underfull_pattern, line):
                badness = re.search(underfull_pattern, line).group(1)
                if int(badness) > 1000:
                    warnings.append(f"High badness underfull box: {line.strip()}")
            elif re.search(overfull_pattern, line):
                warnings.append(f"Overfull box: {line.strip()}")
                
        return warnings
    
    def run_chktex(self) -> List[str]:
        """Run ChkTeX style checker."""
        try:
            result = subprocess.run(
                ["chktex", self.main_file],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            warnings = []
            for line in result.stdout.split('\n'):
                if line.startswith("Warning"):
                    warnings.append(line.strip())
                    
            return warnings
            
        except subprocess.TimeoutExpired:
            return ["ChkTeX timeout"]
        except Exception as e:
            return [f"ChkTeX error: {str(e)}"]
    
    def validate_cross_references(self) -> List[str]:
        """Check for undefined references and citations."""
        success, output = self.compile_latex()
        if not success:
            return ["Compilation failed"]
            
        issues = []
        
        for line in output.split('\n'):
            if "undefined" in line.lower():
                issues.append(line.strip())
                
        return issues
    
    def generate_report(self) -> str:
        """Generate comprehensive validation report."""
        report = []
        report.append("=" * 80)
        report.append("ACGS-PGP Enhanced LaTeX Paper - Modular Structure Validation")
        report.append("=" * 80)
        report.append("")
        
        # File existence check
        report.append("1. FILE EXISTENCE CHECK")
        report.append("-" * 40)
        file_results = self.check_file_existence()
        all_files_exist = True
        
        for file, exists in file_results.items():
            status = "✓" if exists else "✗"
            report.append(f"{status} {file}")
            if not exists:
                all_files_exist = False
                
        report.append(f"\nResult: {'PASS' if all_files_exist else 'FAIL'}")
        report.append("")
        
        # Compilation check
        report.append("2. COMPILATION CHECK")
        report.append("-" * 40)
        compile_success, compile_output = self.compile_latex()
        report.append(f"Status: {'PASS' if compile_success else 'FAIL'}")
        
        if not compile_success:
            report.append("Compilation errors:")
            report.append(compile_output[-1000:])  # Last 1000 chars
        report.append("")
        
        # Typography warnings
        report.append("3. TYPOGRAPHY WARNINGS")
        report.append("-" * 40)
        typo_warnings = self.check_typography_warnings()
        if typo_warnings:
            for warning in typo_warnings[:10]:  # Limit to first 10
                report.append(f"⚠ {warning}")
        else:
            report.append("✓ No critical typography warnings")
        report.append("")
        
        # ChkTeX style check
        report.append("4. CHKTEX STYLE CHECK")
        report.append("-" * 40)
        style_warnings = self.run_chktex()
        if style_warnings:
            report.append(f"Found {len(style_warnings)} style warnings:")
            for warning in style_warnings[:10]:  # Limit to first 10
                report.append(f"⚠ {warning}")
        else:
            report.append("✓ No style warnings")
        report.append("")
        
        # Cross-references check
        report.append("5. CROSS-REFERENCES CHECK")
        report.append("-" * 40)
        ref_issues = self.validate_cross_references()
        if ref_issues:
            for issue in ref_issues[:10]:  # Limit to first 10
                report.append(f"⚠ {issue}")
        else:
            report.append("✓ All references resolved")
        report.append("")
        
        # Summary
        report.append("6. SUMMARY")
        report.append("-" * 40)
        total_issues = len(typo_warnings) + len(style_warnings) + len(ref_issues)
        if not all_files_exist:
            total_issues += 1
        if not compile_success:
            total_issues += 1
            
        if total_issues == 0:
            report.append("✓ ALL CHECKS PASSED - Publication ready!")
        else:
            report.append(f"⚠ {total_issues} issues found - Review needed")
            
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Main validation function."""
    validator = LaTeXValidator()
    report = validator.generate_report()
    
    print(report)
    
    # Save report to file
    with open("validation_report.txt", "w") as f:
        f.write(report)
    
    print(f"\nDetailed report saved to: validation_report.txt")

if __name__ == "__main__":
    main()
