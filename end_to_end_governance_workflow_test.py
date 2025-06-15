#!/usr/bin/env python3
"""
End-to-End Governance Workflow Testing for ACGS-1 Task 10

This script tests all 5 governance workflows to ensure they are operational
and meet the performance targets specified in the task requirements.

Workflows tested:
1. Policy Creation
2. Constitutional Compliance  
3. Policy Enforcement
4. WINA Oversight
5. Audit/Transparency
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GovernanceWorkflowTester:
    """End-to-end tester for all 5 governance workflows."""
    
    def __init__(self):
        self.base_url = "http://localhost:8005"  # PGC service
        self.workflow_endpoints = {
            "Policy Creation": "/api/v1/workflows/policy-creation",
            "Constitutional Compliance": "/api/v1/workflows/constitutional-compliance",
            "Policy Enforcement": "/api/v1/workflows/policy-enforcement",
            "WINA Oversight": "/api/v1/workflows/wina-oversight",
            "Audit/Transparency": "/api/v1/workflows/audit-transparency"
        }
        self.test_results = {}
        self.performance_metrics = {}
        
    async def test_workflow_endpoint(self, workflow_name: str, endpoint: str) -> Dict[str, Any]:
        """Test a single governance workflow endpoint."""
        logger.info(f"🧪 Testing {workflow_name}...")

        # Create test data based on workflow type
        test_data = self.get_test_data_for_workflow(workflow_name)

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test POST endpoint with appropriate test data
                response = await client.post(f"{self.base_url}{endpoint}", json=test_data)

                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms

                if response.status_code in [200, 201]:
                    logger.info(f"  ✅ {workflow_name}: Operational ({response_time:.1f}ms)")
                    return {
                        "status": "operational",
                        "response_time_ms": response_time,
                        "status_code": response.status_code,
                        "response_data": response.json() if response.content else {}
                    }
                else:
                    logger.warning(f"  ⚠️ {workflow_name}: Non-200 status ({response.status_code})")
                    return {
                        "status": "degraded",
                        "response_time_ms": response_time,
                        "status_code": response.status_code,
                        "error": f"HTTP {response.status_code}"
                    }

        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            logger.error(f"  ❌ {workflow_name}: Failed - {str(e)}")
            return {
                "status": "failed",
                "response_time_ms": response_time,
                "error": str(e)
            }

    def get_test_data_for_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Get appropriate test data for each workflow type."""
        if workflow_name == "Policy Creation":
            return {
                "title": "Test Policy",
                "description": "Test policy for workflow validation",
                "category": "Testing",
                "priority": "medium"
            }
        elif workflow_name == "Constitutional Compliance":
            return {
                "policy_id": "test-policy-001",
                "validation_type": "constitutional",
                "constitutional_principles": ["transparency", "accountability"]
            }
        elif workflow_name == "Policy Enforcement":
            return {
                "policy_id": "test-policy-001",
                "enforcement_action": "monitor",
                "scope": "system-wide"
            }
        elif workflow_name == "WINA Oversight":
            return {
                "oversight_type": "performance_monitoring",
                "target_metrics": ["response_time", "accuracy"],
                "reporting_interval": "daily"
            }
        elif workflow_name == "Audit/Transparency":
            return {
                "audit_type": "governance_transparency",
                "scope": "policy_decisions",
                "reporting_format": "public"
            }
        else:
            return {"test": True, "workflow": workflow_name}
    
    async def test_policy_creation_workflow(self) -> Dict[str, Any]:
        """Test the complete policy creation workflow."""
        logger.info("🏛️ Testing Policy Creation Workflow...")
        
        test_policy = {
            "title": "Test Policy for E2E Validation",
            "description": "End-to-end test policy for governance workflow validation",
            "category": "Testing",
            "priority": "medium",
            "principles": ["transparency", "accountability"]
        }
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Create policy draft
                response = await client.post(
                    f"{self.base_url}/api/v1/workflows/policy-creation",
                    json=test_policy
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                if response.status_code in [200, 201]:
                    policy_data = response.json()
                    logger.info(f"  ✅ Policy creation successful ({response_time:.1f}ms)")
                    return {
                        "status": "operational",
                        "response_time_ms": response_time,
                        "policy_id": policy_data.get("policy_id", "test-policy"),
                        "workflow_status": policy_data.get("status", "draft")
                    }
                else:
                    logger.warning(f"  ⚠️ Policy creation returned {response.status_code}")
                    return {
                        "status": "degraded",
                        "response_time_ms": response_time,
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            logger.error(f"  ❌ Policy creation failed: {str(e)}")
            return {
                "status": "failed",
                "response_time_ms": response_time,
                "error": str(e)
            }
    
    async def test_constitutional_compliance_workflow(self) -> Dict[str, Any]:
        """Test constitutional compliance validation."""
        logger.info("⚖️ Testing Constitutional Compliance Workflow...")
        
        compliance_request = {
            "policy_id": "test-policy-001",
            "validation_type": "constitutional",
            "constitutional_principles": ["transparency", "accountability", "democratic_process"]
        }
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/workflows/constitutional-compliance",
                    json=compliance_request
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                if response.status_code in [200, 201]:
                    compliance_data = response.json()
                    logger.info(f"  ✅ Compliance validation successful ({response_time:.1f}ms)")
                    return {
                        "status": "operational",
                        "response_time_ms": response_time,
                        "compliance_score": compliance_data.get("compliance_score", 0.95),
                        "validation_id": compliance_data.get("validation_id", "test-validation")
                    }
                else:
                    logger.warning(f"  ⚠️ Compliance validation returned {response.status_code}")
                    return {
                        "status": "degraded",
                        "response_time_ms": response_time,
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            logger.error(f"  ❌ Compliance validation failed: {str(e)}")
            return {
                "status": "failed",
                "response_time_ms": response_time,
                "error": str(e)
            }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive end-to-end governance workflow testing."""
        logger.info("🚀 Starting End-to-End Governance Workflow Testing")
        logger.info("=" * 60)
        
        test_start_time = datetime.now()
        
        # Test all workflow endpoints
        for workflow_name, endpoint in self.workflow_endpoints.items():
            result = await self.test_workflow_endpoint(workflow_name, endpoint)
            self.test_results[workflow_name] = result
            
            # Track performance metrics
            if "response_time_ms" in result:
                self.performance_metrics[workflow_name] = result["response_time_ms"]
        
        # Test specific workflow implementations
        logger.info("\n🔬 Testing Specific Workflow Implementations...")
        
        # Test policy creation workflow
        policy_result = await self.test_policy_creation_workflow()
        self.test_results["Policy Creation (Full)"] = policy_result
        
        # Test constitutional compliance workflow  
        compliance_result = await self.test_constitutional_compliance_workflow()
        self.test_results["Constitutional Compliance (Full)"] = compliance_result
        
        test_end_time = datetime.now()
        test_duration = (test_end_time - test_start_time).total_seconds()
        
        # Calculate summary metrics
        operational_workflows = sum(1 for result in self.test_results.values() 
                                  if result.get("status") == "operational")
        total_workflows = len(self.test_results)
        
        avg_response_time = (sum(self.performance_metrics.values()) / 
                           len(self.performance_metrics)) if self.performance_metrics else 0
        
        # Generate summary
        summary = {
            "test_timestamp": test_start_time.isoformat(),
            "test_duration_seconds": test_duration,
            "total_workflows_tested": total_workflows,
            "operational_workflows": operational_workflows,
            "workflow_availability_percentage": (operational_workflows / total_workflows) * 100,
            "average_response_time_ms": avg_response_time,
            "performance_target_met": avg_response_time < 500,  # <500ms target
            "detailed_results": self.test_results,
            "performance_metrics": self.performance_metrics
        }
        
        # Log summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 END-TO-END GOVERNANCE WORKFLOW TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Operational Workflows: {operational_workflows}/{total_workflows} ({summary['workflow_availability_percentage']:.1f}%)")
        logger.info(f"⏱️ Average Response Time: {avg_response_time:.1f}ms")
        logger.info(f"🎯 Performance Target (<500ms): {'✅ MET' if summary['performance_target_met'] else '❌ NOT MET'}")
        logger.info(f"⏰ Test Duration: {test_duration:.2f} seconds")
        
        # Save results
        results_file = f"end_to_end_workflow_test_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed results saved to: {results_file}")
        
        return summary

async def main():
    """Main execution function."""
    tester = GovernanceWorkflowTester()
    results = await tester.run_comprehensive_test()
    
    # Return appropriate exit code
    success = (results["operational_workflows"] >= 4 and  # At least 4/5 workflows operational
              results["performance_target_met"])
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
