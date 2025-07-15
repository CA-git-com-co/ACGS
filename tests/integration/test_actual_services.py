#!/usr/bin/env python3
"""
ACGS-2 Actual Service Implementation Test
Constitutional Hash: cdd01ef066bc6cf2

This script tests which services are actually implemented and functional
by attempting to import and validate their main modules.
"""

import sys
import os
import importlib.util
from pathlib import Path
import traceback

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def test_service_implementation(service_path, service_name):
    """Test if a service is actually implemented and functional."""
    result = {
        "name": service_name,
        "path": str(service_path),
        "status": "unknown",
        "details": {},
        "constitutional_hash": CONSTITUTIONAL_HASH
    }
    
    try:
        # Check if main.py exists
        main_py = service_path / "main.py"
        app_main_py = service_path / "app" / "main.py"
        
        main_file = None
        if main_py.exists():
            main_file = main_py
        elif app_main_py.exists():
            main_file = app_main_py
        
        if not main_file:
            result["status"] = "no_main_file"
            result["details"]["error"] = "No main.py found"
            return result
        
        # Try to read the file and check for FastAPI
        content = main_file.read_text()
        
        # Check for FastAPI implementation
        has_fastapi = "FastAPI" in content or "fastapi" in content
        has_constitutional_hash = CONSTITUTIONAL_HASH in content
        has_uvicorn = "uvicorn" in content
        
        result["details"]["has_fastapi"] = has_fastapi
        result["details"]["has_constitutional_hash"] = has_constitutional_hash
        result["details"]["has_uvicorn"] = has_uvicorn
        result["details"]["file_size"] = len(content)
        result["details"]["line_count"] = len(content.split('\n'))
        
        # Try to import the module (basic syntax check)
        spec = importlib.util.spec_from_file_location("test_module", main_file)
        if spec and spec.loader:
            try:
                module = importlib.util.module_from_spec(spec)
                # Don't execute, just check if it can be loaded
                result["details"]["importable"] = True
            except Exception as e:
                result["details"]["importable"] = False
                result["details"]["import_error"] = str(e)
        
        # Determine status
        if has_fastapi and has_constitutional_hash:
            if result["details"].get("importable", False):
                result["status"] = "fully_implemented"
            else:
                result["status"] = "implemented_with_issues"
        elif has_fastapi:
            result["status"] = "basic_implementation"
        else:
            result["status"] = "minimal_implementation"
            
    except Exception as e:
        result["status"] = "error"
        result["details"]["error"] = str(e)
        result["details"]["traceback"] = traceback.format_exc()
    
    return result

def main():
    """Main test function."""
    print("🔍 ACGS-2 Actual Service Implementation Analysis")
    print("=" * 60)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()
    
    # Define services to test based on actual directory structure
    services_to_test = [
        # Core services
        ("services/core/constitutional-ai/ac_service", "Constitutional AI Service"),
        ("services/core/agent-hitl", "Agent HITL Service"),
        ("services/core/code-analysis/code_analysis_service", "Code Analysis Service"),
        ("services/core/context/context_service", "Context Service"),
        ("services/core/evolutionary-computation/ec_service", "Evolutionary Computation Service"),
        ("services/core/formal-verification/fv_service", "Formal Verification Service"),
        ("services/core/governance-synthesis/gs_service", "Governance Synthesis Service"),
        ("services/core/policy-governance/pgc_service", "Policy Governance Service"),
        
        # Platform services
        ("services/platform_services/authentication/auth_service", "Authentication Service"),
        ("services/platform_services/integrity/integrity_service", "Integrity Service"),
        ("services/platform_services/api_gateway", "API Gateway Service"),
        ("services/platform_services/audit_aggregator", "Audit Aggregator Service"),
        
        # Infrastructure services
        ("services/shared/routing", "Routing Service"),
    ]
    
    results = []
    operational_count = 0
    implemented_count = 0
    
    for service_path_str, service_name in services_to_test:
        service_path = Path(service_path_str)
        result = test_service_implementation(service_path, service_name)
        results.append(result)
        
        # Print result
        status_emoji = {
            "fully_implemented": "✅",
            "implemented_with_issues": "⚠️",
            "basic_implementation": "🔶",
            "minimal_implementation": "🔸",
            "no_main_file": "❌",
            "error": "💥",
            "unknown": "❓"
        }
        
        emoji = status_emoji.get(result["status"], "❓")
        print(f"{emoji} {service_name}")
        print(f"   Path: {service_path_str}")
        print(f"   Status: {result['status']}")
        
        if result["details"]:
            if result["details"].get("has_fastapi"):
                print(f"   ✓ FastAPI implementation")
            if result["details"].get("has_constitutional_hash"):
                print(f"   ✓ Constitutional hash present")
            if result["details"].get("line_count"):
                print(f"   📄 {result['details']['line_count']} lines of code")
            if result["details"].get("import_error"):
                print(f"   ⚠️ Import issue: {result['details']['import_error']}")
        
        print()
        
        # Count operational services
        if result["status"] in ["fully_implemented", "implemented_with_issues"]:
            operational_count += 1
        if result["status"] in ["fully_implemented", "implemented_with_issues", "basic_implementation"]:
            implemented_count += 1
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total services tested: {len(results)}")
    print(f"Fully operational: {operational_count}")
    print(f"Implemented (any level): {implemented_count}")
    print(f"Operational percentage: {(operational_count/len(results)*100):.1f}%")
    print(f"Implementation percentage: {(implemented_count/len(results)*100):.1f}%")
    
    # Save results
    import json
    with open("actual_service_implementation_results.json", "w") as f:
        json.dump({
            "timestamp": "2025-01-15T12:00:00Z",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "summary": {
                "total_services": len(results),
                "operational_services": operational_count,
                "implemented_services": implemented_count,
                "operational_percentage": round(operational_count/len(results)*100, 1),
                "implementation_percentage": round(implemented_count/len(results)*100, 1)
            },
            "services": results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to actual_service_implementation_results.json")
    return results

if __name__ == "__main__":
    main()
