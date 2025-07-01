"""
Output formatters for Gemini CLI
"""

import json
from typing import Any, Dict, List
from tabulate import tabulate


def format_output(data: Any, format_type: str = "table") -> str:
    """Format output based on specified type"""
    if format_type == "json":
        return format_json(data)
    elif format_type == "table":
        return format_table(data)
    else:  # text
        return format_text(data)


def format_json(data: Any) -> str:
    """Format output as JSON"""
    return json.dumps(data, indent=2, default=str)


def format_table(data: Any) -> str:
    """Format output as table"""
    if isinstance(data, dict):
        if "error" in data:
            return f"Error: {data['error']}"
        
        # Handle special cases
        if "agents" in data:
            # Agent list
            agents = data.get("agents", [])
            if agents:
                headers = ["ID", "Name", "Type", "Status", "Created"]
                rows = [
                    [
                        a.get("id", "")[:8],
                        a.get("name", ""),
                        a.get("type", ""),
                        a.get("status", ""),
                        a.get("created_at", "")[:19]
                    ]
                    for a in agents
                ]
                return tabulate(rows, headers=headers, tablefmt="grid")
            else:
                return "No agents found"
        
        elif "entries" in data:
            # Audit entries
            entries = data.get("entries", [])
            if entries:
                headers = ["Timestamp", "Operation ID", "Agent ID", "Action", "Status"]
                rows = [
                    [
                        e.get("timestamp", "")[:19],
                        e.get("operation_id", "")[:8],
                        e.get("agent_id", "")[:8],
                        e.get("action", ""),
                        e.get("result", {}).get("status", "")
                    ]
                    for e in entries
                ]
                return tabulate(rows, headers=headers, tablefmt="grid")
            else:
                return "No audit entries found"
        
        elif "health" in data:
            # Health status
            health = data.get("health", {})
            headers = ["Service", "Status"]
            rows = [[service, "✓ Healthy" if status else "✗ Unhealthy"] 
                   for service, status in health.items()]
            return tabulate(rows, headers=headers, tablefmt="grid")
        
        elif "alerts" in data:
            # Alerts
            alerts = data.get("alerts", [])
            if alerts:
                headers = ["Time", "Severity", "Service", "Message", "Ack"]
                rows = [
                    [
                        a.get("timestamp", "")[:19],
                        a.get("severity", "").upper(),
                        a.get("service", ""),
                        a.get("message", "")[:50],
                        "Yes" if a.get("acknowledged") else "No"
                    ]
                    for a in alerts
                ]
                return tabulate(rows, headers=headers, tablefmt="grid")
            else:
                return "No alerts"
        
        # Default: key-value pairs
        rows = [[k, v] for k, v in data.items() if k != "error"]
        return tabulate(rows, headers=["Key", "Value"], tablefmt="grid")
    
    elif isinstance(data, list):
        if data and isinstance(data[0], dict):
            # List of dicts
            headers = list(data[0].keys())
            rows = [[item.get(h, "") for h in headers] for item in data]
            return tabulate(rows, headers=headers, tablefmt="grid")
        else:
            # Simple list
            return "\n".join(str(item) for item in data)
    
    else:
        return str(data)


def format_text(data: Any) -> str:
    """Format output as plain text"""
    if isinstance(data, dict):
        if "error" in data:
            return f"Error: {data['error']}"
        
        lines = []
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                lines.append(f"{key}:")
                lines.append(f"  {format_text(value)}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    elif isinstance(data, list):
        return "\n".join(f"- {format_text(item)}" for item in data)
    
    else:
        return str(data)