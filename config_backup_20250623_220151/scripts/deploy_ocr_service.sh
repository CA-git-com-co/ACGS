#!/bin/bash
# OCR Service Deployment Script for ACGS-1
# This script deploys the OCR service and integrates it with the ACGS-1 system

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ACGS OCR Service Deployment ===${NC}"

# Check if HUGGING_FACE_HUB_TOKEN is set
if [ -z "${HUGGING_FACE_HUB_TOKEN}" ]; then
    echo -e "${RED}Error: HUGGING_FACE_HUB_TOKEN environment variable is not set.${NC}"
    echo -e "Please set it with: export HUGGING_FACE_HUB_TOKEN=your_token"
    exit 1
fi

# Verify Docker and Docker Compose are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    exit 1
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq is not installed. Installing it now...${NC}"
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y jq
    elif command -v yum &> /dev/null; then
        sudo yum install -y jq
    elif command -v brew &> /dev/null; then
        brew install jq
    else
        echo -e "${YELLOW}Warning: Could not install jq automatically. The test at the end of the script may fail.${NC}"
        echo -e "Please install jq manually for JSON processing capabilities."
    fi
fi

# Check for NVIDIA Docker support
echo -e "${YELLOW}Checking for NVIDIA GPU support...${NC}"
if ! docker info | grep -q "Runtimes:.*nvidia"; then
    echo -e "${YELLOW}Warning: NVIDIA Docker runtime not detected. GPU acceleration may not be available.${NC}"
    echo -e "For optimal performance, install nvidia-docker2: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
else
    echo -e "${GREEN}NVIDIA Docker runtime detected. GPU acceleration will be available.${NC}"
fi

# Ensure ACGS network exists
echo -e "${YELLOW}Checking for ACGS network...${NC}"
if ! docker network ls | grep -q "acgs_network"; then
    echo -e "${YELLOW}Creating ACGS network...${NC}"
    docker network create acgs_network
    echo -e "${GREEN}ACGS network created.${NC}"
else
    echo -e "${GREEN}ACGS network already exists.${NC}"
fi

# Stop existing service if running
echo -e "${YELLOW}Checking for existing OCR service...${NC}"
if docker ps | grep -q "acgs_ocr_service"; then
    echo -e "${YELLOW}Stopping existing OCR service...${NC}"
    docker-compose -f docker-compose.ocr.yml down
    echo -e "${GREEN}Existing OCR service stopped.${NC}"
fi

# Build the OCR service
echo -e "${YELLOW}Building OCR service...${NC}"
docker-compose -f docker-compose.ocr.yml build
echo -e "${GREEN}OCR service built successfully.${NC}"

# Start the OCR service
echo -e "${YELLOW}Starting OCR service...${NC}"
docker-compose -f docker-compose.ocr.yml up -d
echo -e "${GREEN}OCR service container started.${NC}"

# Wait for service to be healthy
echo -e "${YELLOW}Waiting for OCR service to initialize (this may take several minutes for first run)...${NC}"
attempt=1
max_attempts=30
until docker ps | grep acgs_ocr_service | grep -q "(healthy)" || [ $attempt -gt $max_attempts ]; do
    if [ $attempt -eq 1 ]; then
        echo -e "${BLUE}The service is downloading the model on first run, which may take several minutes.${NC}"
        echo -e "${BLUE}You can check progress with: docker-compose -f docker-compose.ocr.yml logs --follow ocr-service${NC}"
    fi
    echo -e "${YELLOW}Waiting for OCR service to be healthy (attempt $attempt/$max_attempts)...${NC}"
    sleep 20
    attempt=$((attempt+1))
done

if [ $attempt -gt $max_attempts ]; then
    echo -e "${RED}Error: OCR service failed to become healthy after $(($max_attempts * 20)) seconds.${NC}"
    echo -e "${YELLOW}Showing OCR service logs:${NC}"
    docker-compose -f docker-compose.ocr.yml logs --tail=100 ocr-service
    
    echo -e "${YELLOW}Checking health endpoint directly:${NC}"
    curl -s http://localhost:8667/health
    echo
    
    echo -e "${RED}Deployment failed. Please check the logs above for errors.${NC}"
    echo -e "${YELLOW}You can try increasing start_period in docker-compose.ocr.yml if the model is still downloading.${NC}"
    exit 1
fi

echo -e "${GREEN}OCR service is now running and healthy!${NC}"
echo -e "${GREEN}API endpoint: http://localhost:8666${NC}"
echo -e "${GREEN}Health endpoint: http://localhost:8667/health${NC}"

# Test the OCR service
echo -e "${YELLOW}Testing OCR service with a simple request...${NC}"
echo -e "${BLUE}Request: 'What model are you?'${NC}"

response=$(curl -s -X POST "http://localhost:8666/v1/chat/completions" \
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
    }')

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Could not connect to OCR service.${NC}"
    exit 1
fi

# Extract and display the response
if command -v jq &> /dev/null; then
    content=$(echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null)
    if [ $? -ne 0 ] || [ "$content" == "null" ]; then
        echo -e "${RED}Error: Invalid response format:${NC}"
        echo "$response" | jq . 2>/dev/null || echo "$response"
    else
        echo -e "${GREEN}Response: $content${NC}"
        echo -e "${GREEN}Test successful!${NC}"
    fi
else
    echo -e "${YELLOW}Raw response (jq not available):${NC}"
    echo "$response"
fi

echo -e "${GREEN}OCR service deployment complete!${NC}"
echo ""
echo -e "${BLUE}=== Usage Examples ===${NC}"
echo -e "${YELLOW}1. Using the command-line interface:${NC}"
echo -e "   pip install -e services/ocr_service"
echo -e "   acgs-ocr --image /path/to/image.jpg"
echo -e "   acgs-ocr --image /path/to/image.jpg --type receipt --format pretty"
echo ""
echo -e "${YELLOW}2. Using the Python API:${NC}"
echo -e "   from services.ocr_service import OCRClient"
echo -e "   ocr = OCRClient()"
echo -e "   result = ocr.extract_text('/path/to/image.jpg')"
echo -e "   print(result['text'])"
echo ""
echo -e "${YELLOW}For detailed documentation:${NC}"
echo -e "   cat services/ocr_service/README.md"
echo ""
echo -e "${BLUE}=== Service Information ===${NC}"
echo -e "${YELLOW}Health status:${NC} http://localhost:8667/health"
echo -e "${YELLOW}Container:${NC} acgs_ocr_service"
echo -e "${YELLOW}View logs:${NC} docker-compose -f docker-compose.ocr.yml logs --follow ocr-service"
echo -e "${YELLOW}Restart:${NC} docker-compose -f docker-compose.ocr.yml restart ocr-service"
echo -e "${YELLOW}Stop:${NC} docker-compose -f docker-compose.ocr.yml down"