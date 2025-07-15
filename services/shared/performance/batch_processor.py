"""
Batch Processing Components for ACGS
Constitutional Hash: cdd01ef066bc6cf2

High-performance batch processing utilities for database operations and event processing.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Callable, Generic, List, TypeVar, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    batch_size: int = 100
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    constitutional_validation: bool = True


class BatchProcessor(Generic[T]):
    """Generic batch processor for items of type T."""
    
    def __init__(self, 
                 process_func: Callable[[List[T]], asyncio.Future],
                 config: BatchConfig = None):
        """
        Initialize batch processor.
        
        Args:
            process_func: Function to process a batch of items
            config: Batch processing configuration
        """
        self.process_func = process_func
        self.config = config or BatchConfig()
        self._batch: List[T] = []
        self._lock = asyncio.Lock()
        self._last_flush = datetime.now()
        
    async def add(self, item: T) -> None:
        """Add an item to the batch."""
        async with self._lock:
            self._batch.append(item)
            if len(self._batch) >= self.config.batch_size:
                await self._flush()
                
    async def _flush(self) -> None:
        """Flush the current batch."""
        if not self._batch:
            return
            
        batch_to_process = self._batch[:]
        self._batch.clear()
        self._last_flush = datetime.now()
        
        for attempt in range(self.config.max_retries):
            try:
                await self.process_func(batch_to_process)
                return
            except Exception as e:
                logger.error(f"Batch processing error (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay_seconds)
                else:
                    raise
                    
    async def flush(self) -> None:
        """Manually flush the batch."""
        async with self._lock:
            await self._flush()
            
    async def close(self) -> None:
        """Close the batch processor and flush remaining items."""
        await self.flush()


class DatabaseBatchProcessor(BatchProcessor[dict]):
    """Specialized batch processor for database operations."""
    
    def __init__(self, 
                 db_connection,
                 table_name: str,
                 config: BatchConfig = None):
        """
        Initialize database batch processor.
        
        Args:
            db_connection: Database connection object
            table_name: Name of the table to insert into
            config: Batch processing configuration
        """
        self.db_connection = db_connection
        self.table_name = table_name
        
        async def process_batch(items: List[dict]) -> None:
            """Process a batch of database records."""
            if not items:
                return
                
            # Validate constitutional compliance if enabled
            if config and config.constitutional_validation:
                for item in items:
                    if 'constitutional_hash' not in item:
                        item['constitutional_hash'] = 'cdd01ef066bc6cf2'
                        
            # Perform bulk insert
            async with self.db_connection.transaction():
                await self.db_connection.execute_many(
                    f"INSERT INTO {self.table_name} VALUES ($1)",
                    items
                )
                
        super().__init__(process_batch, config)


class EventBatchProcessor(BatchProcessor[dict]):
    """Specialized batch processor for event processing."""
    
    def __init__(self,
                 event_handler: Callable[[List[dict]], asyncio.Future],
                 config: BatchConfig = None):
        """
        Initialize event batch processor.
        
        Args:
            event_handler: Function to handle a batch of events
            config: Batch processing configuration
        """
        async def process_events(events: List[dict]) -> None:
            """Process a batch of events."""
            if not events:
                return
                
            # Add timestamps and constitutional hash
            for event in events:
                if 'timestamp' not in event:
                    event['timestamp'] = datetime.now().isoformat()
                if 'constitutional_hash' not in event:
                    event['constitutional_hash'] = 'cdd01ef066bc6cf2'
                    
            await event_handler(events)
            
        super().__init__(process_events, config)


__all__ = [
    'BatchConfig',
    'BatchProcessor',
    'DatabaseBatchProcessor',
    'EventBatchProcessor',
]