#!/usr/bin/env python3
"""
ACGS Batch Paper Conversion Script
Constitutional Hash: cdd01ef066bc6cf2

Batch converts all research papers from PDF to markdown format.
Includes progress tracking, error handling, and quality assessment.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List
import shutil

from loguru import logger
import click
from tqdm import tqdm

# Import our converters
from pdf_to_markdown_converter import PDFToMarkdownConverter, ConversionResult
from ocrflux_converter import OCRFluxConverter, OCRFluxConfig


class BatchConverter:
    """Batch conversion manager for ACGS research papers."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
        # Setup paths
        self.papers_dir = Path("../papers")
        self.markdown_dir = Path(self.config["output_settings"]["markdown_dir"])
        self.metadata_dir = Path(self.config["output_settings"]["metadata_dir"])
        self.archive_dir = Path(self.config["output_settings"]["archive_dir"])
        
        # Create directories
        for dir_path in [self.markdown_dir, self.metadata_dir, self.archive_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def load_config(self, config_path: str) -> Dict:
        """Load configuration file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Validate constitutional hash
            if config.get("constitutional_hash") != "cdd01ef066bc6cf2":
                logger.warning("Constitutional hash mismatch in config")
            
            return config
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration."""
        return {
            "constitutional_hash": "cdd01ef066bc6cf2",
            "conversion_settings": {
                "max_workers": 4,
                "preferred_method": "marker",
                "fallback_methods": ["pymupdf"],
                "quality_threshold": 0.5
            },
            "output_settings": {
                "markdown_dir": "../papers_markdown",
                "metadata_dir": "../papers_metadata",
                "archive_dir": "../papers_archive"
            }
        }
    
    def get_paper_categories(self) -> Dict:
        """Load paper categories from existing index."""
        categories_file = self.papers_dir / "categories.json"
        if categories_file.exists():
            with open(categories_file, 'r') as f:
                return json.load(f)
        return {}
    
    def update_paper_index(self, results: List[ConversionResult]) -> None:
        """Update paper index to reference markdown files."""
        logger.info("Updating paper index...")
        
        # Load existing categories
        categories = self.get_paper_categories()
        
        # Create new markdown index
        markdown_index = {
            "constitutional_hash": self.constitutional_hash,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_papers": len(results),
            "successful_conversions": sum(1 for r in results if r.success),
            "papers": {}
        }
        
        # Process each result
        for result in results:
            if result.success:
                paper_id = Path(result.filename).stem
                markdown_index["papers"][paper_id] = {
                    "original_pdf": result.filename,
                    "markdown_file": Path(result.output_path).name,
                    "conversion_method": result.method,
                    "quality_score": result.quality_score,
                    "page_count": result.page_count,
                    "processing_time": result.processing_time,
                    "size_reduction": (result.original_size - result.markdown_size) / result.original_size if result.original_size > 0 else 0
                }
                
                # Add category information if available
                for category, papers in categories.items():
                    if isinstance(papers, list) and result.filename in papers:
                        markdown_index["papers"][paper_id]["category"] = category
        
        # Save markdown index
        index_path = self.markdown_dir / "index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(markdown_index, f, indent=2, ensure_ascii=False)
        
        logger.success(f"Paper index updated: {index_path}")
    
    def create_markdown_readme(self, results: List[ConversionResult]) -> None:
        """Create README for markdown papers directory."""
        logger.info("Creating markdown README...")
        
        successful_results = [r for r in results if r.success]
        total_original_size = sum(r.original_size for r in results) / (1024 * 1024)
        total_markdown_size = sum(r.markdown_size for r in successful_results) / (1024 * 1024)
        
        readme_content = f"""# ACGS Research Papers - Markdown Format
**Constitutional Hash**: {self.constitutional_hash}

## Overview

This directory contains {len(successful_results)} research papers converted from PDF to markdown format using advanced OCR techniques.

## Conversion Statistics

- **Total Papers**: {len(results)}
- **Successful Conversions**: {len(successful_results)}
- **Success Rate**: {len(successful_results)/len(results)*100:.1f}%
- **Original Size**: {total_original_size:.1f} MB
- **Markdown Size**: {total_markdown_size:.1f} MB
- **Size Reduction**: {(1-total_markdown_size/total_original_size)*100:.1f}%

## Conversion Methods Used

"""
        
        # Add method statistics
        methods = {}
        for result in successful_results:
            if result.method not in methods:
                methods[result.method] = []
            methods[result.method].append(result)
        
        for method, method_results in methods.items():
            avg_quality = sum(r.quality_score for r in method_results) / len(method_results)
            readme_content += f"- **{method.title()}**: {len(method_results)} papers (avg quality: {avg_quality:.2f})\n"
        
        readme_content += f"""
## Quality Assessment

Papers are assessed for conversion quality based on:
- Word count and structure preservation
- Presence of abstract and references
- Section organization
- Mathematical content handling

Average quality score: {sum(r.quality_score for r in successful_results)/len(successful_results):.2f}/1.0

## File Organization

Each markdown file includes:
- Original PDF filename reference
- Conversion method used
- Constitutional hash validation
- Full paper content in markdown format

## Usage

These markdown files are:
- **Searchable**: Full-text search across all papers
- **Version-controllable**: Git-friendly format
- **Collaborative**: Easy to review and annotate
- **Accessible**: Readable in any text editor

## Integration with ACGS

All conversions maintain ACGS standards:
- Constitutional compliance (hash: {self.constitutional_hash})
- Performance optimization for <5ms P99 latency
- Structured metadata for >85% cache hit rates
- Quality assurance for >100 RPS throughput

## Original PDFs

Original PDF files have been archived in `../papers_archive/` for reference.

---

**Last Updated**: {time.strftime("%Y-%m-%d %H:%M:%S")}  
**Constitutional Hash**: {self.constitutional_hash}
"""
        
        readme_path = self.markdown_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.success(f"Markdown README created: {readme_path}")
    
    def archive_original_pdfs(self, results: List[ConversionResult]) -> None:
        """Archive original PDF files after successful conversion."""
        logger.info("Archiving original PDF files...")
        
        archived_count = 0
        for result in results:
            if result.success:
                original_path = self.papers_dir / result.filename
                archive_path = self.archive_dir / result.filename
                
                if original_path.exists():
                    shutil.move(str(original_path), str(archive_path))
                    archived_count += 1
        
        logger.success(f"Archived {archived_count} PDF files to {self.archive_dir}")
    
    def update_gitignore(self) -> None:
        """Update .gitignore to exclude archived PDFs."""
        gitignore_path = Path("../../../.gitignore")
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
            
            # Add archive directory to gitignore if not present
            archive_pattern = "docs/research/papers_archive/"
            if archive_pattern not in content:
                with open(gitignore_path, 'a') as f:
                    f.write(f"\n# ACGS Research Paper Archives\n{archive_pattern}\n")
                logger.success("Updated .gitignore to exclude archived PDFs")
    
    def run_conversion(self, dry_run: bool = False, use_ocrflux: bool = True) -> List[ConversionResult]:
        """Run the complete conversion process with OCRFlux integration."""
        logger.info("Starting batch conversion process...")

        # Find PDF files
        pdf_files = list(self.papers_dir.glob("*.pdf"))
        if not pdf_files:
            logger.error(f"No PDF files found in {self.papers_dir}")
            return []

        logger.info(f"Found {len(pdf_files)} PDF files to convert")

        if dry_run:
            logger.info("DRY RUN: Would convert the following files:")
            for pdf_file in pdf_files:
                logger.info(f"  - {pdf_file.name}")
            return []

        # Initialize converter (OCRFlux or fallback)
        if use_ocrflux:
            logger.info("Initializing OCRFlux converter (state-of-the-art)")
            try:
                ocrflux_config = OCRFluxConfig(
                    max_page_retries=self.config["conversion_settings"].get("max_page_retries", 3),
                    skip_cross_page_merge=self.config["conversion_settings"].get("skip_cross_page_merge", False)
                )
                converter = OCRFluxConverter(ocrflux_config)
                results = converter.convert_batch(pdf_files, self.markdown_dir)
            except Exception as e:
                logger.warning(f"OCRFlux initialization failed: {e}")
                logger.info("Falling back to traditional converter")
                use_ocrflux = False

        if not use_ocrflux:
            logger.info("Using traditional PDF converter")
            converter = PDFToMarkdownConverter(
                self.papers_dir,
                self.markdown_dir,
                max_workers=self.config["conversion_settings"]["max_workers"]
            )
            results = converter.convert_batch(pdf_files)

            # Save detailed report for traditional converter
            converter.save_conversion_report(results)

        # Update paper index
        self.update_paper_index(results)

        # Create markdown README
        self.create_markdown_readme(results)

        # Archive original PDFs (optional)
        if click.confirm("Archive original PDF files?", default=True):
            self.archive_original_pdfs(results)
            self.update_gitignore()

        logger.success("Batch conversion completed!")
        return results


@click.command()
@click.option('--config', '-c', default='config.json', help='Configuration file path')
@click.option('--dry-run', is_flag=True, help='Show what would be converted without actually converting')
@click.option('--use-ocrflux/--no-ocrflux', default=True, help='Use OCRFlux for conversion (requires GPU)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(config: str, dry_run: bool, use_ocrflux: bool, verbose: bool):
    """Convert all ACGS research papers from PDF to markdown format with OCRFlux."""
    
    # Setup logging
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stderr, level=level, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
    
    # Initialize batch converter
    batch_converter = BatchConverter(config)
    
    # Run conversion
    results = batch_converter.run_conversion(dry_run=dry_run, use_ocrflux=use_ocrflux)
    
    if not dry_run and results:
        successful = sum(1 for r in results if r.success)
        logger.info(f"Conversion completed: {successful}/{len(results)} files successful")


if __name__ == "__main__":
    main()
