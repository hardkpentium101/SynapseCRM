"""
Entity Validator Agent - Validates extracted entities against database results
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from ..base import BaseAgent, AgentConfig, AGENT_CONFIGS
from ..llm_manager import LLMManager
from ..model_selector import ModelSelector
from ..services.tool_services import HCPService

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of entity validation"""

    validated: bool
    hcp_id: Optional[str] = None
    hcp_name: Optional[str] = None
    confirmation_needed: bool = False
    clarification_options: List[Dict] = None
    suggestion: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "validated": self.validated,
            "hcp_id": self.hcp_id,
            "hcp_name": self.hcp_name,
            "confirmation_needed": self.confirmation_needed,
            "clarification_options": self.clarification_options,
            "suggestion": self.suggestion,
            "error": self.error,
        }


class EntityValidatorAgent(BaseAgent):
    """Agent that validates extracted entities against DB results"""

    def __init__(self, llm_manager: LLMManager, model_selector: ModelSelector):
        config = AGENT_CONFIGS.get(
            "entity_validator",
            AgentConfig(
                name="Entity Validator",
                agent_type=AgentType.ENTITY_VALIDATOR,
                system_prompt="",
                model_task="validation",
            ),
        )
        super().__init__(config, llm_manager, model_selector)

    def _search_hcp(self, name: str, institution: str = None) -> List[Dict]:
        """Search HCP in database"""
        results = HCPService.search_hcp(name, limit=10)

        if institution and results:
            filtered = []
            for r in results:
                if institution.lower() in r.get("institution", "").lower():
                    filtered.append(r)
            return filtered if filtered else results

        return results

    def _build_validation_prompt(
        self,
        extracted_entities: Dict,
        search_results: List[Dict],
    ) -> str:
        """Build prompt for entity validation using LLM"""
        hcp_name = extracted_entities.get("hcp_name", "")
        hcp_institution = extracted_entities.get("hcp_institution", "")

        prompt_parts = [
            f"Extracted from user input:",
            f"  - HCP Name: {hcp_name or 'not specified'}",
            f"  - Institution: {hcp_institution or 'not specified'}",
            "",
            f"Database search results ({len(search_results)} found):",
        ]

        for i, r in enumerate(search_results[:5], 1):
            prompt_parts.append(
                f"  {i}. {r.get('name', 'Unknown')}"
                + (f" - {r.get('specialty', '')}" if r.get("specialty") else "")
                + (f" at {r['institution']}" if r.get("institution") else "")
            )

        if not search_results:
            prompt_parts.append("  (no results found)")

        prompt_parts.extend(
            [
                "",
                "Determine:",
                "1. If 1 exact match → validated = true, include hcp_id",
                "2. If multiple matches → confirmation_needed = true, list options",
                "3. If no match → suggestion = 'No matching HCP found'",
                "",
                "Respond as JSON:",
                '{"validated": true/false, "hcp_id": "id if found", "hcp_name": "confirmed name", "confirmation_needed": true/false, "clarification_options": [...], "suggestion": "..."}',
            ]
        )

        return "\n".join(prompt_parts)

    def validate(self, extracted_entities: Dict, intent: str) -> Dict[str, Any]:
        """Validate entities - main entry point used by orchestrator"""
        result = self.validate_hcp(extracted_entities)
        return {
            "status": "validated"
            if result.validated
            else "confirmation_needed"
            if result.confirmation_needed
            else "not_found",
            "hcp_id": result.hcp_id,
            "hcp_name": result.hcp_name,
            "options": result.clarification_options,
            "suggestion": result.suggestion,
            "error": result.error,
            "validated_entities": {
                "hcp_id": result.hcp_id,
                "hcp_name": result.hcp_name,
            }
            if result.validated
            else None,
        }

    def validate_hcp(
        self,
        extracted_entities: Dict,
        require_llm_validation: bool = False,
    ) -> ValidationResult:
        """
        Validate HCP entity against database

        Args:
            extracted_entities: Dict with hcp_name, hcp_institution, etc.
            require_llm_validation: Use LLM for ambiguous cases

        Returns:
            ValidationResult with validated status and details
        """
        hcp_name = extracted_entities.get("hcp_name", "")
        hcp_institution = extracted_entities.get("hcp_institution", "")

        if not hcp_name:
            return ValidationResult(
                validated=False,
                error="No HCP name in extracted entities",
            )

        # Search in database
        search_results = self._search_hcp(hcp_name, hcp_institution)

        if not search_results:
            return ValidationResult(
                validated=False,
                suggestion=f"No HCP found matching '{hcp_name}'. Would you like to add a new HCP?",
            )

        if len(search_results) == 1:
            # Single match - validate
            result = search_results[0]
            return ValidationResult(
                validated=True,
                hcp_id=result.get("id"),
                hcp_name=result.get("name"),
            )

        # Multiple matches - use LLM or return for confirmation
        if require_llm_validation:
            try:
                messages = [
                    {"role": "system", "content": self.config.system_prompt},
                    {
                        "role": "user",
                        "content": self._build_validation_prompt(
                            extracted_entities,
                            search_results,
                        ),
                    },
                ]
                response = self.complete(messages, use_tools=False)

                if response.content:
                    import json

                    try:
                        result = json.loads(response.content)
                        return ValidationResult(
                            validated=result.get("validated", False),
                            hcp_id=result.get("hcp_id"),
                            hcp_name=result.get("hcp_name"),
                            confirmation_needed=result.get(
                                "confirmation_needed", False
                            ),
                            clarification_options=result.get("clarification_options"),
                            suggestion=result.get("suggestion"),
                        )
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                logger.error(f"LLM validation error: {e}")

        # Return options for user confirmation
        return ValidationResult(
            validated=False,
            confirmation_needed=True,
            clarification_options=[
                {
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "specialty": r.get("specialty"),
                    "institution": r.get("institution"),
                }
                for r in search_results[:5]
            ],
            suggestion=f"Multiple HCPs match '{hcp_name}'. Which one did you mean?",
        )

    def process(self, user_input: str, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate entities from input"""
        extracted = context.get("entities", {}) if context else {}

        result = self.validate_hcp(extracted)

        if result.error:
            logger.warning(f"Entity validation error: {result.error}")

        return result


# For backward compatibility - keep enum reference
from ..base import AgentType
