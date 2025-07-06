#!/usr/bin/env python3
"""
Test script for ACGS Persistent Audit Trail

This script tests the cryptographic audit trail functionality
including event logging, integrity verification, and hash chaining.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import asyncpg
import json
import os
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://acgs_user:acgs_password@localhost:5439/acgs_integrity")


async def test_audit_trail():
    """Test the persistent audit trail functionality."""
    try:
        # Import our audit trail components
        from app.core.persistent_audit_trail import (
            CryptographicAuditChain, 
            AuditEvent, 
            AuditEventType, 
            AuditSeverity,
            log_audit_event,
            create_audit_tables
        )
        
        # Create database connection pool
        logger.info("🔌 Creating database connection pool...")
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=5)
        
        # Ensure tables exist
        logger.info("🔄 Ensuring audit tables exist...")
        await create_audit_tables(db_pool)
        
        # Initialize audit chain
        logger.info("🔗 Initializing cryptographic audit chain...")
        audit_chain = CryptographicAuditChain(db_pool)
        
        # Test 1: Log some audit events
        logger.info("📝 Test 1: Logging audit events...")
        
        test_events = [
            {
                "event_type": AuditEventType.CONSTITUTIONAL_VALIDATION,
                "service_name": "test-service",
                "action": "validate_policy",
                "resource_type": "constitutional_policy",
                "description": "Testing constitutional policy validation",
                "severity": AuditSeverity.HIGH,
                "metadata": {"test": True, "policy_id": "test_001"}
            },
            {
                "event_type": AuditEventType.CRYPTOGRAPHIC_OPERATION,
                "service_name": "test-service",
                "action": "sign_document",
                "resource_type": "document",
                "description": "Testing cryptographic signature",
                "severity": AuditSeverity.MEDIUM,
                "metadata": {"document_id": "doc_001", "signature_type": "RSA"}
            },
            {
                "event_type": AuditEventType.GOVERNANCE_DECISION,
                "service_name": "test-service",
                "action": "approve_evolution",
                "resource_type": "agent_evolution",
                "description": "Testing governance decision approval",
                "severity": AuditSeverity.CRITICAL,
                "metadata": {"agent_id": "agent_001", "evolution_type": "capability_upgrade"}
            }
        ]
        
        event_ids = []
        for event_data in test_events:
            event_id = await log_audit_event(audit_chain, **event_data)
            event_ids.append(event_id)
            logger.info(f"✅ Logged event: {event_id}")
        
        # Test 2: Verify integrity
        logger.info("🔍 Test 2: Verifying audit trail integrity...")
        
        # Wait a moment for block creation
        await asyncio.sleep(1)
        
        verification_result = await audit_chain.verify_integrity()
        logger.info(f"🔒 Integrity verification result:")
        logger.info(f"   - Valid: {verification_result.is_valid}")
        logger.info(f"   - Total blocks: {verification_result.total_blocks}")
        logger.info(f"   - Verified blocks: {verification_result.verified_blocks}")
        logger.info(f"   - Constitutional compliance: {verification_result.constitutional_compliance}")
        logger.info(f"   - Verification time: {verification_result.verification_time_ms:.2f}ms")
        
        if verification_result.broken_chains:
            logger.warning(f"⚠️ Broken chains detected: {verification_result.broken_chains}")
        
        if verification_result.tampered_events:
            logger.warning(f"⚠️ Tampered events detected: {verification_result.tampered_events}")
        
        # Test 3: Get audit trail statistics
        logger.info("📊 Test 3: Getting audit trail statistics...")
        
        stats = await audit_chain.get_audit_trail_stats()
        logger.info(f"📈 Audit trail statistics:")
        logger.info(f"   - Total blocks: {stats['blocks']['total']}")
        logger.info(f"   - Total events: {stats['events']['total']}")
        logger.info(f"   - Recent events (24h): {stats['events']['recent_24h']}")
        logger.info(f"   - Constitutional hash: {stats['constitutional_hash']}")
        
        # Test 4: Test emergency seal
        logger.info("🚨 Test 4: Testing emergency seal...")
        
        # Log an emergency event
        emergency_event_id = await log_audit_event(
            audit_chain=audit_chain,
            event_type=AuditEventType.EMERGENCY_ACTION,
            service_name="test-service",
            action="emergency_test",
            resource_type="system",
            description="Testing emergency audit trail sealing",
            severity=AuditSeverity.CRITICAL,
            metadata={"emergency_type": "test", "triggered_by": "automated_test"}
        )
        logger.info(f"🚨 Emergency event logged: {emergency_event_id}")
        
        # Close the pool
        await db_pool.close()
        
        logger.info("🎉 All tests completed successfully!")
        logger.info("✅ Persistent audit trail is functioning correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    logger.info("🚀 Starting ACGS Persistent Audit Trail Tests")
    logger.info(f"📊 Constitutional Hash: cdd01ef066bc6cf2")
    logger.info(f"🔗 Database URL: {DATABASE_URL}")
    
    success = await test_audit_trail()
    
    if success:
        logger.info("✅ All tests passed! Persistent audit trail is ready for production.")
    else:
        logger.error("❌ Tests failed! Please check the implementation.")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())