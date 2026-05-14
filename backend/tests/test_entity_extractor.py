"""
Tests for Entity Extractor Agent
"""

import pytest
from src.agent.schemas.entities import ExtractedEntities
from src.agent.services.tool_services import HCPService


class TestExtractedEntitiesFromJson:
    """Test ExtractedEntities.from_json() method"""

    def test_parse_valid_json(self):
        """Test parsing valid JSON string"""
        json_str = '{"hcp_name": "Dr. John Smith", "hcp_specialty": "Cardiology", "hcp_institution": "Mayo Clinic"}'
        entities = ExtractedEntities.from_json(json_str)

        assert entities.hcp_name == "Dr. John Smith"
        assert entities.hcp_specialty == "Cardiology"
        assert entities.hcp_institution == "Mayo Clinic"

    def test_parse_empty_json(self):
        """Test parsing empty JSON returns empty entities"""
        entities = ExtractedEntities.from_json("{}")

        assert entities.hcp_name is None
        assert entities.hcp_specialty is None
        assert entities.is_empty()

    def test_parse_null_values_ignored(self):
        """Test that null values are not set"""
        json_str = '{"hcp_name": null, "hcp_specialty": "Oncology"}'
        entities = ExtractedEntities.from_json(json_str)

        assert entities.hcp_name is None
        assert entities.hcp_specialty == "Oncology"

    def test_parse_invalid_json_returns_empty(self):
        """Test parsing invalid JSON returns empty entities"""
        entities = ExtractedEntities.from_json("not valid json")

        assert entities.is_empty()

    def test_parse_none_input_returns_empty(self):
        """Test parsing None returns empty entities"""
        entities = ExtractedEntities.from_json(None)

        assert entities.is_empty()

    def test_parse_with_topics_list(self):
        """Test parsing JSON with topics list"""
        json_str = '{"hcp_name": "Dr. Chen", "topics": ["clinical trial", "new drug"]}'
        entities = ExtractedEntities.from_json(json_str)

        assert entities.hcp_name == "Dr. Chen"
        assert entities.topics == ["clinical trial", "new drug"]

    def test_parse_with_all_fields(self):
        """Test parsing JSON with all fields"""
        json_str = """{
            "hcp_name": "Dr. Sharma",
            "hcp_specialty": "Oncology",
            "hcp_institution": "Tata Memorial",
            "interaction_type": "meeting",
            "date_time": "2024-01-15T10:00:00",
            "sentiment": "positive",
            "topics": ["new trial"],
            "attendees": ["Dr. Kim"],
            "follow_up_type": "call",
            "follow_up_due": "2024-01-20"
        }"""
        entities = ExtractedEntities.from_json(json_str)

        assert entities.hcp_name == "Dr. Sharma"
        assert entities.hcp_specialty == "Oncology"
        assert entities.hcp_institution == "Tata Memorial"
        assert entities.interaction_type == "meeting"
        assert entities.date_time == "2024-01-15T10:00:00"
        assert entities.sentiment == "positive"
        assert entities.topics == ["new trial"]
        assert entities.attendees == ["Dr. Kim"]
        assert entities.follow_up_type == "call"
        assert entities.follow_up_due == "2024-01-20"


class TestExtractedEntitiesContextDict:
    """Test ExtractedEntities.to_context_dict() method"""

    def test_to_context_dict_excludes_none(self):
        """Test that None values are excluded from dict"""
        entities = ExtractedEntities(hcp_name="Dr. Smith", hcp_specialty="Cardiology")
        ctx = entities.to_context_dict()

        assert "hcp_name" in ctx
        assert "hcp_specialty" in ctx
        assert "hcp_id" not in ctx
        assert "date_time" not in ctx

    def test_to_context_dict_includes_non_empty_lists(self):
        """Test that non-empty lists are included"""
        entities = ExtractedEntities(hcp_name="Dr. Smith", topics=["trial"])
        ctx = entities.to_context_dict()

        assert "topics" in ctx
        assert ctx["topics"] == ["trial"]


class TestExtractedEntitiesIsEmpty:
    """Test ExtractedEntities.is_empty() method"""

    def test_is_empty_true_when_all_none(self):
        """Test is_empty returns True when all fields are None"""
        entities = ExtractedEntities()
        assert entities.is_empty() is True

    def test_is_empty_false_when_name_set(self):
        """Test is_empty returns False when name is set"""
        entities = ExtractedEntities(hcp_name="Dr. Smith")
        assert entities.is_empty() is False

    def test_is_empty_false_when_topics_set(self):
        """Test is_empty returns False when topics list has items"""
        entities = ExtractedEntities(topics=["clinical trial"])
        assert entities.is_empty() is False


class TestHCPServiceSearch:
    """Test HCPService database operations"""

    def test_search_hcp_returns_list(self):
        """Test search_hcp returns a list"""
        result = HCPService.search_hcp("test")
        assert isinstance(result, list)

    def test_search_hcp_with_results(self):
        """Test search with actual data"""
        result = HCPService.search_hcp("Sharma")
        assert isinstance(result, list)
        if result:
            assert "id" in result[0]
            assert "name" in result[0]

    def test_search_hcp_empty_results(self):
        """Test search with no matches"""
        result = HCPService.search_hcp("NonExistentXYZ123")
        assert isinstance(result, list)

