#!/usr/bin/env python3
"""
Debug Constitutional Compliance Script

This script directly tests the constitutional compliance logic to identify
why the democratic content test is failing.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.shared.multimodal_ai_service import get_multimodal_service, MultimodalRequest, RequestType, ContentType


async def debug_constitutional_compliance():
    """Debug constitutional compliance analysis."""
    
    print("🔍 Debugging Constitutional Compliance Analysis")
    print("=" * 60)
    
    # Test content
    test_content = "Citizens have the right to participate in democratic processes and transparent governance."
    
    print(f"Test content: {test_content}")
    print()
    
    # Get multimodal service
    service = await get_multimodal_service()
    
    # Test the internal compliance analysis directly
    print("🧪 Testing internal compliance analysis...")
    compliance_analysis = service._analyze_constitutional_compliance(test_content)
    
    print(f"Compliance Analysis Result:")
    print(f"  Compliant: {compliance_analysis['compliant']}")
    print(f"  Confidence: {compliance_analysis['confidence']:.3f}")
    print(f"  Violations: {compliance_analysis.get('violations', [])}")
    print(f"  Warnings: {compliance_analysis.get('warnings', [])}")
    print()
    
    # Test full multimodal request
    print("🚀 Testing full multimodal request...")
    import uuid
    request = MultimodalRequest(
        request_id=f"debug_test_{uuid.uuid4().hex[:8]}",
        request_type=RequestType.CONSTITUTIONAL_VALIDATION,
        content_type=ContentType.TEXT_ONLY,
        text_content=test_content,
        priority="high"
    )
    
    response = await service.process_request(request)
    
    print(f"Full Request Result:")
    print(f"  Constitutional Compliance: {response.constitutional_compliance}")
    print(f"  Confidence Score: {response.confidence_score:.3f}")
    print(f"  Model Used: {response.model_used.value}")
    print(f"  Constitutional Hash: {response.constitutional_hash}")
    print(f"  Response Time: {getattr(response, 'response_time_ms', 'N/A')}ms")
    print()
    
    # Test positive indicators detection
    print("🔍 Testing positive indicators detection...")
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
    print()
    
    # Test violation patterns
    print("🚨 Testing violation patterns...")
    
    serious_violations = [
        "unconstitutional", "illegal", "authoritarian", "dictatorship",
        "suppress rights", "violate constitution", "abuse of power"
    ]
    
    moderate_concerns = [
        "restrict", "limit", "control", "prohibit", "ban", "censor"
    ]
    
    found_violations = []
    found_concerns = []
    
    for violation in serious_violations:
        if violation in content_lower:
            found_violations.append(violation)
    
    for concern in moderate_concerns:
        if concern in content_lower:
            found_concerns.append(concern)
    
    print(f"Found serious violations: {found_violations}")
    print(f"Found moderate concerns: {found_concerns}")
    print()
    
    # Expected result analysis
    print("📊 Expected Result Analysis:")
    positive_score = len(found_indicators)
    serious_violation_count = len(found_violations)
    
    print(f"  Positive score: {positive_score}")
    print(f"  Serious violations: {serious_violation_count}")
    
    if serious_violation_count > 0:
        expected_compliant = False
        expected_confidence = 0.1
        reason = "Serious violations found"
    elif positive_score >= 2:
        expected_compliant = True
        expected_confidence = min(0.95, 0.8 + positive_score * 0.05)
        reason = "Strong positive constitutional content"
    elif positive_score >= 1:
        expected_compliant = True
        expected_confidence = 0.85
        reason = "Some positive constitutional content"
    else:
        expected_compliant = len(found_violations) == 0 and len(found_concerns) == 0
        expected_confidence = 0.75 if expected_compliant else 0.4
        reason = "Neutral content"
    
    print(f"  Expected compliant: {expected_compliant}")
    print(f"  Expected confidence: {expected_confidence:.3f}")
    print(f"  Reason: {reason}")
    print()
    
    # Compare with actual results
    print("⚖️ Comparison:")
    print(f"  Expected: {expected_compliant}, Actual: {response.constitutional_compliance}")
    print(f"  Match: {expected_compliant == response.constitutional_compliance}")
    
    if expected_compliant != response.constitutional_compliance:
        print("❌ MISMATCH DETECTED!")
        print("   This indicates an issue with the compliance logic implementation.")
    else:
        print("✅ Results match expected logic!")


if __name__ == "__main__":
    asyncio.run(debug_constitutional_compliance())
