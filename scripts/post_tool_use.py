#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Post-tool use completion logging & transcript script for Claude using UV single-file pattern.

This script captures tool results from stdin, appends to logs/post_tool_use.json,
and updates /logs/chat.json with a readable conversation line. Provides optional
markdown→plain-text conversion for transcript.

Constitutional Hash: cdd01ef066bc6cf2
"""

import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional


# Constitutional compliance configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
LOGS_DIR = Path("/home/dislove/ACGS-2/logs")
POST_TOOL_USE_LOG = LOGS_DIR / "post_tool_use.json"
CHAT_LOG = LOGS_DIR / "chat.json"


def ensure_logs_directory() -> None:
    """Ensure the logs directory exists."""
    LOGS_DIR.mkdir(exist_ok=True)


def append_to_json_log(file_path: Path, data: Dict[str, Any]) -> None:
    """Append to a JSON log file with constitutional compliance metadata."""
    ensure_logs_directory()
    
    # Add constitutional compliance metadata
    data["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    data["constitutional_hash"] = CONSTITUTIONAL_HASH
    data["compliance_version"] = "2.0.0"
    
    try:
        with file_path.open("a", encoding="utf-8") as log_file:
            json.dump(data, log_file, ensure_ascii=False)
            log_file.write("\n")
    except Exception as e:
        print(f"Warning: Failed to log to {file_path}: {e}", file=sys.stderr)


def markdown_to_text(markdown_str: str) -> str:
    """Convert markdown text to plain text using regex patterns.
    
    Args:
        markdown_str: Input markdown string
        
    Returns:
        Plain text with markdown formatting removed
    """
    if not markdown_str:
        return ""
    
    text = markdown_str
    
    # Remove markdown formatting patterns
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # bold **text**
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # italic *text*
    text = re.sub(r'`(.*?)`', r'\1', text)  # inline code `text`
    text = re.sub(r'```.*?\n(.*?)\n```', r'\1', text, flags=re.DOTALL)  # code blocks
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # headers
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # links [text](url)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # images ![alt](url)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)  # blockquotes
    text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)  # unordered lists
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)  # ordered lists
    text = re.sub(r'^\|.*\|$', '', text, flags=re.MULTILINE)  # table rows
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)  # horizontal rules
    text = re.sub(r'\n{3,}', '\n\n', text)  # multiple newlines
    
    return text.strip()


def extract_tool_content(tool_result: Dict[str, Any]) -> str:
    """Extract meaningful content from tool result for transcript.
    
    Args:
        tool_result: Tool result dictionary
        
    Returns:
        Extracted content string
    """
    # Try different common fields for content
    content_fields = [
        "content", "message", "output", "result", 
        "response", "text", "data", "value"
    ]
    
    for field in content_fields:
        if field in tool_result and tool_result[field]:
            content = str(tool_result[field])
            if content.strip():
                return content
    
    # If no standard content field, try to stringify the whole result
    # but exclude common metadata fields
    filtered_result = {
        k: v for k, v in tool_result.items() 
        if k not in ["timestamp", "constitutional_hash", "compliance_version", "id", "type"]
    }
    
    if filtered_result:
        return json.dumps(filtered_result, indent=2)
    
    return str(tool_result)


def create_conversation_entry(tool_result: Dict[str, Any], enable_markdown_conversion: bool = True) -> Dict[str, Any]:
    """Create a readable conversation entry for chat.json.
    
    Args:
        tool_result: Tool result dictionary
        enable_markdown_conversion: Whether to convert markdown to plain text
        
    Returns:
        Conversation entry dictionary
    """
    # Extract content from tool result
    raw_content = extract_tool_content(tool_result)
    
    # Convert markdown to plain text if enabled
    if enable_markdown_conversion:
        content = markdown_to_text(raw_content)
    else:
        content = raw_content
    
    # Create conversation entry
    conversation_entry = {
        "role": "tool",
        "content": content[:1000] + "..." if len(content) > 1000 else content,  # Truncate for readability
        "tool_name": tool_result.get("tool_name", "unknown"),
        "success": tool_result.get("success", True),
        "content_type": "markdown" if not enable_markdown_conversion else "text"
    }
    
    # Add error information if present
    if "error" in tool_result:
        conversation_entry["error"] = tool_result["error"]
        conversation_entry["success"] = False
    
    return conversation_entry


def validate_tool_result(data: Any) -> Optional[str]:
    """Validate tool result data structure.
    
    Args:
        data: Parsed input data
        
    Returns:
        Error message if validation fails, None if valid
    """
    if not isinstance(data, dict):
        return "Tool result must be a JSON object"
    
    # Check for required constitutional compliance
    if "constitutional_hash" in data and data["constitutional_hash"] != CONSTITUTIONAL_HASH:
        return f"Constitutional hash mismatch: expected {CONSTITUTIONAL_HASH}"
    
    return None


def main() -> None:
    """Main completion logging function."""
    try:
        # Read tool result from stdin
        input_data = sys.stdin.read().strip()
        
        if not input_data:
            tool_result = {"error": "No tool result provided", "success": False}
        else:
            try:
                tool_result = json.loads(input_data)
            except json.JSONDecodeError as e:
                tool_result = {
                    "error": f"Invalid JSON input: {str(e)}",
                    "success": False,
                    "raw_input": input_data[:200]  # First 200 chars for debugging
                }
        
        # Validate tool result
        validation_error = validate_tool_result(tool_result)
        if validation_error:
            tool_result["validation_error"] = validation_error
            tool_result["success"] = False
        
        # Append to post_tool_use.json
        log_entry = {
            "tool_result": tool_result,
            "log_type": "post_tool_use"
        }
        append_to_json_log(POST_TOOL_USE_LOG, log_entry)
        
        # Create readable conversation entry with markdown conversion
        conversation_entry = create_conversation_entry(tool_result, enable_markdown_conversion=True)
        append_to_json_log(CHAT_LOG, conversation_entry)
        
        # Output success confirmation (optional)
        print(json.dumps({
            "logged": True,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "logs_updated": [str(POST_TOOL_USE_LOG), str(CHAT_LOG)]
        }))
        
    except Exception as e:
        # Catch-all error handler
        error_entry = {
            "error": f"Post-tool use logging error: {str(e)}",
            "success": False,
            "log_type": "post_tool_use_error"
        }
        
        try:
            append_to_json_log(POST_TOOL_USE_LOG, error_entry)
        except:
            # If we can't log, at least print to stderr
            print(f"Critical: Failed to log post-tool use error: {e}", file=sys.stderr)
        
        print(json.dumps({
            "logged": False,
            "error": str(e),
            "constitutional_hash": CONSTITUTIONAL_HASH
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
