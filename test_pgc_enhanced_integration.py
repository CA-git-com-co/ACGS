#!/usr/bin/env python3
"""
PGC Service Enhanced Constitutional Analyzer Integration Test

This test validates the integration between the PGC service and the Enhanced
Constitutional Analyzer with Qwen3 embedding support.
"""

import asyncio
import json
import logging
import time
import sys
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent / "services" / "shared"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_pgc_enhanced_integration():
    """Test PGC service integration with Enhanced Constitutional Analyzer."""

    logger.info("🚀 Starting PGC Enhanced Constitutional Analyzer Integration Test")
    logger.info("=" * 70)

    # Reset metrics to avoid collision
    try:
        from constitutional_metrics import reset_constitutional_metrics
        reset_constitutional_metrics()
        logger.info("✅ Metrics registry reset successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to reset metrics registry: {e}")
    
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_details": []
    }
    
    # Test 1: Basic Enhanced Constitutional Analyzer availability
    logger.info("🧪 Test 1: Enhanced Constitutional Analyzer availability")
    test_results["total_tests"] += 1
    
    try:
        from enhanced_constitutional_analyzer import (
            get_enhanced_constitutional_analyzer,
            integrate_with_pgc_service,
            AnalysisType
        )
        
        analyzer = await get_enhanced_constitutional_analyzer()
        health = await analyzer.health_check()
        
        if health["status"] in ["healthy", "degraded"]:
            logger.info("✅ Enhanced Constitutional Analyzer is available")
            test_results["passed_tests"] += 1
            test_results["test_details"].append({
                "test": "analyzer_availability",
                "status": "PASS",
                "message": f"Analyzer status: {health['status']}"
            })
        else:
            logger.warning("⚠️ Enhanced Constitutional Analyzer is unhealthy")
            test_results["failed_tests"] += 1
            test_results["test_details"].append({
                "test": "analyzer_availability", 
                "status": "FAIL",
                "message": f"Analyzer status: {health['status']}"
            })
            
    except ImportError as e:
        logger.warning(f"⚠️ Enhanced Constitutional Analyzer not available: {e}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append({
            "test": "analyzer_availability",
            "status": "FAIL", 
            "message": f"Import error: {e}"
        })
    except Exception as e:
        logger.error(f"❌ Error testing analyzer availability: {e}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append({
            "test": "analyzer_availability",
            "status": "FAIL",
            "message": f"Error: {e}"
        })
    
    # Test 2: PGC Service Integration Function
    logger.info("🧪 Test 2: PGC Service Integration Function")
    test_results["total_tests"] += 1
    
    try:
        # Test the PGC integration function
        start_time = time.time()
        
        result = await integrate_with_pgc_service(
            policy_id="TEST-PGC-001",
            policy_content="Test policy for constitutional compliance validation",
            enforcement_context={"risk_level": "medium", "test_mode": True}
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        # Validate result structure
        required_fields = [
            "policy_id", "enforcement_action", "compliance_score",
            "confidence_score", "constitutional_hash", "processing_time_ms"
        ]
        
        if all(field in result for field in required_fields):
            logger.info(f"✅ PGC integration successful: {result['enforcement_action']} ({processing_time:.1f}ms)")
            test_results["passed_tests"] += 1
            test_results["test_details"].append({
                "test": "pgc_integration_function",
                "status": "PASS",
                "message": f"Integration successful: {result['enforcement_action']} in {processing_time:.1f}ms"
            })
        else:
            missing_fields = [f for f in required_fields if f not in result]
            logger.error(f"❌ PGC integration missing fields: {missing_fields}")
            test_results["failed_tests"] += 1
            test_results["test_details"].append({
                "test": "pgc_integration_function",
                "status": "FAIL",
                "message": f"Missing fields: {missing_fields}"
            })
            
    except Exception as e:
        logger.error(f"❌ Error testing PGC integration: {e}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append({
            "test": "pgc_integration_function",
            "status": "FAIL",
            "message": f"Error: {e}"
        })
    
    # Test 3: Multi-Model Manager Integration
    logger.info("🧪 Test 3: Multi-Model Manager Integration")
    test_results["total_tests"] += 1
    
    try:
        from multi_model_manager import get_multi_model_manager, ConsensusStrategy
        
        multi_model_manager = await get_multi_model_manager()
        health = await multi_model_manager.health_check()
        
        if health["status"] in ["healthy", "degraded"]:
            logger.info(f"✅ Multi-Model Manager is available: {health['status']}")
            test_results["passed_tests"] += 1
            test_results["test_details"].append({
                "test": "multi_model_manager",
                "status": "PASS",
                "message": f"Manager status: {health['status']}"
            })
        else:
            logger.warning(f"⚠️ Multi-Model Manager is unhealthy: {health['status']}")
            test_results["failed_tests"] += 1
            test_results["test_details"].append({
                "test": "multi_model_manager",
                "status": "FAIL",
                "message": f"Manager status: {health['status']}"
            })
            
    except Exception as e:
        logger.error(f"❌ Error testing Multi-Model Manager: {e}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append({
            "test": "multi_model_manager",
            "status": "FAIL",
            "message": f"Error: {e}"
        })
    
    # Test 4: Performance Validation
    logger.info("🧪 Test 4: Performance Validation")
    test_results["total_tests"] += 1
    
    try:
        # Test multiple operations for performance
        response_times = []
        
        for i in range(5):
            start_time = time.time()
            
            result = await integrate_with_pgc_service(
                policy_id=f"PERF-TEST-{i:03d}",
                policy_content=f"Performance test policy {i} for constitutional compliance validation",
                enforcement_context={"test_iteration": i}
            )
            
            response_time = (time.time() - start_time) * 1000
            response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        target_met_count = sum(1 for rt in response_times if rt < 500)  # <500ms target
        
        if avg_response_time < 500 and target_met_count >= 4:  # 80% should meet target
            logger.info(f"✅ Performance validation passed: {avg_response_time:.1f}ms avg, {target_met_count}/5 meet target")
            test_results["passed_tests"] += 1
            test_results["test_details"].append({
                "test": "performance_validation",
                "status": "PASS",
                "message": f"Performance: {avg_response_time:.1f}ms avg, {target_met_count}/5 meet target"
            })
        else:
            logger.warning(f"⚠️ Performance validation failed: {avg_response_time:.1f}ms avg, {target_met_count}/5 meet target")
            test_results["failed_tests"] += 1
            test_results["test_details"].append({
                "test": "performance_validation",
                "status": "FAIL",
                "message": f"Performance: {avg_response_time:.1f}ms avg, {target_met_count}/5 meet target"
            })
            
    except Exception as e:
        logger.error(f"❌ Error in performance validation: {e}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append({
            "test": "performance_validation",
            "status": "FAIL",
            "message": f"Error: {e}"
        })
    
    # Generate final report
    success_rate = (test_results["passed_tests"] / test_results["total_tests"]) * 100
    
    logger.info("=" * 70)
    logger.info("🏁 PGC Enhanced Constitutional Analyzer Integration Test Complete")
    logger.info(f"📊 Results: {test_results['passed_tests']}/{test_results['total_tests']} tests passed ({success_rate:.1f}%)")
    logger.info(f"🎯 Overall Status: {'PASS' if success_rate >= 75 else 'FAIL'}")
    logger.info("=" * 70)
    
    # Save detailed report
    report = {
        "test_suite": "PGC Enhanced Constitutional Analyzer Integration Test",
        "timestamp": time.time(),
        "test_summary": test_results,
        "success_rate_percentage": success_rate,
        "overall_status": "PASS" if success_rate >= 75 else "FAIL",
        "constitution_hash": "cdd01ef066bc6cf2",
        "recommendations": [
            "✅ Integration tests completed" if success_rate >= 75 else "🚨 Fix integration issues before deployment",
            "🔧 Monitor performance in production environment",
            "📊 Validate constitutional compliance accuracy >95%"
        ]
    }
    
    report_filename = f"pgc_enhanced_integration_test_report_{int(time.time())}.json"
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"📄 Test report saved to: {report_filename}")
    
    return 0 if success_rate >= 75 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_pgc_enhanced_integration())
    sys.exit(exit_code)
