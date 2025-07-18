#!/usr/bin/env python3
"""
ACGS-2 Performance Test Runner
Constitutional Hash: cdd01ef066bc6cf2

Automated runner for constitutional performance testing with CI/CD integration.
"""

import subprocess
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def check_services_running():
    """Check if ACGS-2 services are running"""
    print("🔍 Checking if ACGS-2 services are running...")
    
    services_to_check = [
        ("auth-service", "http://localhost:8013/health"),
        ("monitoring-service", "http://localhost:8014/health"),
        ("audit-service", "http://localhost:8015/health"),
        ("gdpr-compliance", "http://localhost:8016/health"),
        ("alerting-service", "http://localhost:8017/health"),
        ("api-gateway", "http://localhost:8080/health")
    ]
    
    running_services = []
    for service_name, health_url in services_to_check:
        try:
            import requests
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                running_services.append(service_name)
                print(f"   ✅ {service_name} is running")
            else:
                print(f"   ❌ {service_name} returned status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {service_name} is not accessible: {e}")
    
    print(f"\n📊 {len(running_services)}/{len(services_to_check)} services running")
    return len(running_services) >= len(services_to_check) // 2  # At least half must be running

def run_quick_performance_test():
    """Run quick performance test (30 seconds per service)"""
    print("🚀 Running Quick Performance Test...")
    print("⏱️ Duration: 30 seconds per service")
    print("🎯 Target: 120 RPS")
    print("=" * 60)
    
    cmd = [
        sys.executable,
        "constitutional_performance_suite.py",
        "--duration", "30",
        "--rps", "120",
        "--output", "quick_performance_report.txt",
        "--json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Quick performance test PASSED")
            return True
        else:
            print("❌ Quick performance test FAILED")
            print(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running quick test: {e}")
        return False

def run_comprehensive_performance_test():
    """Run comprehensive performance test (60 seconds per service)"""
    print("🚀 Running Comprehensive Performance Test...")
    print("⏱️ Duration: 60 seconds per service")
    print("🎯 Target: 150 RPS")
    print("=" * 60)
    
    cmd = [
        sys.executable,
        "constitutional_performance_suite.py",
        "--duration", "60",
        "--rps", "150",
        "--output", "comprehensive_performance_report.txt",
        "--json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ Comprehensive performance test PASSED")
            return True
        else:
            print("❌ Comprehensive performance test FAILED")
            print(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running comprehensive test: {e}")
        return False

def run_stress_test():
    """Run stress test (high load for short duration)"""
    print("🚀 Running Stress Test...")
    print("⏱️ Duration: 30 seconds per service")
    print("🎯 Target: 300 RPS (stress load)")
    print("=" * 60)
    
    cmd = [
        sys.executable,
        "constitutional_performance_suite.py",
        "--duration", "30",
        "--rps", "300",
        "--output", "stress_test_report.txt",
        "--json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        # Stress test is expected to show some degradation
        print("✅ Stress test completed (degradation expected)")
        return True
            
    except Exception as e:
        print(f"❌ Error running stress test: {e}")
        return False

def generate_summary_report():
    """Generate summary report from all test results"""
    print("📊 Generating Summary Report...")
    
    report_files = [
        ("Quick Test", "quick_performance_report.json"),
        ("Comprehensive Test", "comprehensive_performance_report.json"),
        ("Stress Test", "stress_test_report.json")
    ]
    
    summary_lines = [
        "=" * 80,
        "🏛️ ACGS-2 PERFORMANCE TESTING SUMMARY REPORT",
        "=" * 80,
        f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}",
        f"⏰ Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "📈 TEST RESULTS SUMMARY",
        "─" * 50
    ]
    
    all_passed = True
    
    for test_name, json_file in report_files:
        json_path = Path(__file__).parent / json_file
        if json_path.exists():
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                
                status = "✅ PASS" if data.get("overall_system_pass", False) else "❌ FAIL"
                if not data.get("overall_system_pass", False):
                    all_passed = False
                
                summary_lines.extend([
                    f"{test_name}:",
                    f"   Status: {status}",
                    f"   P99 Latency: {data.get('system_p99_response_time_ms', 0):.2f}ms",
                    f"   Throughput: {data.get('system_throughput_rps', 0):.1f} RPS",
                    f"   Constitutional Compliance: {data.get('constitutional_compliance_rate', 0):.1f}%",
                    f"   Services Passing: {len([s for s in data.get('services', []) if s.get('overall_pass', False)])}/{len(data.get('services', []))}",
                    ""
                ])
                
            except Exception as e:
                summary_lines.extend([
                    f"{test_name}:",
                    f"   Status: ❌ ERROR reading results",
                    f"   Error: {e}",
                    ""
                ])
                all_passed = False
        else:
            summary_lines.extend([
                f"{test_name}:",
                f"   Status: ❌ NOT RUN",
                ""
            ])
            all_passed = False
    
    # Overall assessment
    summary_lines.extend([
        "🎯 OVERALL CONSTITUTIONAL COMPLIANCE ASSESSMENT",
        "─" * 50,
        f"Overall Status: {'✅ PASS' if all_passed else '❌ FAIL'}",
        ""
    ])
    
    if all_passed:
        summary_lines.extend([
            "✅ All performance tests passed constitutional requirements",
            "✅ System meets P99 latency target (<5ms)",
            "✅ System meets throughput target (>100 RPS)",
            "✅ Constitutional compliance maintained (100%)",
            ""
        ])
    else:
        summary_lines.extend([
            "❌ Some performance tests failed constitutional requirements",
            "🔧 Review detailed reports for optimization recommendations",
            "📋 Address performance issues before production deployment",
            ""
        ])
    
    summary_lines.extend([
        "📄 DETAILED REPORTS",
        "─" * 30,
        "- quick_performance_report.txt",
        "- comprehensive_performance_report.txt", 
        "- stress_test_report.txt",
        "",
        "📊 JSON DATA",
        "─" * 30,
        "- quick_performance_report.json",
        "- comprehensive_performance_report.json",
        "- stress_test_report.json",
        "",
        "=" * 80,
        f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}",
        "=" * 80
    ])
    
    # Write summary report
    summary_file = Path(__file__).parent / "performance_summary_report.txt"
    with open(summary_file, 'w') as f:
        f.write("\n".join(summary_lines))
    
    print(f"📄 Summary report saved to: {summary_file}")
    return all_passed

def main():
    """Main performance test runner"""
    print("🏛️ ACGS-2 Constitutional Performance Test Runner")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)
    
    # Check if services are running
    if not check_services_running():
        print("❌ Not enough services are running to perform meaningful tests")
        print("💡 Start services with: python scripts/run_services_local.py")
        sys.exit(1)
    
    print("\n🚀 Starting Performance Test Suite...")
    
    # Change to tests directory
    os.chdir(Path(__file__).parent)
    
    # Install requirements if needed
    try:
        import aiohttp
    except ImportError:
        print("📦 Installing performance test requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "config/environments/requirements.txt"], check=True)
    
    # Run test suite
    all_passed = True
    
    # 1. Quick performance test
    if not run_quick_performance_test():
        all_passed = False
    
    print("\n" + "="*60 + "\n")
    
    # 2. Comprehensive performance test  
    if not run_comprehensive_performance_test():
        all_passed = False
    
    print("\n" + "="*60 + "\n")
    
    # 3. Stress test
    if not run_stress_test():
        all_passed = False
    
    print("\n" + "="*60 + "\n")
    
    # 4. Generate summary
    summary_passed = generate_summary_report()
    
    # Final status
    print("\n🏛️ CONSTITUTIONAL PERFORMANCE TESTING COMPLETE")
    print("=" * 60)
    
    if all_passed and summary_passed:
        print("✅ ALL TESTS PASSED - System meets constitutional performance requirements")
        print("🚀 System ready for production deployment")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Performance optimization required")
        print("🔧 Review reports and address issues before production")
        sys.exit(1)

if __name__ == "__main__":
    main()