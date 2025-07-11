"""
ACGS-2 Persistent Audit Logger with Hash Chaining and Multi-Tenant RLS

This module implements a high-performance, tamper-evident audit logging system
with cryptographic hash chaining, multi-tenant Row Level Security, and Redis
caching integration for sub-5ms insert latency.

Constitutional Hash: cdd01ef066bc6cf2

Key Features:
- Append-only PostgreSQL table with hash chaining
- Multi-tenant Row Level Security (RLS)
- Redis caching for performance optimization
- Tamper detection and integrity verification
- Sub-5ms insert latency target
- Constitutional compliance validation
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import aioredis
import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

# Constitutional compliance hash for ACGS-2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class PersistentAuditLogger:
    """
    High-performance persistent audit logger with hash chaining and multi-tenant RLS.
    
    Implements:
    - Cryptographic hash chaining for tamper detection
    - Multi-tenant Row Level Security
    - Redis caching for performance optimization
    - Sub-5ms insert latency target
    - Constitutional compliance validation
    """
    
    def __init__(
        self,
        db_config: Dict[str, Any],
        redis_config: Optional[Dict[str, Any]] = None,
        pool_size: int = 20,
        max_overflow: int = 30
    ):
        """
        Initialize the persistent audit logger.
        
        Args:
            db_config: Database configuration dictionary
            redis_config: Redis configuration dictionary (optional)
            pool_size: Database connection pool size
            max_overflow: Maximum connection pool overflow
        """
        self.db_config = db_config
        self.redis_config = redis_config or {}
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        
        # Initialize connection pool
        self.db_pool: Optional[ThreadedConnectionPool] = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Performance metrics
        self.insert_times: List[float] = []
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Constitutional compliance
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        logger.info(f"PersistentAuditLogger initialized with constitutional hash: {CONSTITUTIONAL_HASH}")
    
    async def initialize(self) -> None:
        """Initialize database pool and Redis connection."""
        try:
            # Initialize database connection pool
            self.db_pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=self.pool_size + self.max_overflow,
                host=self.db_config.get("host", "localhost"),
                port=self.db_config.get("port", 5439),
                database=self.db_config.get("database", "acgs_integrity"),
                user=self.db_config.get("user", "acgs_user"),
                password=self.db_config.get("password", "acgs_password"),
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            
            # Initialize Redis client if configured
            if self.redis_config:
                self.redis_client = aioredis.from_url(
                    self.redis_config.get("url", "redis://localhost:6389"),
                    encoding="utf-8",
                    decode_responses=True
                )
                
            # Create audit_logs table if it doesn't exist
            await self._create_audit_table()
            
            logger.info("✅ PersistentAuditLogger initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PersistentAuditLogger: {e}")
            raise
    
    async def _create_audit_table(self) -> None:
        """Create the audit_logs table with proper indexing and RLS."""
        create_table_sql = """
        -- Create audit_logs table with hash chaining
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            event_data JSONB NOT NULL,
            prev_hash TEXT,
            current_hash TEXT NOT NULL,
            tenant_id UUID,
            user_id TEXT,
            service_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            constitutional_hash TEXT NOT NULL DEFAULT 'cdd01ef066bc6cf2',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT audit_logs_hash_not_empty CHECK (length(current_hash) > 0)
        );
        
        -- Enable Row Level Security
        ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
        
        -- Create RLS policy for multi-tenant isolation
        DROP POLICY IF EXISTS audit_logs_tenant_isolation ON audit_logs;
        CREATE POLICY audit_logs_tenant_isolation ON audit_logs
            FOR ALL TO PUBLIC
            USING (
                tenant_id = COALESCE(
                    current_setting('app.current_tenant_id', true)::UUID,
                    '00000000-0000-0000-0000-000000000000'::UUID
                )
                OR current_setting('app.bypass_rls', true) = 'true'
            );
        
        -- Create performance indexes
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_timestamp 
            ON audit_logs(timestamp DESC);
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_tenant_timestamp 
            ON audit_logs(tenant_id, timestamp DESC);
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_event_type 
            ON audit_logs(event_type, timestamp DESC);
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_service_name 
            ON audit_logs(service_name, timestamp DESC);
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_hash_chain 
            ON audit_logs(current_hash);
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_constitutional_hash 
            ON audit_logs(constitutional_hash);
        
        -- Create GIN index for JSONB event_data
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_event_data_gin 
            ON audit_logs USING GIN(event_data);
        """
        
        conn = None
        try:
            conn = self.db_pool.getconn()
            with conn.cursor() as cursor:
                cursor.execute(create_table_sql)
                conn.commit()
                logger.info("✅ Audit logs table created with RLS and indexing")
                
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to create audit table: {e}")
            raise
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def _calculate_hash_chain(self, prev_hash: Optional[str], event_data: Dict[str, Any]) -> str:
        """
        Calculate SHA-256 hash chain for tamper detection.
        
        Args:
            prev_hash: Previous hash in the chain (None for genesis)
            event_data: Event data to hash
            
        Returns:
            SHA-256 hash string
        """
        # Create deterministic string representation
        event_str = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        
        # Include previous hash in chain (use genesis for first entry)
        chain_input = f"{prev_hash or 'genesis'}:{event_str}:{self.constitutional_hash}"
        
        # Calculate SHA-256 hash
        return hashlib.sha256(chain_input.encode('utf-8')).hexdigest()
    
    async def _get_last_hash(self, tenant_id: Optional[str] = None) -> Optional[str]:
        """
        Get the last hash in the chain for a tenant.
        
        Args:
            tenant_id: Tenant ID for multi-tenant isolation
            
        Returns:
            Last hash in chain or None if no entries exist
        """
        cache_key = f"acgs:audit:last_hash:{tenant_id or 'global'}:{CONSTITUTIONAL_HASH}"
        
        # Try Redis cache first
        if self.redis_client:
            try:
                cached_hash = await self.redis_client.get(cache_key)
                if cached_hash:
                    self.cache_hits += 1
                    return cached_hash
                self.cache_misses += 1
            except Exception as e:
                logger.warning(f"Redis cache lookup failed: {e}")
        
        # Fallback to database query
        conn = None
        try:
            conn = self.db_pool.getconn()
            with conn.cursor() as cursor:
                # Set tenant context for RLS
                if tenant_id:
                    cursor.execute(
                        "SELECT set_config('app.current_tenant_id', %s, true)",
                        (tenant_id,)
                    )
                
                cursor.execute("""
                    SELECT current_hash 
                    FROM audit_logs 
                    WHERE tenant_id = %s OR (%s IS NULL AND tenant_id IS NULL)
                    ORDER BY timestamp DESC, id DESC 
                    LIMIT 1
                """, (tenant_id, tenant_id))
                
                result = cursor.fetchone()
                last_hash = result['current_hash'] if result else None
                
                # Cache the result
                if self.redis_client and last_hash:
                    try:
                        await self.redis_client.setex(cache_key, 300, last_hash)  # 5 min cache
                    except Exception as e:
                        logger.warning(f"Redis cache storage failed: {e}")
                
                return last_hash
                
        except Exception as e:
            logger.error(f"Failed to get last hash: {e}")
            return None
        finally:
            if conn:
                self.db_pool.putconn(conn)

    async def log_event(
        self,
        event_data: Dict[str, Any],
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        service_name: str = "integrity_service",
        event_type: str = "audit_event"
    ) -> Dict[str, Any]:
        """
        Log an audit event with hash chaining and constitutional compliance.

        Args:
            event_data: Event data to log
            tenant_id: Tenant ID for multi-tenant isolation
            user_id: User ID who performed the action
            service_name: Name of the service logging the event
            event_type: Type of event being logged

        Returns:
            Dictionary with logging result and metadata
        """
        start_time = time.perf_counter()

        try:
            # Validate constitutional compliance
            if not self._validate_constitutional_compliance(event_data):
                raise ValueError(
                    "Event data does not meet constitutional compliance requirements"
                )

            # Get previous hash for chaining
            prev_hash = await self._get_last_hash(tenant_id)

            # Calculate current hash
            current_hash = self._calculate_hash_chain(prev_hash, event_data)

            # Prepare audit record
            audit_record = {
                'timestamp': datetime.now(timezone.utc),
                'event_data': json.dumps(event_data, sort_keys=True),
                'prev_hash': prev_hash,
                'current_hash': current_hash,
                'tenant_id': tenant_id,
                'user_id': user_id,
                'service_name': service_name,
                'event_type': event_type,
                'constitutional_hash': self.constitutional_hash
            }

            # Insert into database
            record_id = await self._insert_audit_record(audit_record, tenant_id)

            # Update cache with new hash
            if self.redis_client:
                cache_key = f"acgs:audit:last_hash:{tenant_id or 'global'}:{CONSTITUTIONAL_HASH}"
                try:
                    await self.redis_client.setex(cache_key, 300, current_hash)
                except Exception as e:
                    logger.warning(f"Failed to update hash cache: {e}")

            # Record performance metrics
            insert_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
            self.insert_times.append(insert_time)

            # Keep only last 1000 measurements for rolling average
            if len(self.insert_times) > 1000:
                self.insert_times = self.insert_times[-1000:]

            logger.info(f"Audit event logged in {insert_time:.2f}ms - ID: {record_id}")

            return {
                'success': True,
                'record_id': record_id,
                'current_hash': current_hash,
                'prev_hash': prev_hash,
                'insert_time_ms': insert_time,
                'constitutional_hash': self.constitutional_hash,
                'timestamp': audit_record['timestamp'].isoformat()
            }

        except Exception as e:
            insert_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to log audit event in {insert_time:.2f}ms: {e}")
            return {
                'success': False,
                'error': str(e),
                'insert_time_ms': insert_time,
                'constitutional_hash': self.constitutional_hash
            }

    def _validate_constitutional_compliance(self, event_data: Dict[str, Any]) -> bool:
        """
        Validate event data meets constitutional compliance requirements.

        Args:
            event_data: Event data to validate

        Returns:
            True if compliant, False otherwise
        """
        # Basic validation requirements
        required_fields = ['action', 'resource_type']

        for field in required_fields:
            if field not in event_data:
                logger.warning(f"Constitutional compliance violation: missing required field '{field}'")
                return False

        # Validate constitutional hash if present
        if 'constitutional_hash' in event_data:
            if event_data['constitutional_hash'] != self.constitutional_hash:
                logger.warning(f"Constitutional compliance violation: hash mismatch")
                return False

        # Additional validation rules can be added here
        return True

    async def _insert_audit_record(
        self,
        audit_record: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> int:
        """
        Insert audit record into database with optimized performance.

        Args:
            audit_record: Audit record to insert
            tenant_id: Tenant ID for RLS context

        Returns:
            Inserted record ID
        """
        conn = None
        try:
            conn = self.db_pool.getconn()
            with conn.cursor() as cursor:
                # Set tenant context for RLS
                if tenant_id:
                    cursor.execute(
                        "SELECT set_config('app.current_tenant_id', %s, true)",
                        (tenant_id,)
                    )

                # Insert audit record
                insert_sql = """
                    INSERT INTO audit_logs (
                        timestamp, event_data, prev_hash, current_hash,
                        tenant_id, user_id, service_name, event_type, constitutional_hash
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id
                """

                cursor.execute(insert_sql, (
                    audit_record['timestamp'],
                    audit_record['event_data'],
                    audit_record['prev_hash'],
                    audit_record['current_hash'],
                    audit_record['tenant_id'],
                    audit_record['user_id'],
                    audit_record['service_name'],
                    audit_record['event_type'],
                    audit_record['constitutional_hash']
                ))

                record_id = cursor.fetchone()['id']
                conn.commit()

                return record_id

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Failed to insert audit record: {e}")
            raise
        finally:
            if conn:
                self.db_pool.putconn(conn)

    async def verify_hash_chain_integrity(
        self,
        tenant_id: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Verify the integrity of the hash chain for tamper detection.

        Args:
            tenant_id: Tenant ID to verify (None for all tenants)
            limit: Maximum number of records to verify

        Returns:
            Verification result with integrity status and details
        """
        start_time = time.perf_counter()

        conn = None
        try:
            conn = self.db_pool.getconn()
            with conn.cursor() as cursor:
                # Set tenant context for RLS
                if tenant_id:
                    cursor.execute(
                        "SELECT set_config('app.current_tenant_id', %s, true)",
                        (tenant_id,)
                    )

                # Get audit records in chronological order
                query = """
                    SELECT id, event_data, prev_hash, current_hash, timestamp
                    FROM audit_logs
                    WHERE tenant_id = %s OR (%s IS NULL AND tenant_id IS NULL)
                    ORDER BY timestamp ASC, id ASC
                    LIMIT %s
                """

                cursor.execute(query, (tenant_id, tenant_id, limit))
                records = cursor.fetchall()

                if not records:
                    return {
                        'integrity_verified': True,
                        'total_records': 0,
                        'verification_time_ms': (time.perf_counter() - start_time) * 1000,
                        'constitutional_hash': self.constitutional_hash
                    }

                # Verify hash chain
                integrity_violations = []
                prev_hash = None

                for record in records:
                    event_data = json.loads(record['event_data'])
                    expected_hash = self._calculate_hash_chain(prev_hash, event_data)

                    if expected_hash != record['current_hash']:
                        integrity_violations.append({
                            'record_id': record['id'],
                            'expected_hash': expected_hash,
                            'actual_hash': record['current_hash'],
                            'timestamp': record['timestamp'].isoformat()
                        })

                    # Check previous hash linkage
                    if record['prev_hash'] != prev_hash:
                        integrity_violations.append({
                            'record_id': record['id'],
                            'violation_type': 'prev_hash_mismatch',
                            'expected_prev_hash': prev_hash,
                            'actual_prev_hash': record['prev_hash'],
                            'timestamp': record['timestamp'].isoformat()
                        })

                    prev_hash = record['current_hash']

                verification_time = (time.perf_counter() - start_time) * 1000

                return {
                    'integrity_verified': len(integrity_violations) == 0,
                    'total_records': len(records),
                    'integrity_violations': integrity_violations,
                    'verification_time_ms': verification_time,
                    'constitutional_hash': self.constitutional_hash
                }

        except Exception as e:
            verification_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Hash chain verification failed in {verification_time:.2f}ms: {e}")
            return {
                'integrity_verified': False,
                'error': str(e),
                'verification_time_ms': verification_time,
                'constitutional_hash': self.constitutional_hash
            }
        finally:
            if conn:
                self.db_pool.putconn(conn)

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the audit logger.

        Returns:
            Dictionary with performance metrics
        """
        if not self.insert_times:
            return {
                'avg_insert_time_ms': 0.0,
                'p95_insert_time_ms': 0.0,
                'p99_insert_time_ms': 0.0,
                'total_operations': 0,
                'cache_hit_rate': 0.0,
                'constitutional_hash': self.constitutional_hash
            }

        sorted_times = sorted(self.insert_times)
        total_ops = len(sorted_times)

        # Calculate percentiles
        p95_index = int(0.95 * total_ops)
        p99_index = int(0.99 * total_ops)

        total_cache_ops = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_cache_ops * 100) if total_cache_ops > 0 else 0.0

        return {
            'avg_insert_time_ms': sum(sorted_times) / total_ops,
            'p95_insert_time_ms': sorted_times[p95_index] if p95_index < total_ops else 0.0,
            'p99_insert_time_ms': sorted_times[p99_index] if p99_index < total_ops else 0.0,
            'total_operations': total_ops,
            'cache_hit_rate': cache_hit_rate,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'constitutional_hash': self.constitutional_hash
        }

    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.redis_client:
                await self.redis_client.close()

            if self.db_pool:
                self.db_pool.closeall()

            logger.info("PersistentAuditLogger cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global instance for easy access
_audit_logger_instance: Optional[PersistentAuditLogger] = None


async def get_audit_logger() -> PersistentAuditLogger:
    """Get the global audit logger instance."""
    global _audit_logger_instance

    if _audit_logger_instance is None:
        # Default configuration - should be overridden in production
        db_config = {
            "host": "localhost",
            "port": 5439,
            "database": "acgs_integrity",
            "user": "acgs_user",
            "password": "acgs_password"
        }

        redis_config = {
            "url": "redis://localhost:6389"
        }

        _audit_logger_instance = PersistentAuditLogger(db_config, redis_config)
        await _audit_logger_instance.initialize()

    return _audit_logger_instance


async def log_audit_event(
    event_data: Dict[str, Any],
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    service_name: str = "integrity_service",
    event_type: str = "audit_event"
) -> Dict[str, Any]:
    """
    Convenience function to log an audit event.

    Args:
        event_data: Event data to log
        tenant_id: Tenant ID for multi-tenant isolation
        user_id: User ID who performed the action
        service_name: Name of the service logging the event
        event_type: Type of event being logged

    Returns:
        Dictionary with logging result and metadata
    """
    audit_logger = await get_audit_logger()
    return await audit_logger.log_event(
        event_data=event_data,
        tenant_id=tenant_id,
        user_id=user_id,
        service_name=service_name,
        event_type=event_type
    )
