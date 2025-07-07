"""
Constitutional validation framework for ACGS.
Constitutional Hash: cdd01ef066bc6cf2
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ConstitutionalBaseModel(BaseModel):
    """Base model with strict constitutional compliance validation."""
    
    constitutional_hash: str = Field(
        default=CONSTITUTIONAL_HASH,
        description="Constitutional compliance hash",
        pattern=f"^{CONSTITUTIONAL_HASH}$"
    )
    
    @field_validator("constitutional_hash")
    @classmethod
    def validate_constitutional_hash(cls, v):
        """Validate constitutional hash matches required value."""
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}")
        return v
    
    class Config:
        str_strip_whitespace = True
        validate_assignment = True
        extra = "forbid"
        json_schema_extra = {"constitutional_hash": CONSTITUTIONAL_HASH}


class ConstitutionalRequest(ConstitutionalBaseModel):
    """Base request model with constitutional compliance."""
    
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Request timestamp"
    )


class ConstitutionalResponse(ConstitutionalBaseModel):
    """Base response model with constitutional compliance."""
    
    request_id: str = Field(..., description="Original request identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp"
    )
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


def validate_constitutional_compliance(data: Dict[str, Any]) -> bool:
    """
    Utility function to validate constitutional compliance in data.
    
    Args:
        data: Data dictionary to validate
        
    Returns:
        True if compliant, False otherwise
    """
    return data.get("constitutional_hash") == CONSTITUTIONAL_HASH


def ensure_constitutional_compliance(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Utility function to ensure constitutional compliance in data.
    
    Args:
        data: Data dictionary to ensure compliance
        
    Returns:
        Data with constitutional hash added/corrected
    """
    data["constitutional_hash"] = CONSTITUTIONAL_HASH
    return data
