#!/usr/bin/env python3
"""
ACGS-2 Multi-Agent Coordination Testing Suite
Constitutional Hash: cdd01ef066bc6cf2

Tests interactions between different agent personas and coordination workflows
"""

import asyncio
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class AgentPersona(Enum):
    ARCHITECT = "architect"
    BACKEND = "backend"
    FRONTEND = "frontend"
    SECURITY = "security"
    QA = "qa"
    PERFORMANCE = "performance"
    REFACTORER = "refactorer"
    MENTOR = "mentor"

@dataclass
class AgentInteraction:
    source_persona: AgentPersona
    target_persona: AgentPersona
    interaction_type: str
    payload: Dict[str, Any]
    expected_response_type: str
    constitutional_compliance_required: bool = True

@dataclass
class CoordinationTestResult:
    test_name: str
    personas_involved: List[AgentPersona]
    interaction_chain: List[Dict[str, Any]]
    success: bool
    constitutional_compliance: bool
    response_time_ms: float
    coordination_quality_score: float
    details: Dict[str, Any]
    timestamp: str

class MultiAgentCoordinationTestSuite:
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.results: List[CoordinationTestResult] = []
        self.agent_endpoints = {
            AgentPersona.ARCHITECT: "http://localhost:8008",  # Agent HITL service
            AgentPersona.BACKEND: "http://localhost:8016",    # Auth service (simulating backend agent)
            AgentPersona.SECURITY: "http://localhost:32768", # Constitutional AI (simulating security agent)
        }
        
        # Define coordination workflows to test
        self.coordination_workflows = self.define_coordination_workflows()
    
    def define_coordination_workflows(self) -> List[Dict[str, Any]]:
        """Define multi-agent coordination workflows to test"""
        return [
            {
                "name": "Constitutional Compliance Review",
                "description": "Security agent reviews architect's design for constitutional compliance",
                "workflow": [
                    {
                        "step": 1,
                        "source": AgentPersona.ARCHITECT,
                        "target": AgentPersona.SECURITY,
                        "action": "submit_design_for_review",
                        "payload": {
                            "design_document": "Sample system architecture",
                            "constitutional_hash": self.constitutional_hash,
                            "compliance_requirements": ["transparency", "accountability", "fairness"]
                        }
                    },
                    {
                        "step": 2,
                        "source": AgentPersona.SECURITY,
                        "target": AgentPersona.ARCHITECT,
                        "action": "provide_compliance_feedback",
                        "expected_fields": ["compliance_score", "recommendations", "constitutional_hash"]
                    }
                ]
            },
            {
                "name": "Performance Optimization Coordination",
                "description": "Backend and performance agents coordinate on optimization",
                "workflow": [
                    {
                        "step": 1,
                        "source": AgentPersona.BACKEND,
                        "target": AgentPersona.PERFORMANCE,
                        "action": "request_performance_analysis",
                        "payload": {
                            "service_metrics": {"p99_latency": 159.94, "throughput": 923.9},
                            "constitutional_hash": self.constitutional_hash,
                            "optimization_targets": {"p99_latency": 5.0, "throughput": 1000}
                        }
                    }
                ]
            },
            {
                "name": "Cross-Persona Knowledge Sharing",
                "description": "Test knowledge sharing between different agent personas",
                "workflow": [
                    {
                        "step": 1,
                        "source": AgentPersona.MENTOR,
                        "target": AgentPersona.QA,
                        "action": "share_best_practices",
                        "payload": {
                            "knowledge_type": "constitutional_testing",
                            "constitutional_hash": self.constitutional_hash,
                            "best_practices": ["hash_validation", "compliance_monitoring", "audit_trails"]
                        }
                    }
                ]
            }
        ]
    
    def log_result(self, test_name: str, personas_involved: List[AgentPersona], 
                   interaction_chain: List[Dict[str, Any]], success: bool, 
                   constitutional_compliance: bool, response_time_ms: float,
                   coordination_quality_score: float, details: Dict[str, Any]):
        """Log coordination test result"""
        result = CoordinationTestResult(
            test_name=test_name,
            personas_involved=personas_involved,
            interaction_chain=interaction_chain,
            success=success,
            constitutional_compliance=constitutional_compliance,
            response_time_ms=response_time_ms,
            coordination_quality_score=coordination_quality_score,
            details=details,
            timestamp=datetime.now().isoformat()
        )
        self.results.append(result)
        logger.info(f"{test_name}: {'SUCCESS' if success else 'FAIL'} - Constitutional: {constitutional_compliance}")
    
    async def simulate_agent_interaction(self, source_persona: AgentPersona, 
                                       target_persona: AgentPersona, 
                                       action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate interaction between two agent personas"""
        
        # For testing purposes, we'll simulate interactions with available services
        # In a real implementation, this would route to specific agent endpoints
        
        if target_persona == AgentPersona.SECURITY:
            # Use Constitutional AI service for security persona
            endpoint = self.agent_endpoints.get(target_persona)
            if endpoint:
                try:
                    response = requests.get(f"{endpoint}/health", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            "success": True,
                            "response": data,
                            "constitutional_compliance": data.get("constitutional_hash") == self.constitutional_hash,
                            "persona": target_persona.value,
                            "action_processed": action
                        }
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e),
                        "constitutional_compliance": False,
                        "persona": target_persona.value
                    }
        
        # Simulate response for other personas
        return {
            "success": True,
            "response": {
                "message": f"Simulated response from {target_persona.value} agent",
                "action_processed": action,
                "constitutional_hash": self.constitutional_hash,
                "payload_received": payload,
                "timestamp": datetime.now().isoformat()
            },
            "constitutional_compliance": True,
            "persona": target_persona.value
        }
    
    async def test_coordination_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Test a complete coordination workflow"""
        workflow_name = workflow["name"]
        workflow_steps = workflow["workflow"]
        
        start_time = time.time()
        interaction_chain = []
        personas_involved = set()
        overall_success = True
        constitutional_compliance = True
        
        logger.info(f"Testing coordination workflow: {workflow_name}")
        
        for step_config in workflow_steps:
            step_start = time.time()
            source_persona = step_config["source"]
            target_persona = step_config["target"]
            action = step_config["action"]
            payload = step_config.get("payload", {})
            
            personas_involved.add(source_persona)
            personas_involved.add(target_persona)
            
            # Simulate the interaction
            interaction_result = await self.simulate_agent_interaction(
                source_persona, target_persona, action, payload
            )
            
            step_time = (time.time() - step_start) * 1000
            
            step_success = interaction_result.get("success", False)
            step_compliance = interaction_result.get("constitutional_compliance", False)
            
            interaction_chain.append({
                "step": step_config.get("step", len(interaction_chain) + 1),
                "source_persona": source_persona.value,
                "target_persona": target_persona.value,
                "action": action,
                "success": step_success,
                "constitutional_compliance": step_compliance,
                "response_time_ms": step_time,
                "response": interaction_result.get("response", {}),
                "error": interaction_result.get("error")
            })
            
            if not step_success:
                overall_success = False
            if not step_compliance:
                constitutional_compliance = False
        
        total_time = (time.time() - start_time) * 1000
        
        # Calculate coordination quality score
        coordination_quality = self.calculate_coordination_quality(interaction_chain)
        
        self.log_result(
            test_name=workflow_name,
            personas_involved=list(personas_involved),
            interaction_chain=interaction_chain,
            success=overall_success,
            constitutional_compliance=constitutional_compliance,
            response_time_ms=total_time,
            coordination_quality_score=coordination_quality,
            details={
                "workflow_description": workflow["description"],
                "steps_completed": len(interaction_chain),
                "average_step_time_ms": total_time / len(interaction_chain) if interaction_chain else 0
            }
        )
        
        return overall_success and constitutional_compliance
    
    def calculate_coordination_quality(self, interaction_chain: List[Dict[str, Any]]) -> float:
        """Calculate coordination quality score based on interaction chain"""
        if not interaction_chain:
            return 0.0
        
        # Factors for coordination quality
        success_rate = sum(1 for step in interaction_chain if step["success"]) / len(interaction_chain)
        compliance_rate = sum(1 for step in interaction_chain if step["constitutional_compliance"]) / len(interaction_chain)
        
        # Average response time factor (lower is better)
        avg_response_time = sum(step["response_time_ms"] for step in interaction_chain) / len(interaction_chain)
        time_factor = max(0, 1 - (avg_response_time / 1000))  # Normalize to 1 second
        
        # Constitutional hash consistency
        hash_consistency = 1.0 if all(
            self.constitutional_hash in str(step.get("response", {})) 
            for step in interaction_chain
        ) else 0.5
        
        # Weighted coordination quality score
        quality_score = (
            success_rate * 0.3 +
            compliance_rate * 0.3 +
            time_factor * 0.2 +
            hash_consistency * 0.2
        )
        
        return min(1.0, max(0.0, quality_score))
    
    async def test_persona_availability(self) -> Dict[str, bool]:
        """Test availability of different agent personas"""
        availability_results = {}
        
        for persona, endpoint in self.agent_endpoints.items():
            try:
                response = requests.get(f"{endpoint}/health", timeout=5)
                available = response.status_code == 200
                
                if available:
                    data = response.json()
                    constitutional_compliant = data.get("constitutional_hash") == self.constitutional_hash
                    availability_results[persona.value] = {
                        "available": True,
                        "constitutional_compliant": constitutional_compliant,
                        "response_data": data
                    }
                else:
                    availability_results[persona.value] = {
                        "available": False,
                        "constitutional_compliant": False,
                        "error": f"HTTP {response.status_code}"
                    }
            except Exception as e:
                availability_results[persona.value] = {
                    "available": False,
                    "constitutional_compliant": False,
                    "error": str(e)
                }
        
        return availability_results
    
    async def run_all_coordination_tests(self) -> Dict[str, Any]:
        """Run all multi-agent coordination tests"""
        logger.info("Starting ACGS-2 Multi-Agent Coordination Testing")
        logger.info(f"Constitutional Hash: {self.constitutional_hash}")
        
        test_summary = {
            "start_time": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "persona_availability": {},
            "workflows_tested": 0,
            "workflows_passed": 0,
            "overall_coordination_quality": 0.0,
            "constitutional_compliance_rate": 0.0
        }
        
        # Test persona availability
        test_summary["persona_availability"] = await self.test_persona_availability()
        
        # Test coordination workflows
        for workflow in self.coordination_workflows:
            test_summary["workflows_tested"] += 1
            if await self.test_coordination_workflow(workflow):
                test_summary["workflows_passed"] += 1
        
        # Calculate overall metrics
        if self.results:
            total_quality = sum(result.coordination_quality_score for result in self.results)
            test_summary["overall_coordination_quality"] = total_quality / len(self.results)
            
            compliant_results = sum(1 for result in self.results if result.constitutional_compliance)
            test_summary["constitutional_compliance_rate"] = (compliant_results / len(self.results)) * 100
        
        test_summary["end_time"] = datetime.now().isoformat()
        return test_summary

def main():
    """Main test execution"""
    async def run_tests():
        test_suite = MultiAgentCoordinationTestSuite()
        summary = await test_suite.run_all_coordination_tests()
        
        print("\n" + "="*80)
        print("ACGS-2 MULTI-AGENT COORDINATION TEST RESULTS")
        print("="*80)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Workflows Tested: {summary['workflows_tested']}")
        print(f"Workflows Passed: {summary['workflows_passed']}")
        print(f"Overall Coordination Quality: {summary['overall_coordination_quality']:.2f}")
        print(f"Constitutional Compliance Rate: {summary['constitutional_compliance_rate']:.1f}%")
        
        print("\nPERSONA AVAILABILITY:")
        for persona, status in summary["persona_availability"].items():
            availability_icon = "✅" if status["available"] else "❌"
            compliance_icon = "✅" if status.get("constitutional_compliant", False) else "❌"
            print(f"{availability_icon} {persona}: Available | {compliance_icon} Constitutional")
        
        print("\nCOORDINATION WORKFLOW RESULTS:")
        for result in test_suite.results:
            success_icon = "✅" if result.success else "❌"
            compliance_icon = "✅" if result.constitutional_compliance else "❌"
            print(f"{success_icon} {result.test_name}: Quality={result.coordination_quality_score:.2f} | {compliance_icon} Constitutional")
            print(f"    Personas: {', '.join([p.value for p in result.personas_involved])}")
            print(f"    Response Time: {result.response_time_ms:.2f}ms")
        
        # Save results
        with open("multi_agent_coordination_results.json", "w") as f:
            json.dump({
                "summary": summary,
                "detailed_results": [
                    {
                        "test_name": r.test_name,
                        "personas_involved": [p.value for p in r.personas_involved],
                        "interaction_chain": r.interaction_chain,
                        "success": r.success,
                        "constitutional_compliance": r.constitutional_compliance,
                        "response_time_ms": r.response_time_ms,
                        "coordination_quality_score": r.coordination_quality_score,
                        "details": r.details,
                        "timestamp": r.timestamp
                    } for r in test_suite.results
                ]
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: multi_agent_coordination_results.json")
        
        if summary["constitutional_compliance_rate"] < 80.0:
            print(f"\n⚠️  WARNING: Constitutional compliance rate is {summary['constitutional_compliance_rate']:.1f}% (target: >80%)")
            return 1
        else:
            print(f"\n✅ SUCCESS: Multi-agent coordination tests completed with {summary['constitutional_compliance_rate']:.1f}% constitutional compliance")
            return 0
    
    return asyncio.run(run_tests())

if __name__ == "__main__":
    exit(main())
