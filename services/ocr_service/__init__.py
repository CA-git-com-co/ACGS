"""
ACGS OCR Service Client Package

This package provides a client library and command-line interface for interacting
with the OCR (Optical Character Recognition) service in ACGS-1.
"""

__version__ = "0.1.0"
__author__ = "ACGS Team"
__all__ = ["OCRClient", "OCRServiceException", "cli"]

from .ocr_client import OCRClient, OCRServiceException