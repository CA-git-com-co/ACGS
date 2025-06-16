import multiprocessing
import os
import sys
import time
from unittest.mock import MagicMock, patch

import grpc
import pytest
from fastapi.testclient import TestClient

# Add the project root to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from services.research.federated_evaluation.federated_service.app.core.federated_evaluator import (
        FederatedEvaluator,
        EvaluationTask,
    )
    from services.research.federated_evaluation.coordinator.main import app as coordinator_app
    from services.research.federated_evaluation.agent.main import serve_agent
    FEDERATED_AVAILABLE = True
except ImportError:
    # Mock for testing when federated evaluation is not available
    from fastapi import FastAPI

    class FederatedEvaluator:
        def __init__(self):
            pass

    class EvaluationTask:
        def __init__(self):
            pass

    # Mock coordinator app
    coordinator_app = FastAPI()

    @coordinator_app.post("/tests")
    async def mock_dispatch_test(test_data: dict):
        return {"status": "test dispatched", "task_id": "mock-task-123"}

    def serve_agent():
        """Mock agent server function"""
        pass

    FEDERATED_AVAILABLE = False


# Fixture to manage the agent server lifecycle
@pytest.fixture(scope="function")
def agent_server():
    """
    Starts the node agent gRPC server in a separate process for each test function.
    """
    server_process = multiprocessing.Process(target=serve_agent)
    server_process.start()

    # Give the server a moment to start
    time.sleep(1)

    # Verify the server is up
    try:
        with grpc.insecure_channel("localhost:50051") as channel:
            grpc.channel_ready_future(channel).result(timeout=1)
    except grpc.FutureTimeoutError:
        pytest.fail("gRPC server did not start in time.")

    yield

    # Teardown: stop the server
    server_process.terminate()
    server_process.join()


client = TestClient(coordinator_app)


@patch("src.federated_evaluation.agent.main.docker")
def test_dispatch_successful(mock_docker, agent_server):
    """
    Tests that the coordinator can successfully dispatch a test to the agent
    and that the agent reports a successful Docker container execution.
    """
    # Mock the Docker client and its methods
    mock_docker_client = MagicMock()
    mock_docker.from_env.return_value = mock_docker_client

    # Mock the container run to return a log output
    mock_docker_client.containers.run.return_value = b"Test execution successful\n"

    test_payload = {
        "test_id": "integration-test-001",
        "test_content": "This is a test.",
    }

    response = client.post("/tests", json=test_payload)

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["status"] == "test dispatched"
    assert "task_id" in response_data

    agent_response = response_data.get("agent_response", {})
    assert agent_response.get("status") == "Test execution successful"
    assert "task_id" in agent_response

    # Verify that the Docker methods were called
    mock_docker.from_env.assert_called_once()
    mock_docker_client.images.pull.assert_called_once_with("alpine", "latest")
    mock_docker_client.containers.run.assert_called_once_with(
        "alpine:latest", 'echo "Test execution successful"', detach=False
    )


def test_dispatch_agent_not_running():
    """
    Tests that the coordinator handles the case where the agent is not running.
    """
    # Note: This test runs without the `agent_server` fixture
    test_payload = {
        "test_id": "integration-test-002",
        "test_content": "This should fail.",
    }

    response = client.post("/tests", json=test_payload)

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["status"] == "failed to dispatch test"
    assert "task_id" in response_data
