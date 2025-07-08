"""
ACGS Utility Functions
Constitutional Hash: cdd01ef066bc6cf2

Common utility functions for ACGS scripts.
"""

import asyncio
import functools
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, TypeVar, Union, List
import re

from .exceptions import ConstitutionalComplianceError, RetryExhaustedError

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

T = TypeVar('T')


def ensure_constitutional_hash(data: Union[Dict[str, Any], str], strict: bool = True) -> bool:
    """
    Ensure constitutional hash is present in data.
    
    Args:
        data: Dictionary or string to check
        strict: If True, raises exception on failure. If False, returns bool.
    
    Returns:
        True if hash is found, False otherwise (if strict=False)
        
    Raises:
        ConstitutionalComplianceError: If hash not found and strict=True
    """
    hash_found = False
    
    if isinstance(data, dict):
        # Check for hash in various possible keys
        hash_keys = ["constitutional_hash", "hash", "acgs_hash", "compliance_hash"]
        for key in hash_keys:
            if key in data and data[key] == CONSTITUTIONAL_HASH:
                hash_found = True
                break
    elif isinstance(data, str):
        # Check if hash is present in string
        if CONSTITUTIONAL_HASH in data:
            hash_found = True
    
    if not hash_found and strict:
        raise ConstitutionalComplianceError(
            f"Constitutional hash {CONSTITUTIONAL_HASH} not found in data",
            expected_hash=CONSTITUTIONAL_HASH,
            actual_hash=data.get("constitutional_hash") if isinstance(data, dict) else None
        )
    
    return hash_found


def validate_service_response(response: Dict[str, Any]) -> None:
    """
    Validate service response for constitutional compliance.
    
    Args:
        response: Service response dictionary
        
    Raises:
        ConstitutionalComplianceError: If response is not compliant
    """
    if not isinstance(response, dict):
        raise ConstitutionalComplianceError("Service response must be a dictionary")
    
    # Check for constitutional hash
    ensure_constitutional_hash(response, strict=True)
    
    # Check for required fields
    if "status" not in response:
        raise ConstitutionalComplianceError("Service response missing 'status' field")


def retry_async(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Async retry decorator with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        raise RetryExhaustedError(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}",
                            max_retries=max_retries,
                            last_error=e
                        ) from e
                    
                    # Wait before retrying
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def format_duration(duration_seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        duration_seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if duration_seconds < 1:
        return f"{duration_seconds * 1000:.1f}ms"
    elif duration_seconds < 60:
        return f"{duration_seconds:.1f}s"
    elif duration_seconds < 3600:
        minutes = int(duration_seconds // 60)
        seconds = duration_seconds % 60
        return f"{minutes}m {seconds:.1f}s"
    else:
        hours = int(duration_seconds // 3600)
        remaining = duration_seconds % 3600
        minutes = int(remaining // 60)
        seconds = remaining % 60
        return f"{hours}h {minutes}m {seconds:.1f}s"


def get_timestamp(format_type: str = "iso") -> str:
    """
    Get current timestamp in various formats.
    
    Args:
        format_type: Type of format ("iso", "unix", "readable", "filename")
        
    Returns:
        Formatted timestamp string
    """
    now = datetime.now()
    
    if format_type == "iso":
        return now.isoformat()
    elif format_type == "unix":
        return str(int(now.timestamp()))
    elif format_type == "readable":
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "filename":
        return now.strftime("%Y%m%d_%H%M%S")
    else:
        return now.isoformat()


def parse_duration(duration_str: str) -> float:
    """
    Parse duration string to seconds.
    
    Args:
        duration_str: Duration string (e.g., "5s", "2m", "1h", "500ms")
        
    Returns:
        Duration in seconds
        
    Raises:
        ValueError: If duration string is invalid
    """
    duration_str = duration_str.strip().lower()
    
    # Regular expression to match duration patterns
    pattern = r'^(\d+(?:\.\d+)?)(ms|s|m|h)$'
    match = re.match(pattern, duration_str)
    
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")
    
    value, unit = match.groups()
    value = float(value)
    
    if unit == "ms":
        return value / 1000
    elif unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    else:
        raise ValueError(f"Unsupported time unit: {unit}")


def validate_port_number(port: Union[int, str]) -> int:
    """
    Validate and normalize port number.
    
    Args:
        port: Port number as int or string
        
    Returns:
        Validated port number as int
        
    Raises:
        ValueError: If port number is invalid
    """
    try:
        port_int = int(port)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid port number: {port}")
    
    if not (1 <= port_int <= 65535):
        raise ValueError(f"Port number must be between 1 and 65535, got: {port_int}")
    
    return port_int


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def create_progress_tracker(total: int, description: str = "Processing") -> Callable[[int], None]:
    """
    Create a simple progress tracker function.
    
    Args:
        total: Total number of items to process
        description: Description of the process
        
    Returns:
        Function to call with current progress
    """
    start_time = time.time()
    
    def update_progress(current: int) -> None:
        if total <= 0:
            return
        
        elapsed = time.time() - start_time
        progress = current / total
        
        if progress > 0:
            eta = elapsed / progress - elapsed
            eta_str = format_duration(eta)
        else:
            eta_str = "unknown"
        
        print(f"\r{description}: {current}/{total} ({progress*100:.1f}%) "
              f"- Elapsed: {format_duration(elapsed)} - ETA: {eta_str}", end="", flush=True)
        
        if current >= total:
            print()  # New line when complete
    
    return update_progress


def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")
    
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback.
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        import json
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        print(f"{self.description} completed in {format_duration(self.duration)}")
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        current_time = self.end_time or time.time()
        return current_time - self.start_time