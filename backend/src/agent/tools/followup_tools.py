"""
Follow-up Tools - Tools for follow-up operations
"""

from typing import Dict, Any, Optional, List
import json
from ..tools.registry import ToolRegistry, ToolDefinition


FOLLOW_UP_PROMPT = """Analyze this interaction and suggest exactly 3 follow-up actions.

Consider:
- Topics discussed (e.g., if efficacy data was shared, suggest follow-up with results)
- HCP engagement level (high engagement → deeper discussions, low → brief check-in)
- Time since last interaction
- Previous follow-up patterns
- Any materials shared during the interaction

Return EXACTLY 3 follow-up actions as a JSON array:
[
  {"type": "call", "description": "Follow up on efficacy data discussed", "due_in_days": 7, "priority": "high"},
  {"type": "meeting", "description": "Schedule follow-up meeting to review results", "due_in_days": 14, "priority": "medium"},
  {"type": "email", "description": "Send additional materials or resources", "due_in_days": 3, "priority": "low"}
]

Valid types: call, meeting, email, send_material, sample_request, other.
Always return exactly 3 items. Never fewer."""


def register_followup_tools(registry: ToolRegistry):
    """Register all follow-up tools"""

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

    registry.register(
        name="suggest_follow_up_actions",
        func=_suggest_follow_up_actions,
        definition=ToolDefinition(
            name="suggest_follow_up_actions",
            description="AI-driven follow-up suggestions based on interaction context, HCP history, and engagement patterns.",
            parameters={
                "interaction_id": {
                    "type": "string",
                    "description": "Interaction ID to base suggestions on",
                },
                "hcp_id": {
                    "type": "string",
                    "description": "HCP ID for context",
                },
                "context": {
                    "type": "string",
                    "description": "Additional context about the interaction or HCP",
                },
            },
            required=[],
        ),
    )

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
    """Create new follow-up with DB persistence"""
    from ..services.tool_services import FollowUpService

    result = FollowUpService.create_follow_up(
        description=description,
        interaction_id=interaction_id,
        hcp_id=hcp_id,
        type=type,
        due_date=due_date,
        user_id="default",
    )
    return result


def _suggest_follow_up_actions(
    interaction_id: str = None,
    hcp_id: str = None,
    context: str = None,
) -> Dict[str, Any]:
    """AI-driven follow-up suggestions based on interaction context"""
    from ..services.tool_services import InteractionService, HCPService

    suggestions = []
    interaction_context = ""
    hcp_context = ""

    if interaction_id:
        interaction_data = InteractionService.get_interaction_summary(interaction_id)
        if interaction_data:
            interaction_context = f"Interaction: type={interaction_data.get('type')}, topics={interaction_data.get('topics')}, sentiment={interaction_data.get('sentiment')}"

    if hcp_id:
        hcp_data = HCPService.get_hcp_by_id(hcp_id)
        if hcp_data:
            hcp_context = f"HCP: {hcp_data.get('name')}, specialty={hcp_data.get('specialty')}, institution={hcp_data.get('institution')}"
            history = HCPService.get_hcp_history(hcp_id, limit=5)
            if history:
                hcp_context += f", recent_interactions={len(history)}"

    user_context = f"{interaction_context}\n{hcp_context}\n{context or ''}".strip()

    from ..llm_manager import get_llm_manager

    llm = get_llm_manager()
    messages = [
        {"role": "system", "content": FOLLOW_UP_PROMPT},
        {"role": "user", "content": f"Context:\n{user_context}\n\nSuggest follow-up actions."},
    ]

    try:
        response = llm.complete(messages, model="llama-3.1-8b-instant", temperature=0.3, max_tokens=512)
        if response.content:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            suggestions = json.loads(content)
            if not isinstance(suggestions, list):
                suggestions = [suggestions]
    except Exception as e:
        suggestions = _rule_based_fallback(interaction_context, hcp_context, context)

    return {
        "success": True,
        "suggestions": suggestions,
        "count": len(suggestions),
        "interaction_id": interaction_id,
        "hcp_id": hcp_id,
    }


def _rule_based_fallback(interaction_context: str, hcp_context: str, context: str) -> List[Dict]:
    """Fallback suggestions based on simple rules — always returns exactly 3"""
    suggestions = []
    text = f"{interaction_context} {hcp_context} {context}".lower()

    if "efficacy" in text or "trial" in text or "data" in text:
        suggestions.append({
            "type": "call",
            "description": "Follow up on efficacy data discussed",
            "due_in_days": 7,
            "priority": "high",
        })

    if "sample" in text or "brochure" in text or "material" in text:
        suggestions.append({
            "type": "email",
            "description": "Send additional materials requested",
            "due_in_days": 3,
            "priority": "medium",
        })

    if "meeting" in text or "discussed" in text:
        suggestions.append({
            "type": "meeting",
            "description": "Schedule follow-up meeting",
            "due_in_days": 14,
            "priority": "medium",
        })

    defaults = [
        {"type": "call", "description": "Routine check-in call", "due_in_days": 14, "priority": "low"},
        {"type": "meeting", "description": "Schedule follow-up meeting", "due_in_days": 21, "priority": "low"},
        {"type": "email", "description": "Send follow-up email with resources", "due_in_days": 5, "priority": "low"},
    ]
    for d in defaults:
        if len(suggestions) >= 3:
            break
        suggestions.append(d)

    return suggestions[:3]


def _get_follow_ups(
    interaction_id: str = None, hcp_id: str = None, status: str = None, limit: int = 20
) -> Dict[str, Any]:
    """Get follow-ups"""
    from ..services.tool_services import FollowUpService

    results = FollowUpService.get_follow_ups(
        interaction_id=interaction_id,
        hcp_id=hcp_id,
        status=status,
        limit=limit,
    )
    return {"follow_ups": results, "count": len(results)}


def _update_follow_up(
    follow_up_id: str, status: str, notes: str = None
) -> Dict[str, Any]:
    """Update follow-up status"""
    from ..services.tool_services import FollowUpService

    result = FollowUpService.update_follow_up(
        follow_up_id=follow_up_id,
        status=status,
        notes=notes,
    )
    if result:
        return result
    return {"error": f"Follow-up {follow_up_id} not found", "updated": False}
