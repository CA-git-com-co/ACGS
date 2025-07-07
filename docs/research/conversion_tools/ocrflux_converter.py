#!/usr/bin/env python3
"""
ACGS OCRFlux Integration Module
Constitutional Hash: cdd01ef066bc6cf2

Enhanced PDF to Markdown converter using OCRFlux for superior academic paper conversion.
Includes GPU detection, model management, and fallback mechanisms.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import time
import tempfile
import shutil

import click
from loguru import logger
import torch

# Try to import OCRFlux components
OCRFLUX_AVAILABLE = False
try:
    from vllm import LLM
    # OCRFlux will be imported dynamically after installation
    OCRFLUX_AVAILABLE = True
    logger.info("OCRFlux dependencies available")
except ImportError as e:
    logger.warning(f"OCRFlux dependencies not available: {e}")

# Import our fallback converters
from pdf_to_markdown_converter import PDFToMarkdownConverter, ConversionResult


@dataclass
class OCRFluxConfig:
    """Configuration for OCRFlux conversion."""
    model_path: str = "ChatDOC/OCRFlux-3B"
    gpu_memory_utilization: float = 0.8
    max_model_len: int = 8192
    max_page_retries: int = 3
    skip_cross_page_merge: bool = False
    target_longest_image_dim: int = 1024
    constitutional_hash: str = "cdd01ef066bc6cf2"


class OCRFluxConverter:
    """Enhanced PDF to Markdown converter using OCRFlux."""
    
    def __init__(self, config: OCRFluxConfig):
        self.config = config
        self.llm = None
        self.ocrflux_available = False
        self.fallback_converter = None
        
        # Check GPU availability
        self.gpu_available = torch.cuda.is_available()
        if self.gpu_available:
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            logger.info(f"GPU detected: {torch.cuda.get_device_name(0)} ({gpu_memory:.1f}GB)")
            
            if gpu_memory < 12:
                logger.warning("GPU has less than 12GB memory. OCRFlux may not work optimally.")
        else:
            logger.warning("No GPU detected. OCRFlux requires GPU for optimal performance.")
        
        # Initialize OCRFlux if available
        self._initialize_ocrflux()
    
    def _initialize_ocrflux(self) -> bool:
        """Initialize OCRFlux model and dependencies."""
        if not OCRFLUX_AVAILABLE or not self.gpu_available:
            logger.info("OCRFlux not available, will use fallback methods")
            return False
        
        try:
            # Check if OCRFlux is installed
            import ocrflux
            from ocrflux.inference import parse
            
            # Initialize VLLM model
            logger.info(f"Loading OCRFlux model: {self.config.model_path}")
            self.llm = LLM(
                model=self.config.model_path,
                gpu_memory_utilization=self.config.gpu_memory_utilization,
                max_model_len=self.config.max_model_len,
                trust_remote_code=True
            )
            
            self.ocrflux_available = True
            logger.success("OCRFlux initialized successfully")
            return True
            
        except ImportError:
            logger.warning("OCRFlux not installed. Use setup script to install.")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize OCRFlux: {e}")
            return False
    
    def _setup_fallback_converter(self, input_dir: Path, output_dir: Path) -> None:
        """Setup fallback converter for when OCRFlux is not available."""
        if not self.fallback_converter:
            self.fallback_converter = PDFToMarkdownConverter(
                input_dir=input_dir,
                output_dir=output_dir,
                max_workers=2  # Conservative for fallback
            )
    
    def convert_with_ocrflux(self, pdf_path: Path) -> Tuple[str, float, Dict]:
        """Convert PDF using OCRFlux."""
        if not self.ocrflux_available:
            raise ValueError("OCRFlux not available")
        
        start_time = time.time()
        
        try:
            from ocrflux.inference import parse
            
            # Convert PDF using OCRFlux
            result = parse(
                self.llm,
                str(pdf_path),
                max_page_retries=self.config.max_page_retries
            )
            
            processing_time = time.time() - start_time
            
            if result is None:
                raise ValueError("OCRFlux parsing failed")
            
            # Extract markdown content
            markdown_content = result.get('document_text', '')
            
            # Additional metadata from OCRFlux
            metadata = {
                'num_pages': result.get('num_pages', 0),
                'fallback_pages': result.get('fallback_pages', []),
                'page_texts': result.get('page_texts', {}),
                'cross_page_merged': not self.config.skip_cross_page_merge
            }
            
            return markdown_content, processing_time, metadata
            
        except Exception as e:
            logger.error(f"OCRFlux conversion failed for {pdf_path}: {e}")
            raise
    
    def assess_ocrflux_quality(self, markdown_content: str, metadata: Dict) -> float:
        """Assess OCRFlux conversion quality."""
        try:
            # Basic quality metrics
            word_count = len(markdown_content.split())
            line_count = len(markdown_content.split('\n'))
            
            # OCRFlux-specific quality indicators
            has_structure = markdown_content.count('#') > 2
            has_tables = '|' in markdown_content or 'table' in markdown_content.lower()
            has_equations = any(eq in markdown_content for eq in ['$$', '$', '\\(', '\\['])
            
            # Check for academic paper elements
            has_abstract = 'abstract' in markdown_content.lower()
            has_references = any(ref in markdown_content.lower() 
                               for ref in ['references', 'bibliography', 'citations'])
            
            # Factor in OCRFlux metadata
            fallback_pages = metadata.get('fallback_pages', [])
            total_pages = metadata.get('num_pages', 1)
            success_rate = 1 - (len(fallback_pages) / max(total_pages, 1))
            
            # Calculate quality score (0-1)
            quality_score = 0.0
            
            # Content quality (40%)
            if word_count > 500:
                quality_score += 0.2
            if has_structure:
                quality_score += 0.1
            if has_tables:
                quality_score += 0.05
            if has_equations:
                quality_score += 0.05
            
            # Academic elements (30%)
            if has_abstract:
                quality_score += 0.15
            if has_references:
                quality_score += 0.15
            
            # OCRFlux success rate (30%)
            quality_score += 0.3 * success_rate
            
            return min(quality_score, 1.0)
            
        except Exception:
            return 0.5  # Default score if assessment fails
    
    def convert_single_pdf(self, pdf_path: Path, output_dir: Path) -> ConversionResult:
        """Convert a single PDF using OCRFlux with fallback."""
        logger.info(f"Converting {pdf_path.name} with OCRFlux")
        
        result = ConversionResult(
            filename=pdf_path.name,
            success=False,
            method="none",
            original_size=pdf_path.stat().st_size
        )
        
        # Try OCRFlux first
        if self.ocrflux_available:
            try:
                markdown_content, processing_time, metadata = self.convert_with_ocrflux(pdf_path)
                
                # Save markdown file
                output_filename = pdf_path.stem + ".md"
                output_path = output_dir / output_filename
                
                # Create enhanced markdown with OCRFlux metadata
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {pdf_path.stem}\n\n")
                    f.write(f"**Original PDF**: {pdf_path.name}\n")
                    f.write(f"**Conversion Method**: OCRFlux-3B\n")
                    f.write(f"**Constitutional Hash**: {self.config.constitutional_hash}\n")
                    f.write(f"**Pages**: {metadata.get('num_pages', 'Unknown')}\n")
                    f.write(f"**Cross-page Merging**: {'Enabled' if metadata.get('cross_page_merged') else 'Disabled'}\n")
                    
                    if metadata.get('fallback_pages'):
                        f.write(f"**Fallback Pages**: {metadata['fallback_pages']}\n")
                    
                    f.write("\n---\n\n")
                    f.write(markdown_content)
                
                # Update result
                result.success = True
                result.method = "ocrflux"
                result.output_path = str(output_path)
                result.processing_time = processing_time
                result.markdown_size = output_path.stat().st_size
                result.page_count = metadata.get('num_pages', 0)
                result.quality_score = self.assess_ocrflux_quality(markdown_content, metadata)
                
                logger.success(f"OCRFlux conversion successful: {pdf_path.name} (quality: {result.quality_score:.2f})")
                return result
                
            except Exception as e:
                logger.warning(f"OCRFlux failed for {pdf_path.name}: {e}")
                result.error_message = f"OCRFlux error: {str(e)}"
        
        # Fallback to traditional methods
        logger.info(f"Using fallback conversion for {pdf_path.name}")
        self._setup_fallback_converter(pdf_path.parent, output_dir)
        
        fallback_result = self.fallback_converter.convert_single_pdf(pdf_path)
        fallback_result.method = f"fallback-{fallback_result.method}"
        
        return fallback_result
    
    def convert_batch(self, pdf_files: List[Path], output_dir: Path) -> List[ConversionResult]:
        """Convert multiple PDFs with OCRFlux and fallback methods."""
        results = []
        
        logger.info(f"Starting batch conversion of {len(pdf_files)} files with OCRFlux")
        
        for pdf_path in pdf_files:
            try:
                result = self.convert_single_pdf(pdf_path, output_dir)
                results.append(result)
                
                # Log progress
                success_count = sum(1 for r in results if r.success)
                ocrflux_count = sum(1 for r in results if r.method == "ocrflux")
                
                logger.info(f"Progress: {len(results)}/{len(pdf_files)} "
                          f"(Success: {success_count}, OCRFlux: {ocrflux_count})")
                
            except Exception as e:
                logger.error(f"Failed to convert {pdf_path.name}: {e}")
                results.append(ConversionResult(
                    filename=pdf_path.name,
                    success=False,
                    method="error",
                    error_message=str(e),
                    original_size=pdf_path.stat().st_size if pdf_path.exists() else 0
                ))
        
        return results


@click.command()
@click.option('--input-dir', '-i', default='../papers', help='Input directory containing PDF files')
@click.option('--output-dir', '-o', default='../papers_markdown', help='Output directory for markdown files')
@click.option('--model-path', '-m', default='ChatDOC/OCRFlux-3B', help='OCRFlux model path')
@click.option('--gpu-memory', '-g', default=0.8, help='GPU memory utilization (0.1-0.9)')
@click.option('--skip-cross-page', is_flag=True, help='Skip cross-page merging for speed')
@click.option('--pattern', '-p', default='*.pdf', help='File pattern to match')
def main(input_dir: str, output_dir: str, model_path: str, gpu_memory: float, 
         skip_cross_page: bool, pattern: str):
    """Convert PDF research papers using OCRFlux with fallback methods."""
    
    # Setup logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", 
              format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_path}")
        return
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find PDF files
    pdf_files = list(input_path.glob(pattern))
    if not pdf_files:
        logger.error(f"No PDF files found in {input_path} matching pattern {pattern}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to convert")
    
    # Initialize OCRFlux converter
    config = OCRFluxConfig(
        model_path=model_path,
        gpu_memory_utilization=gpu_memory,
        skip_cross_page_merge=skip_cross_page
    )
    
    converter = OCRFluxConverter(config)
    
    # Convert files
    results = converter.convert_batch(pdf_files, output_path)
    
    # Print summary
    total_files = len(results)
    successful = sum(1 for r in results if r.success)
    ocrflux_count = sum(1 for r in results if r.method == "ocrflux")
    
    print(f"\n{'='*60}")
    print("OCRFlux CONVERSION SUMMARY")
    print(f"{'='*60}")
    print(f"Total files processed: {total_files}")
    print(f"Successful conversions: {successful}")
    print(f"OCRFlux conversions: {ocrflux_count}")
    print(f"Fallback conversions: {successful - ocrflux_count}")
    print(f"Success rate: {successful/total_files*100:.1f}%")
    print(f"OCRFlux rate: {ocrflux_count/total_files*100:.1f}%")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
