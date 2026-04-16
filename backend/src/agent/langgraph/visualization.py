"""
LangGraph Visualization - Export graph for custom visualization
"""

from typing import Dict, Any, List


def get_graph_definition() -> Dict[str, Any]:
    """Get the graph definition for visualization"""
    return {
        "nodes": [
            {
                "id": "intent_classifier",
                "type": "agent",
                "label": "Intent Classifier",
                "description": "Classifies user intent using fast LLM",
                "model": "llama-3.1-8b-instant",
                "input": "user_message",
                "output": "intent + confidence",
            },
            {
                "id": "entity_extractor",
                "type": "agent",
                "label": "Entity Extractor",
                "description": "Extracts structured entities from message",
                "model": "llama-3.1-70b-versatile",
                "input": "user_message + intent",
                "output": "entities object",
            },
            {
                "id": "orchestrator",
                "type": "agent",
                "label": "Orchestrator",
                "description": "Executes tools and synthesizes response",
                "model": "llama3-groq-70b-8192-tool-use-preview",
                "input": "user_message + entities + intent",
                "output": "response + tool_results",
            },
            {
                "id": "format_response",
                "type": "utility",
                "label": "Format Response",
                "description": "Formats final response for user",
                "input": "response + entities",
                "output": "formatted_message",
            },
        ],
        "edges": [
            {
                "from": "intent_classifier",
                "to": "entity_extractor",
                "condition": "needs_entity_extraction",
                "intents": [
                    "add_hcp",
                    "create_interaction",
                    "search_hcp",
                    "create_follow_up",
                ],
            },
            {
                "from": "intent_classifier",
                "to": "orchestrator",
                "condition": "skip_entity_extraction",
                "intents": ["get_summary", "general_query", "unknown"],
            },
            {
                "from": "entity_extractor",
                "to": "orchestrator",
                "condition": "always",
                "intents": [],
            },
            {
                "from": "orchestrator",
                "to": "format_response",
                "condition": "always",
                "intents": [],
            },
            {
                "from": "format_response",
                "to": "END",
                "condition": "always",
                "intents": [],
            },
        ],
        "tools": [
            {
                "name": "search_hcp",
                "category": "HCP",
                "used_by": ["entity_extractor", "orchestrator"],
            },
            {"name": "get_hcp_by_id", "category": "HCP", "used_by": ["orchestrator"]},
            {"name": "create_hcp", "category": "HCP", "used_by": ["orchestrator"]},
            {"name": "get_hcp_history", "category": "HCP", "used_by": ["orchestrator"]},
            {
                "name": "create_interaction",
                "category": "Interaction",
                "used_by": ["orchestrator"],
            },
            {
                "name": "get_interactions",
                "category": "Interaction",
                "used_by": ["orchestrator"],
            },
            {
                "name": "get_interaction_summary",
                "category": "Interaction",
                "used_by": ["orchestrator"],
            },
            {
                "name": "create_follow_up",
                "category": "Follow-up",
                "used_by": ["orchestrator"],
            },
            {
                "name": "get_follow_ups",
                "category": "Follow-up",
                "used_by": ["orchestrator"],
            },
            {
                "name": "update_follow_up",
                "category": "Follow-up",
                "used_by": ["orchestrator"],
            },
        ],
        "models": {
            "classification": {
                "primary": "llama-3.1-8b-instant",
                "fallback": "llama3-groq-8b-8192-tool-use-preview",
                "speed": "fast",
                "cost": "low",
            },
            "extraction": {
                "primary": "llama-3.1-70b-versatile",
                "fallback": "mixtral-8x7b-32768",
                "speed": "medium",
                "cost": "medium",
            },
            "tool_use": {
                "primary": "llama3-groq-70b-8192-tool-use-preview",
                "fallback": "llama-3.1-70b-versatile",
                "speed": "medium",
                "cost": "high",
            },
        },
    }


def get_flow_diagram_mermaid() -> str:
    """Get graph definition in Mermaid format"""
    return """```mermaid
flowchart TD
    START([User Input]) --> INTENT[Intent Classifier]
    INTENT --> |add_hcp, create_interaction, search_hcp, create_follow_up| EXTRACT[Entity Extractor]
    INTENT --> |general_query, get_summary, unknown| ORCH[Orchestrator]
    
    EXTRACT --> ORCH
    
    ORCH --> |tool calls| TOOLS
    TOOLS[Tools: search_hcp, create_interaction, create_follow_up, ...]
    TOOLS --> RESPONSE[Format Response]
    
    ORCH --> |no tools| RESPONSE
    
    RESPONSE --> END([Response])
    
    subgraph Intent Classification
        INTENT
    end
    
    subgraph Entity Extraction
        EXTRACT
    end
    
    subgraph Tool Orchestration
        ORCH
        TOOLS
    end
    
    subgraph Response Formatting
        RESPONSE
    end
```"""


def get_flow_diagram_ascii() -> str:
    """Get graph definition in ASCII format"""
    return """
┌─────────────────────────────────────────────────────────────────────┐
│                        HCP AGENT FLOW                               │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │  User Input   │
    └───────┬──────┘
            │
            ▼
    ┌──────────────────┐
    │ Intent Classifier │  llama-3.1-8b-instant (fast)
    └────────┬─────────┘
             │
       ┌─────┴─────┐
       │           │
       ▼           ▼
  ┌─────────┐  ┌──────────────┐
  │ Skip?   │  │ Extract      │  llama-3.1-70b-versatile
  │ (query, │  │ Entities      │  (quality)
  │ summary)│  └───────┬──────┘
       │           │
       └─────┬─────┘
             │
             ▼
    ┌──────────────────┐
    │   Orchestrator   │  llama3-groq-70b-tool-use
    └────────┬─────────┘  (tool calling)
             │
       ┌─────┴─────┐
       │           │
       ▼           ▼
  ┌────────┐  ┌──────────────────────┐
  │ Tools  │  │  Format Response     │
  └────────┘  └──────────┬─────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Response   │
                    └──────────────┘

TOOLS AVAILABLE:
  HCP: search_hcp, get_hcp_by_id, create_hcp, get_hcp_history
  Interaction: create_interaction, get_interactions, get_interaction_summary
  Follow-up: create_follow_up, get_follow_ups, update_follow_up
  Context: get_conversation_history, get_extracted_entities, add_context, clear_session
"""
