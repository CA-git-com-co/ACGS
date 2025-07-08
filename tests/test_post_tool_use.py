#!/usr/bin/env python3
"""
Test demonstration for post_tool_use.py completion logging system.

This script demonstrates various tool result scenarios and markdown conversion.
"""

import json
import subprocess
import sys
from pathlib import Path


def run_post_tool_use(tool_result_data: dict) -> dict:
    """Run post_tool_use.py with given tool result data."""
    script_path = Path(__file__).parent / "post_tool_use.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=json.dumps(tool_result_data),
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running post_tool_use.py: {e}")
        print(f"Stderr: {e.stderr}")
        return {"error": str(e)}


def test_scenarios():
    """Test various tool result scenarios."""
    
    print("=== Testing post_tool_use.py ===\n")
    
    # Test 1: Successful tool with markdown content
    print("Test 1: Successful tool with markdown content")
    result1 = run_post_tool_use({
        "tool_name": "file_reader",
        "content": "# File Contents\n\n**Important:** This file contains `sensitive` data.\n\n- Item 1\n- Item 2\n\n[Documentation](https://example.com)",
        "success": True,
        "file_path": "/example/file.txt"
    })
    print(f"Result: {result1}\n")
    
    # Test 2: Error scenario
    print("Test 2: Error scenario")
    result2 = run_post_tool_use({
        "tool_name": "database_query",
        "error": "Connection timeout after 30 seconds",
        "success": False,
        "query": "SELECT * FROM users"
    })
    print(f"Result: {result2}\n")
    
    # Test 3: Complex tool result with multiple content fields
    print("Test 3: Complex tool result")
    result3 = run_post_tool_use({
        "tool_name": "api_call",
        "response": {
            "status": 200,
            "data": "**API Response:** Successfully retrieved data"
        },
        "message": "API call completed",
        "success": True,
        "execution_time": "1.2s"
    })
    print(f"Result: {result3}\n")
    
    # Test 4: Constitutional compliance validation
    print("Test 4: Constitutional compliance validation")
    result4 = run_post_tool_use({
        "tool_name": "compliance_check",
        "constitutional_hash": "cdd01ef066bc6cf2",
        "content": "Constitutional compliance verified",
        "success": True
    })
    print(f"Result: {result4}\n")
    
    # Test 5: Empty/minimal input
    print("Test 5: Minimal input")
    result5 = run_post_tool_use({})
    print(f"Result: {result5}\n")
    
    print("=== All tests completed ===")


def check_log_files():
    """Check the generated log files."""
    print("\n=== Checking log files ===\n")
    
    logs_dir = Path("/home/dislove/ACGS-2/logs")
    
    # Check post_tool_use.json
    post_tool_log = logs_dir / "post_tool_use.json"
    if post_tool_log.exists():
        print(f"post_tool_use.json exists ({post_tool_log.stat().st_size} bytes)")
        print("Last few entries:")
        try:
            with open(post_tool_log) as f:
                lines = f.readlines()
                for line in lines[-3:]:
                    data = json.loads(line.strip())
                    print(f"  - {data.get('timestamp', 'Unknown time')}: {data.get('log_type', 'Unknown type')}")
        except Exception as e:
            print(f"  Error reading file: {e}")
    else:
        print("post_tool_use.json does not exist")
    
    # Check chat.json
    chat_log = logs_dir / "chat.json"
    if chat_log.exists():
        print(f"\nchat.json exists ({chat_log.stat().st_size} bytes)")
        print("Last few entries:")
        try:
            with open(chat_log) as f:
                lines = f.readlines()
                for line in lines[-3:]:
                    data = json.loads(line.strip())
                    print(f"  - {data.get('timestamp', 'Unknown time')}: {data.get('tool_name', 'Unknown tool')} - {data.get('content', '')[:50]}...")
        except Exception as e:
            print(f"  Error reading file: {e}")
    else:
        print("chat.json does not exist")


if __name__ == "__main__":
    test_scenarios()
    check_log_files()
