"""
Interaction Tools - Tools for interaction operations
"""

from typing import Dict, Any, List
import logging

from ..tools.registry import ToolRegistry, ToolDefinition

logger = logging.getLogger(__name__)


def register_interaction_tools(registry: ToolRegistry):
    """Register all interaction tools"""

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
                "materials": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Material/product names shared during the interaction (e.g. ['OncoBoost Brochure', 'NeuroPlus Clinical Summary'])",
                },
            },
            required=["hcp_id", "type", "date_time"],
        ),
    )

    registry.register(
        name="update_interaction",
        func=_update_interaction,
        definition=ToolDefinition(
            name="update_interaction",
            description="Update an existing interaction record. Provide interaction_id and fields to change. Can also reassign hcp_id.",
            parameters={
                "interaction_id": {
                    "type": "string",
                    "description": "The interaction's unique identifier",
                },
                "hcp_id": {
                    "type": "string",
                    "description": "Reassign to a different HCP (optional)",
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
                "reason": {
                    "type": "string",
                    "description": "Reason for the update (for audit log)",
                },
            },
            required=["interaction_id"],
        ),
    )

    registry.register(
        name="get_last_interaction",
        func=_get_last_interaction,
        definition=ToolDefinition(
            name="get_last_interaction",
            description="Get the most recently created interaction for the current user",
            parameters={
                "user_id": {
                    "type": "string",
                    "description": "User ID (optional, defaults to current user)",
                },
            },
            required=[],
        ),
    )

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
    materials: List[str] = None,
) -> Dict[str, Any]:
    """Create new interaction with DB persistence"""
    from ..services.tool_services import InteractionService

    result = InteractionService.create_interaction(
        hcp_id=hcp_id,
        type=type,
        date_time=date_time,
        user_id="default",
        topics=topics,
        sentiment=sentiment,
        outcome=outcome,
        attendees=attendees,
        notes=notes,
        materials=materials,
    )
    return result


def _update_interaction(
    interaction_id: str,
    hcp_id: str = None,
    type: str = None,
    date_time: str = None,
    topics: List[str] = None,
    sentiment: str = None,
    outcome: str = None,
    attendees: List[str] = None,
    notes: str = None,
    reason: str = None,
) -> Dict[str, Any]:
    """Update existing interaction with audit logging"""
    from ..services.tool_services import InteractionService

    fields = {
        "type": type,
        "date_time": date_time,
        "topics": topics,
        "sentiment": sentiment,
        "outcome": outcome,
        "attendees": attendees,
        "notes": notes,
    }
    fields = {k: v for k, v in fields.items() if v is not None}

    if hcp_id:
        fields["hcp_id"] = hcp_id

    if not fields:
        return {"success": False, "error": "No fields provided to update"}

    result = InteractionService.update_interaction(
        interaction_id=interaction_id,
        fields=fields,
        reason=reason or "User-initiated update",
    )
    return result


def _get_last_interaction(user_id: str = "default") -> Dict[str, Any]:
    """Get the most recent interaction"""
    from ..services.tool_services import InteractionService

    result = InteractionService.get_last_interaction(user_id=user_id)
    if result:
        return {"success": True, "interaction": result}
    return {"success": False, "error": "No interactions found"}


def _get_interactions(
    hcp_id: str = None, user_id: str = None, limit: int = 20
) -> Dict[str, Any]:
    """Get interactions with filters"""
    from ..services.tool_services import InteractionService

    results = InteractionService.get_interactions(
        hcp_id=hcp_id, user_id=user_id, limit=limit
    )
    return {"interactions": results, "count": len(results)}


def _get_interaction_summary(interaction_id: str) -> Dict[str, Any]:
    """Get interaction summary"""
    from ..services.tool_services import InteractionService

    result = InteractionService.get_interaction_summary(interaction_id)
    if result:
        return result
    return {"error": f"Interaction {interaction_id} not found"}
