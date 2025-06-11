#!/usr/bin/env python3
"""
Quantumagi Event Monitor - Real-time Solana Event Processing
Monitors blockchain events and triggers GS Engine policy synthesis
Integrates with ACGS backend for principle retrieval and policy management
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional

import aiohttp
import websockets

# Import our GS Engine
from governance_synthesis import PolicyCategory, QuantumagiGSEngine
from solana.rpc.commitment import Confirmed
from solana.rpc.websocket_api import connect
from solders.pubkey import Pubkey


@dataclass
class SolanaEvent:
    """Represents a Solana program event"""

    event_type: str
    program_id: str
    account: str
    data: Dict
    slot: int
    timestamp: datetime
    signature: str


@dataclass
class PolicySynthesisRequest:
    """Request for policy synthesis from constitutional principle"""

    principle_id: str
    principle_content: str
    category: str
    priority: str
    requester: str
    timestamp: datetime


class QuantumagiEventMonitor:
    """
    Real-time event monitor for Quantumagi governance system
    Listens for Solana events and triggers appropriate responses
    """

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize GS Engine
        self.gs_engine = QuantumagiGSEngine(config.get("gs_engine", {}))

        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "constitution_initialized": [],
            "policy_proposed": [],
            "policy_enacted": [],
            "vote_cast": [],
            "compliance_check_performed": [],
            "appeal_submitted": [],
            "security_alert": [],
        }

        # WebSocket connections
        self.solana_ws = None
        self.acgs_ws = None

        # Monitoring state
        self.is_monitoring = False
        self.processed_events = set()
        self.event_queue = asyncio.Queue()

        # Performance metrics
        self.metrics = {
            "events_processed": 0,
            "policies_synthesized": 0,
            "compliance_checks": 0,
            "errors": 0,
            "avg_processing_time": 0.0,
        }

    async def start_monitoring(self):
        """Start the event monitoring system"""
        self.logger.info("🚀 Starting Quantumagi Event Monitor")

        self.is_monitoring = True

        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_solana_events()),
            asyncio.create_task(self._monitor_acgs_events()),
            asyncio.create_task(self._process_event_queue()),
            asyncio.create_task(self._periodic_health_check()),
            asyncio.create_task(self._periodic_metrics_report()),
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Event monitoring failed: {e}")
            await self.stop_monitoring()
            raise

    async def stop_monitoring(self):
        """Stop the event monitoring system"""
        self.logger.info("🛑 Stopping Quantumagi Event Monitor")

        self.is_monitoring = False

        # Close WebSocket connections
        if self.solana_ws:
            await self.solana_ws.close()
        if self.acgs_ws:
            await self.acgs_ws.close()

    async def _monitor_solana_events(self):
        """Monitor Solana program events via WebSocket"""
        solana_url = self.config.get("solana_ws_url", "wss://api.devnet.solana.com")
        program_id = self.config.get(
            "program_id", "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS"
        )

        self.logger.info(f"📡 Connecting to Solana WebSocket: {solana_url}")

        try:
            async with connect(solana_url) as websocket:
                self.solana_ws = websocket

                # Subscribe to program account changes
                await websocket.program_subscribe(
                    Pubkey.from_string(program_id), commitment=Confirmed
                )

                self.logger.info(f"✅ Subscribed to program events: {program_id}")

                async for notification in websocket:
                    if not self.is_monitoring:
                        break

                    try:
                        await self._handle_solana_notification(notification)
                    except Exception as e:
                        self.logger.error(f"Error handling Solana notification: {e}")
                        self.metrics["errors"] += 1

        except Exception as e:
            self.logger.error(f"Solana WebSocket connection failed: {e}")
            if self.is_monitoring:
                # Attempt reconnection after delay
                await asyncio.sleep(5)
                await self._monitor_solana_events()

    async def _monitor_acgs_events(self):
        """Monitor ACGS backend events for new constitutional principles"""
        acgs_ws_url = self.config.get(
            "acgs_ws_url", "ws://localhost:8000/ws/governance"
        )

        if not acgs_ws_url:
            self.logger.warning(
                "ACGS WebSocket URL not configured, skipping ACGS monitoring"
            )
            return

        self.logger.info(f"📡 Connecting to ACGS WebSocket: {acgs_ws_url}")

        try:
            async with websockets.connect(acgs_ws_url) as websocket:
                self.acgs_ws = websocket

                # Send subscription message
                await websocket.send(
                    json.dumps(
                        {
                            "type": "subscribe",
                            "events": [
                                "principle_created",
                                "principle_updated",
                                "synthesis_requested",
                            ],
                        }
                    )
                )

                self.logger.info("✅ Subscribed to ACGS events")

                async for message in websocket:
                    if not self.is_monitoring:
                        break

                    try:
                        data = json.loads(message)
                        await self._handle_acgs_event(data)
                    except Exception as e:
                        self.logger.error(f"Error handling ACGS event: {e}")
                        self.metrics["errors"] += 1

        except Exception as e:
            self.logger.error(f"ACGS WebSocket connection failed: {e}")
            # Continue without ACGS if connection fails

    async def _handle_solana_notification(self, notification):
        """Process Solana program notifications"""
        try:
            # Parse notification data
            account_info = notification.get("result", {}).get("value", {})
            account_data = account_info.get("account", {}).get("data", [])

            if not account_data:
                return

            # Decode account data (simplified - would use proper Anchor decoding)
            event_type = self._determine_event_type(account_data)

            if event_type:
                event = SolanaEvent(
                    event_type=event_type,
                    program_id=self.config.get("program_id", ""),
                    account=notification.get("result", {})
                    .get("value", {})
                    .get("pubkey", ""),
                    data=account_info,
                    slot=notification.get("result", {})
                    .get("context", {})
                    .get("slot", 0),
                    timestamp=datetime.now(),
                    signature="",  # Would be populated from transaction
                )

                await self.event_queue.put(event)
                self.logger.debug(f"Queued Solana event: {event_type}")

        except Exception as e:
            self.logger.error(f"Error processing Solana notification: {e}")

    async def _handle_acgs_event(self, data):
        """Process ACGS backend events"""
        try:
            event_type = data.get("type")

            if event_type == "principle_created":
                await self._handle_new_principle(data.get("principle", {}))
            elif event_type == "synthesis_requested":
                await self._handle_synthesis_request(data.get("request", {}))
            elif event_type == "principle_updated":
                await self._handle_principle_update(data.get("principle", {}))

            self.logger.debug(f"Processed ACGS event: {event_type}")

        except Exception as e:
            self.logger.error(f"Error processing ACGS event: {e}")

    async def _process_event_queue(self):
        """Process queued events"""
        while self.is_monitoring:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)

                start_time = asyncio.get_event_loop().time()

                # Process event based on type
                await self._dispatch_event(event)

                # Update metrics
                processing_time = asyncio.get_event_loop().time() - start_time
                self.metrics["events_processed"] += 1
                self.metrics["avg_processing_time"] = (
                    self.metrics["avg_processing_time"]
                    * (self.metrics["events_processed"] - 1)
                    + processing_time
                ) / self.metrics["events_processed"]

                self.event_queue.task_done()

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
                self.metrics["errors"] += 1

    async def _dispatch_event(self, event: SolanaEvent):
        """Dispatch event to appropriate handlers"""
        handlers = self.event_handlers.get(event.event_type, [])

        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                self.logger.error(f"Event handler failed: {e}")

        # Built-in event processing
        if event.event_type == "policy_proposed":
            await self._handle_policy_proposed(event)
        elif event.event_type == "compliance_check_performed":
            await self._handle_compliance_check(event)
            self.metrics["compliance_checks"] += 1
        elif event.event_type == "appeal_submitted":
            await self._handle_appeal_submitted(event)

    async def _handle_new_principle(self, principle_data: Dict):
        """Handle new constitutional principle from ACGS"""
        self.logger.info(
            f"📜 New constitutional principle: {principle_data.get('id', 'Unknown')}"
        )

        try:
            # Automatically trigger policy synthesis for new principles
            if principle_data.get("auto_synthesize", True):
                synthesis_request = PolicySynthesisRequest(
                    principle_id=principle_data.get("id", ""),
                    principle_content=principle_data.get("content", ""),
                    category=principle_data.get("category", "governance"),
                    priority=principle_data.get("priority", "medium"),
                    requester="acgs_system",
                    timestamp=datetime.now(),
                )

                await self._synthesize_policy_from_principle(synthesis_request)

        except Exception as e:
            self.logger.error(f"Failed to process new principle: {e}")

    async def _synthesize_policy_from_principle(self, request: PolicySynthesisRequest):
        """Synthesize policy from constitutional principle"""
        self.logger.info(
            f"🧠 Synthesizing policy for principle: {request.principle_id}"
        )

        try:
            # Create mock principle object for GS Engine
            from governance_synthesis import MockConstitutionalPrinciple

            principle = MockConstitutionalPrinciple(
                id=request.principle_id,
                title=f"Principle {request.principle_id}",
                content=request.principle_content,
                category=request.category,
                rationale="Auto-generated from ACGS principle",
            )

            # Map category to PolicyCategory enum
            category_map = {
                "safety": PolicyCategory.SAFETY,
                "governance": PolicyCategory.GOVERNANCE,
                "financial": PolicyCategory.FINANCIAL,
                "prompt_constitution": PolicyCategory.PROMPT_CONSTITUTION,
            }

            category = category_map.get(
                request.category.lower(), PolicyCategory.GOVERNANCE
            )

            # Synthesize policy
            policy = await self.gs_engine.synthesize_policy_from_principle(
                principle, category
            )

            self.logger.info(f"✅ Policy synthesized: {policy.rule[:50]}...")
            self.metrics["policies_synthesized"] += 1

            # TODO: Submit policy to Solana program
            await self._submit_policy_to_solana(policy)

        except Exception as e:
            self.logger.error(f"Policy synthesis failed: {e}")

    async def _submit_policy_to_solana(self, policy):
        """Submit synthesized policy to Solana program"""
        # This would integrate with the Solana client to submit the policy
        self.logger.info(f"📋 Submitting policy to Solana: {policy.id}")

        # Mock implementation
        await asyncio.sleep(0.1)  # Simulate transaction time

        self.logger.info(f"✅ Policy submitted to Solana: {policy.id}")

    async def _handle_policy_proposed(self, event: SolanaEvent):
        """Handle policy proposal events"""
        self.logger.info("📋 Policy proposed event detected")

        # Extract policy data from event
        policy_data = event.data

        # Notify ACGS backend
        await self._notify_acgs_policy_proposed(policy_data)

    async def _handle_compliance_check(self, event: SolanaEvent):
        """Handle compliance check events"""
        self.logger.debug("🔍 Compliance check performed")

        # Log compliance metrics
        # Could trigger alerts for violations

    async def _handle_appeal_submitted(self, event: SolanaEvent):
        """Handle appeal submission events"""
        self.logger.info("⚖️ Appeal submitted")

        # Could trigger human review notifications

    async def _notify_acgs_policy_proposed(self, policy_data: Dict):
        """Notify ACGS backend of new policy proposal"""
        acgs_url = self.config.get("acgs_backend_url", "http://localhost:8000")

        if not acgs_url:
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{acgs_url}/api/policies/proposed", json=policy_data
                ) as response:
                    if response.status == 200:
                        self.logger.debug("✅ ACGS notified of policy proposal")
                    else:
                        self.logger.warning(
                            f"ACGS notification failed: {response.status}"
                        )

        except Exception as e:
            self.logger.error(f"Failed to notify ACGS: {e}")

    def _determine_event_type(self, account_data) -> Optional[str]:
        """Determine event type from account data"""
        # Simplified event type detection
        # In production, would properly decode Anchor account data

        if not account_data:
            return None

        # Mock event type detection based on data patterns
        data_str = str(account_data)

        if "constitution" in data_str.lower():
            return "constitution_initialized"
        elif "policy" in data_str.lower():
            return "policy_proposed"
        elif "vote" in data_str.lower():
            return "vote_cast"
        elif "compliance" in data_str.lower():
            return "compliance_check_performed"

        return None

    async def _periodic_health_check(self):
        """Perform periodic health checks"""
        while self.is_monitoring:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Check WebSocket connections
                solana_healthy = self.solana_ws and not self.solana_ws.closed
                acgs_healthy = not self.acgs_ws or not self.acgs_ws.closed

                if not solana_healthy:
                    self.logger.warning("⚠️ Solana WebSocket connection unhealthy")

                if not acgs_healthy:
                    self.logger.warning("⚠️ ACGS WebSocket connection unhealthy")

                # Log health status
                self.logger.info(
                    f"💓 Health check: Solana={solana_healthy}, ACGS={acgs_healthy}"
                )

            except Exception as e:
                self.logger.error(f"Health check failed: {e}")

    async def _periodic_metrics_report(self):
        """Report metrics periodically"""
        while self.is_monitoring:
            try:
                await asyncio.sleep(300)  # Report every 5 minutes

                self.logger.info(f"📊 Metrics Report:")
                self.logger.info(
                    f"  Events Processed: {self.metrics['events_processed']}"
                )
                self.logger.info(
                    f"  Policies Synthesized: {self.metrics['policies_synthesized']}"
                )
                self.logger.info(
                    f"  Compliance Checks: {self.metrics['compliance_checks']}"
                )
                self.logger.info(f"  Errors: {self.metrics['errors']}")
                self.logger.info(
                    f"  Avg Processing Time: {self.metrics['avg_processing_time']:.3f}s"
                )

            except Exception as e:
                self.logger.error(f"Metrics report failed: {e}")

    def register_event_handler(self, event_type: str, handler: Callable):
        """Register custom event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        self.logger.info(f"Registered handler for {event_type}")


# Example usage
async def main():
    """Example of running the event monitor"""

    config = {
        "solana_ws_url": "wss://api.devnet.solana.com",
        "program_id": "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS",
        "acgs_ws_url": "ws://localhost:8000/ws/governance",
        "acgs_backend_url": "http://localhost:8000",
        "gs_engine": {"llm_model": "gpt-4", "validation_threshold": 0.85},
    }

    monitor = QuantumagiEventMonitor(config)

    # Register custom event handlers
    async def custom_policy_handler(event):
        print(f"Custom handler: Policy event {event.event_type}")

    monitor.register_event_handler("policy_proposed", custom_policy_handler)

    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("Stopping monitor...")
        await monitor.stop_monitoring()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
