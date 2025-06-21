# OCR Service Backend for ACGS-1

This service provides the backend OCR (Optical Character Recognition) processing capabilities to the ACGS-1 system using the Nanonets OCR model through vLLM.

**Note**: This is the OCR service backend for Docker deployment. The Python client library for consuming this service is located in `services/ocr_service/` (note the underscore).

## Features

- Extract text from images and documents
- Process various document types (forms, receipts, invoices, IDs)
- GPU-accelerated processing for high performance
- Integrates with the ACGS-1 service mesh
- RESTful API compatible with OpenAI's Chat Completions API

## Requirements

- Docker with NVIDIA Container Toolkit (for GPU acceleration)
- Hugging Face account with access token
- Python 3.8+ (for client usage)

## Deployment

### Environment Setup

Before deploying, set your Hugging Face token:

```bash
export HUGGING_FACE_HUB_TOKEN=your_token_here
```

### Deployment with Docker Compose

Use the provided deployment script:

```bash
chmod +x scripts/deploy_ocr_service.sh
./scripts/deploy_ocr_service.sh
```

Or manually with Docker Compose:

```bash
docker-compose -f docker-compose.ocr.yml up -d
```

## Usage

### Direct API Access

The OCR service exposes an OpenAI-compatible API endpoint:

```bash
curl -X POST "http://localhost:8666/v1/chat/completions" \
    -H "Content-Type: application/json" \
    --data '{
        "model": "nanonets/Nanonets-OCR-s",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all text from this image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://example.com/image.jpg"
                        }
                    }
                ]
            }
        ]
    }'
```

### Using the Python Client

Process an image with the provided client:

```bash
python services/ocr-service/client.py --image /path/to/image.jpg --prompt "Extract all text from this image"
```

### Integration with ACGS-1 Services

Import the OCR integration module in your service:

```python
from services.ocr_service.ocr_integration import OCRIntegration

# Initialize the OCR integration
ocr = OCRIntegration()

# Check if the OCR service is healthy
if ocr.check_health():
    # Extract text from an image
    result = ocr.extract_text('/path/to/image.jpg')

    # Process a specific document type
    invoice_data = ocr.analyze_document('/path/to/invoice.jpg', 'invoice')
```

## Configuration

The OCR service can be configured through environment variables:

| Variable                 | Description                | Default                   |
| ------------------------ | -------------------------- | ------------------------- |
| `MODEL_NAME`             | OCR model to use           | `nanonets/Nanonets-OCR-s` |
| `PORT`                   | Port to expose the API     | `8666`                    |
| `HUGGING_FACE_HUB_TOKEN` | Token for Hugging Face Hub | Required                  |

## Performance Considerations

- The OCR service requires a GPU for optimal performance
- First-time startup may be slow as the model is downloaded
- Processing time depends on image size and complexity

## Troubleshooting

### Common Issues

1. **Service fails to start or becomes unhealthy**:

   - Check Docker logs: `docker-compose -f docker-compose.ocr.yml logs ocr-service`
   - Verify GPU availability: `nvidia-smi`
   - Check Hugging Face token is valid

2. **Slow response times**:

   - Ensure GPU acceleration is enabled
   - Check if other processes are using GPU resources
   - Consider increasing container resource limits

3. **Poor OCR quality**:
   - Try different prompts for better results
   - Ensure image quality is sufficient
   - Pre-process images to improve contrast and resolution

## License

This service is part of the ACGS-1 project and subject to its licensing terms.
