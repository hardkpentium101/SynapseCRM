"""
Conversation Memory - In-memory session storage (not persisted to DB)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from threading import Lock
import uuid

from ..schemas.entities import ExtractedEntities


@dataclass
class Message:
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tool_calls: List[Dict] = field(default_factory=list)
    tool_result: Dict = field(default_factory=None)

    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "tool_calls": self.tool_calls,
            "tool_result": self.tool_result,
        }


@dataclass
class SessionData:
    session_id: str
    user_id: str
    created_at: str
    messages: List[Message] = field(default_factory=list)
    entities: ExtractedEntities = field(default_factory=ExtractedEntities)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationMemory:
    """In-memory conversation memory per session"""

    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}
        self._lock = Lock()

    def create_session(self, user_id: str) -> SessionData:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        session = SessionData(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow().isoformat(),
        )
        with self._lock:
            self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session by ID"""
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str):
        """Delete a session"""
        with self._lock:
            self._sessions.pop(session_id, None)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: List[Dict] = None,
        tool_result: Dict = None,
    ):
        """Add a message to session history"""
        session = self.get_session(session_id)
        if not session:
            return

        message = Message(
            role=role,
            content=content,
            tool_calls=tool_calls or [],
            tool_result=tool_result,
        )

        with self._lock:
            session.messages.append(message)

    def get_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages from session"""
        session = self.get_session(session_id)
        if not session:
            return []

        messages = session.messages[-limit:]
        return [msg.to_dict() for msg in messages]

    def set_entities(self, session_id: str, entities: ExtractedEntities):
        """Update extracted entities"""
        session = self.get_session(session_id)
        if session:
            session.entities = entities

    def get_entities(self, session_id: str) -> ExtractedEntities:
        """Get extracted entities"""
        session = self.get_session(session_id)
        if session:
            return session.entities
        return ExtractedEntities()

    def set_context(self, session_id: str, key: str, value: Any):
        """Set session context"""
        session = self.get_session(session_id)
        if session:
            session.context[key] = value

    def get_context(self, session_id: str, key: str) -> Any:
        """Get session context"""
        session = self.get_session(session_id)
        if session:
            return session.context.get(key)
        return None

    def clear(self, session_id: str):
        """Clear session data (keep session, clear history)"""
        session = self.get_session(session_id)
        if session:
            with self._lock:
                session.messages.clear()
                session.entities = ExtractedEntities()
                session.context.clear()


# Global memory instance (per-process, not shared across instances)
_global_memory: Optional[ConversationMemory] = None


def get_memory() -> ConversationMemory:
    """Get or create global memory instance"""
    global _global_memory
    if _global_memory is None:
        _global_memory = ConversationMemory()
    return _global_memory


def clear_memory():
    """Clear all memory (use with caution)"""
    global _global_memory
    _global_memory = None


def get_memory_context() -> Dict[str, Any]:
    """Get current memory context (for tool injection)"""
    memory = get_memory()
    return {"memory": memory}
