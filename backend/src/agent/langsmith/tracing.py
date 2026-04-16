"""
LangSmith Integration - Tracing and visualization for LangGraph
"""

import os
from typing import Optional, Dict, Any
from functools import wraps

from ..config import settings


def setup_langsmith():
    """Setup LangSmith tracing if API key is available"""
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY")

    if not langsmith_api_key:
        print("⚠ LangSmith API key not set. Set LANGSMITH_API_KEY to enable tracing.")
        return None

    try:
        from langsmith import Client
        from langchain_core.tracers import LangSmithTracer

        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "hcp-agent")

        client = Client(api_key=langsmith_api_key)
        tracer = LangSmithTracer()

        print(
            f"✓ LangSmith tracing enabled for project: {os.getenv('LANGSMITH_PROJECT', 'hcp-agent')}"
        )

        return {
            "client": client,
            "tracer": tracer,
            "project": os.getenv("LANGSMITH_PROJECT", "hcp-agent"),
        }
    except ImportError:
        print("⚠ langsmith package not installed. Run: pip install langsmith")
        return None
    except Exception as e:
        print(f"⚠ LangSmith setup failed: {e}")
        return None


def traceable(name: str = None, tags: list = None):
    """
    Decorator to trace a function with LangSmith

    Usage:
        @traceable(name="intent-classifier")
        def classify_intent(text):
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            langsmith_config = setup_langsmith()

            if langsmith_config:
                try:
                    tracer = langsmith_config["tracer"]
                    with tracer.trace(name=name or func.__name__) as run:
                        result = func(*args, **kwargs)
                        run.end(outputs={"result": str(result)[:1000]})
                        return result
                except Exception as e:
                    print(f"LangSmith tracing error: {e}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


class LangSmithTracer:
    """Wrapper for LangSmith tracing"""

    def __init__(self):
        self.config = setup_langsmith()
        self.enabled = self.config is not None

    def trace_node(
        self, node_name: str, inputs: Dict[str, Any], outputs: Dict[str, Any] = None
    ):
        """Trace a graph node execution"""
        if not self.enabled:
            return

        try:
            from langchain_core.tracers import LangSmithTracer

            tracer = self.config["tracer"]
            with tracer.trace(
                name=node_name,
                tags=["langgraph", "hcp-agent"],
                metadata={"agent": "hcp-agent"},
            ) as run:
                run.end(outputs=outputs or {})
        except Exception as e:
            print(f"Tracing error: {e}")

    def trace_tool_call(self, tool_name: str, arguments: Dict[str, Any], result: Any):
        """Trace a tool call"""
        if not self.enabled:
            return

        self.trace_node(
            node_name=f"tool:{tool_name}",
            inputs={"arguments": arguments},
            outputs={"result": str(result)[:500]},
        )

    def trace_llm_call(self, model: str, prompt: str, response: str):
        """Trace an LLM call"""
        if not self.enabled:
            return

        self.trace_node(
            node_name=f"llm:{model}",
            inputs={"prompt_length": len(prompt)},
            outputs={
                "response_length": len(response),
                "response_preview": response[:200],
            },
        )


# Singleton tracer instance
_langsmith_tracer: Optional[LangSmithTracer] = None


def get_tracer() -> Optional[LangSmithTracer]:
    """Get or create LangSmith tracer"""
    global _langsmith_tracer
    if _langsmith_tracer is None:
        _langsmith_tracer = LangSmithTracer()
    return _langsmith_tracer if _langsmith_tracer.enabled else None
