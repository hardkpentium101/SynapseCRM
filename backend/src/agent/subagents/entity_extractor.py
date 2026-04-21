"""
Entity Extractor Agent - Extracts structured entities from messages
"""

from typing import Dict, Any
import json
from ..base import BaseAgent, AgentConfig, AGENT_CONFIGS
from ..llm_manager import LLMManager
from ..model_selector import ModelSelector
from ..schemas.entities import ExtractedEntities


class EntityExtractorAgent(BaseAgent):
    """Agent that extracts structured entities from user messages"""

    def __init__(self, llm_manager: LLMManager, model_selector: ModelSelector):
        config = AGENT_CONFIGS["entity_extractor"]
        super().__init__(config, llm_manager, model_selector)

    def process(self, input: str, context: Dict[str, Any] = None) -> ExtractedEntities:
        """Extract entities from user input"""
        messages = self._build_messages(input, context)

        # Add JSON format instruction
        messages.append(
            {
                "role": "system",
                "content": 'Return ONLY valid JSON matching this schema: {"hcp_name":null,"hcp_specialty":null,"hcp_institution":null,"hcp_id":null,"interaction_type":null,"date_time":null,"sentiment":null,"topics":[],"attendees":[],"materials":[],"follow_up_type":null,"follow_up_due":null}',
            }
        )

        response = self.complete(messages, use_tools=False)

        if response.content:
            return ExtractedEntities.from_json(response.content)

        return ExtractedEntities()

    def extract_with_raw(
        self, input: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Extract entities with raw model response"""
        entities = self.process(input, context)
        return {
            "entities": entities,
            "raw_json": entities.model_dump_json()
            if hasattr(entities, "model_dump_json")
            else str(entities),
            "model_used": self._get_model(),
        }
