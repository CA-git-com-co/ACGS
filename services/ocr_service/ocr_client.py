#!/usr/bin/env python3
"""
OCR Service Client Module for ACGS-1

This module provides a client for interacting with the OCR service.
It allows applications to extract text from images using a unified interface.
"""

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

# Configure logging
logger = logging.getLogger("acgs.ocr_service")


class OCRServiceException(Exception):
    """Exception raised for errors in the OCR service."""

    pass


class OCRRequestException(OCRServiceException):
    """Exception raised for errors when making requests to the OCR service."""

    pass


class OCRResponseException(OCRServiceException):
    """Exception raised for errors in the OCR service response."""

    pass


class OCRConnectionException(OCRServiceException):
    """Exception raised for connection errors to the OCR service."""

    pass


class OCRClient:
    """Client class for the OCR service within ACGS-1."""

    # Document analysis types and their corresponding prompts
    DOCUMENT_TYPES = {
        "general": "Extract all text from this document and maintain its structure.",
        "form": "Extract all fields and values from this form document. Format as field: value pairs.",
        "receipt": "Extract the vendor name, date, all items with prices, and total amount from this receipt. Format as structured data.",
        "invoice": "Extract the invoice number, date, vendor name, all line items with quantities and prices, and total amount from this invoice. Format as structured data.",
        "id": "Extract all information from this ID card or document including name, ID number, date of birth, and other personal information. Format as field: value pairs.",
        "table": "Extract all tables from this document and convert them to markdown format with proper column alignment.",
        "code": "Extract any code or programming snippets from this image and maintain proper formatting and indentation.",
    }

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        health_port: int | None = None,
        timeout: int = 30,
        model: str | None = None,
    ):
        """
        Initialize the OCR client with service connection details.

        Args:
            host: Hostname of the OCR service
            port: Port for the OCR API
            health_port: Port for the health check endpoint
            timeout: Request timeout in seconds
            model: Model name to use for OCR requests
        """
        self.host = host or os.environ.get("OCR_SERVICE_HOST", "localhost")
        self.port = port or int(os.environ.get("OCR_SERVICE_PORT", "8666"))
        self.health_port = health_port or int(
            os.environ.get("OCR_SERVICE_HEALTH_PORT", "8667")
        )
        self.timeout = timeout
        self.model = model or os.environ.get(
            "OCR_SERVICE_MODEL", "nanonets/Nanonets-OCR-s"
        )

        # API endpoints
        self.endpoint = f"http://{self.host}:{self.port}/v1/chat/completions"
        self.health_endpoint = f"http://{self.host}:{self.health_port}/health"

        logger.debug(f"OCR client initialized with API endpoint: {self.endpoint}")
        logger.debug(f"Health check endpoint: {self.health_endpoint}")

    def check_health(self) -> tuple[bool, str | None]:
        """
        Check if the OCR service is healthy.

        Returns:
            Tuple of (is_healthy, error_message)
        """
        try:
            response = requests.get(self.health_endpoint, timeout=self.timeout)
            if response.status_code == 200:
                return True, None
            error_msg = f"Health check failed with status code: {response.status_code}"
            logger.warning(error_msg)
            return False, error_msg
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error during health check: {e}"
            logger.warning(error_msg)
            return False, error_msg
        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout during health check: {e}"
            logger.warning(error_msg)
            return False, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error during health check: {e}"
            logger.warning(error_msg)
            return False, error_msg

    def _is_url(self, image_path: str) -> bool:
        """
        Check if the provided path is a URL.

        Args:
            image_path: Path to check

        Returns:
            True if the path is a URL, False otherwise
        """
        try:
            result = urlparse(image_path)
            return all([result.scheme, result.netloc])
        except:
            return False

    def encode_image(self, image_path: str | Path) -> str:
        """
        Encode an image file to base64.

        Args:
            image_path: Path to the image file

        Returns:
            Base64-encoded image data

        Raises:
            OCRRequestException: If the image file cannot be read
        """
        try:
            image_path = Path(image_path)
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except OSError as e:
            error_msg = f"Failed to read image file {image_path}: {e}"
            logger.error(error_msg)
            raise OCRRequestException(error_msg)

    def _prepare_image_url(self, image_data: str | Path | bytes) -> str:
        """
        Prepare the image URL for the OCR request.

        Args:
            image_data: Image data as a file path, URL, or raw bytes

        Returns:
            Image URL for the OCR request

        Raises:
            OCRRequestException: If the image data is invalid
        """
        try:
            if isinstance(image_data, (str, Path)):
                path_str = str(image_data)
                if self._is_url(path_str):
                    # It's a URL
                    return path_str

                path = Path(image_data)
                if path.exists():
                    # Local file
                    image_base64 = self.encode_image(path)
                    return f"data:image/jpeg;base64,{image_base64}"
                error_msg = f"Image file not found: {path}"
                logger.error(error_msg)
                raise OCRRequestException(error_msg)
            if isinstance(image_data, bytes):
                # Raw bytes
                image_base64 = base64.b64encode(image_data).decode("utf-8")
                return f"data:image/jpeg;base64,{image_base64}"
            error_msg = f"Unsupported image data type: {type(image_data)}"
            logger.error(error_msg)
            raise OCRRequestException(error_msg)
        except Exception as e:
            if isinstance(e, OCRRequestException):
                raise
            error_msg = f"Error preparing image URL: {e}"
            logger.error(error_msg)
            raise OCRRequestException(error_msg)

    def extract_text(
        self,
        image_data: str | Path | bytes,
        prompt: str = "Extract all text from this image.",
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        Extract text from an image using the OCR service.

        Args:
            image_data: Image data as a file path, URL, or raw bytes
            prompt: Specific instruction for the OCR model
            model: Optional model override

        Returns:
            Dictionary containing the extracted text and metadata

        Raises:
            OCRRequestException: If the request preparation fails
            OCRConnectionException: If connecting to the service fails
            OCRResponseException: If processing the response fails
        """
        # Validate health before proceeding
        is_healthy, error_msg = self.check_health()
        if not is_healthy:
            raise OCRConnectionException(f"OCR service is not healthy: {error_msg}")

        try:
            # Prepare image URL
            image_url = self._prepare_image_url(image_data)

            # Prepare request payload
            payload = {
                "model": model or self.model,
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

            logger.debug(f"Sending OCR request with prompt: {prompt}")
            response = requests.post(self.endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()

            # Process the response
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "text": content,
                    "metadata": {
                        "model": result.get("model", model or self.model),
                        "usage": result.get("usage", {}),
                    },
                }
            error_msg = "No content in OCR response"
            logger.warning(f"{error_msg}: {result}")
            return {
                "success": False,
                "error": error_msg,
                "raw_response": result,
            }

        except OCRRequestException:
            # Re-raise existing OCRRequestException
            raise
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error to OCR service: {e}"
            logger.error(error_msg)
            raise OCRConnectionException(error_msg)
        except requests.exceptions.Timeout as e:
            error_msg = f"Request timeout to OCR service: {e}"
            logger.error(error_msg)
            raise OCRConnectionException(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error from OCR service: {e}"
            logger.error(error_msg)
            raise OCRResponseException(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error to OCR service: {e}"
            logger.error(error_msg)
            raise OCRConnectionException(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in OCR client: {e}"
            logger.error(error_msg)
            raise OCRServiceException(error_msg)

    def analyze_document(
        self,
        image_data: str | Path | bytes,
        document_type: str = "general",
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        Perform document analysis with the OCR service.

        Args:
            image_data: Image data as a file path, URL, or raw bytes
            document_type: Type of document analysis to perform
            model: Optional model override

        Returns:
            Dictionary containing the analysis results

        Raises:
            OCRRequestException: If the document type is invalid
            OCRServiceException: For other OCR service errors
        """
        if document_type not in self.DOCUMENT_TYPES:
            valid_types = ", ".join(self.DOCUMENT_TYPES.keys())
            error_msg = (
                f"Invalid document type '{document_type}'. Valid types: {valid_types}"
            )
            logger.error(error_msg)
            raise OCRRequestException(error_msg)

        prompt = self.DOCUMENT_TYPES[document_type]
        logger.info(f"Analyzing document as type '{document_type}'")

        return self.extract_text(image_data, prompt, model)


if __name__ == "__main__":
    # Simple test when run directly
    import sys

    # Configure console logging when run directly
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if len(sys.argv) < 2:
        print("Usage: python ocr_client.py <image_path> [document_type]")
        sys.exit(1)

    image_path = sys.argv[1]
    doc_type = sys.argv[2] if len(sys.argv) > 2 else "general"

    client = OCRClient()
    is_healthy, error = client.check_health()

    if not is_healthy:
        print(f"Error: OCR service is not healthy - {error}")
        sys.exit(1)

    try:
        result = client.analyze_document(image_path, doc_type)
        print(json.dumps(result, indent=2))
    except OCRServiceException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
