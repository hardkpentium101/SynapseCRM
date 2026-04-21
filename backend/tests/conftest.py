"""
Pytest configuration and shared fixtures
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_hcp_data():
    """Sample HCP data for testing"""
    return {
        "name": "Dr. Test Doctor",
        "specialty": "Cardiology",
        "institution": "Test Hospital",
        "email": "test@hospital.com",
        "phone": "+1-555-0100",
    }


@pytest.fixture
def sample_interaction_data():
    """Sample interaction data for testing"""
    return {
        "type": "meeting",
        "date_time": "2024-01-15T10:00:00",
        "topics": ["clinical trial"],
        "sentiment": "positive",
    }


@pytest.fixture
def sample_followup_data():
    """Sample follow-up data for testing"""
    return {
        "type": "call",
        "description": "Follow up on clinical trial",
        "due_date": "2024-01-20T10:00:00",
    }
