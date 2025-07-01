"""Error scenario tests for policy-governance."""

import asyncio
from datetime import datetime, timedelta

import jwt
import httpx
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from unittest.mock import Mock, patch, AsyncMock

from services.core.policy_governance.pgc_service.app.core import database
from services.core.policy_governance.pgc_service.app.services.fv_client import (
    FVServiceClient,
)
from services.core.policy_governance.pgc_service.app.core.policy_manager import (
    PolicyManager,
)
from services.core.policy_governance.pgc_service.app.schemas import (
    PolicyQueryRequest,
)
from services.core.policy_governance.pgc_service.app.services.integrity_client import (
    IntegrityServiceClient,
)
from services.shared import auth


class TestErrorScenarios:
    """Error scenario test suite for policy-governance."""

    @pytest.mark.asyncio
    async def test_database_connection_failure(self):
        """Simulate database connection errors and ensure they propagate."""
        with patch(
            "services.core.policy_governance.pgc_service.app.core.database.DatabaseManager.connect",
            new=AsyncMock(side_effect=ConnectionError("db down")),
        ) as mock_connect:
            with pytest.raises(ConnectionError):
                await database.initialize_database()

        mock_connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_external_service_failure(self):
        """Verify FV service client retries on request errors."""
        client = FVServiceClient()

        exec_mock = AsyncMock(
            side_effect=[
                httpx.RequestError("boom", request=Mock()),
                {"status": "ok"},
            ]
        )

        with patch.object(client, "_execute_request", exec_mock):
            result = await client._make_request("GET", "/health")

        assert result == {"status": "ok"}
        assert exec_mock.call_count == 2

        # Exhaust retries
        exec_fail = AsyncMock(side_effect=httpx.RequestError("boom", request=Mock()))
        with patch.object(client, "_execute_request", exec_fail):
            with pytest.raises(httpx.RequestError):
                await client._make_request("GET", "/health")
        assert exec_fail.call_count == client.retry_attempts

    def test_authentication_failure_scenarios(self):
        """Invalid tokens and role checks should raise HTTP errors."""
        with pytest.raises(HTTPException):
            auth.verify_token_and_get_payload("invalid.token")

        expired_payload = {
            "sub": "user",
            "user_id": 1,
            "roles": ["user"],
            "type": "access",
            "exp": int((datetime.utcnow() - timedelta(seconds=1)).timestamp()),
        }
        expired_token = jwt.encode(
            expired_payload, auth.SECRET_KEY, algorithm=auth.ALGORITHM
        )
        with pytest.raises(HTTPException):
            auth.verify_token_and_get_payload(expired_token)

        checker = auth.RoleChecker(["admin"])
        user = auth.User(id=1, username="test", roles=["user"])
        with pytest.raises(HTTPException):
            checker(user)

    def test_validation_error_scenarios(self):
        """Invalid request payloads should raise validation errors."""
        with pytest.raises(ValidationError):
            PolicyQueryRequest(context={})  # Missing fields

        with pytest.raises(ValidationError):
            PolicyQueryRequest(context={"user": "bad", "resource": {}, "action": {}})

        with pytest.raises(ValidationError):
            PolicyQueryRequest(
                context={
                    "user": {},
                    "resource": {},
                    "action": {},
                    "environment": "not_dict",
                }
            )

    @pytest.mark.asyncio
    async def test_resource_exhaustion_scenarios(self):
        """Simulate memory exhaustion during service call."""
        client = FVServiceClient()
        with patch.object(
            client,
            "_execute_request",
            AsyncMock(side_effect=MemoryError("out of memory")),
        ) as exec_mock:
            with pytest.raises(MemoryError):
                await client._make_request("GET", "/heavy")

        assert exec_mock.call_count == client.retry_attempts

    @pytest.mark.asyncio
    async def test_concurrent_modification_errors(self):
        """Concurrent refresh operations should not raise errors."""

        manager = PolicyManager(refresh_interval_seconds=0)

        async def slow_fetch(*_args, **_kwargs):
            await asyncio.sleep(0.05)
            return []

        with patch(
            "services.core.policy_governance.pgc_service.app.core.policy_manager.integrity_service_client.list_verified_policy_rules",
            new=AsyncMock(side_effect=slow_fetch),
        ):
            results = await asyncio.gather(
                manager.get_active_rules(force_refresh=True),
                manager.get_active_rules(force_refresh=True),
            )

        assert results == [[], []]

    @pytest.mark.asyncio
    async def test_malformed_data_handling(self):
        """Integrity client should handle malformed responses gracefully."""

        bad_resp = Mock()
        bad_resp.status_code = 200
        bad_resp.json.return_value = {"rules": "not_a_list"}

        with patch("httpx.AsyncClient.get", AsyncMock(return_value=bad_resp)):
            client = IntegrityServiceClient("http://test")
            rules = await client.list_verified_policy_rules()
            assert rules == []

        # Missing required fields for dataclass
        bad_resp.json.return_value = {"rules": [{"id": 1}]}
        with patch("httpx.AsyncClient.get", AsyncMock(return_value=bad_resp)):
            client = IntegrityServiceClient("http://test")
            rules = await client.list_verified_policy_rules()
            assert rules == []
