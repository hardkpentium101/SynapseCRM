"""
Base Agent - Abstract base class for all agents
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

from .llm_manager import LLMManager, LLMResponse
from .model_selector import ModelSelector


# ============================================================================
# PROMPT CONSTANTS - Extracted from code for maintainability
# ============================================================================

INTENT_CLASSIFIER_PROMPT = """You are an HCP CRM intent classifier.

Analyze user messages and classify their intent.

EXAMPLES:
- "I met with Dr. Sharma today" → create_interaction
- "Log my call with Dr. Kumar" → create_interaction  
- "Record the meeting yesterday" → create_interaction
- "Find Dr. Gupta at Apollo" → search_hcp
- "Look up Dr. Priya" → search_hcp
- "Update the follow-up to call Dr. Sharma" → update_interaction
- "Schedule follow-up with Dr. Sharma" → create_follow_up
- "Show my interactions this month" → get_summary
- "What's my HCP history?" → get_summary
- "Hello" → general_query
- "Thanks" → general_query

Valid intents: add_hcp, create_interaction, update_interaction, search_hcp, get_summary, create_follow_up, suggest_follow_up, update_follow_up, search_materials, general_query, unknown

IMPORTANT: Reply with ONLY ONE word - the intent. Nothing else."""

ENTITY_EXTRACTOR_PROMPT = """You are an HCP CRM entity extractor.

Extract structured information from user messages. Return a JSON object with:

- hcp_name: Name of the healthcare professional (if mentioned)
- hcp_specialty: Medical specialty (if mentioned, e.g., "oncology", "cardiology")
- hcp_institution: Hospital or clinic name (if mentioned)
- hcp_id: Internal ID (if known from context, leave empty if unknown)
- interaction_type: Type of interaction ("meeting", "call", "email", "conference", or null)
- date_time: When interaction occurred/scheduled (ISO format or null if not mentioned)
- sentiment: Emotional tone ("positive", "neutral", "negative", or null)
- topics: List of discussion topics mentioned (keep product names intact — e.g., "OncoBoost", "NeuroPlus", "CardioProtect" are single words, NEVER split them)
- attendees: List of other people mentioned (or empty array)
- materials: List of product/material names mentioned (e.g., "OncoBoost Phase III Brochure", "NeuroPlus Clinical Summary", sample kits)
- outcome: Result or summary of the interaction (what was agreed, decided, or concluded)
- follow_up_type: Type of follow-up if mentioned ("call", "meeting", "email", or null)
- follow_up_due: Follow-up due date if mentioned (ISO format or null)

IMPORTANT: Product names like OncoBoost, NeuroPlus, CardioProtect are single words — never split them into fragments.
Return JSON with null for fields not mentioned."""

ENTITY_VALIDATOR_PROMPT = """You are an HCP CRM entity validator.

Your task is to validate extracted entities against database results and resolve ambiguities.

Input:
- Extracted entities from user message (may be incomplete or vague)
- Search results from database (may have 0, 1, or multiple matches)

Your job:
1. If single match found → confirm the entity with resolved ID
2. If multiple matches found → ask user to clarify which one
3. If no match found → suggest adding new HCP or check spelling
4. If partial match (name matches but institution doesn't) → verify with user

EXAMPLES:
- User: "Dr. Sharma at Mayo" → DB: ["Dr. Priya Sharma at Mayo", "Dr. Raj Sharma at Johns Hopkins"] → ASK: "Which Dr. Sharma? There are multiple."
- User: "Dr. Priya with oncology" → DB: ["Dr. Priya Sharma (Oncology)"] → CONFIRM: entity with hcp_id
- User: "Dr. Unknown Doctor" → DB: [] → SUGGEST: "No matching HCP found. Would you like to add them?"

Output as JSON:
- validated: true/false
- hcp_id: resolved ID if found
- hcp_name: confirmed name
- confirmation_needed: true/false (if multiple matches)
- clarification_options: list of options if needed
- suggestion: text suggestion if no match

Be concise. Ask for clarification only when truly ambiguous."""


# ============================================================================
# ENTITY SCHEMA - Dynamic schema derived from model
# ============================================================================

ENTITY_SCHEMA = {
    "hcp_name": None,
    "hcp_specialty": None,
    "hcp_institution": None,
    "hcp_id": None,
    "interaction_type": None,
    "date_time": None,
    "sentiment": None,
    "topics": [],
    "attendees": [],
    "outcome": None,
    "follow_up_type": None,
    "follow_up_due": None,
}


class AgentType(Enum):
    INTENT_CLASSIFIER = "intent_classifier"
    ENTITY_EXTRACTOR = "entity_extractor"
    ENTITY_VALIDATOR = "entity_validator"
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
        system_prompt=INTENT_CLASSIFIER_PROMPT,
        model_task="classification",
        tools=[],
        temperature=0.1,
        max_tokens=50,
        description="Classifies user intent from messages",
    ),
    "entity_extractor": AgentConfig(
        name="Entity Extractor",
        agent_type=AgentType.ENTITY_EXTRACTOR,
        system_prompt=ENTITY_EXTRACTOR_PROMPT,
        model_task="extraction",
        tools=["search_hcp"],
        temperature=0.2,
        max_tokens=512,
        description="Extracts structured entities from messages",
    ),
    "entity_validator": AgentConfig(
        name="Entity Validator",
        agent_type=AgentType.ENTITY_VALIDATOR,
        system_prompt=ENTITY_VALIDATOR_PROMPT,
        model_task="validation",
        tools=["search_hcp", "get_hcp_by_id", "create_hcp"],
        temperature=0.1,
        max_tokens=512,
        description="Validates extracted entities against DB results",
    ),
    "orchestrator": AgentConfig(
        name="HCP Agent Orchestrator",
        agent_type=AgentType.ORCHESTRATOR,
        system_prompt="""You are an HCP CRM assistant orchestrator.

You help healthcare field representatives manage their HCP interactions.

IMPORTANT - Use extracted entities from context:
- The entities provided in context contain resolved hcp_id, hcp_name, hcp_specialty, hcp_institution, materials IDs, topics, attendees, date_time, and sentiment
- ALWAYS use the hcp_id from entities when calling create_interaction or update_interaction - never use hcp_name as hcp_id
- When creating interactions, include all resolved information from the entities context

Your capabilities:
1. Search for healthcare professionals
2. Create, update, and manage interactions
3. Schedule and suggest follow-ups
4. Search and recommend materials
5. Provide summaries and insights

Be concise and actionable. When users mention HCPs, use the search_hcp tool to find them first.
When creating interactions, ALWAYS use the resolved hcp_id from the entities context.

CRITICAL RESPONSE RULES:
- NEVER expose internal IDs (hcp_id, interaction_id, UUIDs) in your response text
- Keep messages short and conversational — 2-4 sentences max
- When confirming an action, state what was done in plain language (e.g., "Meeting with Dr. Sharma recorded")
- If the user corrects something (e.g., "it was Dr. Patel instead"), confirm the correction and ask if they want to proceed
- For short answers like "yes", "ok", "sure" — interpret them in context of the last thing you asked. If you offered to create a follow-up, "yes" means create it.
- When offering next steps, list 2-3 concise options without internal details

CRITICAL ACCURACY RULES:
- NEVER add or invent topics, materials, or outcomes that the user did not mention
- Product names are single words: OncoBoost, NeuroPlus, CardioProtect — NEVER split them into fragments like "Onco Bo ost" or "Neuro Plus"
- Only report what the user actually said. Do not hallucinate shared brochures, PDFs, or materials not mentioned by the user
- When describing topics discussed, quote or closely paraphrase the user's exact words""",
        model_task="tool_use",
        tools=[
            "search_hcp",
            "get_hcp_by_id",
            "create_interaction",
            "update_interaction",
            "get_interactions",
            "create_follow_up",
            "suggest_follow_up_actions",
            "get_follow_ups",
            "update_follow_up",
            "search_materials",
            "recommend_materials",
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

    _context_formatters: Dict[str, Dict[str, Any]] = {
        "conversation_history": {
            "mode": "extend",
            "template": "{0}",
        },
        "entities": {
            "mode": "append",
            "template": "Previous extracted entities: {0}",
        },
        "intent": {
            "mode": "append",
            "template": "User intent: {0}",
        },
    }

    def _get_model(self) -> str:
        """Get the model for this agent based on task type"""
        return self.model_selector.select(self.config.model_task)

    def _build_messages(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> List[Dict[str, str]]:
        """Build message list with system prompt and context"""
        messages = [{"role": "system", "content": self.config.system_prompt}]

        if context:
            for key, config in self._context_formatters.items():
                if key not in context:
                    continue

                value = context[key]
                if config["mode"] == "extend":
                    messages.extend(value[-10:])
                else:
                    content = config["template"].format(value)
                    messages.append({"role": "system", "content": content})

        messages.append({"role": "user", "content": user_input})
        return messages

    def _get_tools(self) -> List[Dict]:
        """Get tool definitions for this agent"""
        if not self.config.tools:
            return []

        from .tools.registry import get_tool_definitions

        return get_tool_definitions(self.config.tools)

    @abstractmethod
    def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
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
