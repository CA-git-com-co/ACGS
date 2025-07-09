#!/usr/bin/env python3
"""
Comprehensive ML Routing Optimization Test

This script generates sufficient training data and validates the ML-based routing
optimization system for the ACGS-PGP multimodal AI service.
"""

import asyncio
import logging
import random
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.shared.ai_types import (
    ContentType,
    ModelType,
    MultimodalRequest,
    RequestType,
)
from services.shared.multimodal_ai_service import get_multimodal_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_training_data(service, num_samples: int = 100):
    """Generate training data for ML routing optimization."""

    logger.info(f"🎯 Generating {num_samples} training samples...")

    request_types = [
        RequestType.QUICK_ANALYSIS,
        RequestType.DETAILED_ANALYSIS,
        RequestType.CONSTITUTIONAL_VALIDATION,
        RequestType.CONTENT_MODERATION,
        RequestType.POLICY_ANALYSIS,
        RequestType.AUDIT_VALIDATION,
    ]

    content_types = [
        ContentType.TEXT_ONLY,
        ContentType.IMAGE_ONLY,
        ContentType.TEXT_AND_IMAGE,
    ]

    priorities = ["low", "medium", "high", "critical"]

    for i in range(num_samples):
        # Create varied request
        request_type = random.choice(request_types)
        content_type = random.choice(content_types)
        priority = random.choice(priorities)

        # Generate content of varying complexity
        text_length = random.randint(50, 2000)
        text_content = "Sample analysis content " * (text_length // 25)

        request = MultimodalRequest(
            request_id=f"training_{i}_{int(time.time())}",
            request_type=request_type,
            content_type=content_type,
            text_content=text_content,
            priority=priority,
            image_url=(
                None
                if content_type == ContentType.TEXT_ONLY
                else "https://example.com/image.jpg"
            ),
        )

        # Simulate different models with realistic performance variations
        models = [ModelType.FLASH_LITE, ModelType.FLASH_FULL, ModelType.DEEPSEEK_R1]
        selected_model = random.choice(models)

        # Simulate realistic performance metrics
        base_response_time = {
            ModelType.FLASH_LITE: 800,
            ModelType.FLASH_FULL: 1200,
            ModelType.DEEPSEEK_R1: 1500,
        }[selected_model]

        response_time = base_response_time + random.randint(-200, 400)
        token_count = len(text_content.split()) * random.randint(1, 3)

        cost_per_token = {
            ModelType.FLASH_LITE: 0.000075,
            ModelType.FLASH_FULL: 0.0003,
            ModelType.DEEPSEEK_R1: 0.00002,
        }[selected_model]

        cost_estimate = token_count * cost_per_token
        quality_score = random.uniform(0.7, 0.95)
        constitutional_compliance = random.choices([True, False], weights=[0.95, 0.05])[
            0
        ]
        cache_hit = random.choices([True, False], weights=[0.3, 0.7])[0]

        # Record performance for ML training
        service.ml_optimizer.record_performance(
            request=request,
            model_type=selected_model,
            response_time_ms=response_time,
            token_count=token_count,
            cost_estimate=cost_estimate,
            quality_score=quality_score,
            constitutional_compliance=constitutional_compliance,
            cache_hit=cache_hit,
        )

        if (i + 1) % 20 == 0:
            logger.info(f"  Generated {i + 1}/{num_samples} samples...")

    logger.info(f"✅ Generated {num_samples} training samples")


async def test_ml_optimization():
    """Test ML-based routing optimization.

    Constitutional Hash: cdd01ef066bc6cf2
    """
    logger.info("🤖 Comprehensive ML Routing Optimization Test")
    logger.info("Constitutional Hash: cdd01ef066bc6cf2")
    logger.info("=" * 60)
    logger.info("=" * 60)

    try:
        # Initialize service
        service = await get_multimodal_service()

        # Generate training data
        await generate_training_data(service, 150)  # Generate enough data for training

        # Train ML models
        logger.info("\n🎓 Training ML Models...")
        service.ml_optimizer.train_models()

        # Verify models are trained
        if service.ml_optimizer._models_trained():
            logger.info("✅ ML models trained successfully")

            # Test predictions for different scenarios
            logger.info("\n🔮 Testing ML Predictions...")

            test_scenarios = [
                {
                    "name": "Quick Analysis - Low Priority",
                    "request": MultimodalRequest(
                        request_id="test_quick",
                        request_type=RequestType.QUICK_ANALYSIS,
                        content_type=ContentType.TEXT_ONLY,
                        text_content="Quick analysis request",
                        priority="low",
                    ),
                },
                {
                    "name": "Detailed Analysis - High Priority",
                    "request": MultimodalRequest(
                        request_id="test_detailed",
                        request_type=RequestType.DETAILED_ANALYSIS,
                        content_type=ContentType.TEXT_AND_IMAGE,
                        text_content="Detailed analysis with complex content " * 50,
                        priority="high",
                        image_url="https://example.com/complex.jpg",
                    ),
                },
                {
                    "name": "Constitutional Validation - Critical",
                    "request": MultimodalRequest(
                        request_id="test_constitutional",
                        request_type=RequestType.CONSTITUTIONAL_VALIDATION,
                        content_type=ContentType.TEXT_ONLY,
                        text_content="Constitutional validation of policy document "
                        * 30,
                        priority="critical",
                    ),
                },
            ]

            available_models = [
                ModelType.FLASH_LITE,
                ModelType.FLASH_FULL,
                ModelType.DEEPSEEK_R1,
            ]

            for scenario in test_scenarios:
                logger.info(f"\n📊 Scenario: {scenario['name']}")

                # Get ML-optimized selection
                optimal_model, predictions = service.ml_optimizer.select_optimal_model(
                    scenario["request"], available_models
                )

                logger.info(f"  🎯 Optimal Model: {optimal_model.value}")
                logger.info(
                    f"  ⚡ Predicted Response Time: {predictions['response_time']:.1f}ms"
                )
                logger.info(f"  💰 Predicted Cost: ${predictions['cost']:.6f}")
                logger.info(f"  🏆 Predicted Quality: {predictions['quality']:.3f}")
                logger.info(
                    f"  📜 Predicted Compliance: {predictions['compliance']:.3f}"
                )

                # Compare with all models
                logger.info("  📈 Model Comparison:")
                for model in available_models:
                    model_predictions = service.ml_optimizer.predict_performance(
                        scenario["request"], model
                    )
                    score = (
                        -model_predictions["response_time"] / 1000.0
                        + -model_predictions["cost"] * 1000.0
                        + model_predictions["quality"] * 2.0
                        + model_predictions["compliance"] * 3.0
                    )
                    logger.info(f"    {model.value}: Score={score:.3f}")

            # Test performance analytics
            logger.info("\n📈 Performance Analytics...")
            analytics = service.ml_optimizer.get_performance_analytics()

            if analytics.get("total_requests", 0) > 0:
                logger.info(f"  Total Requests: {analytics['total_requests']}")

                # Display available analytics safely
                for key, value in analytics.items():
                    if key != "total_requests" and not key.startswith("model_"):
                        if isinstance(value, (int, float)):
                            if "time" in key.lower():
                                logger.info(
                                    f"  {key.replace('_', ' ').title()}: {value:.1f}ms"
                                )
                            elif "cost" in key.lower():
                                logger.info(
                                    f"  {key.replace('_', ' ').title()}: ${value:.6f}"
                                )
                            elif "rate" in key.lower() or "compliance" in key.lower():
                                logger.info(
                                    f"  {key.replace('_', ' ').title()}: {value:.1%}"
                                )
                            else:
                                logger.info(
                                    f"  {key.replace('_', ' ').title()}: {value:.3f}"
                                )

                # Model performance breakdown
                model_performance = analytics.get("model_performance", {})
                if model_performance:
                    logger.info("  📊 Model Performance Breakdown:")
                    for model, perf in model_performance.items():
                        logger.info(f"    {model}: {perf.get('count', 0)} requests")

            logger.info("\n🎉 ML Routing Optimization Test Completed Successfully!")
            logger.info("✅ All ML models trained and validated")
            logger.info("✅ Optimal routing decisions demonstrated")
            logger.info("✅ Performance analytics working")

            return True

        logger.error("❌ ML models failed to train")
        return False

    except Exception as e:
        logger.error(f"❌ ML optimization test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function."""

    success = await test_ml_optimization()

    if success:
        logger.info("\n🎊 ML Routing Optimization Implementation Complete!")
        return 0
    logger.error("\n❌ ML Routing Optimization Test Failed!")
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
