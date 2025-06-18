#!/usr/bin/env python3
"""
Test coverage demonstration script.
"""

import subprocess
import sys
import os

def run_coverage_test():
    """Run a simple coverage test to validate reporting works."""
    
    # Create a simple test module
    test_module = """
def add_numbers(a, b):
    return a + b

def multiply_numbers(a, b):
    return a * b

def divide_numbers(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
"""
    
    test_file = """
import pytest
from simple_math import add_numbers, multiply_numbers, divide_numbers

def test_add_numbers():
    assert add_numbers(2, 3) == 5
    assert add_numbers(-1, 1) == 0

def test_multiply_numbers():
    assert multiply_numbers(3, 4) == 12
    assert multiply_numbers(0, 5) == 0

def test_divide_numbers():
    assert divide_numbers(10, 2) == 5
    with pytest.raises(ValueError):
        divide_numbers(10, 0)
"""
    
    # Write test files
    with open("simple_math.py", "w") as f:
        f.write(test_module)
    
    with open("test_simple_math.py", "w") as f:
        f.write(test_file)
    
    try:
        # Run coverage
        print("🧪 Running coverage test...")
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_simple_math.py", 
            "--cov=simple_math",
            "--cov-report=term-missing",
            "--cov-report=html:coverage_demo_html",
            "-v"
        ], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        
        # Check if HTML report was generated
        if os.path.exists("coverage_demo_html/index.html"):
            print("✅ HTML coverage report generated successfully!")
            print("📊 Coverage report available at: coverage_demo_html/index.html")
        else:
            print("⚠️ HTML coverage report not found")
        
        return result.returncode == 0
        
    finally:
        # Cleanup
        for file in ["simple_math.py", "test_simple_math.py"]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    success = run_coverage_test()
    if success:
        print("✅ Coverage reporting is working correctly!")
    else:
        print("❌ Coverage reporting has issues")
    sys.exit(0 if success else 1)
