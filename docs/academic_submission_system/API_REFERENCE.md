# Academic Submission System API Reference

## Overview

The Academic Submission System provides multiple APIs for programmatic access to validation and compliance checking functionality:

1. **Python API**: Direct access to validation classes and functions
2. **Command Line API**: Full-featured CLI for automation and scripting
3. **REST API**: HTTP endpoints for web integration
4. **Configuration API**: Customizable validation rules and settings

## Python API

### Core Classes

#### SubmissionValidator

The main validation engine for academic submissions.

```python
from quality_assurance.submission_validator import SubmissionValidator

class SubmissionValidator:
    def __init__(self, submission_path: str)
    def validate_submission(self) -> SubmissionReport
```

**Parameters:**
- `submission_path` (str): Path to the submission directory

**Returns:**
- `SubmissionReport`: Comprehensive validation results

**Example:**
```python
validator = SubmissionValidator("/path/to/paper/")
report = validator.validate_submission()

print(f"Status: {report.overall_status}")
print(f"Score: {report.compliance_score:.1f}%")

for result in report.validation_results:
    print(f"{result.check_name}: {result.status}")
```

#### ComplianceChecker

Venue-specific compliance validation.

```python
from quality_assurance.compliance_checker import ComplianceChecker

class ComplianceChecker:
    def __init__(self)
    def check_compliance(self, submission_path: str, venue: str) -> List[ComplianceResult]
```

**Parameters:**
- `submission_path` (str): Path to the submission directory
- `venue` (str): Target venue ('arxiv', 'ieee', 'acm')

**Returns:**
- `List[ComplianceResult]`: List of compliance check results

**Example:**
```python
checker = ComplianceChecker()
results = checker.check_compliance("/path/to/paper/", "arxiv")

for result in results:
    print(f"{result.rule_id}: {result.status} - {result.message}")
```

### Data Classes

#### ValidationResult

Individual validation check result.

```python
@dataclass
class ValidationResult:
    check_name: str
    status: str  # 'PASS', 'WARNING', 'FAIL'
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = None
```

#### SubmissionReport

Comprehensive validation report.

```python
@dataclass
class SubmissionReport:
    submission_path: str
    validation_results: List[ValidationResult]
    overall_status: str
    compliance_score: float
    recommendations: List[str]
    timestamp: str = None
```

#### ComplianceResult

Venue-specific compliance check result.

```python
@dataclass
class ComplianceResult:
    rule_id: str
    status: str  # 'PASS', 'WARNING', 'FAIL'
    message: str
    details: Optional[Dict[str, Any]] = None
```

### Utility Functions

#### generate_validation_report

Generate markdown validation report.

```python
def generate_validation_report(
    report: SubmissionReport, 
    output_path: str = None
) -> str
```

**Parameters:**
- `report` (SubmissionReport): Validation report to format
- `output_path` (str, optional): Output file path

**Returns:**
- `str`: Path to generated report file

**Example:**
```python
from quality_assurance.submission_validator import generate_validation_report

validator = SubmissionValidator("/path/to/paper/")
report = validator.validate_submission()
report_file = generate_validation_report(report, "validation_report.md")
```

#### generate_compliance_report

Generate venue-specific compliance report.

```python
def generate_compliance_report(
    results: List[ComplianceResult],
    venue: str,
    output_path: str = None
) -> str
```

**Parameters:**
- `results` (List[ComplianceResult]): Compliance check results
- `venue` (str): Target venue name
- `output_path` (str, optional): Output file path

**Returns:**
- `str`: Path to generated report file

## Command Line API

### Main Command Structure

```bash
python cli/academic_cli.py [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGUMENTS]
```

### Global Options

```bash
--verbose, -v          Enable verbose output
--quiet, -q           Suppress non-essential output
--config CONFIG_FILE  Path to configuration file
--help, -h           Show help message
```

### Commands

#### validate

Perform comprehensive validation of academic submission.

```bash
python cli/academic_cli.py validate SUBMISSION_PATH [OPTIONS]
```

**Options:**
- `--venue VENUE`: Target venue (default: arxiv)
- `--output, -o FILE`: Output file for report
- `--format FORMAT`: Output format (markdown, json, html)

**Examples:**
```bash
# Basic validation
python cli/academic_cli.py validate /path/to/paper/

# JSON output for automation
python cli/academic_cli.py validate /path/to/paper/ --format json --output results.json

# Verbose validation with custom venue
python cli/academic_cli.py --verbose validate /path/to/paper/ --venue ieee
```

**Exit Codes:**
- `0`: Validation passed (no failures)
- `1`: Validation failed (one or more failures)
- `130`: Operation cancelled by user

#### compliance

Check venue-specific compliance requirements.

```bash
python cli/academic_cli.py compliance SUBMISSION_PATH [OPTIONS]
```

**Options:**
- `--venue VENUE`: Target venue (arxiv, ieee, acm)
- `--output, -o FILE`: Output file for report

**Examples:**
```bash
# arXiv compliance check
python cli/academic_cli.py compliance /path/to/paper/ --venue arxiv

# Multiple venue checks
for venue in arxiv ieee acm; do
  python cli/academic_cli.py compliance /path/to/paper/ --venue $venue --output ${venue}_report.md
done
```

#### status

Show quick submission status and overview.

```bash
python cli/academic_cli.py status SUBMISSION_PATH
```

**Example:**
```bash
python cli/academic_cli.py status /path/to/paper/
```

**Output:**
```
📄 Academic Submission Status
==================================================
Path: /path/to/paper/
Last modified: 2025-06-24 14:30:22

📋 Key Files:
  ✅ main.tex
  ✅ README
  ✅ Bibliography
  ✅ Figures

🔍 Quick Validation:
  Overall Status: GOOD
  Compliance Score: 85.7%
  ✅ No issues found
```

#### init

Initialize new academic submission (planned feature).

```bash
python cli/academic_cli.py init SUBMISSION_PATH [OPTIONS]
```

**Options:**
- `--template TEMPLATE`: Template type (basic, arxiv, ieee, acm)

#### package

Package submission for upload (planned feature).

```bash
python cli/academic_cli.py package SUBMISSION_PATH [OPTIONS]
```

**Options:**
- `--output, -o FILE`: Output archive file
- `--venue VENUE`: Target venue for packaging

#### optimize

Optimize submission for better compliance (planned feature).

```bash
python cli/academic_cli.py optimize SUBMISSION_PATH [OPTIONS]
```

**Options:**
- `--fix-warnings`: Automatically fix common warnings
- `--backup`: Create backup before optimization

## REST API

### Base URL

When running the web interface:
```
http://localhost:5000
```

### Authentication

Currently no authentication required for local use. For production deployment, implement appropriate authentication mechanisms.

### Endpoints

#### POST /api/validate

Upload and validate academic submission.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: ZIP file containing submission

**Response:**
```json
{
  "submission_id": "20250624_143022",
  "overall_status": "GOOD",
  "compliance_score": 85.7,
  "validation_results": [
    {
      "check_name": "File Structure",
      "status": "PASS",
      "message": "All required files present"
    }
  ],
  "recommendations": [
    "Consider adding more detailed figure captions"
  ]
}
```

**Example:**
```bash
curl -X POST -F "file=@submission.zip" http://localhost:5000/api/validate
```

#### POST /api/compliance

Check compliance for existing submission.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
  "submission_id": "20250624_143022",
  "venue": "arxiv"
}
```

**Response:**
```json
{
  "venue": "arxiv",
  "results": [
    {
      "rule_id": "arxiv_size_limit",
      "status": "PASS",
      "message": "Submission size within limits"
    }
  ]
}
```

**Example:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"submission_id": "20250624_143022", "venue": "arxiv"}' \
  http://localhost:5000/api/compliance
```

#### GET /download_report/{submission_id}

Download validation report for submission.

**Parameters:**
- `submission_id`: Unique submission identifier

**Response:**
- Content-Type: `application/octet-stream`
- Body: Markdown validation report file

**Example:**
```bash
curl -O http://localhost:5000/download_report/20250624_143022
```

### Error Responses

All API endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (submission not found)
- `413`: Payload Too Large (file size exceeded)
- `500`: Internal Server Error

Error response format:
```json
{
  "error": "Description of the error",
  "details": {
    "additional": "error details"
  }
}
```

## Configuration API

### Configuration File Format

JSON configuration file with validation settings:

```json
{
  "size_limits": {
    "arxiv": 52428800,
    "ieee": 10485760,
    "acm": 20971520
  },
  "abstract_limits": {
    "min_words": 50,
    "max_words": 300
  },
  "required_sections": 3,
  "strict_mode": false,
  "venue_specific": {
    "arxiv": {
      "require_abstract": true,
      "max_figures": 20,
      "allowed_formats": ["png", "pdf", "eps"]
    },
    "ieee": {
      "require_keywords": true,
      "max_pages": 8,
      "reference_style": "ieee"
    }
  },
  "custom_checks": {
    "require_acknowledgments": false,
    "require_author_bio": false,
    "check_plagiarism": false
  }
}
```

### Configuration Options

#### Size Limits
- `size_limits`: Maximum file sizes per venue (bytes)
- `max_figures`: Maximum number of figures allowed
- `max_pages`: Maximum page count (if applicable)

#### Content Requirements
- `abstract_limits`: Word count limits for abstracts
- `required_sections`: Minimum number of sections
- `require_abstract`: Whether abstract is mandatory
- `require_keywords`: Whether keywords are required

#### Validation Behavior
- `strict_mode`: Enable stricter validation rules
- `custom_checks`: Enable/disable optional checks
- `allowed_formats`: Permitted file formats per venue

### Loading Configuration

#### Python API
```python
import json
from pathlib import Path

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Use with validator
validator = SubmissionValidator("/path/to/paper/")
# Apply configuration (implementation-specific)
```

#### CLI
```bash
python cli/academic_cli.py --config custom_config.json validate /path/to/paper/
```

### Environment Variables

Override configuration with environment variables:

```bash
export ACADEMIC_VALIDATOR_STRICT_MODE=true
export ACADEMIC_VALIDATOR_MAX_SIZE=50000000
export ACADEMIC_VALIDATOR_DEFAULT_VENUE=arxiv

python cli/academic_cli.py validate /path/to/paper/
```

## Error Handling

### Exception Classes

#### ValidationError
Raised when validation encounters an error.

```python
class ValidationError(Exception):
    def __init__(self, message: str, details: Dict[str, Any] = None)
```

#### ComplianceError
Raised when compliance checking fails.

```python
class ComplianceError(Exception):
    def __init__(self, venue: str, message: str, details: Dict[str, Any] = None)
```

#### ConfigurationError
Raised when configuration is invalid.

```python
class ConfigurationError(Exception):
    def __init__(self, message: str, config_path: str = None)
```

### Error Handling Examples

```python
from quality_assurance.submission_validator import SubmissionValidator, ValidationError

try:
    validator = SubmissionValidator("/path/to/paper/")
    report = validator.validate_submission()
except ValidationError as e:
    print(f"Validation failed: {e}")
    if e.details:
        print(f"Details: {e.details}")
except FileNotFoundError:
    print("Submission directory not found")
except PermissionError:
    print("Permission denied accessing submission files")
```

## Performance Considerations

### Optimization Tips

1. **Large Submissions**: Use incremental validation for large papers
2. **Batch Processing**: Process multiple papers in parallel
3. **Caching**: Enable result caching for repeated validations
4. **Resource Limits**: Set appropriate memory and CPU limits

### Performance Metrics

- **Typical Validation Time**: 2-5 seconds per paper
- **Memory Usage**: <100MB for standard papers
- **Concurrent Limit**: 10 simultaneous validations recommended
- **File Size Limit**: 50MB per submission (configurable)

### Monitoring

```python
import time
from quality_assurance.submission_validator import SubmissionValidator

start_time = time.time()
validator = SubmissionValidator("/path/to/paper/")
report = validator.validate_submission()
end_time = time.time()

print(f"Validation completed in {end_time - start_time:.2f} seconds")
print(f"Compliance score: {report.compliance_score:.1f}%")
```

## Integration Examples

### CI/CD Integration

```python
#!/usr/bin/env python3
"""CI/CD validation script"""

import sys
import json
from quality_assurance.submission_validator import SubmissionValidator

def main():
    if len(sys.argv) != 2:
        print("Usage: validate_ci.py <paper_path>")
        sys.exit(1)
    
    paper_path = sys.argv[1]
    validator = SubmissionValidator(paper_path)
    report = validator.validate_submission()
    
    # Output JSON for CI system
    result = {
        "status": report.overall_status,
        "score": report.compliance_score,
        "passed": len([r for r in report.validation_results if r.status == "PASS"]),
        "failed": len([r for r in report.validation_results if r.status == "FAIL"])
    }
    
    print(json.dumps(result))
    
    # Exit with appropriate code
    sys.exit(0 if result["failed"] == 0 else 1)

if __name__ == "__main__":
    main()
```

### Custom Validation Rules

```python
from quality_assurance.submission_validator import SubmissionValidator, ValidationResult

class CustomValidator(SubmissionValidator):
    def _validate_custom_requirements(self):
        """Add custom validation logic."""
        # Example: Check for specific keywords
        main_tex = self.submission_path / "main.tex"
        if main_tex.exists():
            with open(main_tex, 'r') as f:
                content = f.read()
            
            required_keywords = ['machine learning', 'artificial intelligence']
            found_keywords = [kw for kw in required_keywords if kw.lower() in content.lower()]
            
            if len(found_keywords) < len(required_keywords):
                self.results.append(ValidationResult(
                    check_name="Custom Keywords",
                    status="WARNING",
                    message=f"Missing keywords: {set(required_keywords) - set(found_keywords)}"
                ))
            else:
                self.results.append(ValidationResult(
                    check_name="Custom Keywords",
                    status="PASS",
                    message="All required keywords present"
                ))
    
    def validate_submission(self):
        """Override to include custom validation."""
        report = super().validate_submission()
        self._validate_custom_requirements()
        return report
```

---

This API reference provides comprehensive documentation for all interfaces provided by the Academic Submission System. For additional examples and use cases, refer to the tutorial and user guide documentation.
