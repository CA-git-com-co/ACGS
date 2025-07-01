#!/usr/bin/env python3
"""
Enhanced OCR Service Integration Module for ACGS

This module provides advanced integration between the OCR service and the ACGS system,
leveraging Nanonets-OCR-s capabilities for comprehensive document processing including
signature detection, watermark extraction, LaTeX equations, and structured parsing.
"""

import base64
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

try:
    from .advanced_document_processor import (
        AdvancedDocumentProcessor,
        ProcessedDocument,
    )
except ImportError:
    from advanced_document_processor import AdvancedDocumentProcessor, ProcessedDocument

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("enhanced-ocr-integration")


class OCRServiceException(Exception):
    """Exception raised for errors in the OCR service."""


class EnhancedOCRIntegration:
    """
    Enhanced OCR integration class leveraging Nanonets-OCR-s advanced capabilities
    for comprehensive document processing within the ACGS system.
    """

    def __init__(self, host: str = None, port: int = None):
        """Initialize the enhanced OCR integration with service connection details."""
        self.host = host or os.environ.get("OCR_SERVICE_HOST", "ocr-service")
        self.port = port or int(os.environ.get("OCR_SERVICE_PORT", "8666"))
        self.endpoint = f"http://{self.host}:{self.port}/v1/chat/completions"
        self.health_endpoint = f"http://{self.host}:{self.port}/health"

        # Initialize advanced document processor
        self.document_processor = AdvancedDocumentProcessor()

        # Enhanced prompt templates for different document types
        self.prompt_templates = self._initialize_prompt_templates()

        logger.info(
            f"Enhanced OCR integration initialized with endpoint: {self.endpoint}"
        )
        logger.info("Advanced document processing capabilities enabled")

    def _initialize_prompt_templates(self) -> dict[str, str]:
        """Initialize enhanced prompt templates for different document types"""
        base_nanonets_prompt = """Extract the text from the above document as if you were reading it naturally. Return the tables in html format. Return the equations in LaTeX representation. If there is an image in the document and image caption is not present, add a small description of the image inside the <img></img> tag; otherwise, add the image caption inside <img></img>. Watermarks should be wrapped in brackets. Ex: <watermark>OFFICIAL COPY</watermark>. Page numbers should be wrapped in brackets. Ex: <page_number>14</page_number> or <page_number>9/22</page_number>. Prefer using ☐ and ☑ for check boxes."""

        return {
            "general": base_nanonets_prompt,
            "constitutional": base_nanonets_prompt
            + "\n\nThis is a constitutional document. Pay special attention to articles, amendments, legal structure, signatures, and official authentication markers.",
            "legal": base_nanonets_prompt
            + "\n\nThis is a legal document. Extract all legal terms, citations, signatures, seals, and formal authentication elements precisely.",
            "policy": base_nanonets_prompt
            + "\n\nThis is a policy document. Focus on rules, procedures, implementation guidelines, tables, approval signatures, and governance structures.",
            "governance_form": base_nanonets_prompt
            + "\n\nThis is a governance form. Extract all fields, checkboxes, signatures, and tabular data with proper formatting.",
            "official_document": base_nanonets_prompt
            + "\n\nThis is an official document. Pay special attention to watermarks, official seals, signatures, and authentication markers.",
            "technical": base_nanonets_prompt
            + "\n\nThis is a technical document. Focus on equations, formulas, technical diagrams, tables, and structured data.",
            "form": base_nanonets_prompt
            + "\n\nThis is a form document. Extract all form fields, checkboxes, signatures, and maintain the form structure.",
            "receipt": base_nanonets_prompt
            + "\n\nThis is a receipt. Extract vendor, date, items, prices, total, and any signatures or stamps.",
            "invoice": base_nanonets_prompt
            + "\n\nThis is an invoice. Extract invoice number, date, vendor, line items, total amount, and payment terms.",
            "contract": base_nanonets_prompt
            + "\n\nThis is a contract. Focus on parties, terms, conditions, signatures, dates, and legal clauses.",
        }

    def check_health(self) -> bool:
        """Check if the OCR service is healthy."""
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.warning(f"OCR service health check failed: {e}")
            return False

    def encode_image(self, image_path: str | Path) -> str:
        """Encode an image file to base64."""
        image_path = Path(image_path)
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def extract_text(
        self,
        image_data: str | Path | bytes,
        prompt: str = "Extract all text from this image.",
    ) -> dict[str, Any]:
        """
        Extract text from an image using the OCR service.

        Args:
            image_data: Can be a file path, URL, or raw bytes
            prompt: Specific instruction for the OCR model

        Returns:
            Dictionary containing the extracted text and metadata
        """
        try:
            # Handle different image_data types
            if isinstance(image_data, (str, Path)):
                path = Path(image_data)
                if path.exists():
                    # Local file
                    image_base64 = self.encode_image(path)
                    image_url = f"data:image/jpeg;base64,{image_base64}"
                else:
                    # Assume it's a URL
                    image_url = str(image_data)
            elif isinstance(image_data, bytes):
                # Raw bytes
                image_base64 = base64.b64encode(image_data).decode("utf-8")
                image_url = f"data:image/jpeg;base64,{image_base64}"
            else:
                raise ValueError(f"Unsupported image data type: {type(image_data)}")

            payload = {
                "model": "nanonets/Nanonets-OCR-s",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
            }

            response = requests.post(self.endpoint, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Extract the actual text content from the response
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "text": content,
                    "metadata": {
                        "model": result.get("model", "unknown"),
                        "usage": result.get("usage", {}),
                    },
                }
            return {
                "success": False,
                "error": "No content in response",
                "raw_response": result,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling OCR service: {e}")
            raise OCRServiceException(f"OCR service request failed: {e!s}")
        except Exception as e:
            logger.error(f"Unexpected error in OCR integration: {e}")
            raise OCRServiceException(f"OCR integration error: {e!s}")

    def analyze_document(
        self, image_data: str | Path | bytes, analysis_type: str = "general"
    ) -> dict[str, Any]:
        """
        Perform enhanced document analysis with structured element extraction.

        Args:
            image_data: Can be a file path, URL, or raw bytes
            analysis_type: Type of analysis to perform (general, constitutional, legal, etc.)

        Returns:
            Dictionary containing the analysis results with structured elements
        """
        # Get the appropriate prompt for the document type
        prompt = self.prompt_templates.get(
            analysis_type, self.prompt_templates["general"]
        )

        # Extract raw text using OCR
        ocr_result = self.extract_text(image_data, prompt)

        if not ocr_result.get("success", False):
            return ocr_result

        # Process the extracted text for structured elements
        raw_text = ocr_result["text"]
        processed_doc = self.document_processor.process_document(raw_text)

        # Enhance the result with structured data
        enhanced_result = {
            "success": True,
            "raw_text": raw_text,
            "processed_document": self.document_processor.to_dict(processed_doc),
            "structured_elements": {
                "signatures": len(processed_doc.signatures),
                "watermarks": len(processed_doc.watermarks),
                "equations": len(processed_doc.equations),
                "tables": len(processed_doc.tables),
                "checkboxes": len(processed_doc.checkboxes),
                "images": len(processed_doc.images),
                "page_numbers": len(processed_doc.page_numbers),
            },
            "confidence_score": processed_doc.confidence_score,
            "metadata": {
                **ocr_result.get("metadata", {}),
                **processed_doc.metadata,
                "analysis_type": analysis_type,
                "processing_timestamp": datetime.now().isoformat(),
            },
        }

        return enhanced_result

    def extract_structured_elements(
        self, image_data: str | Path | bytes, document_type: str = "general"
    ) -> ProcessedDocument:
        """
        Extract structured elements from a document and return ProcessedDocument object.

        Args:
            image_data: Can be a file path, URL, or raw bytes
            document_type: Type of document for optimized processing

        Returns:
            ProcessedDocument with all extracted structured elements
        """
        prompt = self.prompt_templates.get(
            document_type, self.prompt_templates["general"]
        )
        ocr_result = self.extract_text(image_data, prompt)

        if not ocr_result.get("success", False):
            raise OCRServiceException(
                f"OCR extraction failed: {ocr_result.get('error', 'Unknown error')}"
            )

        raw_text = ocr_result["text"]
        processed_doc = self.document_processor.process_document(raw_text)

        return processed_doc

    def get_document_authenticity_score(
        self, image_data: str | Path | bytes
    ) -> dict[str, Any]:
        """
        Analyze document authenticity based on signatures, watermarks, and other markers.

        Args:
            image_data: Can be a file path, URL, or raw bytes

        Returns:
            Dictionary with authenticity analysis
        """
        processed_doc = self.extract_structured_elements(
            image_data, "official_document"
        )

        authenticity_factors = {
            "has_signatures": len(processed_doc.signatures) > 0,
            "has_watermarks": len(processed_doc.watermarks) > 0,
            "has_page_numbers": len(processed_doc.page_numbers) > 0,
            "signature_count": len(processed_doc.signatures),
            "watermark_count": len(processed_doc.watermarks),
        }

        # Calculate authenticity score
        score = 0.5  # Base score
        if authenticity_factors["has_signatures"]:
            score += 0.3
        if authenticity_factors["has_watermarks"]:
            score += 0.2
        if authenticity_factors["has_page_numbers"]:
            score += 0.1

        authenticity_score = min(1.0, score)

        return {
            "authenticity_score": authenticity_score,
            "authenticity_factors": authenticity_factors,
            "signatures": [sig.content for sig in processed_doc.signatures],
            "watermarks": [wm.content for wm in processed_doc.watermarks],
            "confidence": processed_doc.confidence_score,
        }


# Backward compatibility alias
OCRIntegration = EnhancedOCRIntegration


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python ocr_integration.py <image_path> [analysis_type] [--structured]"
        )
        print(
            "Analysis types: general, constitutional, legal, policy, governance_form, etc."
        )
        print("Use --structured flag to get detailed structured element extraction")
        sys.exit(1)

    image_path = sys.argv[1]
    analysis_type = (
        sys.argv[2]
        if len(sys.argv) > 2 and not sys.argv[2].startswith("--")
        else "general"
    )
    structured_mode = "--structured" in sys.argv

    ocr = EnhancedOCRIntegration()
    if not ocr.check_health():
        print("OCR service is not healthy. Please check if it's running.")
        sys.exit(1)

    try:
        if structured_mode:
            # Get detailed structured analysis
            processed_doc = ocr.extract_structured_elements(image_path, analysis_type)
            result = ocr.document_processor.to_dict(processed_doc)
            print("=== STRUCTURED DOCUMENT ANALYSIS ===")
            print(f"Document ID: {processed_doc.document_id}")
            print(f"Confidence Score: {processed_doc.confidence_score}")
            print(f"Signatures found: {len(processed_doc.signatures)}")
            print(f"Watermarks found: {len(processed_doc.watermarks)}")
            print(f"Equations found: {len(processed_doc.equations)}")
            print(f"Tables found: {len(processed_doc.tables)}")
            print(f"Checkboxes found: {len(processed_doc.checkboxes)}")
            print(f"Images found: {len(processed_doc.images)}")
            print("\n=== FULL STRUCTURED DATA ===")
            print(json.dumps(result, indent=2, default=str))
        else:
            # Standard analysis with enhanced features
            result = ocr.analyze_document(image_path, analysis_type)
            print("=== ENHANCED OCR ANALYSIS ===")
            print(f"Analysis Type: {analysis_type}")
            print(f"Confidence Score: {result.get('confidence_score', 'N/A')}")
            structured_elements = result.get("structured_elements", {})
            print(f"Structured Elements Found: {sum(structured_elements.values())}")
            print("\n=== FULL ANALYSIS RESULT ===")
            print(json.dumps(result, indent=2, default=str))

    except OCRServiceException as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
