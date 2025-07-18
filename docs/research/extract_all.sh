# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
# Automated extraction script for ACGS research materials

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "ACGS Research Materials Extraction"
echo "=================================="

# Extract papers archive
if [ -f "papers_archive.tar.gz" ]; then
    echo "Extracting research papers..."
    tar -xzf papers_archive.tar.gz
    echo "✓ Research papers extracted to papers/"
else
    echo "⚠ papers_archive.tar.gz not found"
fi

# Extract arXiv images
if [ -f "arXiv-2506.16507v1/images_archive.tar.gz" ]; then
    echo "Extracting arXiv paper images..."
    cd arXiv-2506.16507v1
    tar -xzf images_archive.tar.gz
    cd ..
    echo "✓ arXiv images extracted to arXiv-2506.16507v1/images/"
else
    echo "⚠ arXiv-2506.16507v1/images_archive.tar.gz not found"
fi

echo ""
echo "Research materials extraction complete!"
echo ""
echo "Available research directories:"
echo "- papers/: 136 research papers"
echo "- arXiv-2506.16507v1/: Complete arXiv paper with figures"
echo "- arxiv_submission_package/: Original submission package"
