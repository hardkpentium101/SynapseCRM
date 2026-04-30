"""
Context Tools - Tools for session/memory operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ..tools.registry import ToolRegistry, ToolDefinition


def register_context_tools(registry: ToolRegistry):
    """Register all context/memory tools"""

    # get_conversation_history
    registry.register(
        name="get_conversation_history",
        func=_get_conversation_history,
        definition=ToolDefinition(
            name="get_conversation_history",
            description="Get recent conversation history for context",
            parameters={
                "limit": {
                    "type": "integer",
                    "description": "Number of recent messages to return",
                    "default": 10,
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID to retrieve history for",
                },
            },
            required=["session_id"],
        ),
    )

    # get_extracted_entities
    registry.register(
        name="get_extracted_entities",
        func=_get_extracted_entities,
        definition=ToolDefinition(
            name="get_extracted_entities",
            description="Get previously extracted entities from this session",
            parameters={},
            required=[],
        ),
    )

    # add_context
    registry.register(
        name="add_context",
        func=_add_context,
        definition=ToolDefinition(
            name="add_context",
            description="Add custom context for this session",
            parameters={
                "key": {"type": "string", "description": "Context key"},
                "value": {"type": "string", "description": "Context value"},
            },
            required=["key", "value"],
        ),
    )

    # clear_session
    registry.register(
        name="clear_session",
        func=_clear_session,
        definition=ToolDefinition(
            name="clear_session",
            description="Clear all session context and history",
            parameters={},
            required=[],
        ),
    )


def _get_conversation_history(session_id: str, limit: int = 10) -> Dict[str, Any]:
    """Get conversation history from session memory"""
    from ..memory.conversation_memory import get_memory

    memory = get_memory()
    history = memory.get_history(session_id=session_id, limit=limit)

    return {
        "messages": [
            {
                "role": msg["role"],
                "content": msg["content"],
            }
            for msg in history
        ],
        "count": len(history),
    }


def _get_extracted_entities() -> Dict[str, Any]:
    """Get extracted entities from session"""
    from ..memory.conversation_memory import get_memory

    memory = get_memory()
    entities = memory.get_entities()

    return {
        "entities": entities.to_context_dict()
        if hasattr(entities, "to_context_dict")
        else entities,
        "is_empty": entities.is_empty() if hasattr(entities, "is_empty") else True,
    }


def _add_context(key: str, value: str) -> Dict[str, Any]:
    """Add context to session"""
    from ..memory.conversation_memory import get_memory

    memory = get_memory()
    memory.set_context(key, value)

    return {
        "success": True,
        "key": key,
        "message": f"Context '{key}' added successfully",
    }


def _clear_session() -> Dict[str, Any]:
    """Clear all session data"""
    from ..memory.conversation_memory import clear_memory

    clear_memory()

    return {"success": True, "message": "Session cleared successfully"}
