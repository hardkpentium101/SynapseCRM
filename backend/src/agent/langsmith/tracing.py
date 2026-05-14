"""
LangSmith Integration - Tracing and visualization for LangGraph
"""

import os
import time
from typing import Optional, Dict, Any, Callable
from functools import wraps

from ...config import get_settings

LANGSMITH_AVAILABLE = False
_langsmith_traceable = None
_langsmith_client: Optional[Any] = None

try:
    from langsmith import traceable as _ls_traceable
    from langsmith import Client
    _langsmith_traceable = _ls_traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    pass

_initialized = False


def setup_langsmith():
    """Setup LangSmith tracing if API key is available. Idempotent."""
    global _initialized
    if _initialized:
        return _initialized

    settings = get_settings()
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY") or settings.LANGSMITH_API_KEY

    if not langsmith_api_key:
        return False

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "hcp-agent")
    _initialized = True
    return True


def is_tracing_enabled() -> bool:
    """Check if tracing is available and enabled."""
    return LANGSMITH_AVAILABLE and _initialized


def _get_langsmith_client():
    """Get or create a cached LangSmith client."""
    global _langsmith_client
    if _langsmith_client is None:
        _langsmith_client = Client()
    return _langsmith_client


def emit_llm_call(
    model: str,
    messages: list,
    response_content: Optional[str],
    usage: Optional[Dict[str, int]],
    latency_ms: float,
    tool_calls: Optional[list] = None,
):
    """Emit a trace for an LLM call using the LangSmith client."""
    if not is_tracing_enabled():
        return

    try:
        client = _get_langsmith_client()
        is_local = model.startswith("localhost") or model.startswith("http://") or model.startswith("file://")
        client.create_run(
            name=f"llm:{model}",
            run_type="llm",
            inputs={
                "model": model,
                "message_count": len(messages),
                "has_tool_calls": bool(tool_calls),
            },
            outputs={
                "content": response_content[:500] if response_content else "",
                "usage": usage or {},
                "latency_ms": latency_ms,
            },
            tags=["llm-call", model],
            metadata={
                "agent": "hcp-agent",
                "ls_model_name": model,
                "is_local_model": is_local,
            },
        )
    except Exception:
        pass


def emit_tool_call(tool_name: str, arguments: Dict[str, Any], result: Any):
    """Emit a trace for a tool execution."""
    if not is_tracing_enabled():
        return

    try:
        client = _get_langsmith_client()
        client.create_run(
            name=f"tool:{tool_name}",
            run_type="tool",
            inputs={"arguments": arguments},
            outputs={"result_preview": _safe_trunc(result, 500)},
            tags=["tool-call", tool_name],
            metadata={"agent": "hcp-agent"},
        )
    except Exception:
        pass


def emit_graph_node(node_name: str, inputs: Dict[str, Any], outputs: Dict[str, Any]):
    """Emit a trace for a LangGraph node execution."""
    if not is_tracing_enabled():
        return

    try:
        client = _get_langsmith_client()
        client.create_run(
            name=f"node:{node_name}",
            run_type="chain",
            inputs={k: _safe_str(v) for k, v in inputs.items()},
            outputs={k: _safe_str(v) for k, v in outputs.items()},
            tags=["langgraph-node", node_name],
            metadata={"agent": "hcp-agent"},
        )
    except Exception:
        pass


def _safe_str(v: Any) -> str:
    """Convert value to string safely (truncate if needed)."""
    s = str(v)
    if len(s) > 1000:
        return s[:1000] + "..."
    return s


def _safe_trunc(v: Any, max_len: int) -> str:
    s = str(v)
    if len(s) > max_len:
        return s[:max_len] + "..."
    return s


def traceable(name: str = None, tags: list = None):
    """
    Decorator to trace a function with LangSmith.

    Usage:
        @traceable(name="intent-classifier")
        def classify_intent(text):
            ...
    """
    if not LANGSMITH_AVAILABLE:
        def passthrough(func):
            return func
        return passthrough

    def decorator(func: Callable):
        @_langsmith_traceable(name=name or func.__name__, tags=tags or ["hcp-agent"])
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def wait_for_all_tracers(timeout: float = 10.0):
    """
    Flush all pending traces to LangSmith.

    Call this at the end of short scripts before process exit to ensure
    traces are sent. Equivalent to langchain's wait_for_all_tracers().

    Args:
        timeout: Maximum seconds to wait for flush to complete.
    """
    if not LANGSMITH_AVAILABLE:
        return

    try:
        client = Client()
        client.flush(timeout=timeout)
    except Exception:
        pass
