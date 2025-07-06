"""
Agent management commands for Gemini CLI
"""
# Constitutional Hash: cdd01ef066bc6cf2

import argparse
from typing import Any


def add_arguments(parser: argparse.ArgumentParser):
    """Add agent command arguments"""
    subparsers = parser.add_subparsers(dest="agent_command", help="Agent commands")

    # Create agent
    create_parser = subparsers.add_parser("create", help="Create a new agent")
    create_parser.add_argument("--name", required=True, help="Agent name")
    create_parser.add_argument("--type", required=True, help="Agent type")
    create_parser.add_argument(
        "--capabilities",
        nargs="+",
        default=["code_generation", "data_analysis"],
        help="Agent capabilities",
    )

    # List agents
    list_parser = subparsers.add_parser("list", help="List all agents")
    list_parser.add_argument(
        "--active", action="store_true", help="Show only active agents"
    )

    # Get agent details
    get_parser = subparsers.add_parser("get", help="Get agent details")
    get_parser.add_argument("agent_id", help="Agent ID")

    # Update agent
    update_parser = subparsers.add_parser("update", help="Update agent")
    update_parser.add_argument("agent_id", help="Agent ID")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--add-capability", help="Add capability")
    update_parser.add_argument("--remove-capability", help="Remove capability")

    # Delete agent
    delete_parser = subparsers.add_parser("delete", help="Delete agent")
    delete_parser.add_argument("agent_id", help="Agent ID")
    delete_parser.add_argument("--force", action="store_true", help="Force deletion")


async def handle_command(args: argparse.Namespace, client) -> dict[str, Any]:
    """Handle agent commands"""

    if args.agent_command == "create":
        # Create new agent
        result = client.create_agent(
            name=args.name, agent_type=args.type, capabilities=args.capabilities
        )

        # Save credentials for future use
        if "api_key" in result:
            return {
                "agent_id": result["agent_id"],
                "api_key": result["api_key"],
                "message": "Agent created successfully. Save the API key - it won't be shown again!",
                "capabilities": result.get("capabilities", []),
            }
        return result

    if args.agent_command == "list":
        # List agents
        agents = client.list_agents()

        if args.active:
            agents = [a for a in agents if a.get("status") == "active"]

        return {"agents": agents, "count": len(agents)}

    if args.agent_command == "get":
        # Get agent details
        agent = client.get_agent(args.agent_id)

        # Get recent operations for the agent
        operations = client.list_agent_operations(args.agent_id)

        return {
            "agent": agent,
            "recent_operations": operations[:5] if operations else [],
            "total_operations": len(operations) if operations else 0,
        }

    if args.agent_command == "update":
        # Update agent (would need to implement in ACGSClient)
        return {"error": "Agent update not yet implemented", "agent_id": args.agent_id}

    if args.agent_command == "delete":
        # Delete agent (would need to implement in ACGSClient)
        return {
            "error": "Agent deletion not yet implemented",
            "agent_id": args.agent_id,
        }

    return {"error": "Unknown agent command"}
