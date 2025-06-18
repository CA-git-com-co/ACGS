#!/bin/bash
# OCR Service Deployment Script for ACGS-1
# This script deploys the OCR service and integrates it with the ACGS-1 system

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting OCR Service Deployment for ACGS-1${NC}"

# Check if HUGGING_FACE_HUB_TOKEN is set
if [ -z "${HUGGING_FACE_HUB_TOKEN}" ]; then
    echo -e "${RED}Error: HUGGING_FACE_HUB_TOKEN environment variable is not set.${NC}"
    echo -e "Please set it with: export HUGGING_FACE_HUB_TOKEN=your_token"
    exit 1
fi

# Verify Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    exit 1
fi

# Check for NVIDIA Docker support
if ! docker info | grep -q "Runtimes:.*nvidia"; then
    echo -e "${YELLOW}Warning: NVIDIA Docker runtime not detected. GPU acceleration may not be available.${NC}"
    echo -e "If you have an NVIDIA GPU, install nvidia-docker2: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
fi

# Ensure ACGS network exists
if ! docker network ls | grep -q "acgs_network"; then
    echo -e "${YELLOW}Creating ACGS network...${NC}"
    docker network create acgs_network
fi

# Build and start the OCR service
echo -e "${GREEN}Building OCR service...${NC}"
docker-compose -f docker-compose.ocr.yml build

echo -e "${GREEN}Starting OCR service...${NC}"
docker-compose -f docker-compose.ocr.yml up -d

# Wait for service to be healthy
echo -e "${YELLOW}Waiting for OCR service to be ready...${NC}"
attempt=1
max_attempts=30
until docker ps | grep acgs_ocr_service | grep -q "(healthy)" || [ $attempt -gt $max_attempts ]; do
    echo -e "${YELLOW}Waiting for OCR service to be healthy (attempt $attempt/$max_attempts)...${NC}"
    sleep 10
    attempt=$((attempt+1))
done

if [ $attempt -gt $max_attempts ]; then
    echo -e "${RED}Error: OCR service failed to become healthy after $(($max_attempts * 10)) seconds.${NC}"
    echo -e "${YELLOW}Checking OCR service logs:${NC}"
    docker-compose -f docker-compose.ocr.yml logs ocr-service
    exit 1
fi

echo -e "${GREEN}OCR service is now running and healthy!${NC}"
echo -e "${GREEN}Service is available at: http://localhost:8666${NC}"

# Test the OCR service
echo -e "${YELLOW}Testing OCR service with a simple request...${NC}"
curl -s -X POST "http://localhost:8666/v1/chat/completions" \
    -H "Content-Type: application/json" \
    --data '{
        "model": "nanonets/Nanonets-OCR-s",
        "messages": [
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": "What model are you?"
                    }
                ]
            }
        ]
    }' | jq -r '.choices[0].message.content' || echo -e "${RED}OCR service test failed${NC}"

echo -e "${GREEN}OCR service deployment complete!${NC}"
echo ""
echo -e "${YELLOW}Usage examples:${NC}"
echo -e "1. Process an image using the client script:"
echo -e "   python services/ocr-service/client.py --image /path/to/image.jpg"
echo ""
echo -e "2. Integrate OCR into your Python code:"
echo -e "   from services.ocr_service.ocr_integration import OCRIntegration"
echo -e "   ocr = OCRIntegration()"
echo -e "   result = ocr.extract_text('/path/to/image.jpg')"
echo ""
echo -e "${YELLOW}For more details, see the documentation in services/ocr-service/README.md${NC}"