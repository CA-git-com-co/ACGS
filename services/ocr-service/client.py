#!/usr/bin/env python3
"""
OCR Service Client for ACGS-1

This script provides a simple client to interact with the OCR service.
"""

import argparse
import base64
import json
import logging
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ocr-client")


class OCRClient:
    """Client for interacting with the OCR service."""

    def __init__(self, host="localhost", port=8666):
        """Initialize the OCR client with the service endpoint."""
        self.endpoint = f"http://{host}:{port}/v1/chat/completions"
        logger.info(f"OCR client initialized with endpoint: {self.endpoint}")

    def encode_image(self, image_path):
        """Encode an image file to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def process_image(self, image_path, prompt="Describe this image in detail."):
        """Process an image with the OCR service."""
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        logger.info(f"Processing image: {image_path}")

        # For local file, encode it
        if image_path.exists():
            image_data = self.encode_image(image_path)
            image_url = f"data:image/jpeg;base64,{image_data}"
        else:
            # Assume it's a URL
            image_url = str(image_path)

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

        try:
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling OCR service: {e}")
            return {"error": str(e)}


def main():
    """Main function to run the OCR client."""
    parser = argparse.ArgumentParser(description="OCR Client for ACGS-1")
    parser.add_argument("--image", required=True, help="Path or URL to the image")
    parser.add_argument(
        "--prompt",
        default="Extract all text from this image.",
        help="Prompt for the OCR model",
    )
    parser.add_argument("--host", default="localhost", help="OCR service host")
    parser.add_argument("--port", default=8666, type=int, help="OCR service port")

    args = parser.parse_args()

    client = OCRClient(host=args.host, port=args.port)
    result = client.process_image(args.image, args.prompt)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
