"""
Intent Schemas - Defines possible user intents
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class Intent(str, Enum):
    ADD_HCP = "add_hcp"
    CREATE_INTERACTION = "create_interaction"
    SEARCH_HCP = "search_hcp"
    GET_SUMMARY = "get_summary"
    CREATE_FOLLOW_UP = "create_follow_up"
    UPDATE_FOLLOW_UP = "update_follow_up"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"


class IntentClassification(BaseModel):
    intent: Intent
    confidence: float = 1.0
    reasoning: Optional[str] = None

    @classmethod
    def from_string(cls, intent_str: str) -> "IntentClassification":
        """Parse intent from string response"""
        intent_str = intent_str.strip().lower().replace("-", "_")

        # Map common variations
        intent_map = {
            "add_hcp": Intent.ADD_HCP,
            "create_hcp": Intent.ADD_HCP,
            "register_hcp": Intent.ADD_HCP,
            "add_hcp": Intent.CREATE_INTERACTION,
            "log_interaction": Intent.CREATE_INTERACTION,
            "record_interaction": Intent.CREATE_INTERACTION,
            "search_hcp": Intent.SEARCH_HCP,
            "find_hcp": Intent.SEARCH_HCP,
            "get_hcp": Intent.SEARCH_HCP,
            "get_summary": Intent.GET_SUMMARY,
            "summary": Intent.GET_SUMMARY,
            "hcp_summary": Intent.GET_SUMMARY,
            "create_follow_up": Intent.CREATE_FOLLOW_UP,
            "schedule_follow_up": Intent.CREATE_FOLLOW_UP,
            "add_follow_up": Intent.CREATE_FOLLOW_UP,
            "update_follow_up": Intent.UPDATE_FOLLOW_UP,
            "follow_up": Intent.UPDATE_FOLLOW_UP,
            "general_query": Intent.GENERAL_QUERY,
            "general": Intent.GENERAL_QUERY,
            "query": Intent.GENERAL_QUERY,
            "unknown": Intent.UNKNOWN,
            "unclear": Intent.UNKNOWN,
        }

        return cls(intent=intent_map.get(intent_str, Intent.UNKNOWN), confidence=1.0)
