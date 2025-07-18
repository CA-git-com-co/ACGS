# Constitutional Hash: cdd01ef066bc6cf2
@echo off
REM Academic Submission System Compilation Script for Windows
REM Simple wrapper for common compilation tasks

setlocal enabledelayedexpansion

REM Set default values
set "COMMAND=all"
set "ENGINE_ARG="
set "VENUE_ARG="

REM Function to print status messages
:print_status
echo [%time%] %~1
goto :eof

:print_success
echo ✅ %~1
goto :eof

:print_warning
echo ⚠️  %~1
goto :eof

:print_error
echo ❌ %~1
goto :eof

REM Function to check if command exists
:command_exists
where %1 >nul 2>&1
goto :eof

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :check_deps
if "%~1"=="latex" (
    set "COMMAND=latex"
    shift
    goto :parse_args
)
if "%~1"=="package" (
    set "COMMAND=package"
    shift
    goto :parse_args
)
if "%~1"=="test" (
    set "COMMAND=test"
    shift
    goto :parse_args
)
if "%~1"=="validate" (
    set "COMMAND=validate"
    shift
    goto :parse_args
)
if "%~1"=="clean" (
    set "COMMAND=clean"
    shift
    goto :parse_args
)
if "%~1"=="all" (
    set "COMMAND=all"
    shift
    goto :parse_args
)
if "%~1"=="quick" (
    set "COMMAND=quick"
    shift
    goto :parse_args
)
if "%~1"=="--engine" (
    set "ENGINE_ARG=--engine %~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--venue" (
    set "VENUE_ARG=--venue %~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--help" goto :show_usage
if "%~1"=="-h" goto :show_usage
call :print_error "Unknown option: %~1"
goto :show_usage

REM Check dependencies
:check_deps
call :print_status "Checking dependencies..."

call :command_exists python
if errorlevel 1 (
    call :command_exists python3
    if errorlevel 1 (
        call :print_error "Python not found. Please install Python 3.9 or later."
        exit /b 1
    ) else (
        set "PYTHON=python3"
    )
) else (
    set "PYTHON=python"
)

call :command_exists pdflatex
if errorlevel 1 (
    call :print_warning "pdflatex not found. LaTeX compilation may fail."
    call :print_warning "Please install TeX Live or MiKTeX."
)

call :print_success "Dependencies checked"
goto :main_logic

REM Show usage information
:show_usage
echo Academic Submission System Compilation Script
echo.
echo Usage: %~nx0 [COMMAND] [OPTIONS]
echo.
echo Commands:
echo   latex          Compile LaTeX paper only
echo   package        Build Python package only
echo   test           Run tests only
echo   validate       Validate submission only
echo   clean          Clean build artifacts
echo   all            Compile everything (default)
echo   quick          Quick build (latex + package, no tests)
echo.
echo Options:
echo   --engine ENGINE    LaTeX engine (pdflatex, xelatex, lualatex)
echo   --venue VENUE      Optimize for venue (arxiv, ieee, acm)
echo   --help, -h         Show this help message
echo.
echo Examples:
echo   %~nx0                 # Full build
echo   %~nx0 latex           # LaTeX only
echo   %~nx0 quick           # Quick build
echo   %~nx0 latex --venue arxiv  # LaTeX optimized for arXiv
exit /b 0

REM Compile LaTeX
:compile_latex
call :print_status "Compiling LaTeX paper..."

if not exist "main.tex" (
    call :print_error "main.tex not found in current directory"
    exit /b 1
)

REM Use Python compiler if available
if exist "latex_compiler.py" (
    %PYTHON% latex_compiler.py --verbose %ENGINE_ARG% %VENUE_ARG%
) else (
    REM Fallback to direct LaTeX compilation
    call :print_status "Running pdflatex (1st pass)..."
    pdflatex -interaction=nonstopmode main.tex

    if exist "*.bib" (
        call :print_status "Running bibtex..."
        bibtex main

        call :print_status "Running pdflatex (2nd pass)..."
        pdflatex -interaction=nonstopmode main.tex
    )

    call :print_status "Running pdflatex (final pass)..."
    pdflatex -interaction=nonstopmode main.tex
)

if exist "main.pdf" (
    for %%A in (main.pdf) do set "PDF_SIZE=%%~zA"
    call :print_success "LaTeX compilation completed! PDF size: !PDF_SIZE! bytes"
) else (
    call :print_error "LaTeX compilation failed - no PDF generated"
    exit /b 1
)
goto :eof

REM Build Python package
:build_package
call :print_status "Building Python package..."

if not exist "setup.py" (
    call :print_error "setup.py not found in current directory"
    exit /b 1
)

REM Use Python compiler if available
if exist "compiler.py" (
    %PYTHON% compiler.py package --verbose
) else (
    REM Fallback to direct setup.py
    %PYTHON% setup.py sdist bdist_wheel
)

if exist "dist" (
    dir /b dist | findstr /r ".*" >nul
    if not errorlevel 1 (
        call :print_success "Package build completed!"
        echo Distribution files:
        dir dist
    ) else (
        call :print_error "Package build failed - no distribution files generated"
        exit /b 1
    )
) else (
    call :print_error "Package build failed - no distribution files generated"
    exit /b 1
)
goto :eof

REM Run tests
:run_tests
call :print_status "Running tests..."

if exist "tests" (
    call :command_exists pytest
    if not errorlevel 1 (
        pytest tests/ -v --tb=short
    ) else (
        %PYTHON% -m unittest discover tests/
    )
    call :print_success "Tests completed!"
) else (
    call :print_warning "No tests directory found, skipping tests"
)
goto :eof

REM Validate submission
:validate_submission
call :print_status "Validating submission..."

if exist "cli\academic_cli.py" (
    %PYTHON% cli\academic_cli.py validate . --output validation_report.md
    call :print_success "Validation completed! Check validation_report.md"
) else (
    call :print_warning "Validation tool not found, skipping validation"
)
goto :eof

REM Clean build artifacts
:clean_build
call :print_status "Cleaning build artifacts..."

REM LaTeX artifacts
del /q *.aux *.bbl *.blg *.fdb_latexmk *.fls *.log *.out *.toc *.synctex.gz 2>nul

REM Python artifacts
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rmdir /s /q "%%d"
for /d /r . %%d in (*.egg-info) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc 2>nul

call :print_success "Cleanup completed!"
goto :eof

REM Main logic
:main_logic
echo ==================================================
echo Academic Submission System Compiler
echo ==================================================
echo.

if "%COMMAND%"=="latex" (
    call :compile_latex
) else if "%COMMAND%"=="package" (
    call :build_package
) else if "%COMMAND%"=="test" (
    call :run_tests
) else if "%COMMAND%"=="validate" (
    call :validate_submission
) else if "%COMMAND%"=="clean" (
    call :clean_build
) else if "%COMMAND%"=="quick" (
    call :compile_latex
    echo.
    call :build_package
) else if "%COMMAND%"=="all" (
    call :compile_latex
    echo.
    call :build_package
    echo.
    call :run_tests
    echo.
    call :validate_submission
) else (
    call :print_error "Unknown command: %COMMAND%"
    goto :show_usage
)

echo.
call :print_success "Compilation script completed!"

REM Show summary of generated files
echo.
echo Generated files:
if exist "main.pdf" echo   📄 main.pdf (LaTeX output)
if exist "dist" (
    dir /b dist | findstr /r ".*" >nul
    if not errorlevel 1 echo   📦 dist\ (Python packages)
)
if exist "validation_report.md" echo   📋 validation_report.md (Validation report)
if exist "build_report.md" echo   📊 build_report.md (Build report)

exit /b 0

REM Parse arguments and start
call :parse_args %*
