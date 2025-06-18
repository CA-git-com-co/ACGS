#!/usr/bin/env python3
"""
OCR Service Integration Module for ACGS-1

This module provides integration between the OCR service and the ACGS-1 system.
It allows other ACGS-1 services to utilize OCR capabilities through a unified interface.
"""

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Union

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ocr-integration")


class OCRServiceException(Exception):
    """Exception raised for errors in the OCR service."""



class OCRIntegration:
    """Integration class for the OCR service within ACGS-1."""

    def __init__(self, host: str = None, port: int = None):
        """Initialize the OCR integration with service connection details."""
        self.host = host or os.environ.get("OCR_SERVICE_HOST", "ocr-service")
        self.port = port or int(os.environ.get("OCR_SERVICE_PORT", "8666"))
        self.endpoint = f"http://{self.host}:{self.port}/v1/chat/completions"
        self.health_endpoint = f"http://{self.host}:{self.port}/health"
        logger.info(f"OCR integration initialized with endpoint: {self.endpoint}")

    def check_health(self) -> bool:
        """Check if the OCR service is healthy."""
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.warning(f"OCR service health check failed: {e}")
            return False

    def encode_image(self, image_path: Union[str, Path]) -> str:
        """Encode an image file to base64."""
        image_path = Path(image_path)
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def extract_text(
        self,
        image_data: Union[str, Path, bytes],
        prompt: str = "Extract all text from this image.",
    ) -> Dict[str, Any]:
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
            else:
                return {
                    "success": False,
                    "error": "No content in response",
                    "raw_response": result,
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling OCR service: {e}")
            raise OCRServiceException(f"OCR service request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OCR integration: {e}")
            raise OCRServiceException(f"OCR integration error: {str(e)}")

    def analyze_document(
        self, image_data: Union[str, Path, bytes], analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Perform document analysis with the OCR service.

        Args:
            image_data: Can be a file path, URL, or raw bytes
            analysis_type: Type of analysis to perform (general, form, receipt, invoice, etc.)

        Returns:
            Dictionary containing the analysis results
        """
        prompts = {
            "general": "Extract all text from this document and maintain its structure.",
            "form": "Extract all fields and values from this form document.",
            "receipt": "Extract the vendor, date, items, prices, and total from this receipt.",
            "invoice": "Extract the invoice number, date, vendor, line items, and total amount from this invoice.",
            "id": "Extract all information from this ID card or document.",
        }

        prompt = prompts.get(analysis_type, prompts["general"])

        return self.extract_text(image_data, prompt)


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ocr_integration.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    analysis_type = sys.argv[2] if len(sys.argv) > 2 else "general"

    ocr = OCRIntegration()
    if not ocr.check_health():
        print("OCR service is not healthy. Please check if it's running.")
        sys.exit(1)

    try:
        result = ocr.analyze_document(image_path, analysis_type)
        print(json.dumps(result, indent=2))
    except OCRServiceException as e:
        print(f"Error: {e}")
        sys.exit(1)
