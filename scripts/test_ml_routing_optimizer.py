#!/usr/bin/env python3
"""
Test ML Routing Optimizer

This script tests the ML-based routing optimization functionality.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.shared.multimodal_ai_service import get_multimodal_service
from services.shared.ai_types import MultimodalRequest, RequestType, ContentType, ModelType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_ml_routing_optimizer():
    """Test the ML routing optimizer functionality."""
    logger.info("🤖 Testing ML Routing Optimizer")
    logger.info("=" * 50)
    
    try:
        # Initialize service
        service = await get_multimodal_service()
        
        # Test requests to generate performance data
        test_requests = [
            {
                "request_type": RequestType.QUICK_ANALYSIS,
                "content": "Analyze this short text for constitutional compliance.",
                "expected_model": ModelType.DEEPSEEK_R1  # Cost-optimized
            },
            {
                "request_type": RequestType.DETAILED_ANALYSIS,
                "content": "Provide a comprehensive analysis of democratic governance principles and their implementation in modern constitutional frameworks.",
                "expected_model": ModelType.FLASH_FULL  # Quality-optimized
            },
            {
                "request_type": RequestType.CONSTITUTIONAL_VALIDATION,
                "content": "Citizens have the right to participate in democratic processes and transparent governance.",
                "expected_model": ModelType.FLASH_FULL  # Accuracy-optimized
            }
        ]
        
        logger.info("📊 Generating performance data...")
        
        # Process test requests to generate ML training data
        for i, test_case in enumerate(test_requests):
            request = MultimodalRequest(
                request_id=f"ml_test_{i}_{int(time.time())}",
                request_type=test_case["request_type"],
                content_type=ContentType.TEXT_ONLY,
                text_content=test_case["content"],
                priority="high"
            )
            
            logger.info(f"Processing request {i+1}: {test_case['request_type'].value}")
            response = await service.process_request(request)
            
            logger.info(f"  Model used: {response.model_used.value}")
            logger.info(f"  Response time: {response.metrics.response_time_ms:.1f}ms")
            logger.info(f"  Cost estimate: ${response.metrics.cost_estimate:.6f}")
            logger.info(f"  Quality score: {response.metrics.quality_score:.3f}")
            logger.info(f"  Constitutional compliance: {response.constitutional_compliance}")
            logger.info("")
        
        # Test ML optimizer functionality
        if service.ml_optimizer:
            logger.info("🧠 Testing ML Optimizer Predictions...")
            
            # Test prediction for each model
            test_request = MultimodalRequest(
                request_id="ml_prediction_test",
                request_type=RequestType.DETAILED_ANALYSIS,
                content_type=ContentType.TEXT_ONLY,
                text_content="Test content for ML prediction",
                priority="medium"
            )
            
            available_models = [ModelType.FLASH_LITE, ModelType.FLASH_FULL, ModelType.DEEPSEEK_R1]
            
            for model in available_models:
                predictions = service.ml_optimizer.predict_performance(test_request, model)
                logger.info(f"  {model.value}:")
                logger.info(f"    Predicted response time: {predictions['response_time']:.1f}ms")
                logger.info(f"    Predicted cost: ${predictions['cost']:.6f}")
                logger.info(f"    Predicted quality: {predictions['quality']:.3f}")
                logger.info(f"    Predicted compliance: {predictions['compliance']:.3f}")
            
            # Test optimal model selection
            logger.info("\n🎯 Testing Optimal Model Selection...")
            optimal_model, predictions = service.ml_optimizer.select_optimal_model(test_request, available_models)
            logger.info(f"  Optimal model: {optimal_model.value}")
            logger.info(f"  Predictions: {predictions}")
            
            # Get performance analytics
            logger.info("\n📈 Performance Analytics...")
            analytics = service.ml_optimizer.get_performance_analytics()

            if 'message' in analytics:
                logger.info(f"  {analytics['message']}")
            else:
                logger.info(f"  Total requests recorded: {analytics['total_requests']}")
                logger.info(f"  Models trained: {analytics['models_trained']}")

                if 'model_statistics' in analytics:
                    for model, stats in analytics['model_statistics'].items():
                        logger.info(f"  {model}:")
                        logger.info(f"    Count: {stats['count']}")
                        logger.info(f"    Avg response time: {stats['avg_response_time']:.1f}ms")
                        logger.info(f"    Avg cost: ${stats['avg_cost']:.6f}")
                        logger.info(f"    Compliance rate: {stats['compliance_rate']:.1%}")
            
            # Train ML models if enough data
            logger.info("\n🎓 Training ML Models...")
            service.ml_optimizer.train_models()
            
            # Test after training
            if service.ml_optimizer._models_trained():
                logger.info("✅ ML models trained successfully")
                
                # Test prediction with trained models
                logger.info("\n🔮 Testing Trained Model Predictions...")
                optimal_model, predictions = service.ml_optimizer.select_optimal_model(test_request, available_models)
                logger.info(f"  Optimal model (trained): {optimal_model.value}")
                logger.info(f"  Trained predictions: {predictions}")
            else:
                logger.info("⚠️ ML models not trained (insufficient data)")
        
        else:
            logger.error("❌ ML optimizer not initialized")
            return False
        
        logger.info("\n" + "=" * 50)
        logger.info("🎉 ML Routing Optimizer test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ ML Routing Optimizer test failed: {e}")
        return False


async def main():
    """Main execution function."""
    logger.info("🤖 ML Routing Optimizer Test")
    logger.info("=" * 50)
    
    start_time = time.time()
    
    success = await test_ml_routing_optimizer()
    
    total_time = time.time() - start_time
    
    if success:
        logger.info(f"✅ Test completed successfully in {total_time:.2f} seconds")
        return 0
    else:
        logger.error(f"❌ Test failed after {total_time:.2f} seconds")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
