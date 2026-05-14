"""
Model Selector - Auto-selects best model based on task type
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

from .llm_manager import LLMManager, Model, OPENROUTER_CHAT_MODELS


@dataclass
class ModelSelection:
    """Represents a model selection with metadata"""
    model_id: str
    latency: float
    is_fallback: bool = False


# Models that support chat completions (exclude whisper, embeddings, etc.)
CHAT_MODELS = {
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "llama-3.1-405b-reasoning",
    "llama3-groq-70b-8192-tool-use-preview",
    "llama3-groq-8b-8192-tool-use-preview",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it",
    "gemma2-9b-it",
}

# Models that explicitly support tool calling (function calling)
TOOL_CALL_MODELS = {
    "llama3-groq-70b-8192-tool-use-preview",
    "llama3-groq-8b-8192-tool-use-preview",
}


class ModelSelector:
    """Selects best model based on task requirements"""

    DEFAULT_MODELS = {
        "classification": {
            "primary": "xiaomi/mimo-v2-flash:free",
            "fallback": "deepseek/deepseek-chat-v3-0324",
        },
        "extraction": {
            "primary": "deepseek/deepseek-chat-v3-0324",
            "fallback": "moonshot/kimi-k2.5",
        },
        "validation": {
            "primary": "xiaomi/mimo-v2-flash:free",
            "fallback": "deepseek/deepseek-chat-v3-0324",
        },
        "tool_use": {
            "primary": "openai/gpt-5-mini",
            "fallback": "deepseek/deepseek-chat-v3-0324",
        },
        "general": {
            "primary": "xiaomi/mimo-v2-flash:free",
            "fallback": "deepseek/deepseek-chat-v3-0324",
        },
    }

    def __init__(self, llm_manager: LLMManager):
        self.llm = llm_manager
        self._selections: Dict[str, ModelSelection] = {}
        self._available_models: Optional[List[Model]] = None
        self._chat_models: Optional[List[Model]] = None
        self._initialized = False

    def _is_chat_model(self, model_id: str) -> bool:
        """Check if model supports chat completions"""
        model_lower = model_id.lower()
        # Check known non-chat models (guard, whisper, embeddings, tts, etc.)
        exclude_patterns = [
            "whisper",
            "embed",
            "tts",
            "speech",
            "vision",
            "image",
            "prompt-guard",
            "safeguard",
            "oss-20b",
        ]
        for pattern in exclude_patterns:
            if pattern in model_lower:
                return False
        # Check known chat models
        if model_id in CHAT_MODELS:
            return True
        # Check OpenRouter chat models
        if model_id in OPENROUTER_CHAT_MODELS:
            return True
        return True

    def initialize(self):
        """Fetch available models and pre-select optimal ones"""
        if self._initialized:
            return

        self._available_models = self.llm.list_models()
        self._chat_models = [
            m for m in self._available_models if self._is_chat_model(m.id)
        ]
        chat_model_ids = {m.id for m in self._chat_models}

        for task, models in self.DEFAULT_MODELS.items():
            primary = models["primary"]
            fallback = models["fallback"]

            if primary in chat_model_ids:
                self._selections[task] = ModelSelection(
                    model_id=primary,
                    latency=0,
                    is_fallback=False,
                )
            elif fallback in chat_model_ids:
                self._selections[task] = ModelSelection(
                    model_id=fallback, latency=0, is_fallback=True
                )
            else:
                # Use first available chat model as fallback
                if self._chat_models:
                    self._selections[task] = ModelSelection(
                        model_id=self._chat_models[0].id,
                        latency=0,
                        is_fallback=True,
                    )
                else:
                    # Ultimate fallback
                    self._selections[task] = ModelSelection(
                        model_id="llama-3.1-8b-instant",
                        latency=0,
                        is_fallback=True,
                    )

        self._initialized = True

    def select(self, task_type: str) -> str:
        """Get the best model for a task"""
        if not self._initialized:
            self.initialize()

        if task_type in self._selections:
            return self._selections[task_type].model_id

        return self._selections.get(
            "general", ModelSelection(model_id="llama-3.1-8b-instant", latency=0)
        ).model_id

    def get_with_fallback(self, task_type: str) -> tuple[str, str]:
        """Get primary model and fallback"""
        if not self._initialized:
            self.initialize()

        task_models = self.DEFAULT_MODELS.get(task_type, self.DEFAULT_MODELS["general"])
        primary = self.select(task_type)
        fallback = task_models["fallback"]

        return primary, fallback

    def benchmark_models(self, models: List[str]) -> Dict[str, float]:
        """Measure latency for specific models"""
        results = {}
        for model in models:
            try:
                latency = self.llm.ping(model)
                results[model] = latency
            except Exception:
                results[model] = float("inf")
        return results

    def get_available_models(self) -> List[Model]:
        """Get all available models from the provider"""
        if not self._available_models:
            self._available_models = self.llm.list_models()
        return self._available_models

    def get_chat_models(self) -> List[Model]:
        """Get only chat-capable models"""
        if not self._chat_models:
            self.initialize()
        return self._chat_models

    def get_model_info(self, model_id: str) -> Optional[Model]:
        """Get info about a specific model"""
        available = self.get_available_models()
        for m in available:
            if m.id == model_id:
                return m
        return None
