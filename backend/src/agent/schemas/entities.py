"""
Entity Schemas - Defines extracted entities
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class ExtractedEntities(BaseModel):
    """Structured entities extracted from user message"""

    hcp_name: Optional[str] = None
    hcp_specialty: Optional[str] = None
    hcp_institution: Optional[str] = None
    hcp_id: Optional[str] = None  # Resolved from search
    interaction_type: Optional[str] = None  # meeting, call, email, conference
    date_time: Optional[str] = None  # ISO format
    sentiment: Optional[str] = None  # positive, neutral, negative
    topics: List[str] = Field(default_factory=list)
    attendees: List[str] = Field(default_factory=list)
    follow_up_type: Optional[str] = None  # call, meeting, email
    follow_up_due: Optional[str] = None  # ISO format

    @classmethod
    def from_json(cls, json_str: str) -> "ExtractedEntities":
        """Parse entities from JSON string"""
        import json

        try:
            data = json.loads(json_str) if isinstance(json_str, str) else json_str
            return cls(**{k: v for k, v in data.items() if v is not None})
        except (json.JSONDecodeError, TypeError):
            return cls()

    def is_empty(self) -> bool:
        """Check if any meaningful entities were extracted"""
        return all(
            [
                not self.hcp_name,
                not self.hcp_specialty,
                not self.hcp_institution,
                not self.interaction_type,
                not self.date_time,
                not self.sentiment,
                not self.topics,
                not self.attendees,
                not self.follow_up_type,
                not self.follow_up_due,
            ]
        )

    def to_context_dict(self) -> dict:
        """Convert to dictionary for context injection"""
        data = self.model_dump()
        # Remove None values and empty lists
        return {k: v for k, v in data.items() if v}


class ConversationContext(BaseModel):
    """Context carried through the conversation"""

    user_id: str
    session_id: str
    current_intent: Optional[str] = None
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    resolved_hcp_id: Optional[str] = None
    last_interaction_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
