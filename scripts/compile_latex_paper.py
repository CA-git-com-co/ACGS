#!/usr/bin/env python3
"""
LaTeX Paper Compilation Script for ACGS-PGP

Compiles the enhanced ACGS-PGP research paper from LaTeX to PDF with proper
academic formatting, figure integration, and error handling.
"""

import subprocess
import sys
import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LaTeXCompiler:
    """Comprehensive LaTeX compilation system for academic papers"""
    
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.latex_dir = self.project_root / "docs/research/enhanced"
        self.figures_dir = self.latex_dir
        self.output_dir = self.latex_dir / "compiled"
        self.output_dir.mkdir(exist_ok=True)
        
        # LaTeX document settings
        self.main_tex_file = "ACGS-PGP-Enhanced.tex"
        self.bib_file = "references.bib"
        self.output_pdf = "ACGS-PGP-Enhanced.pdf"
        
        # Compilation settings
        self.latex_engine = "pdflatex"  # Can be changed to xelatex or lualatex
        self.max_compile_attempts = 3
        
        # Required figures
        self.required_figures = [
            "performance_comparison.png",
            "stability_analysis.png", 
            "scaling_validation.png",
            "service_health.png"
        ]
        
        self.compilation_log = []
    
    def check_latex_installation(self) -> bool:
        """Check if LaTeX is installed and available"""
        try:
            result = subprocess.run([self.latex_engine, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"✅ {self.latex_engine} is available")
                return True
            else:
                logger.error(f"❌ {self.latex_engine} not found")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"❌ LaTeX check failed: {e}")
            return False
    
    def check_required_files(self) -> Dict[str, bool]:
        """Check if all required files are present"""
        file_status = {}
        
        # Check main LaTeX file
        main_tex_path = self.latex_dir / self.main_tex_file
        file_status["main_tex"] = main_tex_path.exists()
        if file_status["main_tex"]:
            logger.info(f"✅ Main LaTeX file found: {main_tex_path}")
        else:
            logger.error(f"❌ Main LaTeX file missing: {main_tex_path}")
        
        # Check bibliography file
        bib_path = self.latex_dir / self.bib_file
        file_status["bibliography"] = bib_path.exists()
        if file_status["bibliography"]:
            logger.info(f"✅ Bibliography file found: {bib_path}")
        else:
            logger.error(f"❌ Bibliography file missing: {bib_path}")
        
        # Check figures
        file_status["figures"] = {}
        for figure in self.required_figures:
            figure_path = self.figures_dir / figure
            figure_exists = figure_path.exists()
            file_status["figures"][figure] = figure_exists
            
            if figure_exists:
                logger.info(f"✅ Figure found: {figure}")
            else:
                logger.warning(f"⚠️ Figure missing: {figure}")
        
        return file_status
    
    def prepare_compilation_environment(self) -> bool:
        """Prepare the compilation environment"""
        try:
            # Copy files to output directory for compilation
            main_tex_src = self.latex_dir / self.main_tex_file
            main_tex_dst = self.output_dir / self.main_tex_file
            shutil.copy2(main_tex_src, main_tex_dst)
            
            bib_src = self.latex_dir / self.bib_file
            bib_dst = self.output_dir / self.bib_file
            shutil.copy2(bib_src, bib_dst)
            
            # Copy figures
            for figure in self.required_figures:
                figure_src = self.figures_dir / figure
                if figure_src.exists():
                    figure_dst = self.output_dir / figure
                    shutil.copy2(figure_src, figure_dst)
                    logger.info(f"📁 Copied figure: {figure}")
            
            logger.info("✅ Compilation environment prepared")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare compilation environment: {e}")
            return False
    
    def run_latex_compilation(self) -> bool:
        """Run the LaTeX compilation process"""
        try:
            os.chdir(self.output_dir)
            
            # First compilation pass
            logger.info("🔄 Running first LaTeX compilation pass...")
            result1 = subprocess.run([
                self.latex_engine, 
                "-interaction=nonstopmode",
                "-file-line-error",
                self.main_tex_file
            ], capture_output=True, text=True, timeout=120)
            
            self.compilation_log.append(("First Pass", result1.returncode, result1.stdout, result1.stderr))
            
            if result1.returncode != 0:
                logger.error("❌ First LaTeX compilation failed")
                logger.error(f"STDOUT: {result1.stdout}")
                logger.error(f"STDERR: {result1.stderr}")
                return False
            
            logger.info("✅ First LaTeX compilation successful")
            
            # Run BibTeX for bibliography
            logger.info("🔄 Running BibTeX compilation...")
            bibtex_result = subprocess.run([
                "bibtex", 
                self.main_tex_file.replace(".tex", "")
            ], capture_output=True, text=True, timeout=60)
            
            self.compilation_log.append(("BibTeX", bibtex_result.returncode, bibtex_result.stdout, bibtex_result.stderr))
            
            if bibtex_result.returncode != 0:
                logger.warning("⚠️ BibTeX compilation had issues (may be normal)")
                logger.warning(f"BibTeX output: {bibtex_result.stdout}")
            else:
                logger.info("✅ BibTeX compilation successful")
            
            # Second compilation pass (for references)
            logger.info("🔄 Running second LaTeX compilation pass...")
            result2 = subprocess.run([
                self.latex_engine,
                "-interaction=nonstopmode", 
                "-file-line-error",
                self.main_tex_file
            ], capture_output=True, text=True, timeout=120)
            
            self.compilation_log.append(("Second Pass", result2.returncode, result2.stdout, result2.stderr))
            
            if result2.returncode != 0:
                logger.error("❌ Second LaTeX compilation failed")
                logger.error(f"STDOUT: {result2.stdout}")
                logger.error(f"STDERR: {result2.stderr}")
                return False
            
            logger.info("✅ Second LaTeX compilation successful")
            
            # Third compilation pass (for final cross-references)
            logger.info("🔄 Running third LaTeX compilation pass...")
            result3 = subprocess.run([
                self.latex_engine,
                "-interaction=nonstopmode",
                "-file-line-error", 
                self.main_tex_file
            ], capture_output=True, text=True, timeout=120)
            
            self.compilation_log.append(("Third Pass", result3.returncode, result3.stdout, result3.stderr))
            
            if result3.returncode != 0:
                logger.error("❌ Third LaTeX compilation failed")
                logger.error(f"STDOUT: {result3.stdout}")
                logger.error(f"STDERR: {result3.stderr}")
                return False
            
            logger.info("✅ Third LaTeX compilation successful")
            
            # Check if PDF was generated
            pdf_path = self.output_dir / self.output_pdf
            if pdf_path.exists():
                logger.info(f"✅ PDF successfully generated: {pdf_path}")
                return True
            else:
                logger.error("❌ PDF file not found after compilation")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ LaTeX compilation timed out")
            return False
        except Exception as e:
            logger.error(f"❌ LaTeX compilation failed: {e}")
            return False
        finally:
            # Return to original directory
            os.chdir(self.project_root)
    
    def validate_pdf_output(self) -> Dict[str, any]:
        """Validate the generated PDF for submission readiness"""
        pdf_path = self.output_dir / self.output_pdf
        validation_results = {
            "pdf_exists": False,
            "file_size_mb": 0,
            "submission_ready": False,
            "issues": []
        }
        
        try:
            if pdf_path.exists():
                validation_results["pdf_exists"] = True
                
                # Check file size
                file_size = pdf_path.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
                validation_results["file_size_mb"] = round(file_size_mb, 2)
                
                # Validate file size for submission (typically <10MB for most venues)
                if file_size_mb > 10:
                    validation_results["issues"].append(f"File size too large: {file_size_mb}MB (>10MB)")
                elif file_size_mb < 0.1:
                    validation_results["issues"].append(f"File size too small: {file_size_mb}MB (<0.1MB)")
                else:
                    logger.info(f"✅ PDF file size acceptable: {file_size_mb}MB")
                
                # Check if PDF can be opened (basic validation)
                try:
                    # Try to get PDF info using pdfinfo if available
                    pdfinfo_result = subprocess.run([
                        "pdfinfo", str(pdf_path)
                    ], capture_output=True, text=True, timeout=10)
                    
                    if pdfinfo_result.returncode == 0:
                        logger.info("✅ PDF structure validation passed")
                    else:
                        validation_results["issues"].append("PDF structure validation failed")
                        
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    logger.warning("⚠️ pdfinfo not available, skipping PDF structure validation")
                
                # Determine submission readiness
                validation_results["submission_ready"] = len(validation_results["issues"]) == 0
                
            else:
                validation_results["issues"].append("PDF file does not exist")
                
        except Exception as e:
            validation_results["issues"].append(f"PDF validation error: {e}")
        
        return validation_results
    
    def generate_compilation_report(self) -> str:
        """Generate a comprehensive compilation report"""
        report_content = f"""# LaTeX Compilation Report

## Compilation Summary
- **LaTeX Engine**: {self.latex_engine}
- **Main File**: {self.main_tex_file}
- **Output Directory**: {self.output_dir}
- **Compilation Passes**: {len(self.compilation_log)}

## File Status
"""
        
        file_status = self.check_required_files()
        
        report_content += f"""
- **Main LaTeX File**: {'✅ Found' if file_status['main_tex'] else '❌ Missing'}
- **Bibliography File**: {'✅ Found' if file_status['bibliography'] else '❌ Missing'}

### Figures Status
"""
        
        for figure, exists in file_status['figures'].items():
            status = '✅ Found' if exists else '❌ Missing'
            report_content += f"- **{figure}**: {status}\n"
        
        report_content += "\n## Compilation Log\n"
        
        for i, (pass_name, return_code, stdout, stderr) in enumerate(self.compilation_log, 1):
            status = '✅ Success' if return_code == 0 else '❌ Failed'
            report_content += f"""
### {pass_name}
- **Status**: {status}
- **Return Code**: {return_code}
"""
            if stderr and return_code != 0:
                report_content += f"- **Errors**: {stderr[:500]}...\n"
        
        # PDF validation
        pdf_validation = self.validate_pdf_output()
        report_content += f"""
## PDF Validation
- **PDF Generated**: {'✅ Yes' if pdf_validation['pdf_exists'] else '❌ No'}
- **File Size**: {pdf_validation['file_size_mb']}MB
- **Submission Ready**: {'✅ Yes' if pdf_validation['submission_ready'] else '❌ No'}
"""
        
        if pdf_validation['issues']:
            report_content += "\n### Issues Found\n"
            for issue in pdf_validation['issues']:
                report_content += f"- {issue}\n"
        
        return report_content
    
    def compile_paper(self) -> bool:
        """Main compilation workflow"""
        logger.info("🚀 Starting LaTeX paper compilation...")
        
        # Check LaTeX installation
        if not self.check_latex_installation():
            logger.error("❌ LaTeX not available. Please install LaTeX distribution.")
            return False
        
        # Check required files
        file_status = self.check_required_files()
        if not file_status["main_tex"] or not file_status["bibliography"]:
            logger.error("❌ Required files missing. Cannot proceed with compilation.")
            return False
        
        # Prepare compilation environment
        if not self.prepare_compilation_environment():
            logger.error("❌ Failed to prepare compilation environment.")
            return False
        
        # Run LaTeX compilation
        if not self.run_latex_compilation():
            logger.error("❌ LaTeX compilation failed.")
            return False
        
        # Validate output
        pdf_validation = self.validate_pdf_output()
        if not pdf_validation["submission_ready"]:
            logger.warning("⚠️ PDF generated but may have issues for submission.")
            for issue in pdf_validation["issues"]:
                logger.warning(f"   - {issue}")
        
        # Generate compilation report
        report_content = self.generate_compilation_report()
        report_path = self.output_dir / "compilation_report.md"
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        logger.info(f"📋 Compilation report saved: {report_path}")
        logger.info("✅ LaTeX paper compilation completed successfully!")
        
        return True


def main():
    """Main execution function"""
    compiler = LaTeXCompiler()
    
    print("📄 ACGS-PGP LaTeX Paper Compilation")
    print("=" * 50)
    
    # Compile the paper
    success = compiler.compile_paper()
    
    if success:
        pdf_path = compiler.output_dir / compiler.output_pdf
        print(f"\n🎉 Compilation Successful!")
        print(f"📄 PDF Location: {pdf_path}")
        print(f"📁 Output Directory: {compiler.output_dir}")
        
        # Show PDF validation results
        validation = compiler.validate_pdf_output()
        print(f"📊 File Size: {validation['file_size_mb']}MB")
        print(f"🎯 Submission Ready: {'✅ Yes' if validation['submission_ready'] else '❌ No'}")
        
        if validation['issues']:
            print("\n⚠️ Issues to address:")
            for issue in validation['issues']:
                print(f"   - {issue}")
    else:
        print("\n❌ Compilation Failed!")
        print("📋 Check the compilation report for details.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
