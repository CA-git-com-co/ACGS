# ACGS OCR Service Client

A comprehensive Python client library and command-line interface for the ACGS OCR (Optical Character Recognition) service, which uses the Nanonets OCR model through vLLM.

## Features

- Extract text from images using state-of-the-art OCR
- Support for various document types (forms, receipts, invoices, IDs, tables, code)
- Multiple input formats (file paths, URLs, raw bytes)
- Customizable prompts for specialized extraction
- Robust error handling with specific exception types
- Command-line interface with multiple output formats
- Health check mechanism for service monitoring
- Comprehensive logging and debugging options

## Installation

### From Source

```bash
# From the ACGS-1 root directory
pip install -e services/ocr_service

# With development dependencies
pip install -e "services/ocr_service[dev]"
```

## Command Line Usage

The package provides a powerful command-line tool:

```bash
# Basic usage
acgs-ocr --image /path/to/image.jpg

# Process a specific document type
acgs-ocr --image /path/to/receipt.jpg --type receipt

# Use a custom prompt
acgs-ocr --image /path/to/document.jpg --prompt "Extract all product codes and prices"

# Save results to a file with pretty JSON formatting
acgs-ocr --image /path/to/document.jpg --output results.json --format pretty

# Save plain text results
acgs-ocr --image /path/to/document.jpg --output results.txt --format text

# Connect to a remote OCR service
acgs-ocr --image /path/to/image.jpg --host ocr.example.com --port 8666 --health-port 8667

# Perform health check only
acgs-ocr --health-check-only
```

### Available Document Types

- `general`: Extract all text maintaining structure
- `form`: Extract fields and values as key-value pairs
- `receipt`: Extract vendor, date, items, prices, and total
- `invoice`: Extract invoice details, line items, and totals
- `id`: Extract information from ID cards or documents
- `table`: Extract and format tables as markdown
- `code`: Extract code snippets with proper formatting

### Output Formats

- `text`: Plain text output (default)
- `json`: Raw JSON output
- `pretty`: Formatted JSON with indentation
- `compact`: Just the extracted text without metadata

## Python API

```python
from services.ocr_service import OCRClient, OCRServiceException

# Initialize the client
ocr = OCRClient(
    host="localhost",  # Optional: OCR service hostname
    port=8666,         # Optional: OCR API port
    health_port=8667,  # Optional: Health check port
    timeout=30,        # Optional: Request timeout in seconds
    model="nanonets/Nanonets-OCR-s"  # Optional: Model name
)

# Check if the service is healthy
is_healthy, error = ocr.check_health()
if is_healthy:
    # Extract text from an image
    result = ocr.extract_text('/path/to/image.jpg')
    print(result['text'])
    
    # Process a specific document type
    invoice_data = ocr.analyze_document('/path/to/invoice.jpg', 'invoice')
    print(invoice_data['text'])
    
    # Use a custom prompt
    custom_result = ocr.extract_text(
        '/path/to/image.jpg',
        prompt="Extract all tabular data and format as a CSV"
    )
```

### Working with Different Image Sources

```python
# From a file path
result = ocr.extract_text('/path/to/image.jpg')

# From a URL
result = ocr.extract_text('https://example.com/image.jpg')

# From raw bytes
with open('/path/to/image.jpg', 'rb') as f:
    image_bytes = f.read()
    result = ocr.extract_text(image_bytes)
```

### Error Handling

```python
from services.ocr_service import (
    OCRClient, 
    OCRServiceException,
    OCRRequestException,
    OCRResponseException,
    OCRConnectionException
)

ocr = OCRClient()

try:
    result = ocr.extract_text('/path/to/image.jpg')
except OCRRequestException as e:
    # Handle image loading or validation errors
    print(f"Request error: {e}")
except OCRConnectionException as e:
    # Handle connection issues
    print(f"Connection error: {e}")
except OCRResponseException as e:
    # Handle API response errors
    print(f"Response error: {e}")
except OCRServiceException as e:
    # Handle other OCR service errors
    print(f"Service error: {e}")
```

## Configuration

The OCR client can be configured through environment variables:

- `OCR_SERVICE_HOST`: Hostname of the OCR service (default: "localhost")
- `OCR_SERVICE_PORT`: Port of the OCR API (default: 8666)
- `OCR_SERVICE_HEALTH_PORT`: Port of the health check endpoint (default: 8667)
- `OCR_SERVICE_MODEL`: Model to use for OCR (default: "nanonets/Nanonets-OCR-s")

## Development

To set up the development environment:

```bash
# Install development dependencies
pip install -e "services/ocr_service[dev]"

# Run tests
pytest services/ocr_service/tests/

# Format code
black services/ocr_service/

# Run type checking
mypy services/ocr_service/

# Run linting
ruff check services/ocr_service/
```

## Docker Integration

This client works with the OCR service running in Docker:

```bash
# Start the OCR service
./scripts/deploy_ocr_service.sh

# Use the client with the service
acgs-ocr --image /path/to/image.jpg
```

## License

This package is licensed under the MIT License - see the LICENSE file for details.