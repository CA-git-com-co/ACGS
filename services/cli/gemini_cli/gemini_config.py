"""
Gemini CLI Configuration with MCP support and maximum capabilities
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json


@dataclass
class MCPServerConfig:
    """Configuration for MCP (Model Context Protocol) servers"""

    name: str
    command: List[str]
    env: Dict[str, str] = field(default_factory=dict)
    args: List[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class GeminiToolConfig:
    """Configuration for Gemini tools"""

    file_system: bool = True
    web_fetch: bool = True
    web_search: bool = True
    shell_execution: bool = True
    memory: bool = True
    multi_file_read: bool = True
    sandbox_execution: bool = True  # ACGS sandbox integration


@dataclass
class GeminiConfig:
    """Main Gemini CLI configuration"""

    # API Configuration
    api_key: Optional[str] = None
    model: str = "gemini-1.5-pro"
    temperature: float = 0.7
    max_tokens: int = 8192

    # ACGS Integration
    acgs_coordinator_url: str = "http://localhost:8000"
    auth_service_url: str = "http://localhost:8006"
    sandbox_service_url: str = "http://localhost:8009"
    formal_verification_url: str = "http://localhost:8010"
    audit_service_url: str = "http://localhost:8011"
    hitl_service_url: str = "http://localhost:8008"

    # Constitutional Configuration
    constitutional_hash: str = "cdd01ef066bc6cf2"
    enforce_constitutional: bool = True

    # Tools Configuration
    tools: GeminiToolConfig = field(default_factory=GeminiToolConfig)

    # MCP Servers Configuration
    mcp_servers: List[MCPServerConfig] = field(default_factory=list)

    # Logging and Monitoring
    telemetry_enabled: bool = True
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Performance Configuration
    request_timeout: int = 300
    max_retries: int = 3
    connection_pool_size: int = 10

    @classmethod
    def load_from_file(cls, config_path: Path) -> "GeminiConfig":
        """Load configuration from JSON file"""
        if config_path.exists():
            with open(config_path, "r") as f:
                data = json.load(f)
                # Convert MCP server configs
                if "mcp_servers" in data:
                    data["mcp_servers"] = [
                        MCPServerConfig(**server) for server in data["mcp_servers"]
                    ]
                # Convert tools config
                if "tools" in data:
                    data["tools"] = GeminiToolConfig(**data["tools"])
                return cls(**data)
        return cls()

    def save_to_file(self, config_path: Path):
        """Save configuration to JSON file"""
        data = {
            "api_key": self.api_key,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "acgs_coordinator_url": self.acgs_coordinator_url,
            "auth_service_url": self.auth_service_url,
            "sandbox_service_url": self.sandbox_service_url,
            "formal_verification_url": self.formal_verification_url,
            "audit_service_url": self.audit_service_url,
            "hitl_service_url": self.hitl_service_url,
            "constitutional_hash": self.constitutional_hash,
            "enforce_constitutional": self.enforce_constitutional,
            "tools": {
                "file_system": self.tools.file_system,
                "web_fetch": self.tools.web_fetch,
                "web_search": self.tools.web_search,
                "shell_execution": self.tools.shell_execution,
                "memory": self.tools.memory,
                "multi_file_read": self.tools.multi_file_read,
                "sandbox_execution": self.tools.sandbox_execution,
            },
            "mcp_servers": [
                {
                    "name": server.name,
                    "command": server.command,
                    "env": server.env,
                    "args": server.args,
                    "enabled": server.enabled,
                }
                for server in self.mcp_servers
            ],
            "telemetry_enabled": self.telemetry_enabled,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "request_timeout": self.request_timeout,
            "max_retries": self.max_retries,
            "connection_pool_size": self.connection_pool_size,
        }

        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)


def get_default_mcp_servers() -> List[MCPServerConfig]:
    """Get default MCP server configurations for maximum capability"""
    return [
        # File system MCP server
        MCPServerConfig(
            name="filesystem",
            command=["python", "-m", "mcp_servers.filesystem"],
            args=["--root", "/"],
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        ),
        # Git MCP server
        MCPServerConfig(
            name="git",
            command=["python", "-m", "mcp_servers.git"],
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        ),
        # Database MCP server
        MCPServerConfig(
            name="database",
            command=["python", "-m", "mcp_servers.database"],
            args=[
                "--connection",
                "postgresql://acgs_user:acgs_password@localhost:5432/acgs_db",
            ],
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        ),
        # ACGS Constitutional MCP server
        MCPServerConfig(
            name="acgs_constitutional",
            command=["python", "-m", "mcp_servers.acgs_constitutional"],
            env={
                "PYTHONPATH": str(Path(__file__).parent.parent.parent.parent),
                "CONSTITUTIONAL_HASH": "cdd01ef066bc6cf2",
            },
        ),
        # Docker MCP server (for sandbox integration)
        MCPServerConfig(
            name="docker",
            command=["python", "-m", "mcp_servers.docker"],
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        ),
        # Monitoring MCP server
        MCPServerConfig(
            name="monitoring",
            command=["python", "-m", "mcp_servers.monitoring"],
            args=["--prometheus-url", "http://localhost:9090"],
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        ),
    ]


def get_default_config() -> GeminiConfig:
    """Get default Gemini configuration with maximum capabilities"""
    config = GeminiConfig()
    config.mcp_servers = get_default_mcp_servers()

    # Set API key from environment if available
    if api_key := os.environ.get("GEMINI_API_KEY"):
        config.api_key = api_key

    return config


# Global configuration instance
_config: Optional[GeminiConfig] = None


def get_config() -> GeminiConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        config_path = Path.home() / ".gemini_cli" / "config.json"
        if config_path.exists():
            _config = GeminiConfig.load_from_file(config_path)
        else:
            _config = get_default_config()
    return _config


def set_config(config: GeminiConfig):
    """Set the global configuration instance"""
    global _config
    _config = config


def save_config():
    """Save current configuration to default location"""
    config = get_config()
    config_path = Path.home() / ".gemini_cli" / "config.json"
    config.save_to_file(config_path)
