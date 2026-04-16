"""
Intent Schemas - Defines possible user intents
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
import re


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
    def from_string(cls, response: str) -> "IntentClassification":
        """Parse intent from string response - handles paragraphs too"""
        response = response.strip().lower()

        # Known intent keywords to look for
        intent_keywords = {
            Intent.CREATE_INTERACTION: [
                "create_interaction",
                "createinteraction",
                "log_interaction",
                "loginteraction",
                "record_interaction",
                "recordinteraction",
                "met ",
                "met with",
                "meeting",
                "call with",
                "visited",
            ],
            Intent.ADD_HCP: [
                "add_hcp",
                "addhcp",
                "register_hcp",
                "registerhcp",
                "new hcp",
                "new hcp",
                "add new",
                "register new",
            ],
            Intent.SEARCH_HCP: [
                "search_hcp",
                "searchhcp",
                "find ",
                "find hcp",
                "look up",
                "look up hcp",
                "find dr",
                "search for",
            ],
            Intent.GET_SUMMARY: [
                "get_summary",
                "getsummary",
                "interactions",
                "history",
                "summary",
                "past visits",
                "previous",
            ],
            Intent.CREATE_FOLLOW_UP: [
                "create_follow_up",
                "create_followup",
                "schedule",
                "follow up",
                "followup",
                "set reminder",
            ],
            Intent.UPDATE_FOLLOW_UP: [
                "update_follow_up",
                "update_followup",
                "complete follow",
                "done follow",
            ],
            Intent.GENERAL_QUERY: [
                "hello",
                "hi ",
                "hey",
                "thanks",
                "thank you",
                "help",
                "what can",
            ],
        }

        # Check for exact match first
        response_clean = response.replace("-", "_").replace(" ", "")

        # Try to find an intent keyword in the response
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword in response:
                    return cls(intent=intent, confidence=0.9)

        # Check for partial matches with underscores
        for intent in Intent:
            intent_name = intent.value.replace("_", "")
            if intent_name in response_clean.replace("_", ""):
                return cls(intent=intent, confidence=0.8)

        return cls(intent=Intent.UNKNOWN, confidence=0.0)
