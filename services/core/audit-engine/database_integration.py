#!/usr/bin/env python3
"""
ACGS Audit Engine Database Integration
Implements persistent PostgreSQL backend for audit trail storage and compliance reporting
"""

import asyncio
import asyncpg
import json
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager

@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_id: str
    timestamp: datetime
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

class AuditEngineDatabase:
    """PostgreSQL-backed audit engine with cryptographic hash chaining"""
    
    def __init__(self, database_url: str = "postgresql://localhost:5432/acgs_audit"):
        self.database_url = database_url
        self.pool = None
        self.constitutional_hash = "cdd01ef066bc6cf2"
        
    async def initialize(self):
        """Initialize database connection pool and create tables"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            await self.create_tables()
            print("✅ Audit Engine Database initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize audit database: {e}")
            # Fallback to SQLite for development
            await self.initialize_sqlite_fallback()
    
    async def initialize_sqlite_fallback(self):
        """Fallback to SQLite for development/testing"""
        import aiosqlite
        self.sqlite_db = "acgs_audit.db"
        
        async with aiosqlite.connect(self.sqlite_db) as db:
            await self.create_sqlite_tables(db)
            await db.commit()
        print("✅ Audit Engine SQLite fallback initialized")
    
    async def create_tables(self):
        """Create audit tables in PostgreSQL"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id VARCHAR(64) PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    service_name VARCHAR(100) NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    constitutional_hash VARCHAR(64) NOT NULL,
                    user_id VARCHAR(100),
                    session_id VARCHAR(100),
                    request_data JSONB,
                    response_data JSONB,
                    compliance_score DECIMAL(5,4) NOT NULL,
                    latency_ms DECIMAL(10,3) NOT NULL,
                    previous_hash VARCHAR(64),
                    event_hash VARCHAR(64) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp);
                CREATE INDEX IF NOT EXISTS idx_audit_service ON audit_events(service_name);
                CREATE INDEX IF NOT EXISTS idx_audit_constitutional ON audit_events(constitutional_hash);
                CREATE INDEX IF NOT EXISTS idx_audit_compliance ON audit_events(compliance_score);
                
                CREATE TABLE IF NOT EXISTS audit_chain_integrity (
                    chain_id SERIAL PRIMARY KEY,
                    last_event_hash VARCHAR(64) NOT NULL,
                    event_count BIGINT NOT NULL,
                    last_updated TIMESTAMPTZ DEFAULT NOW()
                );
            """)
    
    async def create_sqlite_tables(self, db):
        """Create audit tables in SQLite"""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                service_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                constitutional_hash TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                request_data TEXT,
                response_data TEXT,
                compliance_score REAL NOT NULL,
                latency_ms REAL NOT NULL,
                previous_hash TEXT,
                event_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp);
            CREATE INDEX IF NOT EXISTS idx_audit_service ON audit_events(service_name);
        """)
    
    def generate_event_hash(self, event_data: Dict[str, Any], previous_hash: Optional[str] = None) -> str:
        """Generate cryptographic hash for audit event chaining"""
        hash_input = {
            'timestamp': event_data['timestamp'],
            'service_name': event_data['service_name'],
            'event_type': event_data['event_type'],
            'constitutional_hash': event_data['constitutional_hash'],
            'compliance_score': event_data['compliance_score'],
            'previous_hash': previous_hash or ""
        }
        
        hash_string = json.dumps(hash_input, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    async def get_last_event_hash(self) -> Optional[str]:
        """Get the hash of the last audit event for chaining"""
        if hasattr(self, 'sqlite_db'):
            import aiosqlite
            async with aiosqlite.connect(self.sqlite_db) as db:
                cursor = await db.execute(
                    "SELECT event_hash FROM audit_events ORDER BY timestamp DESC LIMIT 1"
                )
                row = await cursor.fetchone()
                return row[0] if row else None
        else:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT event_hash FROM audit_events ORDER BY timestamp DESC LIMIT 1"
                )
                return row['event_hash'] if row else None
    
    async def store_audit_event(self, event_data: Dict[str, Any]) -> str:
        """Store audit event with cryptographic hash chaining"""
        # Get previous hash for chaining
        previous_hash = await self.get_last_event_hash()
        
        # Generate event hash
        event_hash = self.generate_event_hash(event_data, previous_hash)
        
        # Create audit event
        event = AuditEvent(
            event_id=event_data.get('event_id', f"audit_{int(time.time() * 1000)}"),
            timestamp=datetime.now(timezone.utc),
            service_name=event_data['service_name'],
            event_type=event_data['event_type'],
            constitutional_hash=self.constitutional_hash,
            user_id=event_data.get('user_id'),
            session_id=event_data.get('session_id'),
            request_data=event_data.get('request_data', {}),
            response_data=event_data.get('response_data', {}),
            compliance_score=event_data.get('compliance_score', 1.0),
            latency_ms=event_data.get('latency_ms', 0.0),
            previous_hash=previous_hash,
            event_hash=event_hash
        )
        
        # Store in database
        if hasattr(self, 'sqlite_db'):
            await self.store_sqlite_event(event)
        else:
            await self.store_postgres_event(event)
        
        return event_hash
    
    async def store_postgres_event(self, event: AuditEvent):
        """Store audit event in PostgreSQL"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO audit_events (
                    event_id, timestamp, service_name, event_type, constitutional_hash,
                    user_id, session_id, request_data, response_data, compliance_score,
                    latency_ms, previous_hash, event_hash
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """, 
                event.event_id, event.timestamp, event.service_name, event.event_type,
                event.constitutional_hash, event.user_id, event.session_id,
                json.dumps(event.request_data), json.dumps(event.response_data),
                event.compliance_score, event.latency_ms, event.previous_hash, event.event_hash
            )
    
    async def store_sqlite_event(self, event: AuditEvent):
        """Store audit event in SQLite"""
        import aiosqlite
        async with aiosqlite.connect(self.sqlite_db) as db:
            await db.execute("""
                INSERT INTO audit_events (
                    event_id, timestamp, service_name, event_type, constitutional_hash,
                    user_id, session_id, request_data, response_data, compliance_score,
                    latency_ms, previous_hash, event_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id, event.timestamp.isoformat(), event.service_name, event.event_type,
                event.constitutional_hash, event.user_id, event.session_id,
                json.dumps(event.request_data), json.dumps(event.response_data),
                event.compliance_score, event.latency_ms, event.previous_hash, event.event_hash
            ))
            await db.commit()
    
    async def query_audit_events(self, 
                                service_name: Optional[str] = None,
                                event_type: Optional[str] = None,
                                start_time: Optional[datetime] = None,
                                end_time: Optional[datetime] = None,
                                limit: int = 100) -> List[Dict[str, Any]]:
        """Query audit events with filtering"""
        conditions = []
        params = []
        
        if service_name:
            conditions.append("service_name = $1" if not hasattr(self, 'sqlite_db') else "service_name = ?")
            params.append(service_name)
        
        if event_type:
            param_num = len(params) + 1
            conditions.append(f"event_type = ${param_num}" if not hasattr(self, 'sqlite_db') else "event_type = ?")
            params.append(event_type)
        
        if start_time:
            param_num = len(params) + 1
            conditions.append(f"timestamp >= ${param_num}" if not hasattr(self, 'sqlite_db') else "timestamp >= ?")
            params.append(start_time.isoformat() if hasattr(self, 'sqlite_db') else start_time)
        
        if end_time:
            param_num = len(params) + 1
            conditions.append(f"timestamp <= ${param_num}" if not hasattr(self, 'sqlite_db') else "timestamp <= ?")
            params.append(end_time.isoformat() if hasattr(self, 'sqlite_db') else end_time)
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        limit_param = len(params) + 1
        
        query = f"""
            SELECT * FROM audit_events
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT ${limit_param if not hasattr(self, 'sqlite_db') else '?'}
        """
        params.append(limit)
        
        if hasattr(self, 'sqlite_db'):
            import aiosqlite
            async with aiosqlite.connect(self.sqlite_db) as db:
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        else:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
    
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report from audit data"""
        if hasattr(self, 'sqlite_db'):
            import aiosqlite
            async with aiosqlite.connect(self.sqlite_db) as db:
                # Total events
                cursor = await db.execute("SELECT COUNT(*) FROM audit_events")
                total_events = (await cursor.fetchone())[0]
                
                # Compliance metrics
                cursor = await db.execute("SELECT AVG(compliance_score) FROM audit_events")
                avg_compliance = (await cursor.fetchone())[0] or 0
                
                # Service breakdown
                cursor = await db.execute("""
                    SELECT service_name, COUNT(*) as event_count, AVG(compliance_score) as avg_compliance
                    FROM audit_events GROUP BY service_name
                """)
                service_breakdown = await cursor.fetchall()
        else:
            async with self.pool.acquire() as conn:
                total_events = await conn.fetchval("SELECT COUNT(*) FROM audit_events")
                avg_compliance = await conn.fetchval("SELECT AVG(compliance_score) FROM audit_events") or 0
                service_breakdown = await conn.fetch("""
                    SELECT service_name, COUNT(*) as event_count, AVG(compliance_score) as avg_compliance
                    FROM audit_events GROUP BY service_name
                """)
        
        return {
            'report_timestamp': datetime.now(timezone.utc).isoformat(),
            'constitutional_hash': self.constitutional_hash,
            'total_audit_events': total_events,
            'average_compliance_score': float(avg_compliance),
            'service_breakdown': [
                {
                    'service_name': row[0] if hasattr(self, 'sqlite_db') else row['service_name'],
                    'event_count': row[1] if hasattr(self, 'sqlite_db') else row['event_count'],
                    'avg_compliance': float(row[2] if hasattr(self, 'sqlite_db') else row['avg_compliance'])
                }
                for row in service_breakdown
            ],
            'compliance_status': 'COMPLIANT' if avg_compliance >= 0.95 else 'NON_COMPLIANT'
        }
    
    async def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verify cryptographic hash chain integrity"""
        events = await self.query_audit_events(limit=1000)
        
        integrity_status = {
            'chain_valid': True,
            'total_events_checked': len(events),
            'broken_links': [],
            'verification_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        for i in range(len(events) - 1):
            current_event = events[i]
            next_event = events[i + 1]
            
            if current_event['previous_hash'] != next_event['event_hash']:
                integrity_status['chain_valid'] = False
                integrity_status['broken_links'].append({
                    'event_id': current_event['event_id'],
                    'expected_hash': next_event['event_hash'],
                    'actual_hash': current_event['previous_hash']
                })
        
        return integrity_status
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()

# Example usage and testing
async def test_audit_engine():
    """Test the audit engine database integration"""
    print("🔍 Testing ACGS Audit Engine Database Integration")
    print("=" * 55)
    
    audit_db = AuditEngineDatabase()
    await audit_db.initialize()
    
    # Test storing audit events
    test_events = [
        {
            'service_name': 'auth_service',
            'event_type': 'AUTHENTICATION_SUCCESS',
            'user_id': 'test_user_1',
            'session_id': 'session_123',
            'compliance_score': 1.0,
            'latency_ms': 2.5,
            'request_data': {'endpoint': '/login'},
            'response_data': {'status': 'success'}
        },
        {
            'service_name': 'pgc_service',
            'event_type': 'POLICY_VALIDATION',
            'user_id': 'test_user_1',
            'session_id': 'session_123',
            'compliance_score': 0.98,
            'latency_ms': 1.8,
            'request_data': {'policy_id': 'policy_001'},
            'response_data': {'validation_result': 'passed'}
        }
    ]
    
    print("📝 Storing test audit events...")
    for event in test_events:
        event_hash = await audit_db.store_audit_event(event)
        print(f"  ✅ Stored event: {event['event_type']} (Hash: {event_hash[:16]}...)")
    
    # Test querying
    print("\n🔍 Querying audit events...")
    events = await audit_db.query_audit_events(limit=10)
    print(f"  📊 Retrieved {len(events)} audit events")
    
    # Test compliance report
    print("\n📊 Generating compliance report...")
    report = await audit_db.generate_compliance_report()
    print(f"  📈 Total Events: {report['total_audit_events']}")
    print(f"  📈 Average Compliance: {report['average_compliance_score']:.3f}")
    print(f"  📈 Status: {report['compliance_status']}")
    
    # Test chain integrity
    print("\n🔗 Verifying chain integrity...")
    integrity = await audit_db.verify_chain_integrity()
    print(f"  🔒 Chain Valid: {integrity['chain_valid']}")
    print(f"  🔒 Events Checked: {integrity['total_events_checked']}")
    
    await audit_db.close()
    print("\n✅ Audit Engine Database Integration: COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_audit_engine())
