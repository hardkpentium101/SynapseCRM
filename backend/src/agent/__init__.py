"""
HCP Agent - AI Agent for Healthcare CRM
"""

from .llm_manager import (
    LLMManager,
    LLMProvider,
    Model,
    ToolCall,
    LLMResponse,
    GroqLLMManager,
    get_llm_manager,
    OPENROUTER_MODELS,
    OPENROUTER_CHAT_MODELS,
    OPENROUTER_TOOL_CALL_MODELS,
)
from .model_selector import ModelSelector, ModelSelection
from .base import BaseAgent, AgentConfig, AgentType, AGENT_CONFIGS
from .schemas import (
    Intent,
    IntentClassification,
    ExtractedEntities,
    ConversationContext,
)
from .memory import ConversationMemory, SessionData, Message, get_memory, clear_memory
from .tools import ToolRegistry, ToolResult, get_tool_registry
from .subagents import IntentClassifierAgent, EntityExtractorAgent
from .main import HCPAgent, AgentResponse, get_hcp_agent, reset_agent
from .services import get_shared_llm_manager, get_shared_model_selector, reset_singletons

__all__ = [
    # LLM Manager
    "LLMManager",
    "LLMProvider",
    "Model",
    "ToolCall",
    "LLMResponse",
    "GroqLLMManager",
    "get_llm_manager",
    "OPENROUTER_MODELS",
    "OPENROUTER_CHAT_MODELS",
    "OPENROUTER_TOOL_CALL_MODELS",
    # Model Selector
    "ModelSelector",
    "ModelSelection",
    # Base
    "BaseAgent",
    "AgentConfig",
    "AgentType",
    "AGENT_CONFIGS",
    # Schemas
    "Intent",
    "IntentClassification",
    "ExtractedEntities",
    "ConversationContext",
    # Memory
    "ConversationMemory",
    "SessionData",
    "Message",
    "get_memory",
    "clear_memory",
    # Tools
    "ToolRegistry",
    "ToolResult",
    "get_tool_registry",
    # Subagents
    "IntentClassifierAgent",
    "EntityExtractorAgent",
    # Main
    "HCPAgent",
    "AgentResponse",
    "get_hcp_agent",
    "reset_agent",
    # Singletons
    "get_shared_llm_manager",
    "get_shared_model_selector",
    "reset_singletons",
]
