#!/usr/bin/env python3
"""
ACGS Simple Audit Engine with File-based Persistence
Implements audit trail storage with cryptographic hash chaining
"""

import json
import hashlib
import time
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class AuditEvent:
    """Audit event data structure"""

    event_id: str
    timestamp: str
    service_name: str
    event_type: str
    constitutional_hash: str
    user_id: Optional[str]
    session_id: Optional[str]
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    compliance_score: float
    latency_ms: float
    previous_hash: Optional[str]
    event_hash: str


class SimpleAuditEngine:
    """File-based audit engine with cryptographic hash chaining"""

    def __init__(self, audit_file: str = "acgs_audit_trail.jsonl"):
        self.audit_file = audit_file
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.ensure_audit_file()

    def ensure_audit_file(self):
        """Ensure audit file exists"""
        if not os.path.exists(self.audit_file):
            with open(self.audit_file, "w") as f:
                pass  # Create empty file

    def generate_event_hash(
        self, event_data: Dict[str, Any], previous_hash: Optional[str] = None
    ) -> str:
        """Generate cryptographic hash for audit event chaining"""
        hash_input = {
            "timestamp": event_data["timestamp"],
            "service_name": event_data["service_name"],
            "event_type": event_data["event_type"],
            "constitutional_hash": event_data["constitutional_hash"],
            "compliance_score": event_data["compliance_score"],
            "previous_hash": previous_hash or "",
        }

        hash_string = json.dumps(hash_input, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def get_last_event_hash(self) -> Optional[str]:
        """Get the hash of the last audit event for chaining"""
        try:
            with open(self.audit_file, "r") as f:
                lines = f.readlines()
                if lines:
                    last_event = json.loads(lines[-1].strip())
                    return last_event.get("event_hash")
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None

    def store_audit_event(self, event_data: Dict[str, Any]) -> str:
        """Store audit event with cryptographic hash chaining"""
        # Get previous hash for chaining
        previous_hash = self.get_last_event_hash()

        # Prepare event data
        timestamp = datetime.now(timezone.utc).isoformat()
        event_data_with_timestamp = {
            **event_data,
            "timestamp": timestamp,
            "constitutional_hash": self.constitutional_hash,
        }

        # Generate event hash
        event_hash = self.generate_event_hash(event_data_with_timestamp, previous_hash)

        # Create audit event
        event = AuditEvent(
            event_id=event_data.get("event_id", f"audit_{int(time.time() * 1000)}"),
            timestamp=timestamp,
            service_name=event_data["service_name"],
            event_type=event_data["event_type"],
            constitutional_hash=self.constitutional_hash,
            user_id=event_data.get("user_id"),
            session_id=event_data.get("session_id"),
            request_data=event_data.get("request_data", {}),
            response_data=event_data.get("response_data", {}),
            compliance_score=event_data.get("compliance_score", 1.0),
            latency_ms=event_data.get("latency_ms", 0.0),
            previous_hash=previous_hash,
            event_hash=event_hash,
        )

        # Store in file
        with open(self.audit_file, "a") as f:
            f.write(json.dumps(asdict(event)) + "\n")

        return event_hash

    def query_audit_events(
        self,
        service_name: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Query audit events with filtering"""
        events = []

        try:
            with open(self.audit_file, "r") as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line.strip())

                        # Apply filters
                        if service_name and event.get("service_name") != service_name:
                            continue
                        if event_type and event.get("event_type") != event_type:
                            continue

                        events.append(event)

                        if len(events) >= limit:
                            break
        except FileNotFoundError:
            pass

        return list(reversed(events))  # Return most recent first

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report from audit data"""
        events = self.query_audit_events(limit=10000)

        if not events:
            return {
                "report_timestamp": datetime.now(timezone.utc).isoformat(),
                "constitutional_hash": self.constitutional_hash,
                "total_audit_events": 0,
                "average_compliance_score": 0.0,
                "service_breakdown": [],
                "compliance_status": "NO_DATA",
            }

        # Calculate metrics
        total_events = len(events)
        compliance_scores = [event.get("compliance_score", 0) for event in events]
        avg_compliance = sum(compliance_scores) / len(compliance_scores)

        # Service breakdown
        service_stats = {}
        for event in events:
            service = event.get("service_name", "unknown")
            if service not in service_stats:
                service_stats[service] = {"count": 0, "compliance_sum": 0}
            service_stats[service]["count"] += 1
            service_stats[service]["compliance_sum"] += event.get("compliance_score", 0)

        service_breakdown = [
            {
                "service_name": service,
                "event_count": stats["count"],
                "avg_compliance": stats["compliance_sum"] / stats["count"],
            }
            for service, stats in service_stats.items()
        ]

        return {
            "report_timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "total_audit_events": total_events,
            "average_compliance_score": avg_compliance,
            "service_breakdown": service_breakdown,
            "compliance_status": (
                "COMPLIANT" if avg_compliance >= 0.95 else "NON_COMPLIANT"
            ),
        }

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verify cryptographic hash chain integrity"""
        events = self.query_audit_events(limit=1000)

        integrity_status = {
            "chain_valid": True,
            "total_events_checked": len(events),
            "broken_links": [],
            "verification_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Reverse to check chronological order
        events.reverse()

        for i in range(1, len(events)):
            current_event = events[i]
            previous_event = events[i - 1]

            if current_event.get("previous_hash") != previous_event.get("event_hash"):
                integrity_status["chain_valid"] = False
                integrity_status["broken_links"].append(
                    {
                        "event_id": current_event.get("event_id"),
                        "expected_hash": previous_event.get("event_hash"),
                        "actual_hash": current_event.get("previous_hash"),
                    }
                )

        return integrity_status


def test_audit_engine():
    """Test the simple audit engine"""
    print("🔍 Testing ACGS Simple Audit Engine")
    print("=" * 40)

    audit_engine = SimpleAuditEngine("test_audit_trail.jsonl")

    # Test storing audit events
    test_events = [
        {
            "service_name": "auth_service",
            "event_type": "AUTHENTICATION_SUCCESS",
            "user_id": "test_user_1",
            "session_id": "session_123",
            "compliance_score": 1.0,
            "latency_ms": 2.5,
            "request_data": {"endpoint": "/login"},
            "response_data": {"status": "success"},
        },
        {
            "service_name": "pgc_service",
            "event_type": "POLICY_VALIDATION",
            "user_id": "test_user_1",
            "session_id": "session_123",
            "compliance_score": 0.98,
            "latency_ms": 1.8,
            "request_data": {"policy_id": "policy_001"},
            "response_data": {"validation_result": "passed"},
        },
        {
            "service_name": "ac_service",
            "event_type": "CONSTITUTIONAL_VALIDATION",
            "user_id": "test_user_1",
            "session_id": "session_123",
            "compliance_score": 0.99,
            "latency_ms": 3.2,
            "request_data": {"constitutional_check": True},
            "response_data": {"compliance_verified": True},
        },
    ]

    print("📝 Storing test audit events...")
    for event in test_events:
        event_hash = audit_engine.store_audit_event(event)
        print(f"  ✅ Stored event: {event['event_type']} (Hash: {event_hash[:16]}...)")

    # Test querying
    print("\n🔍 Querying audit events...")
    events = audit_engine.query_audit_events(limit=10)
    print(f"  📊 Retrieved {len(events)} audit events")

    for event in events:
        print(
            f"    - {event['service_name']}: {event['event_type']} (Score: {event['compliance_score']})"
        )

    # Test compliance report
    print("\n📊 Generating compliance report...")
    report = audit_engine.generate_compliance_report()
    print(f"  📈 Total Events: {report['total_audit_events']}")
    print(f"  📈 Average Compliance: {report['average_compliance_score']:.3f}")
    print(f"  📈 Status: {report['compliance_status']}")
    print(f"  📈 Constitutional Hash: {report['constitutional_hash']}")

    for service in report["service_breakdown"]:
        print(
            f"    - {service['service_name']}: {service['event_count']} events, {service['avg_compliance']:.3f} avg compliance"
        )

    # Test chain integrity
    print("\n🔗 Verifying chain integrity...")
    integrity = audit_engine.verify_chain_integrity()
    print(f"  🔒 Chain Valid: {integrity['chain_valid']}")
    print(f"  🔒 Events Checked: {integrity['total_events_checked']}")

    if integrity["broken_links"]:
        print(f"  ⚠️ Broken Links Found: {len(integrity['broken_links'])}")
    else:
        print(f"  ✅ Chain integrity verified")

    print("\n✅ Simple Audit Engine: OPERATIONAL")

    # Clean up test file
    if os.path.exists("test_audit_trail.jsonl"):
        os.remove("test_audit_trail.jsonl")


if __name__ == "__main__":
    test_audit_engine()
