"""
LangGraph Nodes - Define nodes for the agent graph
"""

from typing import Dict, Any, Literal
from langgraph.types import Command
from ..schemas.entities import ExtractedEntities


def intent_classifier_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Classify user intent"""
    from ..subagents.intent_classifier import IntentClassifierAgent
    from ..llm_manager import get_llm_manager
    from ..model_selector import ModelSelector

    llm = get_llm_manager()
    selector = ModelSelector(llm)
    selector.initialize()
    agent = IntentClassifierAgent(llm, selector)

    result = agent.classify_with_confidence(state["user_input"])

    return {"intent": result["intent"], "intent_confidence": result["confidence"]}


def entity_extractor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Extract entities from user input"""
    from ..subagents.entity_extractor import EntityExtractorAgent
    from ..llm_manager import get_llm_manager
    from ..model_selector import ModelSelector

    llm = get_llm_manager()
    selector = ModelSelector(llm)
    selector.initialize()
    agent = EntityExtractorAgent(llm, selector)

    context = {"intent": state.get("intent")}
    entities = agent.extract_with_raw(state["user_input"], context)

    return {
        "entities": entities["entities"].to_context_dict()
        if hasattr(entities["entities"], "to_context_dict")
        else {}
    }


def orchestrator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Orchestrate with tool calling"""
    from ..main import HCPAgent
    from ..llm_manager import get_llm_manager

    llm = get_llm_manager()
    agent = HCPAgent(llm)

    context = {"intent": state.get("intent"), "entities": state.get("entities", {})}

    response = agent.orchestrator.process(state["user_input"], context)

    return {"response": response}


def should_continue(
    state: Dict[str, Any],
) -> Literal["entity_extractor", "orchestrator"]:
    """Conditional edge: Decide next step based on intent"""
    intent = state.get("intent", "unknown")

    if intent in ["add_hcp", "create_interaction", "search_hcp", "create_follow_up"]:
        # These intents benefit from entity extraction
        return "entity_extractor"
    elif intent in ["get_summary", "general_query", "unknown"]:
        # These can go directly to orchestration
        return "orchestrator"
    else:
        return "orchestrator"


def format_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node: Format final response"""
    response = state.get("response", "")
    intent = state.get("intent", "")
    entities = state.get("entities", {})

    # Add context to response if needed
    if entities and not response:
        response = f"I've noted the following: {entities}"

    return {"response": response}
