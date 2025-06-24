# Academic Submission System User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Command Line Interface](#command-line-interface)
3. [Web Interface](#web-interface)
4. [Understanding Validation Results](#understanding-validation-results)
5. [Venue-Specific Guidelines](#venue-specific-guidelines)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

Before using the Academic Submission System, ensure you have:

- **Python 3.11 or higher**
- **LaTeX distribution** (TeX Live, MiKTeX, or MacTeX)
- **Git** (for cloning the repository)
- **Text editor** or LaTeX IDE

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/CA-git-com-co/ACGS.git
   cd ACGS/arxiv_submission_package
   ```

2. **Set Up Python Environment**
   ```bash
   # Create virtual environment (recommended)
   python -m venv academic_env
   source academic_env/bin/activate  # Linux/Mac
   # or
   academic_env\Scripts\activate  # Windows
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Verify Installation**
   ```bash
   python cli/academic_cli.py --help
   ```

### Your First Validation

Let's validate the included example paper:

```bash
# Navigate to the submission package
cd arxiv_submission_package

# Run basic validation
python cli/academic_cli.py validate .

# Check arXiv compliance
python cli/academic_cli.py compliance . --venue arxiv
```

## Command Line Interface

### Basic Commands

#### Validate Command
The `validate` command performs comprehensive validation of your academic submission:

```bash
# Basic validation
python cli/academic_cli.py validate /path/to/paper/

# Specify output format and file
python cli/academic_cli.py validate /path/to/paper/ --output report.md --format markdown

# JSON output for automation
python cli/academic_cli.py validate /path/to/paper/ --format json --output results.json

# Verbose output for debugging
python cli/academic_cli.py validate /path/to/paper/ --verbose
```

#### Compliance Command
Check venue-specific compliance requirements:

```bash
# arXiv compliance (default)
python cli/academic_cli.py compliance /path/to/paper/

# IEEE compliance
python cli/academic_cli.py compliance /path/to/paper/ --venue ieee

# ACM compliance
python cli/academic_cli.py compliance /path/to/paper/ --venue acm

# Save compliance report
python cli/academic_cli.py compliance /path/to/paper/ --venue arxiv --output arxiv_compliance.md
```

#### Status Command
Get a quick overview of your submission:

```bash
python cli/academic_cli.py status /path/to/paper/
```

This provides:
- File structure overview
- Key files presence check
- Quick validation summary
- Last modification dates

#### Global Options

```bash
# Verbose output (detailed logging)
python cli/academic_cli.py --verbose validate /path/to/paper/

# Quiet mode (minimal output)
python cli/academic_cli.py --quiet validate /path/to/paper/

# Custom configuration file
python cli/academic_cli.py --config custom_config.json validate /path/to/paper/
```

### Advanced Usage

#### Batch Processing
Validate multiple papers:

```bash
#!/bin/bash
for paper in papers/*/; do
  echo "Validating $paper"
  python cli/academic_cli.py validate "$paper" --output "${paper}/validation_report.md"
done
```

#### Integration with Build Systems
Add to your Makefile:

```makefile
validate:
	python cli/academic_cli.py validate . --format json --output validation.json
	@if [ $$? -eq 0 ]; then echo "✅ Validation passed"; else echo "❌ Validation failed"; fi

compliance-check:
	python cli/academic_cli.py compliance . --venue arxiv --output arxiv_compliance.md
	python cli/academic_cli.py compliance . --venue ieee --output ieee_compliance.md

.PHONY: validate compliance-check
```

## Web Interface

### Starting the Web Server

```bash
# Start with default settings
python web/app.py

# Access at http://localhost:5000
```

### Using the Web Interface

#### 1. Upload Files
- Navigate to the Upload page
- Select multiple files or drag and drop
- Supported formats: `.tex`, `.bib`, `.png`, `.jpg`, `.pdf`, `.eps`, `.txt`, `.md`
- Maximum file size: 50MB total

#### 2. View Validation Results
After upload, you'll see:
- **Overall Status**: EXCELLENT, GOOD, ACCEPTABLE, or NEEDS_IMPROVEMENT
- **Compliance Score**: Percentage score (0-100%)
- **Detailed Results**: Check-by-check breakdown
- **Recommendations**: Specific improvement suggestions

#### 3. Download Reports
- **Markdown Report**: Human-readable validation report
- **JSON Report**: Machine-readable results for automation

#### 4. Compliance Checking
- Select venue (arXiv, IEEE, ACM)
- View venue-specific compliance results
- Download compliance reports

### API Endpoints

#### Validation API
```bash
# Upload ZIP file for validation
curl -X POST -F "file=@submission.zip" http://localhost:5000/api/validate

# Response format:
{
  "submission_id": "20250624_143022",
  "overall_status": "GOOD",
  "compliance_score": 85.7,
  "validation_results": [...],
  "recommendations": [...]
}
```

#### Compliance API
```bash
# Check compliance for existing submission
curl -X POST -H "Content-Type: application/json" \
  -d '{"submission_id": "20250624_143022", "venue": "arxiv"}' \
  http://localhost:5000/api/compliance
```

## Understanding Validation Results

### Status Levels

#### EXCELLENT ✅
- All checks passed
- Maximum 2 warnings
- Ready for submission

#### GOOD ✅
- All critical checks passed
- Some warnings present
- Minor improvements recommended

#### ACCEPTABLE ⚠️
- 1-2 critical issues
- Multiple warnings
- Requires attention before submission

#### NEEDS_IMPROVEMENT ❌
- 3+ critical issues
- Significant problems detected
- Major revisions required

### Validation Checks

#### File Structure
- **Required Files**: `main.tex`, `README.txt`
- **Optional Files**: Bibliography (`.bib`), figures directory
- **Organization**: Proper file naming and structure

#### LaTeX Syntax
- **Brace Matching**: Balanced `{` and `}`
- **References**: All `\ref{}` have corresponding `\label{}`
- **Citations**: All `\cite{}` have bibliography entries
- **Packages**: Compatible package usage

#### Bibliography
- **Completeness**: Required fields for each entry type
- **Formatting**: Proper BibTeX syntax
- **Quality**: No empty fields, valid URLs/DOIs

#### Figures
- **Existence**: All referenced figures exist
- **Formats**: Compatible image formats
- **Captions**: Proper figure captions and labels

#### Content Quality
- **Abstract**: Appropriate length (50-300 words)
- **Structure**: Minimum 3 sections recommended
- **Placeholders**: No TODO, FIXME, or lorem ipsum text

#### Accessibility
- **Captions**: All figures have captions
- **Headings**: Proper section hierarchy
- **Color**: Not relying solely on color for information

#### Reproducibility
- **Documentation**: README and code availability
- **Data**: Data access information
- **Keywords**: Reproducibility-related terms
- **Citations**: Adequate reference count

### Compliance Score Calculation

The compliance score is calculated as:
```
Score = (PASS × 1.0 + WARNING × 0.5 + FAIL × 0.0) / Total Checks × 100%
```

- **90-100%**: Excellent submission quality
- **80-89%**: Good submission quality
- **70-79%**: Acceptable with improvements
- **Below 70%**: Needs significant work

## Venue-Specific Guidelines

### arXiv Submission

#### Requirements
- **File Size**: Maximum 50MB total
- **File Types**: LaTeX, PDF figures, standard formats
- **Structure**: Must include title, author, abstract
- **Bibliography**: BibTeX format recommended

#### Best Practices
- Use PDFLaTeX for compilation
- Include all source files
- Optimize figure sizes
- Provide clear README

#### Common Issues
- **Oversized submissions**: Compress figures, remove unnecessary files
- **Missing abstracts**: Add `\begin{abstract}...\end{abstract}`
- **Broken references**: Check all `\ref{}` and `\cite{}` commands

### IEEE Publications

#### Requirements
- **Template**: Use official IEEE templates
- **References**: IEEE citation style
- **Figures**: High-resolution, professional quality
- **Copyright**: Include IEEE copyright notice

#### Best Practices
- Follow IEEE formatting guidelines strictly
- Use IEEE reference style
- Include author biographies
- Provide high-quality figures

### ACM Publications

#### Requirements
- **Template**: ACM article template
- **Metadata**: Complete author information
- **References**: ACM reference format
- **Accessibility**: Alt text for figures

#### Best Practices
- Use ACM Computing Classification System
- Include complete author affiliations
- Provide accessible content
- Follow ACM ethical guidelines

## Best Practices

### Paper Organization

#### Directory Structure
```
paper/
├── main.tex              # Main LaTeX file
├── README.txt           # Submission description
├── references.bib       # Bibliography
├── figs/               # Figures directory
│   ├── figure1.png
│   ├── figure2.pdf
│   └── ...
├── sections/           # Optional: separate sections
│   ├── introduction.tex
│   ├── methodology.tex
│   └── ...
└── supplementary/      # Optional: additional materials
    ├── code/
    └── data/
```

#### File Naming
- Use descriptive, lowercase names
- Avoid spaces and special characters
- Use underscores for separation: `figure_1_results.png`
- Include version numbers if needed: `main_v2.tex`

### LaTeX Best Practices

#### Document Structure
```latex
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{cite}

\title{Your Paper Title}
\author{Your Name}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
Your abstract here (50-300 words).
\end{abstract}

\section{Introduction}
\label{sec:introduction}
% Content here

\section{Methodology}
\label{sec:methodology}
% Content here

\section{Results}
\label{sec:results}
% Content here

\section{Conclusion}
\label{sec:conclusion}
% Content here

\bibliographystyle{plain}
\bibliography{references}

\end{document}
```

#### Figure Management
```latex
% Good figure inclusion
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{figs/results_comparison}
    \caption{Comparison of results across different methods. Error bars show standard deviation.}
    \label{fig:results}
\end{figure}

% Reference the figure
As shown in Figure~\ref{fig:results}, our method outperforms...
```

#### Bibliography Management
```bibtex
@article{author2023title,
    title={Complete and Descriptive Title},
    author={Last, First and Other, Author},
    journal={Journal Name},
    volume={42},
    number={3},
    pages={123--145},
    year={2023},
    publisher={Publisher Name},
    doi={10.1000/journal.2023.123456}
}
```

### Quality Assurance

#### Pre-Submission Checklist
- [ ] All figures are high-resolution and clearly labeled
- [ ] All references are complete and properly formatted
- [ ] Abstract is within word limits and clearly written
- [ ] All sections have appropriate content and structure
- [ ] No placeholder text or TODO items remain
- [ ] All mathematical notation is consistent
- [ ] Code and data availability is documented
- [ ] Ethical considerations are addressed

#### Validation Workflow
1. **Draft Completion**: Write complete first draft
2. **Initial Validation**: Run basic validation checks
3. **Content Review**: Review and revise content
4. **Figure Optimization**: Optimize figures for size and quality
5. **Bibliography Check**: Verify all references
6. **Final Validation**: Run comprehensive validation
7. **Venue Compliance**: Check specific venue requirements
8. **Submission Preparation**: Package for submission

## Troubleshooting

### Common Validation Errors

#### "Missing required files: main.tex"
**Problem**: The main LaTeX file is not found or named incorrectly.
**Solution**: 
- Ensure your main file is named `main.tex`
- Check file permissions and accessibility
- Verify you're running validation in the correct directory

#### "Unmatched braces: X difference"
**Problem**: LaTeX syntax error with mismatched braces.
**Solution**:
- Use a LaTeX editor with brace matching
- Check for missing `}` after `\begin{environment}`
- Verify all command arguments are properly enclosed

#### "Undefined references: [ref1, ref2]"
**Problem**: References to non-existent labels.
**Solution**:
- Check all `\ref{}` commands have corresponding `\label{}`
- Verify label names match exactly (case-sensitive)
- Ensure labels are defined before references

#### "Citations found but no bibliography file"
**Problem**: Using `\cite{}` without a `.bib` file.
**Solution**:
- Add a `.bib` file with bibliography entries
- Include `\bibliography{filename}` in your LaTeX
- Verify bibliography file is in the correct location

#### "Missing referenced figures"
**Problem**: Figures referenced in text don't exist.
**Solution**:
- Check figure file names match `\includegraphics{}` commands
- Verify figure files are in the correct directory
- Ensure file extensions are included if required

### Performance Issues

#### Slow Validation
**Problem**: Validation takes too long.
**Solution**:
- Check for very large files or many figures
- Optimize figure sizes and formats
- Use incremental validation for large projects

#### Memory Issues
**Problem**: Out of memory errors during validation.
**Solution**:
- Reduce figure sizes and resolution
- Split large documents into smaller parts
- Close other applications to free memory

### Installation Issues

#### Missing Dependencies
**Problem**: Import errors or missing modules.
**Solution**:
```bash
# Update pip and reinstall
pip install --upgrade pip
pip install -r requirements.txt

# For web interface
pip install flask

# For additional features
pip install matplotlib seaborn
```

#### Permission Errors
**Problem**: Cannot access files or directories.
**Solution**:
```bash
# Fix file permissions
chmod +x cli/academic_cli.py
chmod -R 755 arxiv_submission_package/

# Check directory ownership
ls -la arxiv_submission_package/
```

### Getting Additional Help

#### Enable Debug Mode
```bash
# Maximum verbosity
python cli/academic_cli.py --verbose validate /path/to/paper/

# Check specific components
python quality_assurance/submission_validator.py /path/to/paper/
```

#### Check System Requirements
```bash
# Verify Python version
python --version

# Check installed packages
pip list

# Test LaTeX installation
pdflatex --version
```

#### Community Support
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the complete documentation
- **Examples**: Review example papers and configurations
- **Stack Overflow**: Search for LaTeX and academic writing help

---

This user guide provides comprehensive information for using the Academic Submission System effectively. For technical details and API documentation, refer to the other documentation files in this directory.
