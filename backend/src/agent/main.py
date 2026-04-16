"""
Main HCPAgent - Orchestrates all subagents and handles tool execution
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os

from .llm_manager import LLMManager, LLMResponse
from .model_selector import ModelSelector
from .base import BaseAgent, AgentConfig, AGENT_CONFIGS
from .subagents import IntentClassifierAgent, EntityExtractorAgent
from .tools.registry import get_tool_registry, ToolResult
from .memory import get_memory, SessionData
from .schemas import Intent, ExtractedEntities

# Initialize LangSmith tracing if available
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "hcp-agent")

if LANGSMITH_API_KEY:
    try:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
        print(f"✓ LangSmith tracing enabled: {LANGSMITH_PROJECT}")
    except Exception as e:
        print(f"⚠ LangSmith setup failed: {e}")


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


class OrchestratorAgent(BaseAgent):
    """Main orchestrator with tool calling capabilities"""

    def __init__(self, llm_manager: LLMManager, model_selector: ModelSelector):
        config = AGENT_CONFIGS["orchestrator"]
        tool_registry = get_tool_registry()
        super().__init__(
            config,
            llm_manager,
            model_selector,
            {name: tool_registry.execute for name in config.tools},
        )
        self.tool_registry = tool_registry

    def process(self, input: str, context: Dict[str, Any] = None) -> str:
        """Process with tool calling"""
        messages = self._build_messages(input, context)
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            response = self.complete(messages, use_tools=True)

            # If no tool calls, return content
            if not response.tool_calls:
                return response.content or "I'm not sure how to help with that."

            # Process each tool call
            for tool_call in response.tool_calls:
                # Add tool call to messages
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.name,
                                    "arguments": json.dumps(tool_call.arguments)
                                    if isinstance(tool_call.arguments, dict)
                                    else tool_call.arguments,
                                },
                            }
                        ],
                    }
                )

                # Execute tool
                tool_result = self.tool_registry.execute(
                    tool_call.name, tool_call.arguments
                )

                # Add result to messages
                result_content = json.dumps(tool_result.to_dict())
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.name,
                        "content": result_content,
                    }
                )

            # Check if we should continue (model might call more tools)
            # For now, just return the last content

        return response.content or "Processing complete."


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

    def process(
        self,
        user_input: str,
        session_id: str,
        user_id: str = "default",
        include_thinking: bool = False,
    ) -> AgentResponse:
        """
        Process user input through the agent pipeline
        """
        # Ensure session exists
        session = self.memory.get_session(session_id)
        if not session:
            session = self.create_session(user_id)
            session_id = session.session_id

        # Add user message to history
        self.memory.add_message(session_id, "user", user_input)

        try:
            # Step 1: Classify intent
            intent_result = self.intent_classifier.classify_with_confidence(user_input)
            intent = intent_result["intent"]

            # Step 2: Extract entities
            entities_result = self.entity_extractor.extract_with_raw(user_input)
            entities = entities_result["entities"]

            # Update session with entities
            self.memory.set_entities(session_id, entities)

            # Step 3: Get context for orchestrator
            context = {
                "intent": intent,
                "entities": entities,
                "conversation_history": self.memory.get_history(session_id, limit=10),
            }

            # Step 4: Orchestrate response with tools
            response_message = self.orchestrator.process(user_input, context)

            # Add assistant response to history
            self.memory.add_message(session_id, "assistant", response_message)

            return AgentResponse(
                message=response_message,
                intent=intent,
                entities=entities.to_context_dict()
                if hasattr(entities, "to_context_dict")
                else {},
                tool_results=[],
                session_id=session_id,
                success=True,
            )

        except Exception as e:
            return AgentResponse(
                message="I encountered an error processing your request.",
                intent="error",
                entities={},
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
