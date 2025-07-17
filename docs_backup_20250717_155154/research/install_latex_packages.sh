#!/bin/bash
# LaTeX Package Installation Script for ACGS Research Papers
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root for system-wide installation
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        log "Running as root - will install system-wide LaTeX packages"
        INSTALL_MODE="system"
    else
        log "Running as user - will install user-local LaTeX packages"
        INSTALL_MODE="user"
    fi
}

# Detect LaTeX distribution
detect_latex_distribution() {
    log "Detecting LaTeX distribution..."
    
    if command -v tlmgr &> /dev/null; then
        LATEX_DIST="texlive"
        success "Found TeX Live distribution"
    elif command -v miktex &> /dev/null; then
        LATEX_DIST="miktex"
        success "Found MiKTeX distribution"
    else
        error "No LaTeX distribution found. Please install TeX Live or MiKTeX first."
        exit 1
    fi
}

# Update LaTeX package database
update_latex_database() {
    log "Updating LaTeX package database..."
    
    case $LATEX_DIST in
        "texlive")
            if [[ $INSTALL_MODE == "system" ]]; then
                tlmgr update --self --all
            else
                tlmgr --usermode update --self --all
            fi
            ;;
        "miktex")
            miktex packages update
            ;;
    esac
    
    success "LaTeX package database updated"
}

# Core LaTeX packages required for research papers
install_core_packages() {
    log "Installing core LaTeX packages..."
    
    local core_packages=(
        # Document classes and basic packages
        "acmart"
        "amsmath"
        "amsfonts" 
        "amssymb"
        "latexsym"
        "mathtools"
        "bm"
        
        # Table packages
        "multirow"
        "array"
        "tabularx"
        "booktabs"
        "longtable"
        "makecell"
        "siunitx"
        
        # Algorithm packages
        "algorithm2e"
        "algorithmic"
        "algorithmicx"
        "algpseudocode"
        
        # Code listing packages
        "listings"
        "minted"
        "fancyvrb"
        
        # Graphics and figures
        "graphicx"
        "subcaption"
        "tikz"
        "pgfplots"
        "pgfplotstable"
        "float"
        "wrapfig"
        "tcolorbox"
        
        # Bibliography and references
        "natbib"
        "biblatex"
        "biber"
        "cleveref"
        
        # URL and hyperlink packages
        "hyperref"
        "url"
        "xurl"
        
        # Font and encoding packages
        "inputenc"
        "fontenc"
        "lmodern"
        "microtype"
        "fontawesome5"
        
        # Color packages
        "xcolor"
        "color"
        
        # Layout and formatting
        "geometry"
        "fancyhdr"
        "enumitem"
        "placeins"
        "afterpage"
        "caption"
        "subcaption"
        
        # Math and symbols
        "nicefrac"
        "etoolbox"
        "mathrsfs"
        "dsfont"
        
        # Utilities
        "ifpdf"
        "ifthen"
        "calc"
        "xparse"
        "l3packages"
    )
    
    for package in "${core_packages[@]}"; do
        install_package "$package"
    done
    
    success "Core LaTeX packages installed"
}

# Install specialized packages for academic papers
install_academic_packages() {
    log "Installing specialized academic packages..."
    
    local academic_packages=(
        # Conference and journal templates
        "neurips"
        "icml2024"
        "iclr2024"
        "nips"
        "jmlr"
        "ieee"
        "acm"
        
        # Theorem and proof environments
        "amsthm"
        "thmtools"
        "thm-restate"
        
        # Advanced math packages
        "mathtools"
        "mathabx"
        "stmaryrd"
        "bbm"
        "dsfont"
        
        # Diagram and plotting
        "tikz-cd"
        "pgfgantt"
        "forest"
        "qtree"
        
        # Advanced tables
        "threeparttable"
        "adjustbox"
        "rotating"
        "pdflscape"
        
        # Advanced bibliography
        "biblatex-ieee"
        "biblatex-nature"
        "biblatex-science"
        
        # Appendix and supplementary material
        "appendix"
        "subfiles"
        "standalone"
        
        # Review and collaboration
        "todonotes"
        "changes"
        "lineno"
        
        # Advanced formatting
        "titlesec"
        "titletoc"
        "parskip"
        "setspace"
    )
    
    for package in "${academic_packages[@]}"; do
        install_package "$package" "optional"
    done
    
    success "Academic packages installed"
}

# Install a single package
install_package() {
    local package=$1
    local mode=${2:-"required"}
    
    log "Installing package: $package"
    
    case $LATEX_DIST in
        "texlive")
            if [[ $INSTALL_MODE == "system" ]]; then
                if tlmgr install "$package" 2>/dev/null; then
                    success "Installed $package"
                else
                    if [[ $mode == "required" ]]; then
                        warning "Failed to install required package: $package"
                    else
                        log "Optional package $package not available, skipping"
                    fi
                fi
            else
                if tlmgr --usermode install "$package" 2>/dev/null; then
                    success "Installed $package (user mode)"
                else
                    if [[ $mode == "required" ]]; then
                        warning "Failed to install required package: $package"
                    else
                        log "Optional package $package not available, skipping"
                    fi
                fi
            fi
            ;;
        "miktex")
            if miktex packages install "$package" 2>/dev/null; then
                success "Installed $package"
            else
                if [[ $mode == "required" ]]; then
                    warning "Failed to install required package: $package"
                else
                    log "Optional package $package not available, skipping"
                fi
            fi
            ;;
    esac
}

# Install Python packages for LaTeX processing
install_python_packages() {
    log "Installing Python packages for LaTeX processing..."
    
    local python_packages=(
        "pylatex>=1.4.1"
        "latexcodec>=2.0.1"
        "pygments>=2.15.0"  # For minted package
        "matplotlib>=3.7.0"  # For generating figures
        "numpy>=1.24.0"
        "pandas>=2.0.0"
        "seaborn>=0.12.0"
        "plotly>=5.15.0"
        "bibtexparser>=1.4.0"
        "pybtex>=0.24.0"
    )
    
    for package in "${python_packages[@]}"; do
        if pip install "$package" 2>/dev/null; then
            success "Installed Python package: $package"
        else
            warning "Failed to install Python package: $package"
        fi
    done
    
    success "Python packages for LaTeX processing installed"
}

# Verify installation
verify_installation() {
    log "Verifying LaTeX installation..."
    
    # Test basic LaTeX compilation
    local test_dir="/tmp/latex_test_$$"
    mkdir -p "$test_dir"
    
    cat > "$test_dir/test.tex" << 'EOF'
\documentclass{article}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{algorithm}
\usepackage{algpseudocode}
\begin{document}
\title{LaTeX Installation Test}
\author{ACGS Research Team}
\maketitle

\section{Test Section}
This is a test document to verify LaTeX installation.

\subsection{Math Test}
$$E = mc^2$$

\subsection{Table Test}
\begin{table}[h]
\centering
\begin{tabular}{cc}
\toprule
Column 1 & Column 2 \\
\midrule
Data 1 & Data 2 \\
\bottomrule
\end{tabular}
\caption{Test table}
\end{table}

\subsection{Algorithm Test}
\begin{algorithm}
\caption{Test Algorithm}
\begin{algorithmic}
\State $x \leftarrow 1$
\State \Return $x$
\end{algorithmic}
\end{algorithm}

\end{document}
EOF
    
    cd "$test_dir"
    if pdflatex test.tex > /dev/null 2>&1; then
        success "LaTeX compilation test passed"
        rm -rf "$test_dir"
        return 0
    else
        error "LaTeX compilation test failed"
        rm -rf "$test_dir"
        return 1
    fi
}

# Main installation function
main() {
    log "Starting LaTeX package installation for ACGS research papers"
    log "Constitutional Hash: cdd01ef066bc6cf2"
    
    check_permissions
    detect_latex_distribution
    update_latex_database
    install_core_packages
    install_academic_packages
    install_python_packages
    
    if verify_installation; then
        success "LaTeX package installation completed successfully!"
        log "You can now compile the research papers in docs/research/"
    else
        error "Installation verification failed. Please check the logs above."
        exit 1
    fi
}

# Run main function
main "$@"
