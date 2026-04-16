"""
Interaction Tools - Tools for interaction operations
"""

from typing import Dict, Any, Optional, List
from ..tools.registry import ToolRegistry, ToolDefinition


def register_interaction_tools(registry: ToolRegistry):
    """Register all interaction tools"""

    # create_interaction
    registry.register(
        name="create_interaction",
        func=_create_interaction,
        definition=ToolDefinition(
            name="create_interaction",
            description="Create a new interaction record with an HCP",
            parameters={
                "hcp_id": {
                    "type": "string",
                    "description": "The HCP's unique identifier",
                },
                "type": {
                    "type": "string",
                    "description": "Type of interaction (meeting, call, email, conference)",
                },
                "date_time": {
                    "type": "string",
                    "description": "When the interaction occurred (ISO format)",
                },
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Discussion topics covered",
                },
                "sentiment": {
                    "type": "string",
                    "description": "Overall sentiment (positive, neutral, negative)",
                },
                "outcome": {
                    "type": "string",
                    "description": "Outcome or result of the interaction",
                },
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Other people present",
                },
                "notes": {"type": "string", "description": "Additional notes"},
            },
            required=["hcp_id", "type", "date_time"],
        ),
    )

    # get_interactions
    registry.register(
        name="get_interactions",
        func=_get_interactions,
        definition=ToolDefinition(
            name="get_interactions",
            description="Get interactions, optionally filtered by HCP or user",
            parameters={
                "hcp_id": {
                    "type": "string",
                    "description": "Filter by HCP ID (optional)",
                },
                "user_id": {
                    "type": "string",
                    "description": "Filter by user ID (optional)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results to return",
                    "default": 20,
                },
            },
            required=[],
        ),
    )

    # get_interaction_summary
    registry.register(
        name="get_interaction_summary",
        func=_get_interaction_summary,
        definition=ToolDefinition(
            name="get_interaction_summary",
            description="Get a summary of a specific interaction",
            parameters={
                "interaction_id": {
                    "type": "string",
                    "description": "The interaction's unique identifier",
                }
            },
            required=["interaction_id"],
        ),
    )


def _create_interaction(
    hcp_id: str,
    type: str,
    date_time: str,
    topics: List[str] = None,
    sentiment: str = None,
    outcome: str = None,
    attendees: List[str] = None,
    notes: str = None,
) -> Dict[str, Any]:
    """Create new interaction"""
    return {
        "hcp_id": hcp_id,
        "type": type,
        "date_time": date_time,
        "topics": topics or [],
        "sentiment": sentiment,
        "outcome": outcome,
        "attendees": attendees or [],
        "notes": notes,
        "status": "need_integration",
        "message": f"Create {type} interaction with HCP: {hcp_id}",
    }


def _get_interactions(
    hcp_id: str = None, user_id: str = None, limit: int = 20
) -> Dict[str, Any]:
    """Get interactions with filters"""
    return {
        "hcp_id": hcp_id,
        "user_id": user_id,
        "limit": limit,
        "status": "need_integration",
        "message": f"Get interactions (hcp: {hcp_id}, user: {user_id})",
    }


def _get_interaction_summary(interaction_id: str) -> Dict[str, Any]:
    """Get interaction summary"""
    return {
        "interaction_id": interaction_id,
        "status": "need_integration",
        "message": f"Get summary for interaction: {interaction_id}",
    }
