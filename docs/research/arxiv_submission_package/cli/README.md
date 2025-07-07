# Academic Submission CLI Tool
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->


A comprehensive command-line interface for academic paper submission preparation, validation, and optimization.

## Installation

```bash
# Install required dependencies
pip install -r requirements.txt

# Make CLI executable
chmod +x academic_cli.py
```

## Quick Start

```bash
# Validate a submission
python academic_cli.py validate /path/to/paper/

# Check arXiv compliance
python academic_cli.py compliance /path/to/paper/ --venue arxiv

# Get submission status
python academic_cli.py status /path/to/paper/
```

## Commands

### validate

Comprehensive validation of academic submissions.

```bash
python academic_cli.py validate [OPTIONS] PATH

Options:
  --venue {arxiv,ieee,acm}    Target venue (default: arxiv)
  --output, -o TEXT           Output file for report
  --format {markdown,json,html} Report format (default: markdown)
```

**Examples:**

```bash
# Basic validation
python academic_cli.py validate ./my_paper/

# Validate for IEEE with JSON output
python academic_cli.py validate ./my_paper/ --venue ieee --format json

# Save report to specific file
python academic_cli.py validate ./my_paper/ --output validation_report.md
```

### compliance

Check venue-specific compliance requirements.

```bash
python academic_cli.py compliance [OPTIONS] PATH

Options:
  --venue {arxiv,ieee,acm}    Target venue (default: arxiv)
  --output, -o TEXT           Output file for report
```

**Examples:**

```bash
# Check arXiv compliance
python academic_cli.py compliance ./my_paper/ --venue arxiv

# Check ACM compliance with custom output
python academic_cli.py compliance ./my_paper/ --venue acm --output acm_compliance.md
```

### status

Quick overview of submission status.

```bash
python academic_cli.py status PATH
```

**Example:**

```bash
python academic_cli.py status ./my_paper/
```

**Output:**

```
📄 Academic Submission Status
==================================================
Path: ./my_paper/
Last modified: 2025-06-24 10:30:45

📋 Key Files:
  ✅ main.tex
  ✅ README
  ✅ Bibliography
  ✅ Figures

🔍 Quick Validation:
  Overall Status: GOOD
  Compliance Score: 87.5%
  ⚠️  2 warnings
```

### optimize (Coming Soon)

Automatically optimize submissions for better compliance.

```bash
python academic_cli.py optimize [OPTIONS] PATH

Options:
  --fix-warnings              Automatically fix common warnings
  --backup                    Create backup before optimization
```

### package (Coming Soon)

Package submission for upload to various venues.

```bash
python academic_cli.py package [OPTIONS] PATH

Options:
  --venue {arxiv,ieee,acm}    Target venue
  --output, -o TEXT           Output archive file
```

### init (Coming Soon)

Initialize new academic submission with templates.

```bash
python academic_cli.py init [OPTIONS] PATH

Options:
  --template {basic,arxiv,ieee,acm}  Template to use
```

## Global Options

```bash
--verbose, -v               Enable verbose output
--quiet, -q                 Suppress non-essential output
--config TEXT               Path to configuration file
```

## Configuration File

Create a JSON configuration file to customize behavior:

```json
{
  "default_venue": "arxiv",
  "output_format": "markdown",
  "auto_backup": true,
  "validation_rules": {
    "strict_mode": false,
    "ignore_warnings": ["ARXIV_004"]
  },
  "venues": {
    "arxiv": {
      "max_size_mb": 50,
      "required_files": ["main.tex"]
    }
  }
}
```

Use with:

```bash
python academic_cli.py --config config.json validate ./my_paper/
```

## Validation Checks

The tool performs comprehensive validation including:

### File Structure

- ✅ Required files present (main.tex, README)
- ✅ Proper directory organization
- ✅ File naming conventions

### LaTeX Syntax

- ✅ Balanced braces and environments
- ✅ Undefined references detection
- ✅ Missing citations identification
- ✅ Package compatibility

### Bibliography

- ✅ Bibliography file completeness
- ✅ Citation format validation
- ✅ Missing required fields
- ✅ URL and DOI validation

### Figures

- ✅ Figure file existence
- ✅ Reference consistency
- ✅ Caption completeness
- ✅ Format compatibility

### arXiv Compliance

- ✅ File size limits (50MB)
- ✅ Prohibited file types
- ✅ Required document elements
- ✅ Metadata completeness

### Content Quality

- ✅ Abstract length and quality
- ✅ Section structure
- ✅ Placeholder text detection
- ✅ Word count analysis

### Accessibility

- ✅ Figure alt text (captions)
- ✅ Heading structure
- ✅ Color-only information detection
- ✅ Screen reader compatibility

### Reproducibility

- ✅ README file presence
- ✅ Code availability
- ✅ Data availability mentions
- ✅ FAIR compliance indicators

## Exit Codes

- `0`: Success (all checks passed)
- `1`: Validation failed (critical issues found)
- `130`: Operation cancelled by user

## Output Formats

### Markdown (Default)

Human-readable report with status icons and recommendations.

### JSON

Machine-readable format for integration with other tools.

### HTML (Coming Soon)

Web-friendly format with interactive elements.

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/validate-paper.yml
name: Validate Paper
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.9"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Validate submission
        run: python academic_cli.py validate ./paper/ --format json
```

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit
python academic_cli.py validate ./paper/ --quiet
exit $?
```

### Makefile Integration

```makefile
.PHONY: validate compliance status

validate:
	python academic_cli.py validate ./paper/

compliance:
	python academic_cli.py compliance ./paper/ --venue arxiv

status:
	python academic_cli.py status ./paper/

check: validate compliance
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'quality_assurance'**

- Ensure you're running from the correct directory
- Check that all required files are present

**Permission denied**

- Make the script executable: `chmod +x academic_cli.py`
- Check file permissions in submission directory

**Validation fails with "main.tex not found"**

- Ensure main.tex exists in the submission directory
- Check file naming (case-sensitive)

**Large file warnings**

- Compress images to reduce file size
- Remove unnecessary files from submission

### Getting Help

```bash
# General help
python academic_cli.py --help

# Command-specific help
python academic_cli.py validate --help
python academic_cli.py compliance --help
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
