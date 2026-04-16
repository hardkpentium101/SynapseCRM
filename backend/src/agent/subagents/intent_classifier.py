"""
Intent Classifier Agent - Classifies user intent from messages
"""

from typing import Dict, Any
from ..base import BaseAgent, AgentConfig, AGENT_CONFIGS
from ..llm_manager import LLMManager
from ..model_selector import ModelSelector
from ..schemas.intents import IntentClassification


class IntentClassifierAgent(BaseAgent):
    """Agent that classifies user intent"""

    def __init__(self, llm_manager: LLMManager, model_selector: ModelSelector):
        config = AGENT_CONFIGS["intent_classifier"]
        super().__init__(config, llm_manager, model_selector)

    def process(
        self, input: str, context: Dict[str, Any] = None
    ) -> IntentClassification:
        """Classify the intent of user input"""
        messages = self._build_messages(input, context)

        response = self.complete(messages, use_tools=False)

        if response.content:
            return IntentClassification.from_string(response.content.strip())

        return IntentClassification(
            intent="unknown", confidence=0.0, reasoning="No response from model"
        )

    def classify_with_confidence(
        self, input: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Classify with additional metadata"""
        result = self.process(input, context)
        return {
            "intent": result.intent.value,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "model_used": self._get_model(),
        }
