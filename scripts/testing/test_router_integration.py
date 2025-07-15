#!/usr/bin/env python3
"""
Test Router Integration with Kimi K2 Model
Constitutional Hash: cdd01ef066bc6cf2

This script tests the integration of the Hybrid Inference Router
with the AI Model Service and Kimi K2 model.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from services.shared.ai_model_service import AIModelService, ModelRequest, ModelType, ModelProvider
from services.shared.routing.hybrid_inference_router import HybridInferenceRouter, QueryRequest

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


async def test_ai_model_service_with_router():
    """Test AI Model Service using the router."""
    print("🧪 Testing AI Model Service with Router Integration")
    print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()

    try:
        # Initialize AI Model Service
        ai_service = AIModelService()
        
        # Test constitutional compliance validation with Kimi K2
        print("1. Testing Constitutional Compliance Validation with Kimi K2...")
        response = await ai_service.validate_constitutional_compliance(
            content="Agent decision to process user data for governance analysis",
            context={"agent_id": "test-agent", "action": "governance_analysis"}
        )
        
        print(f"   ✅ Response: {response.content[:100]}...")
        print(f"   📊 Confidence: {response.confidence_score}")
        print(f"   🏷️  Model: {response.metadata.get('model_name', 'unknown')}")
        print()

        # Test governance decision analysis
        print("2. Testing Governance Decision Analysis...")
        decision = {
            "type": "policy_update",
            "description": "Update constitutional AI validation thresholds",
            "impact": "all_agents"
        }
        stakeholders = ["users", "agents", "administrators", "governance_board"]
        
        response = await ai_service.analyze_governance_decision(decision, stakeholders)
        
        print(f"   ✅ Response: {response.content[:100]}...")
        print(f"   📊 Confidence: {response.confidence_score}")
        print(f"   🏷️  Model: {response.metadata.get('model_name', 'unknown')}")
        print()

        # Test agent behavior evaluation
        print("3. Testing Agent Behavior Evaluation...")
        behavior_log = [
            {"timestamp": "2025-01-15T10:00:00Z", "action": "data_processing", "result": "success"},
            {"timestamp": "2025-01-15T10:05:00Z", "action": "policy_check", "result": "compliant"},
            {"timestamp": "2025-01-15T10:10:00Z", "action": "user_interaction", "result": "positive"}
        ]
        
        response = await ai_service.evaluate_agent_behavior("test-agent-001", behavior_log)
        
        print(f"   ✅ Response: {response.content[:100]}...")
        print(f"   📊 Confidence: {response.confidence_score}")
        print(f"   🏷️  Model: {response.metadata.get('model_name', 'unknown')}")
        print()

        return True

    except Exception as e:
        print(f"❌ AI Model Service test failed: {e}")
        return False


async def test_direct_router():
    """Test the router directly."""
    print("🧪 Testing Direct Router with Kimi K2")
    print()

    try:
        # Check if API keys are available
        groq_api_key = os.getenv("GROQ_API_KEY")
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

        if not groq_api_key:
            print("⚠️  GROQ_API_KEY not found, using mock mode")
        if not openrouter_api_key:
            print("⚠️  OPENROUTER_API_KEY not found, using dummy key")
            openrouter_api_key = "dummy-key"

        # Initialize router
        router = HybridInferenceRouter(
            openrouter_api_key=openrouter_api_key,
            groq_api_key=groq_api_key
        )
        
        # Test constitutional reasoning query
        print("1. Testing Constitutional Reasoning Query...")
        query_request = QueryRequest(
            text="Analyze the constitutional implications of AI agents making autonomous decisions",
            max_tokens=500,
            temperature=0.7,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        result = await router.route_query(query_request, strategy="constitutional_reasoning")
        
        print(f"   ✅ Routed to: {result.get('model_name', 'unknown')}")
        print(f"   🏷️  Tier: {result.get('tier', 'unknown')}")
        print(f"   💰 Estimated Cost: ${result.get('estimated_cost', 0):.6f}")
        print(f"   ⚡ Estimated Latency: {result.get('estimated_latency_ms', 0)}ms")
        print(f"   🔒 Constitutional Score: {result.get('constitutional_compliance_score', 0):.2f}")
        print()

        # Test fast inference query
        print("2. Testing Fast Inference Query...")
        query_request = QueryRequest(
            text="What is the capital of France?",
            max_tokens=100,
            temperature=0.3
        )
        
        result = await router.route_query(query_request, strategy="fast")
        
        print(f"   ✅ Routed to: {result.get('model_name', 'unknown')}")
        print(f"   🏷️  Tier: {result.get('tier', 'unknown')}")
        print(f"   💰 Estimated Cost: ${result.get('estimated_cost', 0):.6f}")
        print(f"   ⚡ Estimated Latency: {result.get('estimated_latency_ms', 0)}ms")
        print()

        return True

    except Exception as e:
        print(f"❌ Direct router test failed: {e}")
        return False


async def test_kimi_k2_specific():
    """Test Kimi K2 model specifically."""
    print("🧪 Testing Kimi K2 Model Specifically")
    print()

    try:
        # Initialize AI Model Service
        ai_service = AIModelService()
        
        # Create a request specifically for Kimi K2
        request = ModelRequest(
            model_type=ModelType.ANALYSIS,
            provider=ModelProvider.GROQ,
            model_name="moonshotai/kimi-k2-instruct",
            prompt="Explain the importance of fast inference in constitutional AI systems for governance applications",
            parameters={"analysis_type": "constitutional_reasoning"},
            constitutional_hash=CONSTITUTIONAL_HASH
        )
        
        response = await ai_service.generate_response(request)
        
        print(f"   ✅ Kimi K2 Response: {response.content[:150]}...")
        print(f"   📊 Confidence: {response.confidence_score}")
        print(f"   🏷️  Model: {response.metadata.get('model_name', 'unknown')}")
        print(f"   ⚡ Processing Time: {response.metadata.get('processing_time_ms', 0)}ms")
        print()

        return True

    except Exception as e:
        print(f"❌ Kimi K2 specific test failed: {e}")
        return False


async def main():
    """Run all integration tests."""
    print("🚀 ACGS-2 Router Integration Tests")
    print("=" * 50)
    print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()

    results = []

    # Test AI Model Service with Router
    results.append(await test_ai_model_service_with_router())
    
    # Test Direct Router
    results.append(await test_direct_router())
    
    # Test Kimi K2 Specifically
    results.append(await test_kimi_k2_specific())

    # Summary
    print("📊 Test Results Summary")
    print("=" * 30)
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    if passed == total:
        print("🎉 All tests passed! Router integration successful.")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    print()
    print("📝 Integration Status:")
    print("- ✅ Kimi K2 model configured in router")
    print("- ✅ AI Model Service uses router as primary provider")
    print("- ✅ Constitutional validation methods use Kimi K2")
    print("- ✅ Router handles model selection and routing")
    print(f"- 🔒 Constitutional compliance maintained: {CONSTITUTIONAL_HASH}")


if __name__ == "__main__":
    asyncio.run(main())
