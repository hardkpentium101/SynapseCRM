"""
LangGraph Nodes - Define nodes for the agent graph
"""

from typing import Dict, Any, Literal
from ..schemas.entities import ExtractedEntities
from ..services.agent_factory import get_shared_llm_manager, get_shared_model_selector
from ..langsmith.tracing import emit_graph_node


def intent_classifier_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Classify user intent"""
    from ..subagents.intent_classifier import IntentClassifierAgent

    llm = get_shared_llm_manager()
    selector = get_shared_model_selector()
    agent = IntentClassifierAgent(llm, selector)

    result = agent.classify_with_confidence(state["user_input"])

    emit_graph_node(
        "intent_classifier",
        inputs={"user_input": state["user_input"][:200]},
        outputs={"intent": result["intent"], "confidence": result["confidence"]},
    )

    return {"intent": result["intent"], "intent_confidence": result["confidence"]}


def entity_extractor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Extract entities from user input"""
    from ..subagents.entity_extractor import EntityExtractorAgent

    llm = get_shared_llm_manager()
    selector = get_shared_model_selector()
    agent = EntityExtractorAgent(llm, selector)

    context = {"intent": state.get("intent")}
    entities = agent.extract_with_raw(state["user_input"], context)

    emit_graph_node(
        "entity_extractor",
        inputs={"user_input": state["user_input"][:200], "intent": state.get("intent")},
        outputs={"entities": str(entities.get("entities", {}))[:500]},
    )

    return {
        "entities": entities["entities"].to_context_dict()
        if hasattr(entities["entities"], "to_context_dict")
        else {}
    }


def orchestrator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Orchestrate with tool calling"""
    from ..main import HCPAgent

    llm = get_shared_llm_manager()
    agent = HCPAgent(llm)

    context = {"intent": state.get("intent"), "entities": state.get("entities", {})}

    response = agent.orchestrator.process(state["user_input"], context)

    emit_graph_node(
        "orchestrator",
        inputs={"user_input": state["user_input"][:200], "context_keys": list(context.keys())},
        outputs={"response": str(response)[:500]},
    )

    return {"response": response}


def should_continue(
    state: Dict[str, Any],
) -> Literal["entity_extractor", "orchestrator"]:
    """Conditional edge: Decide next step based on intent"""
    intent = state.get("intent", "unknown")

    if intent in ["add_hcp", "create_interaction", "update_interaction", "search_hcp", "create_follow_up", "suggest_follow_up"]:
        return "entity_extractor"
    elif intent in ["search_materials", "get_summary", "general_query", "unknown"]:
        return "orchestrator"
    else:
        return "orchestrator"


def format_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Format final response"""
    response = state.get("response", "")
    intent = state.get("intent", "")
    entities = state.get("entities", {})

    if entities and not response:
        response = f"I've noted the following: {entities}"

    return {"response": response}
