#!/usr/bin/env python3
"""
OCR Service Command Line Interface

This module provides a command-line interface for the OCR service,
allowing users to extract text from images directly from the terminal.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional, TextIO

from .ocr_client import OCRClient, OCRServiceException, OCRRequestException

# Configure logging
logger = logging.getLogger("acgs.ocr_service.cli")


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI application."""
    root_logger = logging.getLogger("acgs")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    log_level = logging.DEBUG if verbose else logging.INFO
    root_logger.setLevel(log_level)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="ACGS OCR Service - Extract text from images using OCR",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Image input options
    parser.add_argument(
        "--image", "-i", 
        required=True, 
        help="Path to image file or URL"
    )
    
    # Connection options
    connection_group = parser.add_argument_group("Connection Options")
    connection_group.add_argument(
        "--host", 
        default=None,
        help="OCR service hostname (default: from OCR_SERVICE_HOST env var or 'localhost')"
    )
    connection_group.add_argument(
        "--port", 
        type=int, 
        default=None,
        help="OCR service port (default: from OCR_SERVICE_PORT env var or 8666)"
    )
    connection_group.add_argument(
        "--health-port", 
        type=int, 
        default=None,
        help="OCR service health check port (default: from OCR_SERVICE_HEALTH_PORT env var or 8667)"
    )
    connection_group.add_argument(
        "--timeout", 
        type=int, 
        default=30,
        help="Request timeout in seconds"
    )
    
    # OCR options
    ocr_group = parser.add_argument_group("OCR Options")
    ocr_group.add_argument(
        "--prompt", "-p", 
        default=None,
        help="Custom prompt for the OCR model"
    )
    ocr_group.add_argument(
        "--type", "-t", 
        choices=list(OCRClient.DOCUMENT_TYPES.keys()),
        default="general",
        help="Type of document analysis to perform"
    )
    ocr_group.add_argument(
        "--model", "-m", 
        default=None,
        help="Model to use for OCR (default: from OCR_SERVICE_MODEL env var or 'nanonets/Nanonets-OCR-s')"
    )
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--output", "-o", 
        type=argparse.FileType("w"), 
        default=sys.stdout,
        help="Output file (default: stdout)"
    )
    output_group.add_argument(
        "--format", "-f", 
        choices=["json", "text", "pretty", "compact"],
        default="text",
        help="Output format"
    )
    
    # Debug options
    debug_group = parser.add_argument_group("Debug Options")
    debug_group.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Enable verbose output"
    )
    debug_group.add_argument(
        "--health-check-only", 
        action="store_true",
        help="Only perform health check and exit"
    )
    
    return parser.parse_args()


def format_output(result: Dict[str, Any], format_type: str) -> str:
    """
    Format the OCR result according to the specified format.
    
    Args:
        result: The OCR result dictionary
        format_type: The output format type ('json', 'text', 'pretty', or 'compact')
        
    Returns:
        Formatted output string
    """
    if format_type == "json":
        return json.dumps(result)
    elif format_type == "pretty":
        return json.dumps(result, indent=2)
    elif format_type == "compact":
        return result["text"] if result["success"] else f"Error: {result.get('error', 'Unknown error')}"
    else:  # text format
        if result["success"]:
            return result["text"]
        else:
            return f"Error: {result.get('error', 'Unknown error')}"


def write_output(output: str, output_file: TextIO) -> None:
    """
    Write output to the specified file or stdout.
    
    Args:
        output: The formatted output string
        output_file: The file object to write to
    """
    print(output, file=output_file)
    
    # If writing to a file (not stdout), also print a confirmation to stdout
    if output_file is not sys.stdout:
        print(f"Results written to {output_file.name}")


def perform_health_check(client: OCRClient) -> bool:
    """
    Perform a health check on the OCR service.
    
    Args:
        client: The OCR client instance
        
    Returns:
        True if healthy, False otherwise
    """
    print("Checking OCR service health...", end=" ", flush=True)
    is_healthy, error = client.check_health()
    
    if is_healthy:
        print("OK")
        return True
    else:
        print(f"FAILED: {error}")
        return False


def main() -> int:
    """
    Main entry point for the OCR CLI application.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    args = parse_arguments()
    setup_logging(args.verbose)
    
    try:
        # Initialize the OCR client
        client = OCRClient(
            host=args.host,
            port=args.port,
            health_port=args.health_port,
            timeout=args.timeout,
            model=args.model
        )
        
        # If only health check is requested, do that and exit
        if args.health_check_only:
            is_healthy = perform_health_check(client)
            return 0 if is_healthy else 1
        
        # Otherwise, check health and proceed if healthy
        is_healthy, error = client.check_health()
        if not is_healthy:
            print(f"Error: OCR service is not healthy - {error}", file=sys.stderr)
            return 1
        
        # Process the image
        if args.prompt:
            # Use custom prompt
            result = client.extract_text(args.image, args.prompt, args.model)
        else:
            # Use document type
            result = client.analyze_document(args.image, args.type, args.model)
        
        # Format and write the output
        output = format_output(result, args.format)
        write_output(output, args.output)
        
        return 0
        
    except OCRRequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except OCRServiceException as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        logger.exception("Unexpected error in CLI")
        return 1


if __name__ == "__main__":
    sys.exit(main())