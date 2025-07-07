# ACGS Research Paper OCR Conversion Tools
**Constitutional Hash**: cdd01ef066bc6cf2

## Overview

This directory contains advanced OCR tools for converting ACGS research papers from PDF to markdown format. The conversion system is designed to handle academic papers with complex formatting, mathematical equations, and figures while maintaining ACGS performance and compliance standards.

## 🎯 Benefits of OCR Conversion

### Repository Optimization
- **Size Reduction**: ~90% reduction from 568MB to ~50MB
- **Git-Friendly**: Text-based files for better version control
- **Searchable Content**: Full-text search across all papers
- **Collaborative**: Easy to review, annotate, and modify

### ACGS Integration
- **Performance**: Supports <5ms P99 latency targets
- **Compliance**: Constitutional hash validation in all operations
- **Caching**: Optimized for >85% cache hit rates
- **Throughput**: Designed for >100 RPS processing

## 🛠️ Tools and Components

### Core Conversion Tools

1. **pdf_to_markdown_converter.py**
   - Advanced PDF to markdown conversion
   - Multiple OCR methods (Marker, PyMuPDF)
   - Parallel processing with progress tracking
   - Quality assessment and error handling

2. **convert_all_papers.py**
   - Batch conversion manager
   - Paper index updates
   - Archive management
   - Integration with ACGS documentation

3. **setup_ocr_tools.sh**
   - Automated installation script
   - System dependency management
   - Virtual environment setup
   - Configuration generation

### OCR Methods

#### Primary: OCRFlux (State-of-the-art)
- **Best for**: Academic papers with complex layouts
- **Features**: Cross-page merging, equations, complex tables
- **Quality**: **96.7% accuracy** (11% better than alternatives)
- **Requirements**: GPU with 12GB+ VRAM
- **Speed**: Moderate (thorough processing with VLLM acceleration)
- **Unique**: Only tool with cross-page table/paragraph merging

#### Fallback: Marker
- **Best for**: Academic papers when GPU unavailable
- **Features**: Handles equations, figures, tables
- **Quality**: Good accuracy for research papers
- **Speed**: Moderate (thorough processing)

#### Fallback: PyMuPDF
- **Best for**: Simple text extraction
- **Features**: Fast, reliable text extraction
- **Quality**: Basic but reliable
- **Speed**: Very fast processing

## 🚀 Quick Start

### 1. Setup OCR Environment

```bash
cd docs/research/conversion_tools
chmod +x setup_ocr_tools.sh
./setup_ocr_tools.sh
```

### 2. Convert All Papers

```bash
# Dry run to see what will be converted
python convert_all_papers.py --dry-run

# Run actual conversion
python convert_all_papers.py
```

### 3. Custom Conversion

```bash
# Convert specific directory with custom settings
python pdf_to_markdown_converter.py \
    --input-dir ../papers \
    --output-dir ../papers_markdown \
    --max-workers 8
```

## 📁 Directory Structure

After conversion, your research directory will be organized as:

```
docs/research/
├── papers/                     # Original PDFs (empty after archiving)
├── papers_markdown/            # Converted markdown files
│   ├── README.md              # Conversion summary
│   ├── index.json             # Paper metadata
│   └── *.md                   # Individual paper markdown files
├── papers_metadata/            # Conversion reports and quality data
│   ├── conversion_report.json # Detailed conversion statistics
│   └── quality_assessment.json # Quality metrics per paper
├── papers_archive/             # Archived original PDFs
│   └── *.pdf                  # Original PDF files (gitignored)
└── conversion_tools/           # OCR conversion scripts
    ├── pdf_to_markdown_converter.py
    ├── convert_all_papers.py
    ├── setup_ocr_tools.sh
    └── requirements.txt
```

## ⚙️ Configuration

### config.json

```json
{
    "constitutional_hash": "cdd01ef066bc6cf2",
    "conversion_settings": {
        "max_workers": 4,
        "preferred_method": "marker",
        "fallback_methods": ["pymupdf"],
        "quality_threshold": 0.5
    },
    "output_settings": {
        "markdown_dir": "../papers_markdown",
        "metadata_dir": "../papers_metadata",
        "archive_dir": "../papers_archive"
    }
}
```

### Environment Variables

```bash
# Optional: Set OCR preferences
export ACGS_OCR_METHOD=marker
export ACGS_MAX_WORKERS=8
export ACGS_QUALITY_THRESHOLD=0.7
```

## 📊 Quality Assessment

The conversion system assesses quality based on:

- **Structure Preservation**: Headers, sections, formatting
- **Content Completeness**: Abstract, references, citations
- **Mathematical Content**: Equations and formulas
- **Figure Handling**: Image descriptions and captions

Quality scores range from 0.0 to 1.0, with >0.7 considered high quality.

## 🔧 Advanced Usage

### Custom OCR Pipeline

```python
from pdf_to_markdown_converter import PDFToMarkdownConverter

# Initialize converter
converter = PDFToMarkdownConverter(
    input_dir="path/to/pdfs",
    output_dir="path/to/markdown",
    max_workers=8
)

# Convert single file
result = converter.convert_single_pdf(Path("paper.pdf"))

# Batch convert
results = converter.convert_batch(pdf_files)
```

### Quality Filtering

```bash
# Only convert high-quality papers
python convert_all_papers.py --quality-threshold 0.8

# Retry failed conversions
python convert_all_papers.py --retry-failed
```

## 📈 Performance Optimization

### Parallel Processing
- Default: 4 workers
- Recommended: CPU cores - 1
- Maximum: 8 workers for optimal performance

### Memory Management
- Large PDFs processed individually
- Automatic cleanup of temporary files
- Progress tracking with memory monitoring

### ACGS Integration
- Constitutional hash validation
- Performance metrics collection
- Cache-friendly output format
- Error handling and recovery

## 🔍 Troubleshooting

### Common Issues

1. **Marker Installation Failed**
   ```bash
   # Use fallback method
   export ACGS_OCR_METHOD=pymupdf
   python convert_all_papers.py
   ```

2. **Memory Issues with Large PDFs**
   ```bash
   # Reduce worker count
   python convert_all_papers.py --max-workers 2
   ```

3. **Poor Conversion Quality**
   ```bash
   # Try different OCR method
   python pdf_to_markdown_converter.py --method pymupdf
   ```

### Log Analysis

```bash
# Check conversion logs
tail -f conversion.log

# View detailed error reports
cat ../papers_metadata/conversion_report.json | jq '.results[] | select(.success == false)'
```

## 🔒 Security and Compliance

### Constitutional Compliance
- All operations include hash validation: `cdd01ef066bc6cf2`
- Metadata tracking for audit trails
- Secure file handling and cleanup

### Data Protection
- Original PDFs archived securely
- No external API calls for sensitive content
- Local processing only

## 📚 Integration with ACGS

### Service Integration
- **Constitutional AI (8001)**: Content validation
- **Governance (8004)**: Policy compliance
- **Coordinator (8008)**: Workflow orchestration

### Performance Targets
- **Latency**: <5ms for markdown file access
- **Throughput**: >100 RPS for search operations
- **Cache Hit**: >85% for frequently accessed papers
- **Compliance**: 100% constitutional hash coverage

## 🤝 Contributing

### Adding New OCR Methods

1. Implement conversion method in `PDFToMarkdownConverter`
2. Add method to configuration options
3. Update quality assessment criteria
4. Test with sample papers

### Improving Quality Assessment

1. Enhance quality metrics in `assess_quality()`
2. Add domain-specific validation
3. Implement feedback mechanisms
4. Update scoring algorithms

## 📋 Maintenance

### Regular Tasks

1. **Quality Monitoring**: Review conversion reports monthly
2. **Performance Tuning**: Optimize based on usage patterns
3. **Tool Updates**: Keep OCR libraries current
4. **Archive Management**: Clean up old archives quarterly

### Health Checks

```bash
# Test OCR installation
python -c "from pdf_to_markdown_converter import PDFToMarkdownConverter; print('OK')"

# Validate constitutional compliance
grep -r "cdd01ef066bc6cf2" ../papers_markdown/ | wc -l
```

## 📖 References

- [Marker Documentation](https://github.com/VikParuchuri/marker)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [ACGS Performance Standards](../../docs/ACGS_SERVICE_OVERVIEW.md)
- [Constitutional Compliance Framework](../../docs/constitutional_compliance_validation_framework.md)

---

**Last Updated**: 2025-01-07  
**Constitutional Hash**: cdd01ef066bc6cf2  
**Version**: 1.0.0
