"""
Base Agent - Abstract base class for all agents
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

from .llm_manager import LLMManager, LLMResponse
from .model_selector import ModelSelector


class AgentType(Enum):
    INTENT_CLASSIFIER = "intent_classifier"
    ENTITY_EXTRACTOR = "entity_extractor"
    ORCHESTRATOR = "orchestrator"


@dataclass
class AgentConfig:
    """Configuration for an agent"""

    name: str
    agent_type: AgentType
    system_prompt: str
    model_task: str  # "classification", "extraction", "tool_use", "general"
    tools: List[str] = field(default_factory=list)  # Tool names available to this agent
    temperature: float = 0.1
    max_tokens: int = 1024
    description: str = ""


# Agent Configurations
AGENT_CONFIGS = {
    "intent_classifier": AgentConfig(
        name="Intent Classifier",
        agent_type=AgentType.INTENT_CLASSIFIER,
        system_prompt="""You are an HCP CRM intent classifier.

Analyze user messages and classify their intent into ONE of the following categories:

INTENTS:
- add_hcp: User wants to register/add a new healthcare professional
- create_interaction: User wants to log a new interaction with an HCP
- search_hcp: User wants to find information about an existing HCP
- get_summary: User wants a summary of HCP history or past interactions
- create_follow_up: User wants to schedule or create a follow-up task
- update_follow_up: User wants to update status of an existing follow-up
- general_query: General question or conversational message
- unknown: Unable to determine the intent

Return ONLY the intent classification as a single word.""",
        model_task="classification",
        tools=[],
        temperature=0.1,
        max_tokens=50,
        description="Classifies user intent from messages",
    ),
    "entity_extractor": AgentConfig(
        name="Entity Extractor",
        agent_type=AgentType.ENTITY_EXTRACTOR,
        system_prompt="""You are an HCP CRM entity extractor.

Extract structured information from user messages. Return a JSON object with:

- hcp_name: Name of the healthcare professional (if mentioned)
- hcp_specialty: Medical specialty (if mentioned, e.g., "oncology", "cardiology")
- hcp_institution: Hospital or clinic name (if mentioned)
- hcp_id: Internal ID (if known from context, leave empty if unknown)
- interaction_type: Type of interaction ("meeting", "call", "email", "conference", or null)
- date_time: When interaction occurred/scheduled (ISO format or null if not mentioned)
- sentiment: Emotional tone ("positive", "neutral", "negative", or null)
- topics: List of discussion topics mentioned
- attendees: List of other people mentioned (or empty array)
- follow_up_type: Type of follow-up if mentioned ("call", "meeting", "email", or null)
- follow_up_due: Follow-up due date if mentioned (ISO format or null)

Return JSON with null for fields not mentioned.""",
        model_task="extraction",
        tools=["search_hcp"],  # Can search to resolve ambiguous HCP names
        temperature=0.2,
        max_tokens=512,
        description="Extracts structured entities from messages",
    ),
    "orchestrator": AgentConfig(
        name="HCP Agent Orchestrator",
        agent_type=AgentType.ORCHESTRATOR,
        system_prompt="""You are an HCP CRM assistant orchestrator.

You help healthcare field representatives manage their HCP interactions.

Your capabilities:
1. Search for healthcare professionals
2. Create and manage interactions
3. Schedule follow-ups
4. Provide summaries and insights

Be concise and actionable. When users mention HCPs, use the search_hcp tool to find them first.
When creating interactions, gather all required information.""",
        model_task="tool_use",
        tools=[
            "search_hcp",
            "get_hcp_by_id",
            "create_interaction",
            "get_interactions",
            "create_follow_up",
            "get_follow_ups",
            "update_follow_up",
            "get_conversation_history",
            "clear_session",
        ],
        temperature=0.3,
        max_tokens=2048,
        description="Main orchestrator with tool access",
    ),
}


class BaseAgent(ABC):
    """Abstract base class for all agents"""

    def __init__(
        self,
        config: AgentConfig,
        llm_manager: LLMManager,
        model_selector: ModelSelector,
        tool_registry: Dict[str, Callable] = None,
    ):
        self.config = config
        self.llm = llm_manager
        self.model_selector = model_selector
        self.tool_registry = tool_registry or {}

    def _get_model(self) -> str:
        """Get the model for this agent based on task type"""
        return self.model_selector.select(self.config.model_task)

    def _build_messages(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> List[Dict[str, str]]:
        """Build message list with system prompt and context"""
        messages = [{"role": "system", "content": self.config.system_prompt}]

        # Add context if provided
        if context:
            if "conversation_history" in context:
                messages.extend(
                    context["conversation_history"][-10:]
                )  # Last 10 messages

            if "entities" in context:
                messages.append(
                    {
                        "role": "system",
                        "content": f"Previous extracted entities: {context['entities']}",
                    }
                )

            if "intent" in context:
                messages.append(
                    {"role": "system", "content": f"User intent: {context['intent']}"}
                )

        messages.append({"role": "user", "content": user_input})
        return messages

    def _get_tools(self) -> List[Dict]:
        """Get tool definitions for this agent"""
        if not self.config.tools:
            return []

        from .tools.registry import get_tool_definitions

        return get_tool_definitions(self.config.tools)

    @abstractmethod
    def process(self, input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process input and return structured response"""
        pass

    def complete(
        self, messages: List[Dict[str, str]], use_tools: bool = False, **kwargs
    ) -> LLMResponse:
        """Send completion request to LLM"""
        model = self._get_model()

        if use_tools and self.config.tools:
            return self.llm.complete_with_tools(
                messages=messages,
                tools=self._get_tools(),
                model=model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **kwargs,
            )
        else:
            return self.llm.complete(
                messages=messages,
                model=model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **kwargs,
            )
