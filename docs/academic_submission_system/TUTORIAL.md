# Academic Submission System Tutorial

## Tutorial Overview

This tutorial will walk you through using the Academic Submission System step-by-step, from installation to submitting a paper to arXiv. We'll use practical examples and real-world scenarios to demonstrate all major features.

## Prerequisites

- Basic knowledge of LaTeX
- Python 3.11+ installed
- Text editor or LaTeX IDE
- Terminal/command prompt access

## Tutorial Structure

1. [Setup and Installation](#setup-and-installation)
2. [Creating Your First Paper](#creating-your-first-paper)
3. [Basic Validation](#basic-validation)
4. [Understanding and Fixing Issues](#understanding-and-fixing-issues)
5. [Venue-Specific Compliance](#venue-specific-compliance)
6. [Using the Web Interface](#using-the-web-interface)
7. [Advanced Features](#advanced-features)
8. [Automation and Integration](#automation-and-integration)

## Setup and Installation

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS/arxiv_submission_package

# Create virtual environment
python -m venv tutorial_env
source tutorial_env/bin/activate  # Linux/Mac
# or
tutorial_env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
# Test the CLI
python cli/academic_cli.py --help

# Test the validator
python quality_assurance/submission_validator.py --help
```

You should see help text for both commands.

## Creating Your First Paper

Let's create a simple academic paper to demonstrate the validation system.

### Step 1: Create Project Directory

```bash
mkdir tutorial_paper
cd tutorial_paper
```

### Step 2: Create Main LaTeX File

Create `main.tex`:

```latex
\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{cite}
\usepackage{url}

\title{A Tutorial Paper for Academic Submission Validation}
\author{Tutorial Author\\
        Tutorial University\\
        \texttt{tutorial@example.com}}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
This is a tutorial paper demonstrating the Academic Submission System. 
The abstract should be between 50 and 300 words to pass validation. 
This paper covers the basic structure required for academic submissions 
and demonstrates how the validation system works. We include multiple 
sections, figures, and references to show comprehensive validation 
capabilities. The system checks for LaTeX syntax, bibliography 
completeness, figure references, and venue-specific compliance.
\end{abstract}

\section{Introduction}
\label{sec:introduction}

Academic paper submission requires careful attention to formatting, 
structure, and compliance with venue requirements. This tutorial 
demonstrates how to use the Academic Submission System to validate 
papers before submission.

The system performs comprehensive checks including:
\begin{itemize}
    \item LaTeX syntax validation
    \item Bibliography completeness
    \item Figure reference checking
    \item Venue-specific compliance
    \item Content quality assessment
\end{itemize}

\section{Methodology}
\label{sec:methodology}

Our approach involves automated validation of academic submissions 
using a multi-stage pipeline. Figure~\ref{fig:workflow} shows the 
validation workflow.

The validation process includes several key components:
\begin{enumerate}
    \item File structure analysis
    \item LaTeX compilation checking
    \item Reference validation
    \item Content quality metrics
\end{enumerate}

\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{figs/validation_workflow}
    \caption{Academic submission validation workflow showing the 
    multi-stage validation process from input to final report.}
    \label{fig:workflow}
\end{figure}

\section{Results}
\label{sec:results}

The validation system successfully identifies common issues in 
academic submissions. Table~\ref{tab:results} shows validation 
results for different paper types.

\begin{table}[htbp]
    \centering
    \begin{tabular}{|l|c|c|c|}
    \hline
    Paper Type & Pass Rate & Warning Rate & Fail Rate \\
    \hline
    Conference & 85\% & 12\% & 3\% \\
    Journal & 92\% & 7\% & 1\% \\
    arXiv & 78\% & 18\% & 4\% \\
    \hline
    \end{tabular}
    \caption{Validation results by paper type showing pass, warning, 
    and failure rates across different submission venues.}
    \label{tab:results}
\end{table}

As cited in~\cite{smith2023validation}, automated validation 
significantly improves submission quality.

\section{Discussion}
\label{sec:discussion}

The results demonstrate the effectiveness of automated validation 
for academic submissions. The system catches common errors and 
provides actionable recommendations for improvement.

Key benefits include:
\begin{itemize}
    \item Reduced submission rejections
    \item Improved paper quality
    \item Time savings for authors
    \item Consistent formatting
\end{itemize}

\section{Conclusion}
\label{sec:conclusion}

This tutorial has demonstrated the Academic Submission System's 
capabilities for validating academic papers. The system provides 
comprehensive checking and clear feedback to help authors prepare 
high-quality submissions.

Future work will include additional venue support and enhanced 
content quality metrics as discussed in~\cite{jones2023future}.

\bibliographystyle{plain}
\bibliography{references}

\end{document}
```

### Step 3: Create Bibliography File

Create `references.bib`:

```bibtex
@article{smith2023validation,
    title={Automated Validation of Academic Submissions: A Comprehensive Study},
    author={Smith, John and Doe, Jane},
    journal={Journal of Academic Publishing},
    volume={15},
    number={3},
    pages={45--62},
    year={2023},
    publisher={Academic Press},
    doi={10.1000/jap.2023.456789}
}

@inproceedings{jones2023future,
    title={Future Directions in Academic Submission Systems},
    author={Jones, Alice and Brown, Bob},
    booktitle={Proceedings of the International Conference on Academic Publishing},
    pages={123--135},
    year={2023},
    organization={IEEE},
    doi={10.1109/ICAP.2023.987654}
}

@misc{wilson2023tools,
    title={Tools for Academic Writing and Submission},
    author={Wilson, Carol},
    year={2023},
    howpublished={\url{https://example.com/academic-tools}},
    note={Accessed: 2023-12-01}
}
```

### Step 4: Create Figures Directory and README

```bash
# Create figures directory
mkdir figs

# Create a simple README
cat > README.txt << EOF
Tutorial Paper for Academic Submission Validation

This is a demonstration paper for the Academic Submission System tutorial.

Files included:
- main.tex: Main LaTeX source file
- references.bib: Bibliography file
- figs/: Directory for figures
- README.txt: This file

Compilation instructions:
1. pdflatex main.tex
2. bibtex main
3. pdflatex main.tex
4. pdflatex main.tex

This paper demonstrates the validation system's capabilities.
EOF
```

### Step 5: Create a Simple Figure

For this tutorial, we'll create a placeholder figure. In practice, you'd have actual figures.

```bash
# Create a simple text-based figure placeholder
cat > figs/validation_workflow.txt << EOF
This is a placeholder for the validation workflow figure.
In a real paper, this would be a PNG, PDF, or EPS file.
EOF
```

## Basic Validation

Now let's validate our tutorial paper using the Academic Submission System.

### Step 1: Run Basic Validation

```bash
# Navigate back to the submission package directory
cd ../

# Run validation on our tutorial paper
python cli/academic_cli.py validate tutorial_paper/
```

You'll see output similar to:
```
2025-06-24 14:30:22 - INFO - Validating submission: tutorial_paper
2025-06-24 14:30:22 - INFO - Target venue: arxiv

📊 Validation Summary
==================================================
Overall Status: NEEDS_IMPROVEMENT
Compliance Score: 42.9%

Results:
  ✅ Passed: 3
  ⚠️  Warnings: 2
  ❌ Failed: 2

❌ Critical Issues:
  • Figures: Missing referenced figures
  • arXiv Compliance: Missing \\title command

💡 Recommendations:
  1. Add missing figure files or fix references
  2. Fix arXiv compliance: Missing \\title command
```

### Step 2: Generate Detailed Report

```bash
# Generate a detailed markdown report
python cli/academic_cli.py validate tutorial_paper/ --output tutorial_validation.md --format markdown

# View the report
cat tutorial_validation.md
```

### Step 3: Check Status

```bash
# Get quick status overview
python cli/academic_cli.py status tutorial_paper/
```

## Understanding and Fixing Issues

Let's analyze and fix the issues found in our validation.

### Issue 1: Missing Figure File

The validation found that we reference `figs/validation_workflow` but the actual file doesn't exist in the expected format.

**Fix**: Create a proper figure file or update the reference.

```bash
# Option 1: Create a simple PDF figure (requires LaTeX)
cd tutorial_paper/
cat > create_figure.tex << EOF
\documentclass{standalone}
\usepackage{tikz}
\begin{document}
\begin{tikzpicture}
\node[draw, rectangle] (input) at (0,0) {Input Paper};
\node[draw, rectangle] (validate) at (3,0) {Validation};
\node[draw, rectangle] (report) at (6,0) {Report};
\draw[->] (input) -- (validate);
\draw[->] (validate) -- (report);
\end{tikzpicture}
\end{document}
EOF

# Compile to create PDF figure
pdflatex create_figure.tex
mv create_figure.pdf figs/validation_workflow.pdf

# Clean up
rm create_figure.*

# Option 2: Use a PNG placeholder (simpler)
# Create a simple image file (this is just a placeholder)
echo "Validation Workflow Diagram" > figs/validation_workflow.png
```

### Issue 2: Update LaTeX Reference

Update the figure reference in `main.tex` to match the actual file:

```latex
% Change this line:
\includegraphics[width=0.8\textwidth]{figs/validation_workflow}

% To this (if using PNG):
\includegraphics[width=0.8\textwidth]{figs/validation_workflow.png}

% Or this (if using PDF):
\includegraphics[width=0.8\textwidth]{figs/validation_workflow.pdf}
```

### Step 3: Re-run Validation

```bash
cd ../
python cli/academic_cli.py validate tutorial_paper/
```

You should now see improved results:
```
📊 Validation Summary
==================================================
Overall Status: GOOD
Compliance Score: 85.7%

Results:
  ✅ Passed: 6
  ⚠️  Warnings: 1
  ❌ Failed: 0
```

## Venue-Specific Compliance

Let's check compliance for different academic venues.

### arXiv Compliance

```bash
# Check arXiv compliance
python cli/academic_cli.py compliance tutorial_paper/ --venue arxiv --output arxiv_compliance.md

# View results
cat arxiv_compliance.md
```

### IEEE Compliance

```bash
# Check IEEE compliance
python cli/academic_cli.py compliance tutorial_paper/ --venue ieee --output ieee_compliance.md
```

### ACM Compliance

```bash
# Check ACM compliance
python cli/academic_cli.py compliance tutorial_paper/ --venue acm --output acm_compliance.md
```

### Comparing Venue Requirements

```bash
# Generate all compliance reports
for venue in arxiv ieee acm; do
    echo "Checking $venue compliance..."
    python cli/academic_cli.py compliance tutorial_paper/ --venue $venue --output ${venue}_compliance.md
done

# Compare results
echo "=== Compliance Summary ==="
for venue in arxiv ieee acm; do
    echo "$venue:"
    grep -A 5 "Compliance Rate" ${venue}_compliance.md
    echo ""
done
```

## Using the Web Interface

Let's explore the web interface for a more user-friendly experience.

### Step 1: Start the Web Server

```bash
# Start the web interface
python web/app.py
```

You'll see:
```
Starting Academic Submission Web Interface...
Access the application at: http://localhost:5000
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[::1]:5000
```

### Step 2: Upload Files via Web Interface

1. Open your browser and go to `http://localhost:5000`
2. Click "Start Validation" or navigate to the Upload page
3. Select all files from your `tutorial_paper/` directory:
   - `main.tex`
   - `references.bib`
   - `README.txt`
   - `figs/validation_workflow.png` (or .pdf)
4. Click "Upload Files"

### Step 3: View Results

The web interface will show:
- **Overall Status**: Visual indicator (EXCELLENT, GOOD, etc.)
- **Compliance Score**: Percentage with color coding
- **Detailed Results**: Expandable sections for each check
- **Recommendations**: Actionable improvement suggestions

### Step 4: Download Reports

- Click "Download Report" to get a markdown file
- Use the API endpoints for programmatic access

### Step 5: Check Compliance

- Select different venues from the compliance checker
- Compare results across venues
- Download venue-specific reports

## Advanced Features

### Custom Configuration

Create a custom configuration file for your specific needs:

```bash
cat > custom_config.json << EOF
{
  "size_limits": {
    "arxiv": 52428800,
    "ieee": 10485760,
    "custom_venue": 20971520
  },
  "abstract_limits": {
    "min_words": 75,
    "max_words": 250
  },
  "required_sections": 4,
  "strict_mode": true,
  "custom_checks": {
    "require_acknowledgments": true,
    "require_author_bio": false,
    "max_figures": 10
  }
}
EOF

# Use custom configuration
python cli/academic_cli.py --config custom_config.json validate tutorial_paper/
```

### Batch Processing

Process multiple papers automatically:

```bash
#!/bin/bash
# batch_validate.sh

echo "Batch validation starting..."

for paper_dir in papers/*/; do
    if [ -d "$paper_dir" ]; then
        echo "Processing: $paper_dir"
        
        # Validate paper
        python cli/academic_cli.py validate "$paper_dir" \
            --output "${paper_dir}/validation_report.md" \
            --format markdown
        
        # Check arXiv compliance
        python cli/academic_cli.py compliance "$paper_dir" \
            --venue arxiv \
            --output "${paper_dir}/arxiv_compliance.md"
        
        # Generate summary
        echo "$(basename "$paper_dir"): $(grep 'Overall Status' "${paper_dir}/validation_report.md")"
    fi
done

echo "Batch validation complete!"
```

### Integration with LaTeX Editors

#### VS Code Integration

Create `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Validate Paper",
            "type": "shell",
            "command": "python",
            "args": [
                "cli/academic_cli.py",
                "validate",
                "${workspaceFolder}",
                "--output",
                "validation_report.md"
            ],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        }
    ]
}
```

#### Makefile Integration

Create a `Makefile` in your paper directory:

```makefile
# Makefile for academic paper

PAPER = main
VALIDATOR = ../cli/academic_cli.py

.PHONY: all validate compliance clean

all: $(PAPER).pdf validate

$(PAPER).pdf: $(PAPER).tex references.bib
	pdflatex $(PAPER)
	bibtex $(PAPER)
	pdflatex $(PAPER)
	pdflatex $(PAPER)

validate: $(PAPER).tex
	python $(VALIDATOR) validate . --output validation_report.md
	@echo "Validation complete. Check validation_report.md"

compliance: $(PAPER).tex
	python $(VALIDATOR) compliance . --venue arxiv --output arxiv_compliance.md
	python $(VALIDATOR) compliance . --venue ieee --output ieee_compliance.md
	@echo "Compliance checks complete."

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.fdb_latexmk *.fls
	rm -f validation_report.md *_compliance.md

submit-ready: all validate compliance
	@if grep -q "EXCELLENT\|GOOD" validation_report.md; then \
		echo "✅ Paper is ready for submission!"; \
	else \
		echo "❌ Paper needs improvement before submission."; \
		exit 1; \
	fi
```

## Automation and Integration

### Continuous Integration

#### GitHub Actions

Create `.github/workflows/paper-validation.yml`:

```yaml
name: Paper Validation

on:
  push:
    paths:
      - 'paper/**'
  pull_request:
    paths:
      - 'paper/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd arxiv_submission_package
        pip install -r requirements.txt
    
    - name: Validate paper
      run: |
        cd arxiv_submission_package
        python cli/academic_cli.py validate ../paper/ --format json --output validation.json
    
    - name: Check compliance
      run: |
        cd arxiv_submission_package
        python cli/academic_cli.py compliance ../paper/ --venue arxiv --output arxiv_compliance.md
    
    - name: Upload validation results
      uses: actions/upload-artifact@v3
      with:
        name: validation-results
        path: |
          arxiv_submission_package/validation.json
          arxiv_submission_package/arxiv_compliance.md
    
    - name: Comment on PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const validation = JSON.parse(fs.readFileSync('arxiv_submission_package/validation.json', 'utf8'));
          
          const comment = `## Paper Validation Results
          
          **Overall Status:** ${validation.overall_status}
          **Compliance Score:** ${validation.compliance_score.toFixed(1)}%
          
          **Summary:**
          - ✅ Passed: ${validation.validation_results.filter(r => r.status === 'PASS').length}
          - ⚠️ Warnings: ${validation.validation_results.filter(r => r.status === 'WARNING').length}
          - ❌ Failed: ${validation.validation_results.filter(r => r.status === 'FAIL').length}
          
          ${validation.recommendations.length > 0 ? '**Recommendations:**\n' + validation.recommendations.map(r => `- ${r}`).join('\n') : ''}
          `;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-paper
        name: Validate Academic Paper
        entry: python arxiv_submission_package/cli/academic_cli.py validate paper/
        language: system
        pass_filenames: false
        files: 'paper/.*\.(tex|bib)$'
```

### API Integration

Create a Python script for automated validation:

```python
#!/usr/bin/env python3
"""
Automated paper validation script
"""

import sys
import json
import subprocess
from pathlib import Path

def validate_paper(paper_path, venues=['arxiv']):
    """Validate paper and return results."""
    results = {}
    
    # Run validation
    cmd = [
        'python', 'cli/academic_cli.py', 'validate', 
        str(paper_path), '--format', 'json', '--output', 'temp_validation.json'
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        
        with open('temp_validation.json', 'r') as f:
            results['validation'] = json.load(f)
        
        # Check compliance for each venue
        results['compliance'] = {}
        for venue in venues:
            cmd = [
                'python', 'cli/academic_cli.py', 'compliance',
                str(paper_path), '--venue', venue
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            results['compliance'][venue] = {
                'success': result.returncode == 0,
                'output': result.stdout
            }
        
        return results
        
    except subprocess.CalledProcessError as e:
        return {'error': str(e)}
    
    finally:
        # Cleanup
        Path('temp_validation.json').unlink(missing_ok=True)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python validate_api.py <paper_path>")
        sys.exit(1)
    
    paper_path = sys.argv[1]
    results = validate_paper(paper_path)
    
    print(json.dumps(results, indent=2))
```

## Conclusion

This tutorial has covered:

1. **Setup and Installation**: Getting the system running
2. **Paper Creation**: Building a complete academic paper
3. **Validation Process**: Understanding and fixing issues
4. **Venue Compliance**: Checking different submission requirements
5. **Web Interface**: Using the browser-based interface
6. **Advanced Features**: Custom configuration and batch processing
7. **Automation**: CI/CD integration and automated workflows

### Next Steps

- **Explore Advanced Features**: Custom validation rules, plugins
- **Integrate with Your Workflow**: Add to your existing paper writing process
- **Contribute**: Help improve the system with feedback and contributions
- **Share**: Help other researchers by sharing your experience

### Additional Resources

- **Documentation**: Complete API and user documentation
- **Examples**: More example papers and configurations
- **Community**: Join discussions and get help
- **Updates**: Stay informed about new features and improvements

The Academic Submission System is designed to make academic publishing easier and more reliable. With automated validation and comprehensive checking, you can focus on your research while ensuring your papers meet all submission requirements.
