from typing import Any

from pydantic import BaseModel, Field

# --- Schemas for PGC Service's own API ---


class PolicyQueryContext(BaseModel):
    """
    Represents the context for a policy query.
    This is highly flexible and depends on the types of policies being enforced.
    Examples: user attributes, resource attributes, action details.
    """

    user: dict[str, Any] = Field(
        ...,
        description="Attributes of the user making the request, e.g., {'id': 'user123', 'role': 'editor'}",
    )
    resource: dict[str, Any] = Field(
        ...,
        description="Attributes of the resource being accessed, e.g., {'id': 'doc456', 'sensitivity': 'high'}",
    )
    action: dict[str, Any] = Field(
        ...,
        description="Details of the action being performed, e.g., {'type': 'read', 'parameters': {'version': 2}}",
    )
    environment: dict[str, Any] | None = Field(
        None,
        description="Environmental factors, e.g., {'ip_address': '192.168.1.100', 'time_of_day': '14:30'}",
    )


class PolicyQueryRequest(BaseModel):
    context: PolicyQueryContext = Field(
        ..., description="The context against which policies will be evaluated."
    )
    # query: Optional[str] = Field(None, description="Specific query string if not inferable from context, e.g., 'can_read(user123, doc456)'")
    # target_decision_variable: Optional[str] = Field("allow", description="The Datalog variable to query for the decision, e.g., 'allow', 'deny'")


class PolicyQueryResponse(BaseModel):
    decision: str = Field(
        ...,
        description="The outcome of the policy evaluation, e.g., 'permit', 'deny', 'not_applicable'.",
    )
    matching_rules: list[dict[str, Any]] | None = Field(
        None,
        description="List of rules that led to the decision, with details like ID or content.",
    )
    reason: str | None = Field(
        None, description="A human-readable explanation for the decision."
    )
    error_message: str | None = Field(
        None, description="Any error that occurred during evaluation."
    )


# --- Schemas for PETs and TEEs (Placeholders) ---


class PETContextInput(BaseModel):
    data: dict[str, Any]
    transformation: str  # e.g., "homomorphic_encryption", "differential_privacy"


class PETContextOutput(BaseModel):
    processed_data: Any  # Could be encrypted data, anonymized data, etc.
    status: str


class TEEContextInput(BaseModel):
    data: dict[str, Any]
    code_to_execute: str  # Reference to code or actual code snippet


class TEEContextOutput(BaseModel):
    result: Any
    attestation_report: str | None = None  # Simulating an attestation
    status: str


# --- Schemas for interacting with Integrity Service ---
class IntegrityPolicyRule(BaseModel):  # Based on Integrity Service's PolicyRule schema
    id: int
    rule_content: str
    version: int
    verification_status: str  # We'd only fetch 'verified' rules
    source_principle_ids: list[int] | None = []


# Placeholder for User (if PGC Service needs to be auth-aware for its own endpoints)
class User(BaseModel):
    id: str
    roles: list[str] = []
