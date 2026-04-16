"""
Follow-up Tools - Tools for follow-up operations
"""

from typing import Dict, Any, Optional
from ..tools.registry import ToolRegistry, ToolDefinition


def register_followup_tools(registry: ToolRegistry):
    """Register all follow-up tools"""

    # create_follow_up
    registry.register(
        name="create_follow_up",
        func=_create_follow_up,
        definition=ToolDefinition(
            name="create_follow_up",
            description="Create a new follow-up task",
            parameters={
                "interaction_id": {
                    "type": "string",
                    "description": "Associated interaction ID (optional)",
                },
                "hcp_id": {
                    "type": "string",
                    "description": "HCP ID for the follow-up (optional)",
                },
                "type": {
                    "type": "string",
                    "description": "Follow-up type (call, meeting, email)",
                },
                "description": {
                    "type": "string",
                    "description": "Description of the follow-up",
                },
                "due_date": {"type": "string", "description": "Due date (ISO format)"},
            },
            required=["description"],
        ),
    )

    # get_follow_ups
    registry.register(
        name="get_follow_ups",
        func=_get_follow_ups,
        definition=ToolDefinition(
            name="get_follow_ups",
            description="Get follow-up tasks, optionally filtered",
            parameters={
                "interaction_id": {
                    "type": "string",
                    "description": "Filter by interaction ID (optional)",
                },
                "hcp_id": {
                    "type": "string",
                    "description": "Filter by HCP ID (optional)",
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status (pending, completed, cancelled)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results",
                    "default": 20,
                },
            },
            required=[],
        ),
    )

    # update_follow_up
    registry.register(
        name="update_follow_up",
        func=_update_follow_up,
        definition=ToolDefinition(
            name="update_follow_up",
            description="Update status of a follow-up task",
            parameters={
                "follow_up_id": {
                    "type": "string",
                    "description": "Follow-up ID to update",
                },
                "status": {
                    "type": "string",
                    "description": "New status (pending, completed, cancelled)",
                },
                "notes": {
                    "type": "string",
                    "description": "Additional notes (optional)",
                },
            },
            required=["follow_up_id", "status"],
        ),
    )


def _create_follow_up(
    description: str,
    interaction_id: str = None,
    hcp_id: str = None,
    type: str = None,
    due_date: str = None,
) -> Dict[str, Any]:
    """Create new follow-up"""
    return {
        "description": description,
        "interaction_id": interaction_id,
        "hcp_id": hcp_id,
        "type": type,
        "due_date": due_date,
        "status": "need_integration",
        "message": f"Create follow-up: {description}",
    }


def _get_follow_ups(
    interaction_id: str = None, hcp_id: str = None, status: str = None, limit: int = 20
) -> Dict[str, Any]:
    """Get follow-ups"""
    return {
        "interaction_id": interaction_id,
        "hcp_id": hcp_id,
        "status": status,
        "limit": limit,
        "status": "need_integration",
        "message": f"Get follow-ups (hcp: {hcp_id}, status: {status})",
    }


def _update_follow_up(
    follow_up_id: str, status: str, notes: str = None
) -> Dict[str, Any]:
    """Update follow-up status"""
    return {
        "follow_up_id": follow_up_id,
        "status": status,
        "notes": notes,
        "status": "need_integration",
        "message": f"Update follow-up {follow_up_id} to {status}",
    }
