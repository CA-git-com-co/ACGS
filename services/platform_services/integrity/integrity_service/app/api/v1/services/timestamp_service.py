"""
Timestamp service for ACGS Integrity Service.
Constitutional Hash: cdd01ef066bc6cf2
"""

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class TimestampManager:
    """Timestamp service for creating and verifying timestamps."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.timestamps: Dict[str, Dict[str, Any]] = {}
        self.authority = "ACGS_Integrity_Service"
        self.supported_algorithms = ["SHA-256", "SHA-512", "SHA3-256", "SHA3-512"]
    
    async def create_timestamp(self, data: str, algorithm: str = "SHA-256") -> Dict[str, Any]:
        """Create a timestamp for the given data."""
        try:
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Generate data hash
            data_bytes = data.encode('utf-8')
            
            if algorithm == "SHA-256":
                hash_obj = hashlib.sha256(data_bytes)
            elif algorithm == "SHA-512":
                hash_obj = hashlib.sha512(data_bytes)
            elif algorithm == "SHA3-256":
                hash_obj = hashlib.sha3_256(data_bytes)
            elif algorithm == "SHA3-512":
                hash_obj = hashlib.sha3_512(data_bytes)
            else:
                raise ValueError(f"Algorithm {algorithm} not implemented")
            
            data_hash = hash_obj.hexdigest()
            
            # Create timestamp
            timestamp = datetime.now(timezone.utc)
            timestamp_id = str(uuid.uuid4())
            
            # Create timestamp token (simplified - in production use RFC 3161)
            token_data = f"{data_hash}:{timestamp.isoformat()}:{self.authority}:{algorithm}"
            token_hash = hashlib.sha256(token_data.encode('utf-8')).hexdigest()
            timestamp_token = f"{timestamp_id}:{token_hash}"
            
            # Store timestamp record
            timestamp_record = {
                "timestamp_id": timestamp_id,
                "data_hash": data_hash,
                "timestamp": timestamp,
                "algorithm": algorithm,
                "authority": self.authority,
                "timestamp_token": timestamp_token,
                "constitutional_hash": self.constitutional_hash,
                "created_at": timestamp,
            }
            
            self.timestamps[timestamp_id] = timestamp_record
            
            return {
                "timestamp": timestamp,
                "data_hash": data_hash,
                "timestamp_token": timestamp_token,
                "authority": self.authority,
                "algorithm": algorithm,
                "constitutional_hash": self.constitutional_hash,
            }
            
        except Exception as e:
            logger.error(f"Timestamp creation failed: {e}")
            raise
    
    async def verify_timestamp(
        self, 
        data: str, 
        timestamp_token: str, 
        expected_timestamp: Optional[datetime] = None,
        algorithm: str = "SHA-256"
    ) -> Dict[str, Any]:
        """Verify a timestamp token against the original data."""
        try:
            # Parse timestamp token
            try:
                timestamp_id, token_hash = timestamp_token.split(":", 1)
            except ValueError:
                raise ValueError("Invalid timestamp token format")
            
            # Check if we have the timestamp record
            if timestamp_id not in self.timestamps:
                raise ValueError(f"Timestamp {timestamp_id} not found")
            
            timestamp_record = self.timestamps[timestamp_id]
            
            # Generate data hash
            data_bytes = data.encode('utf-8')
            
            if algorithm == "SHA-256":
                hash_obj = hashlib.sha256(data_bytes)
            elif algorithm == "SHA-512":
                hash_obj = hashlib.sha512(data_bytes)
            elif algorithm == "SHA3-256":
                hash_obj = hashlib.sha3_256(data_bytes)
            elif algorithm == "SHA3-512":
                hash_obj = hashlib.sha3_512(data_bytes)
            else:
                raise ValueError(f"Algorithm {algorithm} not implemented")
            
            data_hash = hash_obj.hexdigest()
            
            # Verify data hash matches
            hash_matches = data_hash == timestamp_record["data_hash"]
            
            # Verify timestamp token
            expected_token_data = f"{data_hash}:{timestamp_record['timestamp'].isoformat()}:{self.authority}:{algorithm}"
            expected_token_hash = hashlib.sha256(expected_token_data.encode('utf-8')).hexdigest()
            expected_token = f"{timestamp_id}:{expected_token_hash}"
            
            token_matches = timestamp_token == expected_token
            
            # Check expected timestamp if provided
            timestamp_matches = True
            if expected_timestamp:
                # Allow small tolerance (1 second) for timestamp comparison
                time_diff = abs((timestamp_record["timestamp"] - expected_timestamp).total_seconds())
                timestamp_matches = time_diff <= 1.0
            
            is_valid = hash_matches and token_matches and timestamp_matches
            
            return {
                "is_valid": is_valid,
                "timestamp": timestamp_record["timestamp"],
                "data_hash": data_hash,
                "authority": self.authority,
                "algorithm": algorithm,
                "verified_at": datetime.now(timezone.utc),
                "verification_details": {
                    "hash_matches": hash_matches,
                    "token_matches": token_matches,
                    "timestamp_matches": timestamp_matches,
                },
                "constitutional_hash": self.constitutional_hash,
            }
            
        except Exception as e:
            logger.error(f"Timestamp verification failed: {e}")
            raise
    
    async def get_timestamp_info(self, timestamp_id: str) -> Dict[str, Any]:
        """Get information about a timestamp."""
        try:
            if timestamp_id not in self.timestamps:
                raise ValueError(f"Timestamp {timestamp_id} not found")
            
            return self.timestamps[timestamp_id].copy()
            
        except Exception as e:
            logger.error(f"Timestamp info retrieval failed: {e}")
            raise
    
    async def list_timestamps(
        self, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List timestamps with optional time range filtering."""
        try:
            filtered_timestamps = []
            
            for timestamp_record in self.timestamps.values():
                timestamp = timestamp_record["timestamp"]
                
                # Apply time range filters
                if start_time and timestamp < start_time:
                    continue
                
                if end_time and timestamp > end_time:
                    continue
                
                filtered_timestamps.append(timestamp_record.copy())
            
            # Sort by timestamp (newest first)
            filtered_timestamps.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Apply limit
            if limit > 0:
                filtered_timestamps = filtered_timestamps[:limit]
            
            return {
                "timestamps": filtered_timestamps,
                "total_count": len(filtered_timestamps),
                "authority": self.authority,
                "constitutional_hash": self.constitutional_hash,
            }
            
        except Exception as e:
            logger.error(f"Timestamp listing failed: {e}")
            raise
    
    async def get_timestamp_statistics(self) -> Dict[str, Any]:
        """Get timestamp service statistics."""
        try:
            total_timestamps = len(self.timestamps)
            
            # Count by algorithm
            algorithm_counts = {}
            for record in self.timestamps.values():
                algorithm = record["algorithm"]
                algorithm_counts[algorithm] = algorithm_counts.get(algorithm, 0) + 1
            
            # Get time range
            if self.timestamps:
                timestamps = [record["timestamp"] for record in self.timestamps.values()]
                earliest = min(timestamps)
                latest = max(timestamps)
            else:
                earliest = None
                latest = None
            
            return {
                "total_timestamps": total_timestamps,
                "algorithm_distribution": algorithm_counts,
                "earliest_timestamp": earliest,
                "latest_timestamp": latest,
                "authority": self.authority,
                "constitutional_hash": self.constitutional_hash,
            }
            
        except Exception as e:
            logger.error(f"Timestamp statistics retrieval failed: {e}")
            raise


# Global timestamp manager instance
timestamp_manager = TimestampManager()
