"""
NATS Client for DGM Service.

Provides NATS message broker integration for event-driven communication
with other ACGS services, supporting publish/subscribe patterns,
request/reply, and streaming capabilities.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

import nats
from nats.aio.client import Client as NATS
from nats.aio.subscription import Subscription
from nats.js import JetStreamContext
from nats.js.api import ConsumerConfig, StreamConfig


@dataclass
class NATSConfig:
    """NATS configuration for DGM service."""

    servers: List[str] = field(default_factory=lambda: ["nats://localhost:4222"])
    name: str = "dgm-service"
    user: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    tls_cert: Optional[str] = None
    tls_key: Optional[str] = None
    tls_ca: Optional[str] = None

    # Connection settings
    max_reconnect_attempts: int = 10
    reconnect_time_wait: float = 2.0
    ping_interval: int = 120
    max_outstanding_pings: int = 2

    # JetStream settings
    enable_jetstream: bool = True
    stream_name: str = "DGM_EVENTS"
    subjects: List[str] = field(
        default_factory=lambda: [
            "dgm.improvement.*",
            "dgm.performance.*",
            "dgm.constitutional.*",
            "dgm.bandit.*",
        ]
    )

    # Message settings
    max_payload: int = 1024 * 1024  # 1MB
    drain_timeout: float = 30.0


class NATSClient:
    """NATS client for DGM service event-driven communication."""

    def __init__(self, config: NATSConfig):
        """Initialize NATS client with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # NATS connections
        self.nc: Optional[NATS] = None
        self.js: Optional[JetStreamContext] = None

        # Subscriptions tracking
        self.subscriptions: Dict[str, Subscription] = {}
        self.handlers: Dict[str, List[Callable]] = {}

        # Connection state
        self.connected = False
        self.connecting = False

        # Metrics
        self.metrics = {
            "messages_published": 0,
            "messages_received": 0,
            "connection_errors": 0,
            "reconnections": 0,
            "last_connected": None,
            "last_error": None,
        }

    async def connect(self) -> bool:
        """Connect to NATS server with retry logic."""
        if self.connected or self.connecting:
            return self.connected

        self.connecting = True

        try:
            self.logger.info(f"Connecting to NATS servers: {self.config.servers}")

            # Connection options
            options = {
                "servers": self.config.servers,
                "name": self.config.name,
                "max_reconnect_attempts": self.config.max_reconnect_attempts,
                "reconnect_time_wait": self.config.reconnect_time_wait,
                "ping_interval": self.config.ping_interval,
                "max_outstanding_pings": self.config.max_outstanding_pings,
                "error_cb": self._error_callback,
                "disconnected_cb": self._disconnected_callback,
                "reconnected_cb": self._reconnected_callback,
                "closed_cb": self._closed_callback,
            }

            # Add authentication if configured
            if self.config.user and self.config.password:
                options["user"] = self.config.user
                options["password"] = self.config.password
            elif self.config.token:
                options["token"] = self.config.token

            # Add TLS if configured
            if self.config.tls_cert and self.config.tls_key:
                options["tls"] = {
                    "cert": self.config.tls_cert,
                    "key": self.config.tls_key,
                    "ca": self.config.tls_ca,
                }

            # Connect to NATS
            self.nc = await nats.connect(**options)

            # Setup JetStream if enabled
            if self.config.enable_jetstream:
                await self._setup_jetstream()

            self.connected = True
            self.metrics["last_connected"] = datetime.utcnow().isoformat()

            self.logger.info("✅ Connected to NATS successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to NATS: {e}")
            self.metrics["connection_errors"] += 1
            self.metrics["last_error"] = str(e)
            return False

        finally:
            self.connecting = False

    async def _setup_jetstream(self):
        """Setup JetStream for persistent messaging."""
        try:
            self.js = self.nc.jetstream()

            # Create or update stream
            stream_config = StreamConfig(
                name=self.config.stream_name,
                subjects=self.config.subjects,
                max_msgs=1000000,
                max_bytes=1024 * 1024 * 1024,  # 1GB
                max_age=7 * 24 * 3600,  # 7 days
                storage="file",
                replicas=1,
            )

            try:
                await self.js.add_stream(stream_config)
                self.logger.info(f"Created JetStream stream: {self.config.stream_name}")
            except Exception as e:
                if "stream name already in use" in str(e).lower():
                    await self.js.update_stream(stream_config)
                    self.logger.info(f"Updated JetStream stream: {self.config.stream_name}")
                else:
                    raise

        except Exception as e:
            self.logger.error(f"Failed to setup JetStream: {e}")
            raise

    async def disconnect(self):
        """Disconnect from NATS server."""
        if not self.connected:
            return

        try:
            # Unsubscribe from all subscriptions
            for subject, subscription in self.subscriptions.items():
                try:
                    await subscription.unsubscribe()
                    self.logger.debug(f"Unsubscribed from {subject}")
                except Exception as e:
                    self.logger.warning(f"Error unsubscribing from {subject}: {e}")

            self.subscriptions.clear()
            self.handlers.clear()

            # Drain and close connection
            if self.nc:
                await self.nc.drain()
                await self.nc.close()

            self.connected = False
            self.nc = None
            self.js = None

            self.logger.info("Disconnected from NATS")

        except Exception as e:
            self.logger.error(f"Error during NATS disconnect: {e}")

    async def publish(
        self, subject: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """Publish message to NATS subject."""
        if not self.connected:
            self.logger.error("Cannot publish: not connected to NATS")
            return False

        try:
            # Prepare message
            message = {
                "id": str(uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "source": self.config.name,
                "data": data,
            }

            payload = json.dumps(message).encode("utf-8")

            if len(payload) > self.config.max_payload:
                self.logger.error(f"Message too large: {len(payload)} bytes")
                return False

            # Publish message
            if self.js and subject.startswith(tuple(self.config.subjects)):
                # Use JetStream for persistent subjects
                ack = await self.js.publish(subject, payload, headers=headers)
                self.logger.debug(f"Published to JetStream {subject}: {ack.seq}")
            else:
                # Use core NATS for non-persistent subjects
                await self.nc.publish(subject, payload, headers=headers)
                self.logger.debug(f"Published to NATS {subject}")

            self.metrics["messages_published"] += 1
            return True

        except Exception as e:
            self.logger.error(f"Failed to publish to {subject}: {e}")
            return False

    async def subscribe(
        self,
        subject: str,
        handler: Callable,
        queue_group: Optional[str] = None,
        durable: Optional[str] = None,
    ) -> bool:
        """Subscribe to NATS subject with message handler."""
        if not self.connected:
            self.logger.error("Cannot subscribe: not connected to NATS")
            return False

        try:
            # Wrapper to handle message processing
            async def message_handler(msg):
                try:
                    # Parse message
                    data = json.loads(msg.data.decode("utf-8"))

                    # Call handler
                    await handler(subject, data, msg.headers)

                    # Acknowledge if JetStream
                    if hasattr(msg, "ack"):
                        await msg.ack()

                    self.metrics["messages_received"] += 1

                except Exception as e:
                    self.logger.error(f"Error handling message on {subject}: {e}")

                    # Negative acknowledge if JetStream
                    if hasattr(msg, "nak"):
                        await msg.nak()

            # Subscribe based on subject type
            if self.js and subject.startswith(tuple(self.config.subjects)):
                # JetStream subscription
                consumer_config = ConsumerConfig(
                    durable_name=durable or f"dgm-{subject.replace('.', '-')}",
                    deliver_policy="new",
                    ack_policy="explicit",
                    max_deliver=3,
                    ack_wait=30,
                )

                subscription = await self.js.subscribe(
                    subject, cb=message_handler, config=consumer_config, queue=queue_group
                )
            else:
                # Core NATS subscription
                subscription = await self.nc.subscribe(
                    subject, cb=message_handler, queue=queue_group
                )

            # Track subscription
            self.subscriptions[subject] = subscription

            if subject not in self.handlers:
                self.handlers[subject] = []
            self.handlers[subject].append(handler)

            self.logger.info(f"Subscribed to {subject}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to subscribe to {subject}: {e}")
            return False

    async def request(
        self, subject: str, data: Dict[str, Any], timeout: float = 5.0
    ) -> Optional[Dict[str, Any]]:
        """Send request and wait for reply."""
        if not self.connected:
            self.logger.error("Cannot send request: not connected to NATS")
            return None

        try:
            # Prepare request message
            message = {
                "id": str(uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "source": self.config.name,
                "data": data,
            }

            payload = json.dumps(message).encode("utf-8")

            # Send request
            response = await self.nc.request(subject, payload, timeout=timeout)

            # Parse response
            response_data = json.loads(response.data.decode("utf-8"))
            return response_data

        except asyncio.TimeoutError:
            self.logger.warning(f"Request to {subject} timed out")
            return None
        except Exception as e:
            self.logger.error(f"Request to {subject} failed: {e}")
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of NATS connection."""
        health = {
            "connected": self.connected,
            "server_info": None,
            "jetstream_enabled": self.config.enable_jetstream and self.js is not None,
            "subscriptions": len(self.subscriptions),
            "metrics": self.metrics.copy(),
        }

        if self.connected and self.nc:
            try:
                # Get server info
                health["server_info"] = {
                    "server_id": self.nc.server_info.get("server_id"),
                    "version": self.nc.server_info.get("version"),
                    "max_payload": self.nc.server_info.get("max_payload"),
                }

                # Test connectivity with ping
                rtt = await self.nc.rtt()
                health["rtt_ms"] = rtt * 1000

            except Exception as e:
                health["error"] = str(e)

        return health

    # Callback methods
    async def _error_callback(self, error):
        """Handle NATS connection errors."""
        self.logger.error(f"NATS error: {error}")
        self.metrics["connection_errors"] += 1
        self.metrics["last_error"] = str(error)

    async def _disconnected_callback(self):
        """Handle NATS disconnection."""
        self.logger.warning("Disconnected from NATS")
        self.connected = False

    async def _reconnected_callback(self):
        """Handle NATS reconnection."""
        self.logger.info("Reconnected to NATS")
        self.connected = True
        self.metrics["reconnections"] += 1
        self.metrics["last_connected"] = datetime.utcnow().isoformat()

    async def _closed_callback(self):
        """Handle NATS connection closure."""
        self.logger.info("NATS connection closed")
        self.connected = False
