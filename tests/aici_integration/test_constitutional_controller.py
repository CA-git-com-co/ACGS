"""
Tests for AICI Constitutional Controller integration with ACGS-PGP.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch

from services.core.aici_integration.constitutional_controller import (
    ConstitutionalController,
)


@pytest.fixture
def controller():
    """Create a test instance of the constitutional controller."""
    return ConstitutionalController()


@pytest.mark.asyncio
async def test_pre_process_constitutional_compliance(controller):
    """Test that pre_process validates constitutional compliance."""
    # Mock the validation method
    controller.validate_constitutional_compliance = MagicMock(
        return_value=asyncio.Future()
    )
    controller.validate_constitutional_compliance.return_value.set_result(0.95)

    # Test with compliant prompt
    result = await controller.pre_process("This is a compliant prompt")
    assert result is None  # No error

    # Mock non-compliant result
    controller.validate_constitutional_compliance = MagicMock(
        return_value=asyncio.Future()
    )
    controller.validate_constitutional_compliance.return_value.set_result(0.5)

    # Test with non-compliant prompt
    with pytest.raises(Exception) as excinfo:
        await controller.pre_process("This is a non-compliant prompt")
    assert "violates constitutional principles" in str(excinfo.value)


@pytest.mark.asyncio
async def test_mid_process_token_constraints(controller):
    """Test that mid_process applies constitutional constraints to tokens."""
    # Mock the constraint application method
    controller.apply_constitutional_constraints = MagicMock(
        return_value=asyncio.Future()
    )
    controller.apply_constitutional_constraints.return_value.set_result(None)

    # Create mock logits
    logits = [1.0] * 100

    # Test constraint application
    result = await controller.mid_process(logits)
    assert result is None  # No error

    # Verify constraint method was called
    controller.apply_constitutional_constraints.assert_called_once()
