"""
Main HCPAgent - Orchestrates all subagents and handles tool execution
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from .llm_manager import LLMManager
from .model_selector import ModelSelector
from .subagents import IntentClassifierAgent, EntityExtractorAgent, OrchestratorAgent
from .memory import get_memory, SessionData
from .schemas import ExtractedEntities
from .langsmith.tracing import emit_graph_node


@dataclass
class AgentResponse:
    """Response from agent processing"""

    message: str
    intent: str
    entities: Dict[str, Any]
    tool_results: List[Dict[str, Any]]
    session_id: str
    success: bool
    error: Optional[str] = None


class HCPAgent:
    """
    Main HCP Agent - Orchestrates all subagents
    """

    def __init__(self, llm_manager: LLMManager):
        self.llm = llm_manager
        self.model_selector = ModelSelector(llm_manager)
        self.model_selector.initialize()

        # Initialize subagents
        self.intent_classifier = IntentClassifierAgent(llm_manager, self.model_selector)
        self.entity_extractor = EntityExtractorAgent(llm_manager, self.model_selector)
        self.orchestrator = OrchestratorAgent(llm_manager, self.model_selector)

        # Memory
        self.memory = get_memory()

    def create_session(self, user_id: str) -> SessionData:
        """Create a new session"""
        return self.memory.create_session(user_id)

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get existing session"""
        return self.memory.get_session(session_id)

    def _extract_entities_regex(self, text: str) -> dict:
        """Simple regex-based entity extraction"""
        import re

        entities = {}

        dr_match = re.search(
            r"(?:Dr\.?|Doctor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text
        )
        if dr_match:
            entities["hcp_name"] = dr_match.group(1)

        date_match = re.search(
            r"(?:next week|tomorrow|(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}))",
            text,
            re.IGNORECASE,
        )
        if date_match:
            if date_match.group(1):
                entities["date_time"] = date_match.group(1)
            else:
                entities["date_time"] = "next_week"

        return entities

    def _extract_materials_from_text(self, text: str) -> list:
        """Extract material names from user input by matching against DB materials"""
        from .services.tool_services import MaterialService

        try:
            all_materials = MaterialService.search_material("", limit=50)
        except Exception:
            return []

        text_lower = text.lower()
        found = []
        for mat in all_materials:
            mat_name = mat.get("name", "")
            if mat_name and mat_name.lower() in text_lower:
                found.append(mat_name)
        return found

    def process(
        self,
        user_input: str,
        session_id: str,
        user_id: str = "default",
        include_thinking: bool = False,
        form_data: dict = None,
    ) -> AgentResponse:
        """
        Process user input through the agent pipeline
        """
        session = self.memory.get_session(session_id)
        if not session:
            session = self.create_session(user_id)
            session_id = session.session_id

        self.memory.add_message(session_id, "user", user_input)

        intent = "unknown"
        entities_dict = {}

        try:
            # Step 1: Classify intent
            try:
                intent_result = self.intent_classifier.classify_with_confidence(
                    user_input
                )
                intent = intent_result["intent"]
            except Exception:
                user_lower = user_input.lower()
                if "suggest" in user_lower or "recommend" in user_lower or "next step" in user_lower:
                    intent = "suggest_follow_up"
                elif "follow" in user_lower or "schedule" in user_lower:
                    intent = "create_follow_up"
                elif "edit" in user_lower or "update" in user_lower or "modify" in user_lower or "change" in user_lower:
                    intent = "update_interaction"
                elif "meet" in user_lower or "met" in user_lower or "meeting" in user_lower:
                    intent = "create_interaction"
                elif ("search" in user_lower or "find" in user_lower or "look for" in user_lower) and (
                    "material" in user_lower or "brochure" in user_lower or "sample" in user_lower
                ):
                    intent = "search_materials"
                elif "search" in user_lower or "find" in user_lower or "look for" in user_lower:
                    intent = "search_hcp"
                elif "material" in user_lower or "brochure" in user_lower:
                    intent = "search_materials"
                else:
                    intent = "unknown"

            emit_graph_node(
                "intent_classifier",
                inputs={"user_input": user_input[:200], "session_id": session_id},
                outputs={"intent": intent},
            )

            # Step 2: Extract entities
            entities = {}
            try:
                entities_result = self.entity_extractor.extract_with_raw(user_input)
                entities = entities_result["entities"]
            except Exception:
                pass

            if hasattr(entities, "model_dump"):
                entities_dict = {
                    k: v for k, v in entities.model_dump().items() if v is not None
                }
            elif isinstance(entities, dict):
                entities_dict = {k: v for k, v in entities.items() if v is not None}
            else:
                entities_dict = {}

            if not entities_dict:
                entities_dict = self._extract_entities_regex(user_input)

            if not entities_dict.get("materials"):
                entities_dict["materials"] = self._extract_materials_from_text(user_input)

            if form_data:
                for key, value in form_data.items():
                    if value is not None and (key not in entities_dict or not entities_dict.get(key)):
                        entities_dict[key] = value

            regex_entities = self._extract_entities_regex(user_input)
            for key, value in regex_entities.items():
                if key not in entities_dict or not entities_dict.get(key):
                    entities_dict[key] = value

            # Step 2.5: Validate and enrich entities
            if intent in ["search_hcp", "create_interaction", "create_follow_up", "update_interaction"]:
                if entities_dict.get("hcp_id") and not entities_dict.get("hcp_name"):
                    from .services.tool_services import HCPService
                    hcp_by_id = HCPService.get_hcp_by_id(entities_dict["hcp_id"])
                    if hcp_by_id:
                        entities_dict["hcp_name"] = hcp_by_id.get("name", "")
                        entities_dict["hcp_specialty"] = hcp_by_id.get("specialty", "")
                        entities_dict["hcp_institution"] = hcp_by_id.get("institution", "")
                elif entities_dict.get("hcp_name") and not entities_dict.get("hcp_id"):
                    hcp_name = entities_dict.get("hcp_name", "")
                    hcp_name = hcp_name.replace("Dr.", "").replace("Dr", "").strip()
                    from .services.tool_services import HCPService
                    search_results = HCPService.search_hcp(hcp_name)
                    if search_results:
                        entities_dict["hcp_id"] = search_results[0].get("id")
                        entities_dict["hcp_name"] = search_results[0].get("name")
                        entities_dict["hcp_specialty"] = search_results[0].get("specialty")
                        entities_dict["hcp_institution"] = search_results[0].get("institution")

            self.memory.set_entities(session_id, entities_dict)

            emit_graph_node(
                "entity_extractor",
                inputs={"user_input": user_input[:200], "intent": intent},
                outputs={"entities_keys": list(entities_dict.keys())},
            )

            # Step 3: Get context for orchestrator
            context = {
                "intent": intent,
                "entities": entities_dict,
                "conversation_history": self.memory.get_history(session_id, limit=20),
            }

            # If intent is unknown, skip the LLM orchestrator entirely
            if intent == "unknown":
                response_message = (
                    "I'm not sure what you'd like me to do. Here's what I can help with:\n"
                    "1. Search for an HCP\n"
                    "2. Record an interaction\n"
                    "3. Create a follow-up\n"
                    "4. Search materials"
                )
                tool_results = []
            else:
                # Step 4: Orchestrate response with tools
                response_message, tool_results = self.orchestrator.process_with_tools(
                    user_input, context
                )

            # Step 4.5: Auto-generate follow-up suggestions after create_interaction
            for tr in tool_results:
                if tr.get("tool_name") == "create_interaction" and tr.get("success"):
                    interaction_data = tr.get("data", {})
                    interaction_id = interaction_data.get("id")
                    hcp_id = interaction_data.get("hcp_id") or interaction_data.get("hcpId")
                    if hcp_id:
                        from .tools.followup_tools import _suggest_follow_up_actions
                        try:
                            suggestions_result = _suggest_follow_up_actions(
                                interaction_id=interaction_id,
                                hcp_id=hcp_id,
                                context=", ".join(entities_dict.get("topics", [])) if isinstance(entities_dict.get("topics"), list) else str(entities_dict.get("topics", "")),
                            )
                            if suggestions_result.get("success"):
                                tool_results.append({
                                    "tool_name": "suggest_follow_up_actions",
                                    "success": True,
                                    "data": suggestions_result,
                                })
                        except Exception:
                            pass
                    break

            if intent == "unknown":
                emit_graph_node(
                    "unknown_intent_handler",
                    inputs={"user_input": user_input[:200]},
                    outputs={"response": response_message[:500], "action": "skipped_orchestrator"},
                )
            else:
                emit_graph_node(
                    "orchestrator",
                    inputs={"user_input": user_input[:200], "intent": intent},
                    outputs={"response": response_message[:500], "tool_call_count": len(tool_results)},
                )

            self.memory.add_message(session_id, "assistant", response_message)

            return AgentResponse(
                message=response_message,
                intent=intent,
                entities=entities_dict,
                tool_results=tool_results,
                session_id=session_id,
                success=True,
            )

        except Exception as e:
            error_msg = f"I encountered an error processing your request: {str(e)}"
            self.memory.add_message(session_id, "assistant", error_msg)
            return AgentResponse(
                message=error_msg,
                intent=intent,
                entities=entities_dict,
                tool_results=[],
                session_id=session_id,
                success=False,
                error=str(e),
            )

    def get_history(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Get conversation history"""
        return self.memory.get_history(session_id, limit)

    def clear_session(self, session_id: str):
        """Clear session data"""
        self.memory.clear(session_id)


# Singleton instance
_agent_instance: Optional[HCPAgent] = None


def get_hcp_agent() -> HCPAgent:
    """Get or create singleton HCP Agent"""
    global _agent_instance
    if _agent_instance is None:
        from .llm_manager import get_llm_manager

        llm = get_llm_manager()
        _agent_instance = HCPAgent(llm)
    return _agent_instance


def reset_agent():
    """Reset agent singleton (for testing)"""
    global _agent_instance
    _agent_instance = None
