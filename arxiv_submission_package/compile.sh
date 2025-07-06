#!/bin/bash
# Academic Submission System Compilation Script
# Simple wrapper for common compilation tasks

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."

    local missing_deps=()

    # Check Python
    if ! command_exists python3; then
        missing_deps+=("python3")
    fi

    # Check LaTeX
    if ! command_exists pdflatex; then
        missing_deps+=("pdflatex (TeX Live)")
    fi

    # Check BibTeX
    if ! command_exists bibtex; then
        missing_deps+=("bibtex")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies and try again."
        exit 1
    fi

    print_success "All dependencies found"
}

# Function to compile LaTeX
compile_latex() {
    print_status "Compiling LaTeX paper..."

    if [ ! -f "main.tex" ]; then
        print_error "main.tex not found in current directory"
        exit 1
    fi

    # Use Python compiler if available, otherwise fallback to direct LaTeX
    if [ -f "latex_compiler.py" ]; then
        python3 latex_compiler.py --verbose "$@"
    else
        # Fallback to direct LaTeX compilation
        print_status "Running pdflatex (1st pass)..."
        pdflatex -interaction=nonstopmode main.tex

        if [ -f "*.bib" ]; then
            print_status "Running bibtex..."
            bibtex main || print_warning "BibTeX had warnings"

            print_status "Running pdflatex (2nd pass)..."
            pdflatex -interaction=nonstopmode main.tex
        fi

        print_status "Running pdflatex (final pass)..."
        pdflatex -interaction=nonstopmode main.tex
    fi

    if [ -f "main.pdf" ]; then
        local pdf_size=$(du -h main.pdf | cut -f1)
        print_success "LaTeX compilation completed! PDF size: $pdf_size"
    else
        print_error "LaTeX compilation failed - no PDF generated"
        exit 1
    fi
}

# Function to build Python package
build_package() {
    print_status "Building Python package..."

    if [ ! -f "setup.py" ]; then
        print_error "setup.py not found in current directory"
        exit 1
    fi

    # Use Python compiler if available
    if [ -f "compiler.py" ]; then
        python3 compiler.py package --verbose
    else
        # Fallback to direct setup.py
        python3 setup.py sdist bdist_wheel
    fi

    if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
        print_success "Package build completed!"
        echo "Distribution files:"
        ls -la dist/
    else
        print_error "Package build failed - no distribution files generated"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."

    if [ -d "tests" ]; then
        if command_exists pytest; then
            pytest tests/ -v --tb=short
        else
            python3 -m unittest discover tests/
        fi
        print_success "Tests completed!"
    else
        print_warning "No tests directory found, skipping tests"
    fi
}

# Function to validate submission
validate_submission() {
    print_status "Validating submission..."

    if [ -f "cli/academic_cli.py" ]; then
        python3 cli/academic_cli.py validate . --output validation_report.md
        print_success "Validation completed! Check validation_report.md"
    else
        print_warning "Validation tool not found, skipping validation"
    fi
}

# Function to clean build artifacts
clean_build() {
    print_status "Cleaning build artifacts..."

    # LaTeX artifacts
    rm -f *.aux *.bbl *.blg *.fdb_latexmk *.fls *.log *.out *.toc *.synctex.gz

    # Python artifacts
    rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/
    find . -name "*.pyc" -delete

    print_success "Cleanup completed!"
}

# Function to show usage
show_usage() {
    echo "Academic Submission System Compilation Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  latex          Compile LaTeX paper only"
    echo "  package        Build Python package only"
    echo "  test           Run tests only"
    echo "  validate       Validate submission only"
    echo "  clean          Clean build artifacts"
    echo "  all            Compile everything (default)"
    echo "  quick          Quick build (latex + package, no tests)"
    echo ""
    echo "Options:"
    echo "  --engine ENGINE    LaTeX engine (pdflatex, xelatex, lualatex)"
    echo "  --venue VENUE      Optimize for venue (arxiv, ieee, acm)"
    echo "  --help, -h         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Full build"
    echo "  $0 latex           # LaTeX only"
    echo "  $0 quick           # Quick build"
    echo "  $0 latex --venue arxiv  # LaTeX optimized for arXiv"
}

# Main script logic
main() {
    local command="all"
    local engine_arg=""
    local venue_arg=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            latex|package|test|validate|clean|all|quick)
                command="$1"
                shift
                ;;
            --engine)
                engine_arg="--engine $2"
                shift 2
                ;;
            --venue)
                venue_arg="--venue $2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Print header
    echo "=================================================="
    echo "Academic Submission System Compiler"
    echo "=================================================="
    echo ""

    # Check dependencies
    check_dependencies
    echo ""

    # Execute command
    case $command in
        latex)
            compile_latex $engine_arg $venue_arg
            ;;
        package)
            build_package
            ;;
        test)
            run_tests
            ;;
        validate)
            validate_submission
            ;;
        clean)
            clean_build
            ;;
        quick)
            compile_latex $engine_arg $venue_arg
            echo ""
            build_package
            ;;
        all)
            compile_latex $engine_arg $venue_arg
            echo ""
            build_package
            echo ""
            run_tests
            echo ""
            validate_submission
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac

    echo ""
    print_success "Compilation script completed!"

    # Show summary of generated files
    echo ""
    echo "Generated files:"
    [ -f "main.pdf" ] && echo "  📄 main.pdf (LaTeX output)"
    [ -d "dist" ] && [ "$(ls -A dist)" ] && echo "  📦 dist/ (Python packages)"
    [ -f "validation_report.md" ] && echo "  📋 validation_report.md (Validation report)"
    [ -f "build_report.md" ] && echo "  📊 build_report.md (Build report)"
}

# Run main function with all arguments
main "$@"
