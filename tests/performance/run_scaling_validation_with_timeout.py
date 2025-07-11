#!/usr/bin/env python3
"""
Run comprehensive scaling validation with proper timeout and error handling
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import subprocess
import sys
import signal
import json
from datetime import datetime

def run_with_timeout(timeout_seconds=1800):  # 30 minutes timeout
    """Run the comprehensive scaling validation with timeout protection"""
    
    print(f"🚀 Starting ACGS-2 Comprehensive Scaling Validation")
    print(f"⏱️  Maximum test duration: {timeout_seconds} seconds")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Run the test with timeout
        result = subprocess.run(
            [sys.executable, "comprehensive_scaling_validation.py"],
            timeout=timeout_seconds,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("⚠️  Errors/Warnings:")
            print(result.stderr)
            
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print(f"\n⏱️  Test exceeded timeout of {timeout_seconds} seconds")
        print("📊 Checking for partial results...")
        
        # Try to load partial results
        try:
            with open("comprehensive_scaling_validation_results.json", "r") as f:
                results = json.load(f)
                print("\n✅ Partial results found:")
                print(json.dumps(results, indent=2))
        except FileNotFoundError:
            print("❌ No results file found")
        
        return 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        print("📊 Checking for partial results...")
        
        # Try to load partial results
        try:
            with open("comprehensive_scaling_validation_results.json", "r") as f:
                results = json.load(f)
                print("\n✅ Partial results found:")
                print(json.dumps(results, indent=2))
        except FileNotFoundError:
            print("❌ No results file found")
        
        return 130  # Standard exit code for SIGINT
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    finally:
        print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    exit_code = run_with_timeout()
    sys.exit(exit_code)