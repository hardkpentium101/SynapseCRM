"""
LangGraph Builder - Builds the agent graph
"""

from typing import Callable
from langgraph.graph import StateGraph
from ..graph import build_agent_graph as _build_agent_graph
from .state import AgentState, initial_state
    """Build the HCP Agent graph (delegates to graph.py)"""
    return _build_agent_graph()


def compile_graph() -> Callable:
    """Compile and return the runnable graph"""
    graph = build_agent_graph()
    return graph.compile()


# Singleton compiled graph
_compiled_graph = None


def get_graph() -> Callable:
    """Get or create singleton compiled graph"""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = compile_graph()
    return _compiled_graph


def run_agent(user_input: str, session_id: str = "", user_id: str = "default") -> dict:
    """Run the agent graph with given input"""
    graph = get_graph()

    state = initial_state(user_input, session_id, user_id)

    result = graph.invoke(state)

    return result
