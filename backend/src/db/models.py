from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Integer,
    TypeDecorator,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid
import json

Base = declarative_base()


class JSONEncodedList(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return "[]"

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return []


class GUID(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return None


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="rep")
    territory = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    interactions = relationship("Interaction", back_populates="user")
    hcps = relationship("HCP", back_populates="creator")


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    specialty = Column(String(255))
    institution = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    notes = Column(Text)
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    creator = relationship("User", back_populates="hcps")
    interactions = relationship("Interaction", back_populates="hcp")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hcp_id = Column(String(36), ForeignKey("hcps.id"))
    user_id = Column(String(36), ForeignKey("users.id"))
    type = Column(String(50), default="meeting")
    date_time = Column(DateTime(timezone=True), nullable=False)
    attendees = Column(JSONEncodedList, default=[])
    topics = Column(Text)
    sentiment = Column(String(20))
    outcome = Column(Text)
    voice_note_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    hcp = relationship("HCP", back_populates="interactions")
    user = relationship("User", back_populates="interactions")
    materials = relationship("InteractionMaterial", back_populates="interaction")
    samples = relationship("Sample", back_populates="interaction")
    follow_ups = relationship("FollowUp", back_populates="interaction")


class Material(Base):
    __tablename__ = "materials"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    type = Column(String(50), default="pdf")
    description = Column(Text)
    file_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    interactions = relationship("InteractionMaterial", back_populates="material")


class InteractionMaterial(Base):
    __tablename__ = "interaction_materials"

    interaction_id = Column(
        String(36), ForeignKey("interactions.id", ondelete="CASCADE"), primary_key=True
    )
    material_id = Column(
        String(36), ForeignKey("materials.id", ondelete="CASCADE"), primary_key=True
    )

    interaction = relationship("Interaction", back_populates="materials")
    material = relationship("Material", back_populates="interactions")


class Sample(Base):
    __tablename__ = "samples"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interaction_id = Column(
        String(36), ForeignKey("interactions.id", ondelete="CASCADE")
    )
    product_name = Column(String(255), nullable=False)
    lot_number = Column(String(100))
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    interaction = relationship("Interaction", back_populates="samples")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interaction_id = Column(
        String(36), ForeignKey("interactions.id", ondelete="CASCADE")
    )
    type = Column(String(50), default="follow_up_meeting")
    description = Column(Text, nullable=False)
    status = Column(String(50), default="pending")
    due_date = Column(DateTime(timezone=True))
    assignee_id = Column(String(36), ForeignKey("users.id"))
    created_by = Column(String(36), ForeignKey("users.id"))
    ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    interaction = relationship("Interaction", back_populates="follow_ups")
    assignee = relationship("User", foreign_keys=[assignee_id])
    creator = relationship("User", foreign_keys=[created_by])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    action = Column(String(50), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"))
    old_values = Column(Text)
    new_values = Column(Text)
    reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
