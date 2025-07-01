#!/usr/bin/env python3
"""
Health Check Server for OCR Service

This script provides a dedicated health check endpoint for the OCR service.
It runs as a separate process and responds to health check requests.
"""

import argparse
import http.server
import logging
import os
import socketserver
import sys
import threading
import time
from typing import Any, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ocr-health-server")


class HealthState:
    """Class to track the health state of the OCR service."""

    def __init__(self):
        self.healthy = False
        self.last_update = time.time()
        self.info: Dict[str, Any] = {"status": "initializing"}

    def set_healthy(self, info: Optional[Dict[str, Any]] = None):
        """Mark the service as healthy."""
        self.healthy = True
        self.last_update = time.time()
        self.info = info or {"status": "healthy"}
        logger.info("Service marked as healthy")

    def set_unhealthy(self, reason: str):
        """Mark the service as unhealthy."""
        self.healthy = False
        self.last_update = time.time()
        self.info = {"status": "unhealthy", "reason": reason}
        logger.warning(f"Service marked as unhealthy: {reason}")

    def get_status(self) -> Tuple[bool, Dict[str, Any]]:
        """Get the current health status."""
        # If we haven't received an update in a while, consider the service unhealthy
        if time.time() - self.last_update > 60:  # 60 seconds timeout
            self.set_unhealthy("No health update received in the last 60 seconds")

        return self.healthy, self.info


# Global health state object
health_state = HealthState()


class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for health check endpoints."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/health":
            is_healthy, info = health_state.get_status()

            if is_healthy:
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"healthy")
            else:
                self.send_response(503)  # Service Unavailable
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                reason = info.get("reason", "Unknown reason")
                self.wfile.write(f"unhealthy: {reason}".encode())
        elif self.path == "/health/status":
            # Detailed health status endpoint
            is_healthy, info = health_state.get_status()

            import json

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            response = {
                "healthy": is_healthy,
                "lastUpdate": health_state.last_update,
                "info": info,
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not found")

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/health/update":
            # Read the request body
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)

            try:
                import json

                data = json.loads(post_data.decode())

                if "healthy" in data:
                    if data["healthy"]:
                        health_state.set_healthy(data.get("info"))
                    else:
                        health_state.set_unhealthy(
                            data.get("reason", "No reason provided")
                        )

                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"Health status updated")
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"Missing 'healthy' field in request")
            except Exception as e:
                logger.error(f"Error processing health update: {e}")
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Invalid request: {str(e)}".encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not found")

    def log_message(self, format, *args):
        """Override log_message to use our logger."""
        logger.debug(f"{self.client_address[0]} - {format%args}")


def run_health_server(port: int, host: str = "0.0.0.0"):
    """
    Run the health check server.

    Args:
        port: Port to listen on
        host: Host to bind to
    """
    # Set initial health state
    health_state.set_healthy({"status": "starting"})

    # Create and run the server
    server = socketserver.ThreadingTCPServer((host, port), HealthCheckHandler)
    server.daemon_threads = True

    logger.info(f"Health check server running on {host}:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Health check server stopped")
    finally:
        server.server_close()


def check_vllm_health(host: str, port: int) -> bool:
    """
    Check if vLLM service is healthy by making a simple request.

    Args:
        host: vLLM service hostname
        port: vLLM service port

    Returns:
        True if healthy, False otherwise
    """
    import requests

    try:
        # Make a simple request to the vLLM API
        response = requests.post(
            f"http://{host}:{port}/v1/chat/completions",
            json={
                "model": "nanonets/Nanonets-OCR-s",
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": "Are you available?"}],
                    }
                ],
            },
            timeout=5,
        )

        return response.status_code == 200
    except Exception as e:
        logger.warning(f"vLLM health check failed: {e}")
        return False


def monitor_vllm_health(vllm_host: str, vllm_port: int, check_interval: int = 30):
    """
    Periodically monitor vLLM service health and update health state.

    Args:
        vllm_host: vLLM service hostname
        vllm_port: vLLM service port
        check_interval: How often to check health in seconds
    """
    logger.info(
        f"Starting vLLM health monitor (checking {vllm_host}:{vllm_port} every {check_interval}s)"
    )

    while True:
        try:
            is_healthy = check_vllm_health(vllm_host, vllm_port)

            if is_healthy:
                health_state.set_healthy({"status": "vLLM service is responding"})
            else:
                health_state.set_unhealthy("vLLM service is not responding")
        except Exception as e:
            logger.error(f"Error in health monitor: {e}")
            health_state.set_unhealthy(f"Health monitor error: {str(e)}")

        # Sleep for the check interval
        time.sleep(check_interval)


def main():
    """Main entry point for the health check server."""
    parser = argparse.ArgumentParser(description="OCR Service Health Check Server")
    parser.add_argument("--port", type=int, default=8667, help="Port to listen on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument(
        "--vllm-host", default="localhost", help="vLLM service hostname"
    )
    parser.add_argument("--vllm-port", type=int, default=8666, help="vLLM service port")
    parser.add_argument(
        "--check-interval",
        type=int,
        default=30,
        help="Health check interval in seconds",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Start health monitor in a background thread
    monitor_thread = threading.Thread(
        target=monitor_vllm_health,
        args=(args.vllm_host, args.vllm_port, args.check_interval),
        daemon=True,
    )
    monitor_thread.start()

    # Start the health check server
    run_health_server(args.port, args.host)

    return 0


if __name__ == "__main__":
    sys.exit(main())
