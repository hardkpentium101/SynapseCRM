"""
LLM Manager - Abstraction layer for LLM providers
Supports: Groq (default), OpenRouter, OpenAI, Anthropic
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import os

from groq import Groq
from openai import OpenAI

from ..config import settings


class LLMProvider(Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"


@dataclass
class Model:
    id: str
    object: str = "model"
    created: int = 0
    owned_by: str = ""
    provider: str = ""


@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any]
    id: str = ""


@dataclass
class LLMResponse:
    content: Optional[str]
    tool_calls: List[ToolCall]
    model: str
    usage: Dict[str, int] = None
    raw_response: Any = None


class LLMManager(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 1024,
        **kwargs,
    ) -> LLMResponse:
        """Send messages and get text completion"""
        pass

    @abstractmethod
    def complete_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        """Complete with tool calling capability"""
        pass

    @abstractmethod
    def list_models(self) -> List[Model]:
        """List available models for this provider"""
        pass

    @abstractmethod
    def ping(self, model: str) -> float:
        """Measure latency for a model (in seconds)"""
        pass


class GroqLLMManager(LLMManager):
    """Groq API implementation"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set")
        self.client = Groq(api_key=self.api_key)
        self._model_cache: Optional[List[Model]] = None

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 1024,
        **kwargs,
    ) -> LLMResponse:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        choice = response.choices[0]
        tool_calls = []

        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                import json

                try:
                    args = (
                        json.loads(tc.function.arguments)
                        if isinstance(tc.function.arguments, str)
                        else tc.function.arguments
                    )
                except json.JSONDecodeError:
                    args = {"raw": tc.function.arguments}

                tool_calls.append(
                    ToolCall(name=tc.function.name, arguments=args, id=tc.id)
                )

        return LLMResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens
                if response.usage
                else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            raw_response=response,
        )

    def complete_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        choice = response.choices[0]
        tool_calls = []

        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                import json

                try:
                    args = (
                        json.loads(tc.function.arguments)
                        if isinstance(tc.function.arguments, str)
                        else tc.function.arguments
                    )
                except json.JSONDecodeError:
                    args = {"raw": tc.function.arguments}

                tool_calls.append(
                    ToolCall(name=tc.function.name, arguments=args, id=tc.id)
                )

        return LLMResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens
                if response.usage
                else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            raw_response=response,
        )

    def list_models(self) -> List[Model]:
        if self._model_cache is None:
            response = self.client.models.list()
            self._model_cache = [
                Model(
                    id=m.id,
                    object=m.object,
                    created=m.created,
                    owned_by=m.owned_by,
                    provider="groq",
                )
                for m in response.data
            ]
        return self._model_cache

    def ping(self, model: str) -> float:
        import time

        start = time.time()
        self.client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": "Hi"}], max_tokens=5
        )
        return time.time() - start


class OpenRouterLLMManager(LLMManager):
    """OpenRouter API implementation (OpenAI-compatible)"""

    # Models sorted by price (cheapest first) - price per 1M tokens
    MODELS_BY_PRICE = [
        {"id": "xiaomi/mimo-v2-flash:free", "input": 0, "output": 0, "owned_by": "xiaomi"},
        {"id": "deepseek/deepseek-r1:free", "input": 0, "output": 0, "owned_by": "deepseek"},
        {"id": "meta-llama/llama-3.3-70b-instruct:free", "input": 0, "output": 0, "owned_by": "meta"},
        {"id": "google/gemma-3-27b-it:free", "input": 0, "output": 0, "owned_by": "google"},
        {"id": "mistralai/mistral-7b-instruct:free", "input": 0, "output": 0, "owned_by": "mistral"},
        {"id": "xiaomi/mimo-v2-flash", "input": 0.09, "output": 0.29, "owned_by": "xiaomi"},
        {"id": "deepseek/deepseek-chat-v3-0324", "input": 0.26, "output": 0.38, "owned_by": "deepseek"},
        {"id": "openai/gpt-5-mini", "input": 0.25, "output": 2.00, "owned_by": "openai"},
        {"id": "moonshot/kimi-k2.5", "input": 0.45, "output": 2.20, "owned_by": "moonshot"},
        {"id": "google/gemini-3-flash", "input": 0.30, "output": 3.00, "owned_by": "google"},
        {"id": "deepseek/deepseek-r1-0528", "input": 1.20, "output": 2.80, "owned_by": "deepseek"},
        {"id": "openai/gpt-5.1", "input": 1.25, "output": 10.00, "owned_by": "openai"},
        {"id": "openai/gpt-5.2", "input": 1.75, "output": 14.00, "owned_by": "openai"},
        {"id": "anthropic/claude-sonnet-4.6", "input": 3.00, "output": 15.00, "owned_by": "anthropic"},
        {"id": "anthropic/claude-opus-4.6", "input": 5.00, "output": 25.00, "owned_by": "anthropic"},
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self._model_cache: Optional[List[Model]] = None

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 1024,
        **kwargs,
    ) -> LLMResponse:
        extra_headers = {
            "HTTP-Referer": "https://crm-ai-agent.local",
            "X-Title": "CRM AI Agent",
        }

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers=extra_headers,
            **kwargs,
        )

        choice = response.choices[0]
        tool_calls = []

        if choice.message.tool_calls:
            import json

            for tc in choice.message.tool_calls:
                try:
                    args = (
                        json.loads(tc.function.arguments)
                        if isinstance(tc.function.arguments, str)
                        else tc.function.arguments
                    )
                except json.JSONDecodeError:
                    args = {"raw": tc.function.arguments}

                tool_calls.append(
                    ToolCall(name=tc.function.name, arguments=args, id=tc.id)
                )

        return LLMResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens
                if response.usage
                else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            raw_response=response,
        )

    def complete_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        extra_headers = {
            "HTTP-Referer": "https://crm-ai-agent.local",
            "X-Title": "CRM AI Agent",
        }

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers=extra_headers,
            **kwargs,
        )

        choice = response.choices[0]
        tool_calls = []

        if choice.message.tool_calls:
            import json

            for tc in choice.message.tool_calls:
                try:
                    args = (
                        json.loads(tc.function.arguments)
                        if isinstance(tc.function.arguments, str)
                        else tc.function.arguments
                    )
                except json.JSONDecodeError:
                    args = {"raw": tc.function.arguments}

                tool_calls.append(
                    ToolCall(name=tc.function.name, arguments=args, id=tc.id)
                )

        return LLMResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens
                if response.usage
                else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            raw_response=response,
        )

    def list_models(self) -> List[Model]:
        if self._model_cache is None:
            # Return sorted by price (cheapest first)
            self._model_cache = [
                Model(
                    id=m["id"],
                    object="model",
                    created=0,
                    owned_by=m["owned_by"],
                    provider="openrouter",
                )
                for m in self.MODELS_BY_PRICE
            ]
        return self._model_cache

    def ping(self, model: str) -> float:
        import time

        start = time.time()
        self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
            extra_headers={
                "HTTP-Referer": "https://crm-ai-agent.local",
                "X-Title": "CRM AI Agent",
            },
        )
        return time.time() - start


def get_llm_manager(provider: Optional[str] = None) -> LLMManager:
    """Factory function to get LLM manager based on provider"""
    provider = provider or settings.LLM_PROVIDER or "groq"

    if provider.lower() == "groq":
        return GroqLLMManager()
    elif provider.lower() == "openai":
        raise NotImplementedError("OpenAI provider not yet implemented")
    elif provider.lower() == "anthropic":
        raise NotImplementedError("Anthropic provider not yet implemented")
    elif provider.lower() == "openrouter":
        return OpenRouterLLMManager()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
