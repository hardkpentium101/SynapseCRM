from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    rep = "rep"
    manager = "manager"
    admin = "admin"


class InteractionType(str, Enum):
    meeting = "meeting"
    call = "call"
    conference = "conference"
    email = "email"


class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class FollowUpType(str, Enum):
    follow_up_meeting = "follow_up_meeting"
    send_material = "send_material"
    sample_request = "sample_request"
    call = "call"
    other = "other"


class FollowUpStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class MaterialType(str, Enum):
    pdf = "pdf"
    physical = "physical"
    digital = "digital"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.rep
    territory: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# HCP Schemas
class HCPBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    institution: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class HCPCreate(HCPBase):
    pass


class HCPUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    institution: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class HCPSimpleResponse(HCPBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HCPDetailResponse(HCPBase):
    id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Material Schemas
class MaterialBase(BaseModel):
    name: str
    type: MaterialType = MaterialType.pdf
    description: Optional[str] = None
    file_url: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialResponse(MaterialBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Sample Schemas
class SampleBase(BaseModel):
    product_name: str
    lot_number: Optional[str] = None
    quantity: int = 1


class SampleCreate(SampleBase):
    interaction_id: Optional[str] = None


class SampleResponse(SampleBase):
    id: str
    interaction_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Follow-up Schemas
class FollowUpBase(BaseModel):
    type: FollowUpType = FollowUpType.follow_up_meeting
    description: str
    status: FollowUpStatus = FollowUpStatus.pending
    due_date: Optional[datetime] = None
    ai_generated: bool = False


class FollowUpCreate(FollowUpBase):
    interaction_id: Optional[str] = None


class FollowUpUpdate(BaseModel):
    type: Optional[FollowUpType] = None
    description: Optional[str] = None
    status: Optional[FollowUpStatus] = None
    due_date: Optional[datetime] = None


class FollowUpResponse(FollowUpBase):
    id: str
    interaction_id: Optional[str] = None
    assignee_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Interaction Schemas
class InteractionBase(BaseModel):
    hcp_id: str
    type: InteractionType = InteractionType.meeting
    date_time: datetime
    attendees: List[str] = []
    topics: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    outcome: Optional[str] = None
    voice_note_url: Optional[str] = None


class InteractionCreate(InteractionBase):
    material_ids: List[str] = []
    samples: List[SampleCreate] = []


class InteractionUpdate(BaseModel):
    hcp_id: Optional[str] = None
    type: Optional[InteractionType] = None
    date_time: Optional[datetime] = None
    attendees: Optional[List[str]] = None
    topics: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    outcome: Optional[str] = None
    voice_note_url: Optional[str] = None
    material_ids: Optional[List[str]] = None
    samples: Optional[List[SampleCreate]] = None


class InteractionDetailResponse(InteractionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    materials: List[MaterialResponse] = []
    samples: List[SampleResponse] = []
    follow_ups: List[FollowUpResponse] = []
    hcp: Optional[HCPSimpleResponse] = None

    class Config:
        from_attributes = True

    @field_validator("materials", mode="before")
    @classmethod
    def unwrap_interaction_materials(cls, v):
        if v:
            cleaned = [im for im in v if im is not None]
            if not cleaned:
                return []
            if hasattr(cleaned[0], "material"):
                materials = [im.material for im in cleaned if im.material is not None]
                return materials
            return cleaned
        return v


class InteractionListResponse(InteractionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    hcp: Optional[HCPSimpleResponse] = None

    class Config:
        from_attributes = True
