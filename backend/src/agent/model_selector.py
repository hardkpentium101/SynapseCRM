"""
Model Selector - Auto-selects best model based on task type
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import time

from .llm_manager import LLMManager, Model


@dataclass
class ModelSelection:
    model_id: str
    latency: float
    is_fallback: bool = False


class ModelSelector:
    """Selects best model based on task requirements"""

    # Default models per task type
    DEFAULT_MODELS = {
        "classification": {
            "primary": "llama-3.1-8b-instant",
            "fallback": "llama3-groq-8b-8192-tool-use-preview",
        },
        "extraction": {
            "primary": "llama-3.1-70b-versatile",
            "fallback": "mixtral-8x7b-32768",
        },
        "tool_use": {
            "primary": "llama3-groq-70b-8192-tool-use-preview",
            "fallback": "llama-3.1-70b-versatile",
        },
        "general": {
            "primary": "llama-3.1-8b-instant",
            "fallback": "llama3-groq-8b-8192-tool-use-preview",
        },
    }

    def __init__(self, llm_manager: LLMManager):
        self.llm = llm_manager
        self._selections: Dict[str, ModelSelection] = {}
        self._available_models: Optional[List[Model]] = None
        self._initialized = False

    def initialize(self):
        """Fetch available models and pre-select optimal ones"""
        if self._initialized:
            return

        self._available_models = self.llm.list_models()
        available_ids = {m.id for m in self._available_models}

        for task, models in self.DEFAULT_MODELS.items():
            primary = models["primary"]
            fallback = models["fallback"]

            # Check if primary is available
            if primary in available_ids:
                self._selections[task] = ModelSelection(
                    model_id=primary,
                    latency=0,  # Don't measure, trust Groq's speed
                    is_fallback=False,
                )
            elif fallback in available_ids:
                self._selections[task] = ModelSelection(
                    model_id=fallback, latency=0, is_fallback=True
                )
            else:
                # Use first available model as fallback
                if self._available_models:
                    self._selections[task] = ModelSelection(
                        model_id=self._available_models[0].id,
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

        # Default to general
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
            except Exception as e:
                results[model] = float("inf")
        return results

    def get_available_models(self) -> List[Model]:
        """Get all available models from the provider"""
        if not self._available_models:
            self._available_models = self.llm.list_models()
        return self._available_models

    def get_model_info(self, model_id: str) -> Optional[Model]:
        """Get info about a specific model"""
        available = self.get_available_models()
        for m in available:
            if m.id == model_id:
                return m
        return None
