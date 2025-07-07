#!/usr/bin/env python3
"""
Simple ACGS Research Paper Converter
Constitutional Hash: cdd01ef066bc6cf2

Simple and reliable PDF to markdown converter using PyMuPDF.
"""

import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

import click
import fitz  # PyMuPDF
from loguru import logger
from tqdm import tqdm


@dataclass
class ConversionResult:
    """Results from PDF to markdown conversion."""

    filename: str
    success: bool
    method: str = "pymupdf"
    output_path: str = ""
    error_message: str = ""
    processing_time: float = 0.0
    original_size: int = 0
    markdown_size: int = 0
    page_count: int = 0
    quality_score: float = 0.0
    constitutional_hash: str = "cdd01ef066bc6cf2"


class SimpleConverter:
    """Simple PDF to Markdown converter using PyMuPDF."""

    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def convert_with_pymupdf(self, pdf_path: Path) -> tuple[str, float]:
        """Convert PDF using PyMuPDF."""
        start_time = time.time()

        try:
            doc = fitz.open(str(pdf_path))
            markdown_content = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()

                # Basic markdown formatting
                if text.strip():
                    # Clean up text
                    lines = text.split("\n")
                    cleaned_lines = []

                    for line in lines:
                        line = line.strip()
                        if line:
                            # Simple heuristics for headers
                            if (
                                len(line) < 100
                                and line.isupper()
                                and len(line.split()) <= 10
                            ):
                                cleaned_lines.append(f"## {line.title()}")
                            elif line.endswith(".") or line.endswith(":"):
                                cleaned_lines.append(line)
                            else:
                                cleaned_lines.append(line)

                    if cleaned_lines:
                        markdown_content.append(
                            f"## Page {page_num + 1}\n\n"
                            + "\n\n".join(cleaned_lines)
                            + "\n"
                        )

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
            line_count = len(markdown_content.split("\n"))

            # Check for common academic paper elements
            has_abstract = "abstract" in markdown_content.lower()
            has_references = any(
                ref in markdown_content.lower()
                for ref in ["references", "bibliography", "citations"]
            )
            has_sections = markdown_content.count("#") > 3

            # Calculate quality score (0-1)
            quality_score = 0.0
            if word_count > 100:
                quality_score += 0.4
            if has_abstract:
                quality_score += 0.2
            if has_references:
                quality_score += 0.2
            if has_sections:
                quality_score += 0.2

            return min(quality_score, 1.0)

        except Exception:
            return 0.5

    def convert_single_pdf(self, pdf_path: Path) -> ConversionResult:
        """Convert a single PDF file to markdown."""
        logger.info(f"Converting {pdf_path.name}")

        result = ConversionResult(
            filename=pdf_path.name, success=False, original_size=pdf_path.stat().st_size
        )

        try:
            markdown_content, processing_time = self.convert_with_pymupdf(pdf_path)

            # Save markdown file
            output_filename = pdf_path.stem + ".md"
            output_path = self.output_dir / output_filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# {pdf_path.stem}\n\n")
                f.write(f"**Original PDF**: {pdf_path.name}\n")
                f.write(f"**Conversion Method**: PyMuPDF\n")
                f.write(f"**Constitutional Hash**: cdd01ef066bc6cf2\n\n")
                f.write("---\n\n")
                f.write(markdown_content)

            # Update result
            result.success = True
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

            logger.success(
                f"Successfully converted {pdf_path.name} (quality: {result.quality_score:.2f})"
            )

        except Exception as e:
            logger.error(f"Conversion failed for {pdf_path.name}: {e}")
            result.error_message = str(e)

        return result

    def convert_batch(self, pdf_files: List[Path]) -> List[ConversionResult]:
        """Convert multiple PDF files."""
        results = []

        with tqdm(total=len(pdf_files), desc="Converting PDFs") as pbar:
            for pdf_path in pdf_files:
                result = self.convert_single_pdf(pdf_path)
                results.append(result)

                # Update progress
                success_count = sum(1 for r in results if r.success)
                pbar.update(1)
                pbar.set_postfix(
                    {
                        "Success": f"{success_count}/{len(results)}",
                        "Quality": (
                            f"{result.quality_score:.2f}"
                            if result.success
                            else "Failed"
                        ),
                    }
                )

        return results

    def save_report(self, results: List[ConversionResult]) -> None:
        """Save conversion report."""
        report_path = self.output_dir.parent / "papers_metadata"
        report_path.mkdir(parents=True, exist_ok=True)

        # Create summary statistics
        total_files = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total_files - successful

        total_original_size = sum(r.original_size for r in results)
        total_markdown_size = sum(r.markdown_size for r in results if r.success)

        avg_quality = sum(r.quality_score for r in results if r.success) / max(
            successful, 1
        )

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
                "size_reduction_percent": (
                    (1 - total_markdown_size / total_original_size) * 100
                    if total_original_size > 0
                    else 0
                ),
                "average_quality_score": avg_quality,
            },
            "results": [asdict(r) for r in results],
        }

        with open(report_path / "conversion_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Conversion report saved to {report_path / 'conversion_report.json'}"
        )

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
@click.option(
    "--input-dir",
    "-i",
    default="../papers",
    help="Input directory containing PDF files",
)
@click.option(
    "--output-dir",
    "-o",
    default="../papers_markdown",
    help="Output directory for markdown files",
)
@click.option("--pattern", "-p", default="*.pdf", help="File pattern to match")
def main(input_dir: str, output_dir: str, pattern: str):
    """Convert PDF research papers to markdown format."""

    # Setup logging
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    )

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
    converter = SimpleConverter(input_path, output_path)

    # Convert files
    results = converter.convert_batch(pdf_files)

    # Save report
    converter.save_report(results)


if __name__ == "__main__":
    main()
