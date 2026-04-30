"""
Agent API Routes - FastAPI endpoints for the agent
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

from ...agent.main import HCPAgent, get_hcp_agent
from ...agent.memory import get_memory
from ...agent.langsmith import setup_langsmith
from ...agent.langgraph import (
    get_graph_definition,
    get_flow_diagram_mermaid,
    get_flow_diagram_ascii,
)
from ...config import settings

router = APIRouter(prefix="/api/agent", tags=["agent"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    message: str
    intent: str
    entities: Dict[str, Any]
    session_id: str
    success: bool
    error: Optional[str] = None
    interaction: Optional[Dict[str, Any]] = None
    ai_suggestions: Optional[List[Dict[str, Any]]] = None


class HistoryResponse(BaseModel):
    messages: List[Dict[str, Any]]
    count: int


class SessionCreateResponse(BaseModel):
    session_id: str
    user_id: str


def get_agent() -> HCPAgent:
    """Get the shared HCPAgent singleton"""
    setup_langsmith()
    return get_hcp_agent()


_ENRICHMENT_KEYS = [
    "hcp_id", "hcp_name", "hcp_specialty", "hcp_institution",
    "topics", "sentiment", "outcome", "attendees", "date_time", "materials",
]


def _extract_ai_suggestions(tool_results: list) -> List[Dict[str, Any]]:
    """Extract AI follow-up suggestions from tool results."""
    suggestions = []
    for tr in tool_results:
        if tr.get("tool_name") == "suggest_follow_up_actions":
            data = tr.get("data", {})
            if data.get("success") and data.get("suggestions"):
                suggestions = data["suggestions"]
            break
    return suggestions


def _build_interaction_data(tool_results: list, entities: dict, form_data: dict = None) -> Optional[Dict[str, Any]]:
    """Build interaction data from tool results and enriched entities."""
    interaction_data = None

    for tr in tool_results:
        tool_name = tr.get("tool_name")
        if tool_name == "create_interaction" and tr.get("success"):
            interaction_data = tr.get("data", {}).copy()
            break
        if tool_name == "update_interaction" and tr.get("success"):
            interaction_data = tr.get("data", {}).copy()
            break

    if not interaction_data:
        if not entities.get("hcp_id"):
            return None
        interaction_data = {
            "hcp_id": entities.get("hcp_id"),
            "type": "meeting",
        }

    for key in _ENRICHMENT_KEYS:
        if entities.get(key):
            interaction_data[key] = entities[key]

    if form_data:
        for key in _ENRICHMENT_KEYS:
            if form_data.get(key) and not interaction_data.get(key):
                interaction_data[key] = form_data[key]

    if "type" not in interaction_data:
        interaction_data["type"] = entities.get("type") or "meeting"

    return interaction_data


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message"""
    agent = get_agent()

    session_id = request.session_id or str(uuid.uuid4())
    user_id = request.user_id or "default"

    memory = get_memory()
    session = memory.get_session(session_id)
    if not session:
        session = memory.create_session(user_id)
        session_id = session.session_id

    try:
        result = agent.process(
            user_input=request.message,
            session_id=session_id,
            user_id=user_id,
            form_data=request.form_data,
        )

        interaction_data = _build_interaction_data(result.tool_results, result.entities, request.form_data)
        ai_suggestions = _extract_ai_suggestions(result.tool_results)

        return ChatResponse(
            message=result.message,
            intent=result.intent,
            entities=result.entities,
            session_id=session_id,
            success=result.success,
            error=result.error,
            interaction=interaction_data,
            ai_suggestions=ai_suggestions if ai_suggestions else None,
        )

    except Exception as e:
        return ChatResponse(
            message="I encountered an error processing your request.",
            intent="error",
            entities={},
            session_id=session_id,
            success=False,
            error=str(e),
        )


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str, limit: int = 20):
    """Get conversation history for a session"""
    memory = get_memory()
    history = memory.get_history(session_id, limit)

    return HistoryResponse(messages=history, count=len(history))


@router.post("/session", response_model=SessionCreateResponse)
async def create_session(user_id: str = "default"):
    """Create a new session"""
    memory = get_memory()
    session = memory.create_session(user_id)

    return SessionCreateResponse(session_id=session.session_id, user_id=session.user_id)


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a session"""
    memory = get_memory()
    memory.clear(session_id)

    return {"success": True, "message": "Session cleared"}


@router.get("/session/{session_id}/entities")
async def get_session_entities(session_id: str):
    """Get session entity data"""
    memory = get_memory()
    session = memory.get_session(session_id)
    if not session:
        return {"entities": {}}

    extracted = memory.get_entities(session_id)
    return {"entities": extracted.model_dump() if extracted else {}}


@router.get("/health")
async def health_check():
    """Check agent health"""
    try:
        agent = get_agent()
        models = agent.llm.list_models()
        return {
            "status": "healthy",
            "provider": settings.LLM_PROVIDER,
            "models_available": len(models),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@router.get("/models")
async def list_models():
    """List available models"""
    try:
        agent = get_agent()
        models = agent.llm.list_models()
        return {
            "models": [{"id": m.id, "provider": m.provider} for m in models],
            "count": len(models),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph")
async def get_graph():
    """Get the agent graph definition for visualization"""
    return get_graph_definition()


@router.get("/graph/mermaid", response_class=PlainTextResponse)
async def get_graph_mermaid():
    """Get the agent graph as Mermaid diagram"""
    return get_flow_diagram_mermaid()


@router.get("/graph/ascii")
async def get_graph_ascii():
    """Get the agent graph as ASCII diagram"""
    return {"diagram": get_flow_diagram_ascii()}
