# Enhanced OCR Service for ACGS

This service provides advanced OCR (Optical Character Recognition) processing capabilities to the ACGS system using the Nanonets-OCR-s model with comprehensive document analysis features.

**Note**: This is the enhanced OCR service backend for Docker deployment. The Python client library for consuming this service is located in `services/ocr_service/` (note the underscore).

## 🚀 Enhanced Features

### Core OCR Capabilities
- **Advanced Text Extraction**: Powered by Nanonets-OCR-s model
- **LaTeX Equation Recognition**: Automatic conversion of mathematical equations to LaTeX format
- **Intelligent Image Description**: Structured image analysis with contextual descriptions
- **Signature Detection & Isolation**: Identifies and extracts signatures with authentication details
- **Watermark Extraction**: Detects and extracts watermark text for authenticity verification
- **Smart Checkbox Handling**: Converts form checkboxes to standardized Unicode symbols (☐, ☑, ☒)
- **Complex Table Extraction**: Accurate table processing in both HTML and markdown formats

### Governance-Specific Features
- **Constitutional Document Analysis**: Specialized processing for legal and governance documents
- **Document Authenticity Validation**: Multi-factor authenticity scoring
- **Compliance Verification**: Automated compliance checking against governance standards
- **Structured Element Parsing**: Comprehensive extraction of document components
- **Policy Document Processing**: Optimized handling of policy and regulatory documents

### Technical Features
- **GPU-accelerated processing** for high performance
- **Redis caching** for improved response times
- **Concurrent request handling** with configurable limits
- **Comprehensive monitoring** with Prometheus metrics
- **RESTful API** compatible with OpenAI's Chat Completions API
- **Health checks** and service discovery integration

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

### Enhanced Python Client Usage

#### Basic Document Processing

```bash
# Basic OCR processing
python services/ocr-service/ocr_integration.py /path/to/document.jpg

# Constitutional document analysis
python services/ocr-service/ocr_integration.py /path/to/constitution.pdf constitutional

# Detailed structured analysis
python services/ocr-service/ocr_integration.py /path/to/document.jpg governance_form --structured
```

#### Advanced Integration with ACGS Services

```python
from services.ocr_service.ocr_integration import EnhancedOCRIntegration
from services.ocr_service.governance_integration_service import GovernanceIntegrationService

# Initialize enhanced OCR integration
ocr = EnhancedOCRIntegration()

# Check service health
if ocr.check_health():
    # Basic document analysis
    result = ocr.analyze_document('/path/to/document.jpg', 'constitutional')

    # Extract structured elements
    processed_doc = ocr.extract_structured_elements('/path/to/document.jpg', 'legal')

    # Get authenticity analysis
    auth_result = ocr.get_document_authenticity_score('/path/to/document.jpg')

    print(f"Signatures found: {len(processed_doc.signatures)}")
    print(f"Watermarks found: {len(processed_doc.watermarks)}")
    print(f"Authenticity score: {auth_result['authenticity_score']}")

# High-level governance integration
governance_service = GovernanceIntegrationService()

# Complete governance document processing
result = governance_service.process_governance_document(
    image_data='/path/to/policy.pdf',
    document_type='policy',
    validation_level='strict',
    include_validation=True
)

print(f"Overall score: {result['validation']['overall_score']}")
print(f"Compliance score: {result['validation']['compliance_score']}")
```

#### Document Type Support

The enhanced OCR service supports specialized processing for:

- **Constitutional Documents**: `constitutional`
- **Legal Documents**: `legal`
- **Policy Documents**: `policy`
- **Governance Forms**: `governance_form`
- **Official Documents**: `official_document`
- **Technical Documents**: `technical`
- **Contracts**: `contract`
- **Forms**: `form`
- **Receipts**: `receipt`
- **Invoices**: `invoice`

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
