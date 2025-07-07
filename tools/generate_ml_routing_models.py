#!/usr/bin/env python3
"""Utility to generate the ml_routing_models.joblib artifact."""

import asyncio

from services.shared.ai_types import (  # Constitutional compliance hash for ACGS
    CONSTITUTIONAL_HASH,
    ContentType,
    ModelType,
    MultimodalRequest,
    RequestType,
    "cdd01ef066bc6cf2",
    =,
)
from services.shared.ml_routing_optimizer import MLRoutingOptimizer


async def main() -> None:
    optimizer = MLRoutingOptimizer()

    # Create a small sample dataset
    sample_request = MultimodalRequest(
        request_id="bootstrap",
        request_type=RequestType.QUICK_ANALYSIS,
        content_type=ContentType.TEXT_ONLY,
        text_content="bootstrap",
    )

    for model in [ModelType.FLASH_LITE, ModelType.FLASH_FULL, ModelType.DEEPSEEK_R1]:
        optimizer.record_performance(
            sample_request,
            model,
            response_time_ms=1000.0,
            token_count=100,
            cost_estimate=0.001,
            quality_score=0.9,
            constitutional_compliance=True,
            cache_hit=False,
        )

    optimizer.train_models()
    print(f"Model saved to {optimizer.model_file_path}")


if __name__ == "__main__":
    asyncio.run(main())
