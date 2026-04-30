"""
Agent Factory - Provides shared singleton instances for graph nodes
"""

from typing import Optional
from ..llm_manager import LLMManager, get_llm_manager
from ..model_selector import ModelSelector

_llm_manager: Optional[LLMManager] = None
_model_selector: Optional[ModelSelector] = None


def get_shared_llm_manager() -> LLMManager:
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = get_llm_manager()
    return _llm_manager


def get_shared_model_selector() -> ModelSelector:
    global _model_selector
    if _model_selector is None:
        _model_selector = ModelSelector(get_shared_llm_manager())
        _model_selector.initialize()
    return _model_selector


def reset_singletons():
    global _llm_manager, _model_selector
    _llm_manager = None
    _model_selector = None
