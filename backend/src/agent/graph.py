"""
LangGraph Graph Definition - Standalone graph file for LangGraph SDK

This file is loaded by LangGraph SDK / LangSmith for visualization.
Can be loaded as: src.agent.graph.graph
"""

import sys
from pathlib import Path

# Ensure we can import the modules correctly
_file = Path(__file__).resolve()
_backend_src = _file.parent.parent
_backend = _backend_src.parent

# Add paths
if str(_backend_src) not in sys.path:
    sys.path.insert(0, str(_backend_src))
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

# Now import using absolute imports from backend root
from src.agent.langgraph.state import AgentState, initial_state
from src.agent.langgraph.nodes import (
    intent_classifier_node,
    entity_extractor_node,
    orchestrator_node,
    format_response_node,
    should_continue,
)
from langgraph.graph import StateGraph, END

# Build the graph
graph_builder = StateGraph(AgentState)

# Add nodes
graph_builder.add_node("intent_classifier", intent_classifier_node)
graph_builder.add_node("entity_extractor", entity_extractor_node)
graph_builder.add_node("orchestrator", orchestrator_node)
graph_builder.add_node("format_response", format_response_node)

# Set entry point
graph_builder.set_entry_point("intent_classifier")

# Add conditional edges
graph_builder.add_conditional_edges(
    "intent_classifier",
    should_continue,
    {"entity_extractor": "entity_extractor", "orchestrator": "orchestrator"},
)

# Add regular edges
graph_builder.add_edge("entity_extractor", "orchestrator")
graph_builder.add_edge("orchestrator", "format_response")
graph_builder.add_edge("format_response", END)

# Compile
graph = graph_builder.compile()

__all__ = ["graph", "AgentState", "initial_state"]
