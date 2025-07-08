#!/bin/bash
# ACGS Repository Reorganization Quick Start Script
#
# This script provides a quick way to set up and run the reorganization

set -e

echo "ACGS Repository Reorganization Quick Start"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if source and target are provided
if [ $# -lt 2 ]; then
    echo -e "${RED}Error: Please provide source repository and target directory${NC}"
    echo "Usage: $0 <source_repo> <target_dir> [--dry-run]"
    exit 1
fi

SOURCE_REPO=$1
TARGET_DIR=$2
DRY_RUN=${3:-""}

# Check if source repository exists
if [ ! -d "$SOURCE_REPO" ]; then
    echo -e "${RED}Error: Source repository $SOURCE_REPO does not exist${NC}"
    exit 1
fi

# Check if git filter-repo is installed
if ! command -v git-filter-repo &> /dev/null; then
    echo -e "${YELLOW}git-filter-repo not found. Installing...${NC}"
    pip install --user git-filter-repo
    export PATH=$PATH:~/.local/bin
fi

# Create target directory
echo -e "${GREEN}Creating target directory...${NC}"
mkdir -p "$TARGET_DIR"

# Run the reorganization
if [ "$DRY_RUN" == "--dry-run" ]; then
    echo -e "${YELLOW}Running in DRY RUN mode...${NC}"
    python acgs_reorganize.py "$SOURCE_REPO" "$TARGET_DIR" --dry-run
else
    echo -e "${GREEN}Starting reorganization...${NC}"
    echo -e "${YELLOW}This may take several minutes for large repositories${NC}"

    # Run with progress indication
    python acgs_reorganize.py "$SOURCE_REPO" "$TARGET_DIR"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Reorganization completed successfully!${NC}"
        echo
        echo "Next steps:"
        echo "1. cd $TARGET_DIR"
        echo "2. python scripts/setup_workspace.py"
        echo "3. Review the REORGANIZATION.md file"
        echo
        echo -e "${GREEN}Your new workspace is ready at: $TARGET_DIR${NC}"
    else
        echo -e "${RED}Reorganization failed. Please check the logs.${NC}"
        exit 1
    fi
fi
