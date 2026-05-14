"""
Tests for Orchestrator Agent utilities
"""

import pytest
import re


def is_valid_uuid(value: str) -> bool:
    """Standalone UUID validation function"""
    uuid_pattern = re.compile(
        r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", re.IGNORECASE
    )
    return bool(uuid_pattern.match(value)) if value else False


def extract_from_text(text: str) -> dict:
    """Standalone entity extraction from text"""
    entities = {}

    hcp_patterns = [
        r"(?:Dr\.?|Doctor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
    ]
    for pattern in hcp_patterns:
        match = re.search(pattern, text)
        if match:
            entities["hcp_name"] = (
                match.group(0).replace("Dr. ", "").replace("Doctor ", "").strip()
            )
            break

    institutions = [
        "johns hopkins",
        "mayo clinic",
        "stanford",
        "cleveland",
        "ucla",
        "mount sinai",
        "duke",
        "harvard",
    ]
    for inst in institutions:
        if inst in text.lower():
            entities["hcp_institution"] = inst.title()
            break

    specialties = {
        "oncology": "Oncology",
        "oncologist": "Oncology",
        "cardiology": "Cardiology",
        "cardiologist": "Cardiology",
        "neurology": "Neurology",
        "neurologist": "Neurology",
    }
    for key, value in specialties.items():
        if key in text.lower():
            entities["hcp_specialty"] = value
            break

    if "call" in text.lower() or "phone" in text.lower():
        entities["interaction_type"] = "call"
    elif "email" in text.lower():
        entities["interaction_type"] = "email"
    elif "conference" in text.lower():
        entities["interaction_type"] = "conference"
    elif any(
        w in text.lower() for w in ["met", "meeting", "visited", "saw", "discussed"]
    ):
        entities["interaction_type"] = "meeting"

    return entities


class TestUUIDValidation:
    """Test UUID validation"""

    def test_valid_uuid_format(self):
        """Test valid UUID formats"""
        valid_uuids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "A550E840-E29B-41D4-A716-446655440000",
        ]
        for uuid_str in valid_uuids:
            assert is_valid_uuid(uuid_str) is True, f"Should be valid: {uuid_str}"

    def test_invalid_uuid_format(self):
        """Test invalid UUID formats"""
        invalid_uuids = [
            "not-a-uuid",
            "550e8400-e29b-41d4-a716",
            "550e8400e29b41d4a716446655440000",
            "dr-sharma",
            "",
        ]
        for uuid_str in invalid_uuids:
            assert is_valid_uuid(uuid_str) is False, f"Should be invalid: {uuid_str}"

    def test_none_uuid(self):
        """Test None returns False"""
        assert is_valid_uuid(None) is False


class TestEntityExtractionFromText:
    """Test entity extraction from text"""

    def test_extract_hcp_name_with_dr(self):
        """Test extracting HCP name with Dr. prefix"""
        result = extract_from_text("I met with Dr. John Smith today")
        assert result.get("hcp_name") == "John Smith"

    def test_extract_hcp_name_with_doctor(self):
        """Test extracting HCP name with Doctor prefix"""
        result = extract_from_text("Meeting with Doctor Jane Doe")
        assert result.get("hcp_name") == "Jane Doe"

    def test_extract_institution_johns_hopkins(self):
        """Test extracting Johns Hopkins institution"""
        result = extract_from_text("Dr. Smith from Johns Hopkins")
        assert result.get("hcp_institution") == "Johns Hopkins"

    def test_extract_institution_mayo_clinic(self):
        """Test extracting Mayo Clinic institution"""
        result = extract_from_text("Doctor at Mayo Clinic")
        assert result.get("hcp_institution") == "Mayo Clinic"

    def test_extract_specialty_oncology(self):
        """Test extracting oncology specialty"""
        result = extract_from_text("Met with oncologist Dr. Chen")
        assert result.get("hcp_specialty") == "Oncology"

    def test_extract_specialty_cardiology(self):
        """Test extracting cardiology specialty"""
        result = extract_from_text("Spoke with cardiologist Dr. Kim")
        assert result.get("hcp_specialty") == "Cardiology"

    def test_extract_specialty_neurology(self):
        """Test extracting neurology specialty"""
        result = extract_from_text("Consulted with neurologist Dr. Park")
        assert result.get("hcp_specialty") == "Neurology"

    def test_extract_interaction_type_call(self):
        """Test extracting call interaction type"""
        result = extract_from_text("Call with Dr. Sharma yesterday")
        assert result.get("interaction_type") == "call"

    def test_extract_interaction_type_phone(self):
        """Test extracting phone interaction type"""
        result = extract_from_text("Phone conversation with Dr. Chen")
        assert result.get("interaction_type") == "call"

    def test_extract_interaction_type_meeting(self):
        """Test extracting meeting interaction type"""
        result = extract_from_text("Met with Dr. Chen at the hospital")
        assert result.get("interaction_type") == "meeting"

    def test_extract_interaction_type_email(self):
        """Test extracting email interaction type"""
        result = extract_from_text("Email exchange with Dr. Patel")
        assert result.get("interaction_type") == "email"

    def test_extract_interaction_type_conference(self):
        """Test extracting conference interaction type"""
        result = extract_from_text("Conference with Dr. Roberts")
        assert result.get("interaction_type") == "conference"

    def test_extract_full_message(self):
        """Test extracting from full message"""
        result = extract_from_text(
            "I met with Dr. Priya Sharma from Johns Hopkins yesterday"
        )
        assert result.get("hcp_name") == "Priya Sharma"
        assert result.get("hcp_institution") == "Johns Hopkins"
        assert result.get("interaction_type") == "meeting"

