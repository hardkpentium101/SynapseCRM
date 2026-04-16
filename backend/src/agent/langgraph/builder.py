"""
LangGraph Builder - Builds the agent graph
"""

from typing import Callable, Literal
from langgraph.graph import StateGraph, END
from .state import AgentState, initial_state
from .nodes import (
    intent_classifier_node,
    entity_extractor_node,
    orchestrator_node,
    format_response_node,
    should_continue,
)


def build_agent_graph() -> StateGraph:
    """Build the HCP Agent graph"""

    # Create graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("intent_classifier", intent_classifier_node)
    graph.add_node("entity_extractor", entity_extractor_node)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("format_response", format_response_node)

    # Set entry point
    graph.set_entry_point("intent_classifier")

    # Add conditional edges from intent_classifier
    graph.add_conditional_edges(
        "intent_classifier",
        should_continue,
        {"entity_extractor": "entity_extractor", "orchestrator": "orchestrator"},
    )

    # Add regular edges
    graph.add_edge("entity_extractor", "orchestrator")
    graph.add_edge("orchestrator", "format_response")
    graph.add_edge("format_response", END)

    return graph


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
