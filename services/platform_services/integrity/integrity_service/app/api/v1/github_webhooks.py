"""
GitHub Webhooks Integration for ACGS Integrity Service
Constitutional Hash: cdd01ef066bc6cf2

Provides webhook endpoints for GitHub integration with constitutional compliance validation.
Tracks repository events, security issues, and compliance validation in the audit trail.
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

# GitHub webhook router
github_router = APIRouter()

# Webhook event types we handle
SUPPORTED_EVENTS = {
    "push": "Code push events for constitutional compliance validation",
    "pull_request": "Pull request events for governance review",
    "security_advisory": "Security advisory events for threat assessment",
    "code_scanning_alert": "Code scanning alerts for security validation",
    "repository": "Repository management events",
    "release": "Release events for audit trail",
    "issues": "Issue tracking for constitutional compliance",
}


class GitHubWebhookProcessor:
    """GitHub webhook processor with constitutional compliance integration."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH

    def verify_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify GitHub webhook signature."""
        if not signature or not secret:
            return False

        # GitHub sends signature as 'sha256=<hash>'
        if not signature.startswith("sha256="):
            return False

        expected_signature = signature[7:]  # Remove 'sha256=' prefix

        # Calculate HMAC signature
        calculated_signature = hmac.new(
            secret.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, calculated_signature)

    def process_push_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Process GitHub push events."""
        repo_name = payload.get("repository", {}).get("full_name", "unknown")
        commits = payload.get("commits", [])
        ref = payload.get("ref", "unknown")

        # Check for constitutional compliance in commit messages
        compliance_violations = []
        for commit in commits:
            message = commit.get("message", "")
            if (
                "constitutional" in message.lower()
                and CONSTITUTIONAL_HASH not in message
            ):
                compliance_violations.append(
                    {
                        "commit_id": commit.get("id"),
                        "message": message,
                        "violation": "Missing constitutional hash in constitutional change",
                    }
                )

        return {
            "event_type": "push",
            "repository": repo_name,
            "ref": ref,
            "commit_count": len(commits),
            "compliance_violations": compliance_violations,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    def process_pull_request_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Process GitHub pull request events."""
        action = payload.get("action", "unknown")
        pr = payload.get("pull_request", {})
        repo_name = payload.get("repository", {}).get("full_name", "unknown")

        # Check for governance-related changes
        pr_title = pr.get("title", "")
        pr_body = pr.get("body", "")

        governance_keywords = [
            "constitutional",
            "governance",
            "policy",
            "compliance",
            "security",
        ]

        governance_flags = [
            keyword
            for keyword in governance_keywords
            if keyword in pr_title.lower() or keyword in pr_body.lower()
        ]

        # Check constitutional hash presence for governance changes
        requires_constitutional_validation = len(governance_flags) > 0
        has_constitutional_hash = CONSTITUTIONAL_HASH in pr_body

        return {
            "event_type": "pull_request",
            "action": action,
            "repository": repo_name,
            "pr_number": pr.get("number"),
            "pr_title": pr_title,
            "governance_flags": governance_flags,
            "requires_constitutional_validation": requires_constitutional_validation,
            "has_constitutional_hash": has_constitutional_hash,
            "constitutional_compliance": has_constitutional_hash
            or not requires_constitutional_validation,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    def process_security_event(
        self, payload: dict[str, Any], event_type: str
    ) -> dict[str, Any]:
        """Process GitHub security-related events."""
        repo_name = payload.get("repository", {}).get("full_name", "unknown")

        if event_type == "security_advisory":
            advisory = payload.get("security_advisory", {})
            severity = advisory.get("severity", "unknown")
            summary = advisory.get("summary", "")

            return {
                "event_type": "security_advisory",
                "repository": repo_name,
                "advisory_id": advisory.get("ghsa_id"),
                "severity": severity,
                "summary": summary,
                "requires_immediate_attention": severity in {"critical", "high"},
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        if event_type == "code_scanning_alert":
            alert = payload.get("alert", {})
            rule = alert.get("rule", {})

            return {
                "event_type": "code_scanning_alert",
                "repository": repo_name,
                "alert_number": alert.get("number"),
                "rule_id": rule.get("id"),
                "severity": rule.get("severity", "unknown"),
                "description": rule.get("description", ""),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        return {
            "event_type": event_type,
            "repository": repo_name,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    def process_repository_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Process GitHub repository management events."""
        action = payload.get("action", "unknown")
        repo = payload.get("repository", {})

        return {
            "event_type": "repository",
            "action": action,
            "repository": repo.get("full_name", "unknown"),
            "private": repo.get("private", False),
            "archived": repo.get("archived", False),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

    async def create_audit_entry(self, webhook_data: dict[str, Any]) -> bool:
        """Create audit trail entry for webhook event."""
        try:
            # Here you would integrate with the integrity service's audit trail
            # For now, we'll log the event with constitutional compliance context

            audit_entry = {
                "event_type": "github_webhook",
                "event_data": webhook_data,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "github_integration",
            }

            logger.info(
                f"GitHub webhook processed: {webhook_data.get('event_type')}",
                extra=audit_entry,
            )

            return True

        except Exception as e:
            logger.exception(f"Failed to create audit entry for GitHub webhook: {e}")
            return False


# Initialize processor
webhook_processor = GitHubWebhookProcessor()


@github_router.post("/webhooks/github")
async def github_webhook_handler(request: Request):
    """
    Handle GitHub webhook events with constitutional compliance validation.

    This endpoint receives webhook events from GitHub and processes them
    according to ACGS constitutional compliance requirements.
    """
    try:
        # Get request headers and body
        signature = request.headers.get("X-Hub-Signature-256", "")
        event_type = request.headers.get("X-GitHub-Event", "")
        delivery_id = request.headers.get("X-GitHub-Delivery", "")

        payload_bytes = await request.body()

        # Verify webhook signature (if secret is configured)
        webhook_secret = "your-webhook-secret"  # Should be from environment/config
        if webhook_secret and not webhook_processor.verify_signature(
            payload_bytes, signature, webhook_secret
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

        # Parse JSON payload
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON payload: {e}",
            )

        # Check if we support this event type
        if event_type not in SUPPORTED_EVENTS:
            logger.warning(f"Unsupported GitHub event type: {event_type}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": f"Event type '{event_type}' not supported",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

        # Process the webhook based on event type
        processed_data = None

        if event_type == "push":
            processed_data = webhook_processor.process_push_event(payload)
        elif event_type == "pull_request":
            processed_data = webhook_processor.process_pull_request_event(payload)
        elif event_type in {"security_advisory", "code_scanning_alert"}:
            processed_data = webhook_processor.process_security_event(
                payload, event_type
            )
        elif event_type == "repository":
            processed_data = webhook_processor.process_repository_event(payload)
        else:
            # Generic processing for other supported events
            processed_data = {
                "event_type": event_type,
                "repository": payload.get("repository", {}).get("full_name", "unknown"),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        # Create audit trail entry
        audit_success = await webhook_processor.create_audit_entry(processed_data)

        # Return response
        response_data = {
            "status": "processed",
            "event_type": event_type,
            "delivery_id": delivery_id,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "audit_recorded": audit_success,
            "processed_data": processed_data,
        }

        return JSONResponse(status_code=status.HTTP_200_OK, content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"GitHub webhook processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {e!s}",
        )


@github_router.get("/webhooks/github/config")
async def get_webhook_config():
    """
    Get GitHub webhook configuration information.

    Returns supported event types and configuration guidance.
    """
    return {
        "supported_events": SUPPORTED_EVENTS,
        "webhook_url": "/api/v1/webhooks/github",
        "required_headers": [
            "X-GitHub-Event",
            "X-GitHub-Delivery",
            "X-Hub-Signature-256",
        ],
        "constitutional_compliance": {
            "hash": CONSTITUTIONAL_HASH,
            "requirements": [
                "All governance-related changes must include constitutional hash",
                "Security events trigger immediate audit trail entries",
                "Pull requests affecting constitutional components require validation",
            ],
        },
        "configuration_guide": {
            "payload_url": "https://your-domain.com/api/v1/webhooks/github",
            "content_type": "application/json",
            "secret": "Configure webhook secret for signature verification",
            "events": list(SUPPORTED_EVENTS.keys()),
        },
    }


@github_router.get("/webhooks/github/health")
async def github_webhook_health():
    """Health check endpoint for GitHub webhook service."""
    return {
        "status": "healthy",
        "service": "github-webhooks",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "supported_events": len(SUPPORTED_EVENTS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@github_router.post("/webhooks/github/test")
async def test_webhook_handler(test_payload: dict[str, Any]):
    """
    Test endpoint for validating webhook processing without GitHub.

    Useful for development and testing webhook processing logic.
    """
    try:
        # Simulate a test push event
        test_event = {
            "repository": {"full_name": "test/repo"},
            "commits": [
                {
                    "id": "abc123",
                    "message": f"Test commit with constitutional hash {CONSTITUTIONAL_HASH}",
                }
            ],
            "ref": "refs/heads/main",
        }

        # Merge with provided payload
        test_event.update(test_payload)

        # Process as push event
        processed_data = webhook_processor.process_push_event(test_event)

        return {
            "status": "test_processed",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "test_data": processed_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.exception(f"Test webhook processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test processing failed: {e!s}",
        )
