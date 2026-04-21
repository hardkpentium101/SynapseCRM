"""
Tests for Intent Classifier
"""

import pytest
from src.agent.schemas.intents import IntentClassification, Intent


class TestIntentClassification:
    """Test IntentClassification parsing"""

    def test_from_string_log_interaction(self):
        """Test parsing 'met' keyword"""
        result = IntentClassification.from_string("met with Dr. Sharma")
        assert result.intent == Intent.CREATE_INTERACTION

    def test_from_string_search_hcp(self):
        """Test parsing 'find' keyword"""
        result = IntentClassification.from_string("find Dr. Sharma")
        assert result.intent == Intent.SEARCH_HCP

    def test_from_string_add_hcp(self):
        """Test parsing 'add new' keyword"""
        result = IntentClassification.from_string("add new doctor")
        assert result.intent == Intent.ADD_HCP

    def test_from_string_follow_up(self):
        """Test parsing 'follow up' keyword"""
        result = IntentClassification.from_string("follow up with Dr. Smith")
        assert result.intent == Intent.CREATE_FOLLOW_UP

    def test_from_string_hello(self):
        """Test parsing greeting"""
        result = IntentClassification.from_string("hello")
        assert result.intent == Intent.GENERAL_QUERY

    def test_from_string_exact_match(self):
        """Test exact intent match"""
        result = IntentClassification.from_string("search_hcp")
        assert result.intent == Intent.SEARCH_HCP
        assert result.confidence == 0.9

    def test_from_string_unknown(self):
        """Test unknown intent"""
        result = IntentClassification.from_string("random text xyz")
        assert result.intent == Intent.UNKNOWN


class TestIntentEnum:
    """Test Intent enum values"""

    def test_intent_values(self):
        """Test all intent enum values exist"""
        assert Intent.ADD_HCP.value == "add_hcp"
        assert Intent.CREATE_INTERACTION.value == "create_interaction"
        assert Intent.SEARCH_HCP.value == "search_hcp"
        assert Intent.GET_SUMMARY.value == "get_summary"
        assert Intent.CREATE_FOLLOW_UP.value == "create_follow_up"
        assert Intent.UPDATE_FOLLOW_UP.value == "update_follow_up"
        assert Intent.GENERAL_QUERY.value == "general_query"
        assert Intent.UNKNOWN.value == "unknown"
