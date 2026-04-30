"""
Orchestrator Agent - Main HCP CRM orchestrator with tool calling capabilities
"""

from typing import Dict, Any, List
import json

from ..base import BaseAgent, AgentConfig, AGENT_CONFIGS
from ..llm_manager import LLMManager
from ..model_selector import ModelSelector
from ..tools.registry import get_tool_registry


class OrchestratorAgent(BaseAgent):
    """Main orchestrator with tool calling capabilities"""

    def __init__(self, llm_manager: LLMManager, model_selector: ModelSelector):
        config = AGENT_CONFIGS["orchestrator"]
        tool_registry = get_tool_registry()
        super().__init__(
            config,
            llm_manager,
            model_selector,
            {name: tool_registry.execute for name in config.tools},
        )
        self.tool_registry = tool_registry

    def process_with_tools(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> tuple[str, List[Dict]]:
        """Process with tool calling and return results"""
        tool_results = []
        messages = self._build_messages(user_input, context)
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            response = self.complete(messages, use_tools=True)

            if not response.tool_calls:
                return response.content or "Done.", tool_results

            for tool_call in response.tool_calls:
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.name,
                                    "arguments": json.dumps(tool_call.arguments)
                                    if isinstance(tool_call.arguments, dict)
                                    else tool_call.arguments,
                                },
                            }
                        ],
                    }
                )

                tool_result = self.tool_registry.execute(
                    tool_call.name, tool_call.arguments
                )
                tool_results.append(tool_result.to_dict())

                result_content = json.dumps(tool_result.to_dict())
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.name,
                        "content": result_content,
                    }
                )

        return response.content or "Processing complete.", tool_results

    def process(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Process with tool calling"""
        messages = self._build_messages(user_input, context)
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            response = self.complete(messages, use_tools=True)

            if not response.tool_calls:
                return response.content or "I'm not sure how to help with that."

            for tool_call in response.tool_calls:
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.name,
                                    "arguments": json.dumps(tool_call.arguments)
                                    if isinstance(tool_call.arguments, dict)
                                    else tool_call.arguments,
                                },
                            }
                        ],
                    }
                )

                tool_result = self.tool_registry.execute(
                    tool_call.name, tool_call.arguments
                )

                result_content = json.dumps(tool_result.to_dict())
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.name,
                        "content": result_content,
                    }
                )

        return response.content or "Processing complete."
