"""
ACGS Code Analysis Engine - File Watcher Service
Monitor code changes using watchdog library with constitutional compliance.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from app.utils.constitutional import (
    CONSTITUTIONAL_HASH,
    ensure_constitutional_compliance,
)
from app.utils.logging import get_logger, performance_logger
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = get_logger("core.file_watcher")


class CodeFileHandler(FileSystemEventHandler):
    """
    File system event handler for code files with constitutional compliance.
    """

    def __init__(
        self,
        callback: Callable[[str, str], None],
        supported_extensions: list[str],
        ignore_patterns: list[str],
    ):
        """
        Initialize code file handler.

        Args:
            callback: Callback function for file changes
            supported_extensions: File extensions to monitor
            ignore_patterns: Patterns to ignore
        """
        super().__init__()
        self.callback = callback
        self.supported_extensions = set(supported_extensions)
        self.ignore_patterns = ignore_patterns

        # Debouncing to avoid duplicate events
        self.last_events: dict[str, float] = {}
        self.debounce_seconds = 1.0

        logger.info(
            "Code file handler initialized",
            extra={
                "supported_extensions": supported_extensions,
                "ignore_patterns": ignore_patterns,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory:
            self._handle_file_event(event.src_path, "modified")

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        if not event.is_directory:
            self._handle_file_event(event.src_path, "created")

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events."""
        if not event.is_directory:
            self._handle_file_event(event.src_path, "deleted")

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file move events."""
        if not event.is_directory and hasattr(event, "dest_path"):
            self._handle_file_event(event.dest_path, "moved")

    def _handle_file_event(self, file_path: str, event_type: str) -> None:
        """
        Handle file system events with debouncing and filtering.

        Args:
            file_path: Path of the changed file
            event_type: Type of event (modified, created, deleted, moved)
        """
        try:
            # Check if file should be processed
            if not self._should_process_file(file_path):
                return

            # Debounce events
            current_time = time.time()
            last_event_time = self.last_events.get(file_path, 0)

            if current_time - last_event_time < self.debounce_seconds:
                return

            self.last_events[file_path] = current_time

            # Log file event
            logger.info(
                f"File {event_type}: {file_path}",
                extra={
                    "file_path": file_path,
                    "event_type": event_type,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

            # Call callback
            if self.callback:
                try:
                    self.callback(file_path, event_type)
                except Exception as e:
                    logger.error(
                        f"File event callback error: {e}",
                        extra={
                            "file_path": file_path,
                            "event_type": event_type,
                            "constitutional_hash": CONSTITUTIONAL_HASH,
                        },
                        exc_info=True,
                    )

        except Exception as e:
            logger.error(
                f"File event handling error: {e}",
                extra={
                    "file_path": file_path,
                    "event_type": event_type,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                exc_info=True,
            )

    def _should_process_file(self, file_path: str) -> bool:
        """
        Check if file should be processed based on extension and ignore patterns.

        Args:
            file_path: Path to check

        Returns:
            bool: True if file should be processed
        """
        path = Path(file_path)

        # Check file extension
        if path.suffix not in self.supported_extensions:
            return False

        # Check ignore patterns
        return all(pattern not in str(path) for pattern in self.ignore_patterns)


class FileWatcherService:
    """
    File watcher service for monitoring code changes with constitutional compliance.
    """

    def __init__(
        self,
        watch_paths: list[str],
        indexer_service: Any | None = None,
        supported_extensions: list[str] | None = None,
        ignore_patterns: list[str] | None = None,
    ):
        """
        Initialize file watcher service.

        Args:
            watch_paths: Paths to monitor for changes
            indexer_service: Indexer service for processing changes
            supported_extensions: File extensions to monitor
            ignore_patterns: Patterns to ignore
        """
        self.watch_paths = watch_paths
        self.indexer_service = indexer_service
        self.supported_extensions = supported_extensions or [
            ".py",
            ".js",
            ".ts",
            ".yml",
            ".yaml",
            ".json",
            ".sql",
            ".md",
        ]
        self.ignore_patterns = ignore_patterns or [
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".venv",
            "venv",
        ]

        # Watchdog components
        self.observer: Observer | None = None
        self.handlers: list[CodeFileHandler] = []

        # State tracking
        self.is_running = False
        self.files_processed = 0
        self.events_received = 0

        logger.info(
            "File watcher service initialized",
            extra={
                "watch_paths": watch_paths,
                "supported_extensions": self.supported_extensions,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )

    async def start(self) -> None:
        """Start the file watcher service."""
        if self.is_running:
            logger.warning("File watcher service is already running")
            return

        try:
            # Create observer
            self.observer = Observer()

            # Set up handlers for each watch path
            for watch_path in self.watch_paths:
                path = Path(watch_path)
                if not path.exists():
                    logger.warning(
                        f"Watch path does not exist: {watch_path}",
                        extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                    )
                    continue

                # Create handler
                handler = CodeFileHandler(
                    callback=self._handle_file_change,
                    supported_extensions=self.supported_extensions,
                    ignore_patterns=self.ignore_patterns,
                )

                # Schedule handler
                self.observer.schedule(handler, str(path), recursive=True)
                self.handlers.append(handler)

                logger.info(
                    f"Watching path: {watch_path}",
                    extra={
                        "watch_path": watch_path,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )

            # Start observer
            self.observer.start()
            self.is_running = True

            logger.info(
                "File watcher service started",
                extra={
                    "watch_paths_count": len(self.watch_paths),
                    "handlers_count": len(self.handlers),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

        except Exception as e:
            logger.error(
                f"Failed to start file watcher service: {e}",
                extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                exc_info=True,
            )
            raise

    async def stop(self) -> None:
        """Stop the file watcher service."""
        if not self.is_running:
            return

        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None

            self.handlers.clear()
            self.is_running = False

            logger.info(
                "File watcher service stopped",
                extra={
                    "files_processed": self.files_processed,
                    "events_received": self.events_received,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

        except Exception as e:
            logger.error(
                f"Error stopping file watcher service: {e}",
                extra={"constitutional_hash": CONSTITUTIONAL_HASH},
                exc_info=True,
            )

    def _handle_file_change(self, file_path: str, event_type: str) -> None:
        """
        Handle file change events.

        Args:
            file_path: Path of the changed file
            event_type: Type of change event
        """
        self.events_received += 1

        try:
            # Log performance metrics
            performance_logger.start_operation(
                operation_id=f"file_change_{self.events_received}",
                operation_type="file_change_processing",
                file_path=file_path,
                event_type=event_type,
            )

            # Process file change
            if self.indexer_service and event_type in {"created", "modified"}:
                # Queue file for reanalysis
                asyncio.create_task(self._queue_file_analysis(file_path))
            elif event_type == "deleted":
                # Handle file deletion
                asyncio.create_task(self._handle_file_deletion(file_path))

            self.files_processed += 1

            # End performance tracking
            performance_logger.end_operation(
                operation_id=f"file_change_{self.events_received}",
                success=True,
                files_processed=1,
            )

        except Exception as e:
            logger.error(
                f"File change handling error: {e}",
                extra={
                    "file_path": file_path,
                    "event_type": event_type,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                exc_info=True,
            )

            # End performance tracking with error
            performance_logger.end_operation(
                operation_id=f"file_change_{self.events_received}",
                success=False,
                error=str(e),
            )

    async def _queue_file_analysis(self, file_path: str) -> None:
        """Queue file for analysis by indexer service."""
        try:
            if self.indexer_service and hasattr(self.indexer_service, "analyze_file"):
                await self.indexer_service.analyze_file(file_path)
            else:
                logger.warning(
                    "Indexer service not available for file analysis",
                    extra={
                        "file_path": file_path,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )
        except Exception as e:
            logger.error(
                f"File analysis queueing error: {e}",
                extra={
                    "file_path": file_path,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                exc_info=True,
            )

    async def _handle_file_deletion(self, file_path: str) -> None:
        """Handle file deletion by removing from database."""
        try:
            if self.indexer_service and hasattr(self.indexer_service, "remove_file"):
                await self.indexer_service.remove_file(file_path)
            else:
                logger.warning(
                    "Indexer service not available for file removal",
                    extra={
                        "file_path": file_path,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )
        except Exception as e:
            logger.error(
                f"File deletion handling error: {e}",
                extra={
                    "file_path": file_path,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                exc_info=True,
            )

    def get_status(self) -> dict[str, Any]:
        """Get file watcher service status."""
        return ensure_constitutional_compliance(
            {
                "is_running": self.is_running,
                "watch_paths": self.watch_paths,
                "handlers_count": len(self.handlers),
                "files_processed": self.files_processed,
                "events_received": self.events_received,
                "supported_extensions": self.supported_extensions,
            }
        )
