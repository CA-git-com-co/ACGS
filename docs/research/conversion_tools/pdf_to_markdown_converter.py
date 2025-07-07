#!/usr/bin/env python3
"""
ACGS Research Paper OCR Conversion Tool
Constitutional Hash: cdd01ef066bc6cf2

Converts PDF research papers to markdown format using advanced OCR techniques.
Designed for academic papers with complex formatting, equations, and figures.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

import click
from tqdm import tqdm
from loguru import logger
import pandas as pd

# OCR Libraries
MARKER_AVAILABLE = False
try:
    import marker
    from marker.convert import convert_single_pdf
    from marker.models import load_all_models
    MARKER_AVAILABLE = True
except ImportError:
    logger.warning("Marker not available, falling back to PyMuPDF")

import fitz  # PyMuPDF
import pdfplumber


@dataclass
class ConversionResult:
    """Results from PDF to markdown conversion."""
    filename: str
    success: bool
    method: str
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    original_size: int = 0
    markdown_size: int = 0
    page_count: int = 0
    quality_score: float = 0.0
    constitutional_hash: str = "cdd01ef066bc6cf2"


class PDFToMarkdownConverter:
    """Advanced PDF to Markdown converter for academic papers."""
    
    def __init__(self, input_dir: Path, output_dir: Path, max_workers: int = 4):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.metadata_dir = self.output_dir.parent / "papers_metadata"
        self.max_workers = max_workers
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize models if Marker is available
        self.marker_models = None
        if MARKER_AVAILABLE:
            try:
                logger.info("Loading Marker models...")
                self.marker_models = load_all_models()
                logger.info("Marker models loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Marker models: {e}")
                MARKER_AVAILABLE = False
    
    def convert_with_marker(self, pdf_path: Path) -> Tuple[str, float]:
        """Convert PDF using Marker (best for academic papers)."""
        if not MARKER_AVAILABLE or not self.marker_models:
            raise ValueError("Marker not available")
        
        start_time = time.time()
        
        try:
            # Convert PDF to markdown
            full_text, images, out_meta = convert_single_pdf(
                str(pdf_path),
                self.marker_models,
                max_pages=None,
                langs=["English"],
                batch_multiplier=2
            )
            
            processing_time = time.time() - start_time
            return full_text, processing_time
            
        except Exception as e:
            logger.error(f"Marker conversion failed for {pdf_path}: {e}")
            raise
    
    def convert_with_pymupdf(self, pdf_path: Path) -> Tuple[str, float]:
        """Convert PDF using PyMuPDF (fallback method)."""
        start_time = time.time()
        
        try:
            doc = fitz.open(str(pdf_path))
            markdown_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # Basic markdown formatting
                if text.strip():
                    markdown_content.append(f"## Page {page_num + 1}\n\n{text}\n")
            
            doc.close()
            processing_time = time.time() - start_time
            
            return "\n".join(markdown_content), processing_time
            
        except Exception as e:
            logger.error(f"PyMuPDF conversion failed for {pdf_path}: {e}")
            raise
    
    def assess_quality(self, markdown_content: str, pdf_path: Path) -> float:
        """Assess the quality of the markdown conversion."""
        try:
            # Basic quality metrics
            word_count = len(markdown_content.split())
            line_count = len(markdown_content.split('\n'))
            
            # Check for common academic paper elements
            has_abstract = 'abstract' in markdown_content.lower()
            has_references = any(ref in markdown_content.lower() 
                               for ref in ['references', 'bibliography', 'citations'])
            has_sections = markdown_content.count('#') > 3
            
            # Calculate quality score (0-1)
            quality_score = 0.0
            if word_count > 100:
                quality_score += 0.3
            if has_abstract:
                quality_score += 0.2
            if has_references:
                quality_score += 0.2
            if has_sections:
                quality_score += 0.3
            
            return min(quality_score, 1.0)
            
        except Exception:
            return 0.0
    
    def convert_single_pdf(self, pdf_path: Path) -> ConversionResult:
        """Convert a single PDF file to markdown."""
        logger.info(f"Converting {pdf_path.name}")
        
        result = ConversionResult(
            filename=pdf_path.name,
            success=False,
            method="none",
            original_size=pdf_path.stat().st_size
        )
        
        # Try conversion methods in order of preference
        conversion_methods = []
        if MARKER_AVAILABLE and self.marker_models:
            conversion_methods.append(("marker", self.convert_with_marker))
        conversion_methods.append(("pymupdf", self.convert_with_pymupdf))
        
        for method_name, convert_func in conversion_methods:
            try:
                markdown_content, processing_time = convert_func(pdf_path)
                
                # Save markdown file
                output_filename = pdf_path.stem + ".md"
                output_path = self.output_dir / output_filename
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {pdf_path.stem}\n\n")
                    f.write(f"**Original PDF**: {pdf_path.name}\n")
                    f.write(f"**Conversion Method**: {method_name}\n")
                    f.write(f"**Constitutional Hash**: cdd01ef066bc6cf2\n\n")
                    f.write("---\n\n")
                    f.write(markdown_content)
                
                # Update result
                result.success = True
                result.method = method_name
                result.output_path = str(output_path)
                result.processing_time = processing_time
                result.markdown_size = output_path.stat().st_size
                result.quality_score = self.assess_quality(markdown_content, pdf_path)
                
                # Get page count
                try:
                    with fitz.open(str(pdf_path)) as doc:
                        result.page_count = len(doc)
                except:
                    result.page_count = 0
                
                logger.success(f"Successfully converted {pdf_path.name} using {method_name}")
                break
                
            except Exception as e:
                logger.warning(f"Method {method_name} failed for {pdf_path.name}: {e}")
                result.error_message = str(e)
                continue
        
        if not result.success:
            logger.error(f"All conversion methods failed for {pdf_path.name}")
        
        return result
    
    def convert_batch(self, pdf_files: List[Path]) -> List[ConversionResult]:
        """Convert multiple PDF files in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all conversion tasks
            future_to_pdf = {
                executor.submit(self.convert_single_pdf, pdf_path): pdf_path
                for pdf_path in pdf_files
            }
            
            # Process completed tasks with progress bar
            with tqdm(total=len(pdf_files), desc="Converting PDFs") as pbar:
                for future in as_completed(future_to_pdf):
                    result = future.result()
                    results.append(result)
                    pbar.update(1)
                    
                    # Update progress description
                    success_count = sum(1 for r in results if r.success)
                    pbar.set_postfix({
                        'Success': f"{success_count}/{len(results)}",
                        'Method': result.method if result.success else 'Failed'
                    })
        
        return results
    
    def save_conversion_report(self, results: List[ConversionResult]) -> None:
        """Save detailed conversion report."""
        report_path = self.metadata_dir / "conversion_report.json"
        
        # Create summary statistics
        total_files = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total_files - successful
        
        total_original_size = sum(r.original_size for r in results)
        total_markdown_size = sum(r.markdown_size for r in results if r.success)
        
        avg_quality = sum(r.quality_score for r in results if r.success) / max(successful, 1)
        
        report = {
            "constitutional_hash": "cdd01ef066bc6cf2",
            "conversion_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_files": total_files,
                "successful_conversions": successful,
                "failed_conversions": failed,
                "success_rate": successful / total_files if total_files > 0 else 0,
                "total_original_size_mb": total_original_size / (1024 * 1024),
                "total_markdown_size_mb": total_markdown_size / (1024 * 1024),
                "size_reduction_percent": (1 - total_markdown_size / total_original_size) * 100 if total_original_size > 0 else 0,
                "average_quality_score": avg_quality
            },
            "method_statistics": {},
            "results": [asdict(r) for r in results]
        }
        
        # Calculate method statistics
        methods = set(r.method for r in results if r.success)
        for method in methods:
            method_results = [r for r in results if r.method == method]
            report["method_statistics"][method] = {
                "count": len(method_results),
                "avg_processing_time": sum(r.processing_time for r in method_results) / len(method_results),
                "avg_quality_score": sum(r.quality_score for r in method_results) / len(method_results)
            }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Conversion report saved to {report_path}")
        
        # Print summary
        print(f"\n{'='*60}")
        print("CONVERSION SUMMARY")
        print(f"{'='*60}")
        print(f"Total files processed: {total_files}")
        print(f"Successful conversions: {successful}")
        print(f"Failed conversions: {failed}")
        print(f"Success rate: {successful/total_files*100:.1f}%")
        print(f"Original size: {total_original_size/(1024*1024):.1f} MB")
        print(f"Markdown size: {total_markdown_size/(1024*1024):.1f} MB")
        print(f"Size reduction: {(1-total_markdown_size/total_original_size)*100:.1f}%")
        print(f"Average quality score: {avg_quality:.2f}")
        print(f"{'='*60}")


@click.command()
@click.option('--input-dir', '-i', default='../papers', help='Input directory containing PDF files')
@click.option('--output-dir', '-o', default='../papers_markdown', help='Output directory for markdown files')
@click.option('--max-workers', '-w', default=4, help='Maximum number of parallel workers')
@click.option('--pattern', '-p', default='*.pdf', help='File pattern to match')
def main(input_dir: str, output_dir: str, max_workers: int, pattern: str):
    """Convert PDF research papers to markdown format."""
    
    # Setup logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_path}")
        return
    
    # Find PDF files
    pdf_files = list(input_path.glob(pattern))
    if not pdf_files:
        logger.error(f"No PDF files found in {input_path} matching pattern {pattern}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to convert")
    
    # Initialize converter
    converter = PDFToMarkdownConverter(input_path, output_path, max_workers)
    
    # Convert files
    results = converter.convert_batch(pdf_files)
    
    # Save report
    converter.save_conversion_report(results)


if __name__ == "__main__":
    main()
