"""
LangGraph State - Defines the state passed through the graph
"""

from typing import List, Optional, Dict, Any, TypedDict
from langchain_core.messages import BaseMessage
from ..schemas.entities import ExtractedEntities


class AgentState(TypedDict):
    """State that flows through the agent graph"""

    messages: List[Dict[str, Any]]  # conversation history
    user_input: str
    intent: Optional[str]
    intent_confidence: float
    entities: Optional[Dict[str, Any]]
    response: Optional[str]
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    error: Optional[str]
    session_id: str
    user_id: str


def initial_state(
    user_input: str, session_id: str = "", user_id: str = "default"
) -> AgentState:
    """Create initial state for a new request"""
    return AgentState(
        messages=[],
        user_input=user_input,
        intent=None,
        intent_confidence=0.0,
        entities=None,
        response=None,
        tool_calls=[],
        tool_results=[],
        error=None,
        session_id=session_id,
        user_id=user_id,
    )
