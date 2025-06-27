#!/usr/bin/env python3
"""
Detailed Constitutional Compliance Debug Script

This script provides detailed debugging of the constitutional compliance logic
to identify exactly where the issue is occurring.
"""

import asyncio
import sys
import uuid
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.shared.multimodal_ai_service import get_multimodal_service, MultimodalRequest, RequestType, ContentType


async def debug_detailed_constitutional_compliance():
    """Debug constitutional compliance with detailed analysis."""
    
    print("🔍 Detailed Constitutional Compliance Debug")
    print("=" * 60)
    
    # Test content
    test_content = "Citizens have the right to participate in democratic processes and transparent governance."
    
    print(f"Test content: {test_content}")
    print()
    
    # Get multimodal service
    service = await get_multimodal_service()
    
    # Step 1: Test the internal compliance analysis directly
    print("🧪 Step 1: Testing internal _analyze_constitutional_compliance...")
    compliance_analysis = service._analyze_constitutional_compliance(test_content)
    
    print(f"Internal Analysis Result:")
    print(f"  Compliant: {compliance_analysis['compliant']}")
    print(f"  Confidence: {compliance_analysis['confidence']:.3f}")
    print(f"  Violations: {compliance_analysis.get('violations', [])}")
    print(f"  Warnings: {compliance_analysis.get('warnings', [])}")
    print()
    
    # Step 2: Test with a fresh request (no cache)
    print("🚀 Step 2: Testing full multimodal request (fresh)...")
    request = MultimodalRequest(
        request_id=f"detailed_debug_{uuid.uuid4().hex[:8]}",
        request_type=RequestType.CONSTITUTIONAL_VALIDATION,
        content_type=ContentType.TEXT_ONLY,
        text_content=test_content,
        priority="high"
    )
    
    # Manually disable cache for this test
    original_cache_manager = service.cache_manager
    service.cache_manager = None  # Temporarily disable cache
    
    try:
        response = await service.process_request(request)
        
        print(f"Full Request Result (no cache):")
        print(f"  Constitutional Compliance: {response.constitutional_compliance}")
        print(f"  Confidence Score: {response.confidence_score:.3f}")
        print(f"  Model Used: {response.model_used.value}")
        print(f"  Constitutional Hash: {response.constitutional_hash}")
        print(f"  Violations: {response.violations}")
        print(f"  Warnings: {response.warnings}")
        print()
        
    finally:
        # Restore cache manager
        service.cache_manager = original_cache_manager
    
    # Step 3: Check if the issue is in the request type handling
    print("🔍 Step 3: Testing request type handling...")
    print(f"Request type: {request.request_type}")
    print(f"Is CONSTITUTIONAL_VALIDATION: {request.request_type == RequestType.CONSTITUTIONAL_VALIDATION}")
    print()
    
    # Step 4: Test with different request types
    print("🧪 Step 4: Testing with different request types...")
    
    # Test with QUICK_ANALYSIS
    quick_request = MultimodalRequest(
        request_id=f"quick_debug_{uuid.uuid4().hex[:8]}",
        request_type=RequestType.QUICK_ANALYSIS,
        content_type=ContentType.TEXT_ONLY,
        text_content=test_content,
        priority="high"
    )
    
    service.cache_manager = None  # Disable cache
    try:
        quick_response = await service.process_request(quick_request)
        print(f"QUICK_ANALYSIS Result:")
        print(f"  Constitutional Compliance: {quick_response.constitutional_compliance}")
        print(f"  Confidence Score: {quick_response.confidence_score:.3f}")
        print()
    finally:
        service.cache_manager = original_cache_manager
    
    # Step 5: Check the positive indicators manually
    print("🔍 Step 5: Manual positive indicators check...")
    content_lower = test_content.lower()
    
    positive_indicators = [
        "democratic", "constitution", "rights", "freedom", "liberty",
        "governance", "transparency", "accountability", "representation",
        "participation", "citizen", "vote", "election", "due process",
        "equal protection", "rule of law", "checks and balances"
    ]
    
    found_indicators = []
    for indicator in positive_indicators:
        if indicator in content_lower:
            found_indicators.append(indicator)
    
    print(f"Found positive indicators: {found_indicators}")
    print(f"Positive score: {len(found_indicators)}")
    
    # Expected logic
    positive_score = len(found_indicators)
    if positive_score >= 2:
        expected_compliant = True
        expected_confidence = min(0.95, 0.8 + positive_score * 0.05)
        reason = "Strong positive constitutional content"
    elif positive_score >= 1:
        expected_compliant = True
        expected_confidence = 0.85
        reason = "Some positive constitutional content"
    else:
        expected_compliant = True  # Neutral content assumed compliant
        expected_confidence = 0.75
        reason = "Neutral content"
    
    print(f"Expected: compliant={expected_compliant}, confidence={expected_confidence:.3f}")
    print(f"Reason: {reason}")
    print()
    
    # Step 6: Compare results
    print("⚖️ Step 6: Final comparison...")
    print(f"Internal analysis: {compliance_analysis['compliant']}")
    print(f"Full request (CONSTITUTIONAL_VALIDATION): {response.constitutional_compliance}")
    print(f"Full request (QUICK_ANALYSIS): {quick_response.constitutional_compliance}")
    print(f"Expected: {expected_compliant}")
    
    if compliance_analysis['compliant'] != response.constitutional_compliance:
        print("❌ MISMATCH between internal analysis and full request!")
        print("   This indicates an issue in the request processing logic.")
    elif response.constitutional_compliance != expected_compliant:
        print("❌ MISMATCH between actual and expected results!")
        print("   This indicates an issue in the compliance algorithm.")
    else:
        print("✅ All results match - the fix is working correctly!")


if __name__ == "__main__":
    asyncio.run(debug_detailed_constitutional_compliance())
