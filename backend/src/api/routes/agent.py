"""
Agent API Routes - FastAPI endpoints for the agent
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

from ...agent.main import HCPAgent
from ...agent.llm_manager import get_llm_manager, GroqLLMManager
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


class HistoryResponse(BaseModel):
    messages: List[Dict[str, Any]]
    count: int


class SessionCreateResponse(BaseModel):
    session_id: str
    user_id: str


# Singleton agent instance
_agent_instance: Optional[HCPAgent] = None


def get_agent() -> HCPAgent:
    """Get or create agent instance"""
    global _agent_instance
    if _agent_instance is None:
        setup_langsmith()
        llm = get_llm_manager()
        _agent_instance = HCPAgent(llm)
    return _agent_instance


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message"""
    agent = get_agent()

    # Use provided session_id or create new one
    session_id = request.session_id or str(uuid.uuid4())
    user_id = request.user_id or "default"

    # Check if session exists, if not create it
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

        interaction_data = None
        if result.tool_results:
            for tr in result.tool_results:
                if tr.get("tool_name") == "create_interaction" and tr.get("success"):
                    interaction_data = tr.get("data", {})

                    enriched_entities = result.entities

                    if enriched_entities.get("hcp_id"):
                        interaction_data["hcp_id"] = enriched_entities["hcp_id"]
                    if enriched_entities.get("hcp_name"):
                        interaction_data["hcp_name"] = enriched_entities["hcp_name"]
                    if enriched_entities.get("hcp_specialty"):
                        interaction_data["hcp_specialty"] = enriched_entities[
                            "hcp_specialty"
                        ]
                    if enriched_entities.get("hcp_institution"):
                        interaction_data["hcp_institution"] = enriched_entities[
                            "hcp_institution"
                        ]

                    if enriched_entities.get("topics"):
                        interaction_data["topics"] = enriched_entities["topics"]
                    if enriched_entities.get("sentiment"):
                        interaction_data["sentiment"] = enriched_entities["sentiment"]
                    if enriched_entities.get("outcome"):
                        interaction_data["outcome"] = enriched_entities["outcome"]
                    if enriched_entities.get("attendees"):
                        interaction_data["attendees"] = enriched_entities["attendees"]
                    if enriched_entities.get("date_time"):
                        interaction_data["date_time"] = enriched_entities["date_time"]
                    if enriched_entities.get("materials"):
                        interaction_data["materials"] = enriched_entities["materials"]

        return ChatResponse(
            message=result.message,
            intent=result.intent,
            entities=result.entities,
            session_id=session_id,
            success=result.success,
            error=result.error,
            interaction=interaction_data,
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


@router.get("/health")
async def health_check():
    """Check agent health"""
    try:
        agent = get_agent()
        # Try to get available models
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
