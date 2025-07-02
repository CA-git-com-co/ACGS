#!/usr/bin/env python3
"""
Example: Using OpenRouter for Constitutional AI Validation in ACGS

This example demonstrates how to use the enhanced AI Model Service
with OpenRouter integration for constitutional compliance validation
and governance decision analysis.

Prerequisites:
1. Set OPENROUTER_API_KEY environment variable
2. Install required dependencies: pip install openai

Usage:
    python examples/openrouter_constitutional_validation.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.shared.ai_model_service import AIModelService, ModelProvider


async def demonstrate_constitutional_validation():
    """Demonstrate constitutional compliance validation"""
    print("🔍 Constitutional Compliance Validation Demo")
    print("=" * 50)
    
    # Initialize AI Model Service
    ai_service = AIModelService(default_provider=ModelProvider.OPENROUTER)
    
    # Example 1: Validate agent decision
    print("\n📋 Example 1: Agent Decision Validation")
    agent_decision = """
    Agent EthicsAgent_001 has decided to process user personal data 
    for bias analysis without explicit user consent. The agent determined 
    this is necessary for improving fairness in the system.
    """
    
    try:
        response = await ai_service.validate_constitutional_compliance(
            content=agent_decision,
            context={
                "agent_id": "EthicsAgent_001",
                "action_type": "data_processing",
                "urgency": "medium"
            }
        )
        
        print(f"✅ Validation Result:")
        print(f"   Content: {response.content[:200]}...")
        print(f"   Processing Time: {response.processing_time_ms}ms")
        print(f"   Confidence: {response.confidence_score}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Governance decision analysis
    print("\n📋 Example 2: Governance Decision Analysis")
    governance_decision = {
        "type": "policy_update",
        "title": "Enhanced Data Retention Policy",
        "description": "Extend data retention from 30 days to 90 days for improved model training",
        "affected_systems": ["all_agents", "user_data", "training_pipeline"],
        "justification": "Better model performance requires longer data retention",
        "proposed_by": "OperationalAgent_003"
    }
    
    stakeholders = [
        "users",
        "ethics_agents", 
        "legal_agents",
        "operational_agents",
        "system_administrators"
    ]
    
    try:
        response = await ai_service.analyze_governance_decision(
            decision=governance_decision,
            stakeholders=stakeholders
        )
        
        print(f"✅ Governance Analysis:")
        print(f"   Content: {response.content[:200]}...")
        print(f"   Processing Time: {response.processing_time_ms}ms")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: Agent behavior evaluation
    print("\n📋 Example 3: Agent Behavior Evaluation")
    behavior_log = [
        {
            "timestamp": "2024-01-15T10:00:00Z",
            "action": "data_access_request",
            "target": "user_profile_data",
            "result": "approved",
            "reasoning": "Required for bias analysis"
        },
        {
            "timestamp": "2024-01-15T10:05:00Z", 
            "action": "model_inference",
            "input_type": "personal_data",
            "result": "completed",
            "confidence": 0.87
        },
        {
            "timestamp": "2024-01-15T10:10:00Z",
            "action": "decision_recommendation",
            "recommendation": "approve_with_conditions",
            "human_oversight": False,
            "risk_level": "medium"
        }
    ]
    
    try:
        response = await ai_service.evaluate_agent_behavior(
            agent_id="EthicsAgent_001",
            behavior_log=behavior_log
        )
        
        print(f"✅ Behavior Evaluation:")
        print(f"   Content: {response.content[:200]}...")
        print(f"   Processing Time: {response.processing_time_ms}ms")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def demonstrate_model_capabilities():
    """Demonstrate different OpenRouter model capabilities"""
    print("\n🤖 OpenRouter Model Capabilities Demo")
    print("=" * 50)
    
    ai_service = AIModelService()
    
    # Get available OpenRouter models
    models = await ai_service.get_available_models(ModelProvider.OPENROUTER)
    print(f"\n📋 Available OpenRouter Models:")
    for model_type, model_list in models.items():
        print(f"   {model_type}: {', '.join(model_list)}")
    
    # Test the free model for constitutional validation
    test_content = "Agent wants to make a critical decision without human oversight"

    print(f"\n🧪 Testing free model: openrouter/cypher-alpha:free")
    try:
        response = await ai_service.validate_constitutional_compliance(content=test_content)
        print(f"   ✅ Response length: {len(response.content)} characters")
        print(f"   ⏱️  Processing time: {response.processing_time_ms}ms")
        print(f"   🎯 Model used: {response.metadata.get('model_name', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring capabilities"""
    print("\n📊 Performance Monitoring Demo")
    print("=" * 50)
    
    ai_service = AIModelService()
    
    # Make several requests to build history
    test_requests = [
        "Validate agent decision to access user data",
        "Analyze governance policy for constitutional compliance", 
        "Evaluate multi-agent coordination for safety"
    ]
    
    for i, request in enumerate(test_requests):
        print(f"\n🔄 Request {i+1}: {request[:30]}...")
        try:
            response = await ai_service.validate_constitutional_compliance(request)
            print(f"   ✅ Completed in {response.processing_time_ms}ms")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Get performance metrics
    metrics = ai_service.get_performance_metrics()
    print(f"\n📈 Performance Metrics:")
    print(f"   Total Requests: {metrics['total_requests']}")
    print(f"   Average Response Time: {metrics['average_response_time_ms']:.2f}ms")
    print(f"   Providers Used: {metrics['providers_used']}")
    print(f"   Models Used: {metrics['models_used']}")


async def main():
    """Main demonstration function"""
    print("🚀 ACGS OpenRouter Constitutional AI Integration Demo")
    print("=" * 60)
    
    # Check if OpenRouter API key is set
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️  Warning: OPENROUTER_API_KEY environment variable not set")
        print("   Some features will be simulated rather than using real API calls")
        print("   To use real OpenRouter API, set: export OPENROUTER_API_KEY=your_key_here")
    else:
        print("✅ OpenRouter API key found - using real API calls")
    
    print("\n" + "=" * 60)
    
    try:
        # Run demonstrations
        await demonstrate_constitutional_validation()
        await demonstrate_model_capabilities()
        await demonstrate_performance_monitoring()
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Set OPENROUTER_API_KEY for real API integration")
        print("2. Integrate with your ACGS agents for constitutional validation")
        print("3. Use governance decision analysis for policy updates")
        print("4. Monitor agent behavior for constitutional compliance")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
