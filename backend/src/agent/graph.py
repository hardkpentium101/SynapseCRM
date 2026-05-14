"""
LangGraph Graph Definition - Standalone graph file for LangGraph SDK

This file is loaded by LangGraph SDK / LangSmith for visualization.
Can be loaded as: src.agent.graph.graph
"""

try:
    from .langgraph.state import AgentState, initial_state
    from .langgraph.nodes import (
        intent_classifier_node,
        entity_extractor_node,
        orchestrator_node,
        format_response_node,
        should_continue,
    )
except ImportError:
    from src.agent.langgraph.state import AgentState, initial_state
    from src.agent.langgraph.nodes import (
        intent_classifier_node,
        entity_extractor_node,
        orchestrator_node,
        format_response_node,
        should_continue,
    )
from langgraph.graph import StateGraph, END


def build_agent_graph() -> StateGraph:
    """Build the HCP Agent graph - single source of truth"""
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("intent_classifier", intent_classifier_node)
    graph_builder.add_node("entity_extractor", entity_extractor_node)
    graph_builder.add_node("orchestrator", orchestrator_node)
    graph_builder.add_node("format_response", format_response_node)

    graph_builder.set_entry_point("intent_classifier")

    graph_builder.add_conditional_edges(
        "intent_classifier",
        should_continue,
        {"entity_extractor": "entity_extractor", "orchestrator": "orchestrator"},
    )

    graph_builder.add_edge("entity_extractor", "orchestrator")
    graph_builder.add_edge("orchestrator", "format_response")
    graph_builder.add_edge("format_response", END)

    return graph_builder


graph = build_agent_graph().compile()

__all__ = ["graph", "build_agent_graph", "AgentState", "initial_state"]
