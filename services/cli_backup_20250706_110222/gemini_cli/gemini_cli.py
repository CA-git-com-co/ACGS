#!/usr/bin/env python3
"""
Gemini CLI - Main entry point with full ACGS integration
"""
# Constitutional Hash: cdd01ef066bc6cf2

import argparse
import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from acgs_client import ACGSClient
from commands import agent, audit, execute, monitor, verify
from formatters import format_output
from gemini_config import get_config, get_default_config, save_config

from tools import ToolManager

logger = logging.getLogger(__name__)


class GeminiCLI:
    """Main Gemini CLI application"""

    def __init__(self):
        self.config = get_config()
        self.acgs_client = ACGSClient(self.config)
        self.tool_manager = ToolManager(self.config)
        self.mcp_processes = []

    def setup_logging(self, log_level: str):
        """Set up logging configuration"""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )

        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            logging.getLogger().addHandler(file_handler)

    def start_mcp_servers(self):
        """Start MCP servers for enhanced capabilities"""
        logger.info("Starting MCP servers...")

        for server_config in self.config.mcp_servers:
            if not server_config.enabled:
                continue

            try:
                # Set up environment
                env = os.environ.copy()
                env.update(server_config.env)

                # Start server process
                cmd = server_config.command + server_config.args
                process = subprocess.Popen(
                    cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

                self.mcp_processes.append((server_config.name, process))
                logger.info(f"Started MCP server: {server_config.name}")

            except Exception as e:
                logger.error(f"Failed to start MCP server {server_config.name}: {e}")

    def stop_mcp_servers(self):
        """Stop all MCP servers"""
        logger.info("Stopping MCP servers...")

        for name, process in self.mcp_processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"Stopped MCP server: {name}")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"Force killed MCP server: {name}")
            except Exception as e:
                logger.error(f"Error stopping MCP server {name}: {e}")

    def check_services_health(self) -> bool:
        """Check health of ACGS services"""
        logger.info("Checking ACGS services health...")
        health_status = self.acgs_client.check_service_health()

        all_healthy = all(health_status.values())

        if not all_healthy:
            logger.warning("Some ACGS services are not healthy:")
            for service, healthy in health_status.items():
                if not healthy:
                    logger.warning(f"  - {service}: DOWN")
        else:
            logger.info("All ACGS services are healthy")

        return all_healthy

    def create_parser(self) -> argparse.ArgumentParser:
        """Create command line parser"""
        parser = argparse.ArgumentParser(
            description="Gemini CLI - AI Constitutional Governance System Interface",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Create a new agent
  gemini-cli agent create --name "analysis-bot" --type "data_processor"
  
  # Execute code with governance
  gemini-cli execute --code "print('Hello ACGS')" --language python
  
  # Verify policy compliance
  gemini-cli verify --policy policy.rego --context context.json
  
  # Check audit trail
  gemini-cli audit list --from "2025-01-01"
  
  # Monitor system status
  gemini-cli monitor status
            """,
        )

        # Global options
        parser.add_argument("--config", type=Path, help="Path to configuration file")
        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="Logging level",
        )
        parser.add_argument("--no-mcp", action="store_true", help="Disable MCP servers")
        parser.add_argument(
            "--format",
            choices=["json", "table", "text"],
            default="table",
            help="Output format",
        )

        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Agent management
        agent_parser = subparsers.add_parser("agent", help="Agent management")
        agent.add_arguments(agent_parser)

        # Code execution
        execute_parser = subparsers.add_parser(
            "execute", help="Execute code with governance"
        )
        execute.add_arguments(execute_parser)

        # Policy verification
        verify_parser = subparsers.add_parser(
            "verify", help="Verify policies and compliance"
        )
        verify.add_arguments(verify_parser)

        # Audit trail
        audit_parser = subparsers.add_parser("audit", help="Audit trail management")
        audit.add_arguments(audit_parser)

        # Monitoring
        monitor_parser = subparsers.add_parser("monitor", help="System monitoring")
        monitor.add_arguments(monitor_parser)

        # Configuration
        config_parser = subparsers.add_parser("config", help="Configuration management")
        config_subparsers = config_parser.add_subparsers(dest="config_command")

        config_show = config_subparsers.add_parser(
            "show", help="Show current configuration"
        )
        config_set = config_subparsers.add_parser("set", help="Set configuration value")
        config_set.add_argument("key", help="Configuration key")
        config_set.add_argument("value", help="Configuration value")

        config_init = config_subparsers.add_parser(
            "init", help="Initialize configuration"
        )

        # Tools management
        tools_parser = subparsers.add_parser("tools", help="Manage Gemini tools")
        tools_subparsers = tools_parser.add_subparsers(dest="tools_command")

        tools_list = tools_subparsers.add_parser("list", help="List available tools")
        tools_enable = tools_subparsers.add_parser("enable", help="Enable a tool")
        tools_enable.add_argument("tool", help="Tool name")
        tools_disable = tools_subparsers.add_parser("disable", help="Disable a tool")
        tools_disable.add_argument("tool", help="Tool name")

        return parser

    async def handle_command(self, args):
        """Handle command execution"""
        try:
            if args.command == "agent":
                result = await agent.handle_command(args, self.acgs_client)

            elif args.command == "execute":
                result = await execute.handle_command(args, self.acgs_client)

            elif args.command == "verify":
                result = await verify.handle_command(args, self.acgs_client)

            elif args.command == "audit":
                result = await audit.handle_command(args, self.acgs_client)

            elif args.command == "monitor":
                result = await monitor.handle_command(args, self.acgs_client)

            elif args.command == "config":
                result = await self.handle_config_command(args)

            elif args.command == "tools":
                result = await self.handle_tools_command(args)

            else:
                result = {"error": "Unknown command"}

            # Format and display output
            output = format_output(result, args.format)
            print(output)

        except Exception as e:
            logger.error(f"Command failed: {e}")
            error_output = format_output({"error": str(e)}, args.format)
            print(error_output, file=sys.stderr)
            sys.exit(1)

    async def handle_config_command(self, args) -> dict:
        """Handle configuration commands"""
        if args.config_command == "show":
            config_dict = {
                "api_key": "***" if self.config.api_key else None,
                "model": self.config.model,
                "temperature": self.config.temperature,
                "acgs_services": {
                    "coordinator": self.config.acgs_coordinator_url,
                    "auth": self.config.auth_service_url,
                    "sandbox": self.config.sandbox_service_url,
                    "formal_verification": self.config.formal_verification_url,
                    "audit": self.config.audit_service_url,
                    "hitl": self.config.hitl_service_url,
                },
                "tools": {
                    "file_system": self.config.tools.file_system,
                    "web_fetch": self.config.tools.web_fetch,
                    "web_search": self.config.tools.web_search,
                    "shell_execution": self.config.tools.shell_execution,
                    "memory": self.config.tools.memory,
                    "sandbox_execution": self.config.tools.sandbox_execution,
                },
                "mcp_servers": [s.name for s in self.config.mcp_servers if s.enabled],
            }
            return config_dict

        if args.config_command == "set":
            # Set configuration value
            if "." in args.key:
                # Handle nested keys
                parts = args.key.split(".")
                if parts[0] == "tools":
                    setattr(self.config.tools, parts[1], args.value.lower() == "true")
                else:
                    setattr(self.config, args.key, args.value)
            else:
                setattr(self.config, args.key, args.value)

            save_config()
            return {"message": f"Set {args.key} = {args.value}"}

        if args.config_command == "init":
            # Initialize with default configuration
            self.config = get_default_config()
            save_config()
            return {"message": "Configuration initialized with defaults"}

        return {"error": "Unknown config command"}

    async def handle_tools_command(self, args) -> dict:
        """Handle tools commands"""
        if args.tools_command == "list":
            tools = {
                "file_system": {
                    "enabled": self.config.tools.file_system,
                    "description": "File system operations (read, write, list)",
                },
                "web_fetch": {
                    "enabled": self.config.tools.web_fetch,
                    "description": "Fetch content from web URLs",
                },
                "web_search": {
                    "enabled": self.config.tools.web_search,
                    "description": "Search the web with Google",
                },
                "shell_execution": {
                    "enabled": self.config.tools.shell_execution,
                    "description": "Execute shell commands",
                },
                "memory": {
                    "enabled": self.config.tools.memory,
                    "description": "Persistent memory across sessions",
                },
                "sandbox_execution": {
                    "enabled": self.config.tools.sandbox_execution,
                    "description": "Execute code in ACGS sandbox",
                },
            }
            return {"tools": tools}

        if args.tools_command == "enable":
            if hasattr(self.config.tools, args.tool):
                setattr(self.config.tools, args.tool, True)
                save_config()
                return {"message": f"Enabled tool: {args.tool}"}
            return {"error": f"Unknown tool: {args.tool}"}

        if args.tools_command == "disable":
            if hasattr(self.config.tools, args.tool):
                setattr(self.config.tools, args.tool, False)
                save_config()
                return {"message": f"Disabled tool: {args.tool}"}
            return {"error": f"Unknown tool: {args.tool}"}

        return {"error": "Unknown tools command"}

    async def run(self):
        """Run the CLI application"""
        parser = self.create_parser()
        args = parser.parse_args()

        # Load custom config if specified
        if args.config:
            from gemini_config import GeminiConfig, set_config

            custom_config = GeminiConfig.load_from_file(args.config)
            set_config(custom_config)
            self.config = custom_config
            self.acgs_client = ACGSClient(custom_config)

        # Set up logging
        self.setup_logging(args.log_level)

        # Check if command provided
        if not args.command:
            parser.print_help()
            sys.exit(0)

        # Start MCP servers if enabled
        if not args.no_mcp:
            self.start_mcp_servers()

        try:
            # Check services health
            if not self.check_services_health():
                logger.warning("Some services are unhealthy, continuing anyway...")

            # Handle command
            await self.handle_command(args)

        finally:
            # Stop MCP servers
            if not args.no_mcp:
                self.stop_mcp_servers()


def main():
    """Main entry point"""
    cli = GeminiCLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()
