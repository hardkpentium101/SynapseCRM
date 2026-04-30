"""
LLM Manager - Abstraction layer for LLM providers
Supports: Groq (default), OpenRouter, OpenAI, Anthropic
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import json
import os
import time

from groq import Groq
from openai import OpenAI

from ..config import settings
from .langsmith.tracing import emit_llm_call


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


# OpenRouter models (single source of truth) sorted by price - price per 1M tokens
OPENROUTER_MODELS = [
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

OPENROUTER_CHAT_MODELS = {m["id"] for m in OPENROUTER_MODELS}

OPENROUTER_TOOL_CALL_MODELS = {
    "deepseek/deepseek-chat-v3-0324",
    "openai/gpt-5-mini",
    "moonshot/kimi-k2.5",
    "openai/gpt-5.1",
    "openai/gpt-5.2",
    "anthropic/claude-sonnet-4.6",
    "anthropic/claude-opus-4.6",
}

def _parse_tool_calls(raw_tool_calls) -> List[ToolCall]:
    """Parse raw tool calls from LLM response into ToolCall objects."""
    tool_calls = []
    if not raw_tool_calls:
        return tool_calls
    for tc in raw_tool_calls:
        try:
            args = (
                json.loads(tc.function.arguments)
                if isinstance(tc.function.arguments, str)
                else tc.function.arguments
            )
        except json.JSONDecodeError:
            args = {"raw": tc.function.arguments}
        tool_calls.append(ToolCall(name=tc.function.name, arguments=args, id=tc.id))
    return tool_calls


def _build_usage(usage) -> Dict[str, int]:
    """Build usage dict from LLM response usage object."""
    if not usage:
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    return {
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
    }


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
        start = time.time()
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        latency_ms = (time.time() - start) * 1000

        choice = response.choices[0]
        tool_calls = _parse_tool_calls(choice.message.tool_calls)
        llm_response = LLMResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            model=response.model,
            usage=_build_usage(response.usage),
            raw_response=response,
        )

        emit_llm_call(
            model=model,
            messages=messages,
            response_content=llm_response.content,
            usage=llm_response.usage,
            latency_ms=latency_ms,
            tool_calls=llm_response.tool_calls,
        )

        return llm_response

    def complete_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        start = time.time()
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        latency_ms = (time.time() - start) * 1000

        choice = response.choices[0]
        tool_calls = _parse_tool_calls(choice.message.tool_calls)
        llm_response = LLMResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            model=response.model,
            usage=_build_usage(response.usage),
            raw_response=response,
        )

        emit_llm_call(
            model=model,
            messages=messages,
            response_content=llm_response.content,
            usage=llm_response.usage,
            latency_ms=latency_ms,
            tool_calls=llm_response.tool_calls,
        )

        return llm_response

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
        start = time.time()
        self.client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": "Hi"}], max_tokens=5
        )
        return time.time() - start


class OpenRouterLLMManager(LLMManager):
    """OpenRouter API implementation (OpenAI-compatible)"""

    MODELS_BY_PRICE = OPENROUTER_MODELS

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self._model_cache: Optional[List[Model]] = None

    _OPENROUTER_HEADERS = {
        "HTTP-Referer": "https://crm-ai-agent.local",
        "X-Title": "CRM AI Agent",
    }

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 1024,
        **kwargs,
    ) -> LLMResponse:
        start = time.time()
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers=self._OPENROUTER_HEADERS,
            **kwargs,
        )
        latency_ms = (time.time() - start) * 1000

        choice = response.choices[0]
        tool_calls = _parse_tool_calls(choice.message.tool_calls)
        llm_response = LLMResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            model=response.model,
            usage=_build_usage(response.usage),
            raw_response=response,
        )

        emit_llm_call(
            model=model,
            messages=messages,
            response_content=llm_response.content,
            usage=llm_response.usage,
            latency_ms=latency_ms,
            tool_calls=llm_response.tool_calls,
        )

        return llm_response

    def complete_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        start = time.time()
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers=self._OPENROUTER_HEADERS,
            **kwargs,
        )
        latency_ms = (time.time() - start) * 1000

        choice = response.choices[0]
        tool_calls = _parse_tool_calls(choice.message.tool_calls)
        llm_response = LLMResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            model=response.model,
            usage=_build_usage(response.usage),
            raw_response=response,
        )

        emit_llm_call(
            model=model,
            messages=messages,
            response_content=llm_response.content,
            usage=llm_response.usage,
            latency_ms=latency_ms,
            tool_calls=llm_response.tool_calls,
        )

        return llm_response

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
