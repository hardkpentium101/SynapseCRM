"""
Tool Registry - Manages all available tools
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str]


class ToolResult:
    """Result from tool execution"""

    def __init__(
        self, success: bool, data: Any = None, error: str = None, tool_name: str = ""
    ):
        self.success = success
        self.data = data
        self.error = error
        self.tool_name = tool_name

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "tool_name": self.tool_name,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class ToolRegistry:
    """Registry of all available tools"""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._definitions: Dict[str, ToolDefinition] = {}

    def register(self, name: str, func: Callable, definition: ToolDefinition):
        """Register a tool"""
        self._tools[name] = func
        self._definitions[name] = definition

    def execute(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool by name"""
        if name not in self._tools:
            return ToolResult(
                success=False, error=f"Tool '{name}' not found", tool_name=name
            )

        try:
            result = self._tools[name](**arguments)
            return ToolResult(success=True, data=result, tool_name=name)
        except TypeError as e:
            # Handle missing required arguments
            return ToolResult(
                success=False,
                error=f"Missing required argument: {str(e)}",
                tool_name=name,
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), tool_name=name)

    def get_definition(self, name: str) -> Optional[ToolDefinition]:
        """Get tool definition"""
        return self._definitions.get(name)

    def get_definitions_for_tools(self, tool_names: List[str]) -> List[Dict]:
        """Get OpenAI-format tool definitions for specific tools"""
        result = []
        for name in tool_names:
            if name in self._definitions:
                tool = self._definitions[name]
                result.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                "type": "object",
                                "properties": tool.parameters,
                                "required": tool.required,
                            },
                        },
                    }
                )
        return result

    def get_all_definitions(self) -> List[Dict]:
        """Get definitions for all registered tools"""
        return self.get_definitions_for_tools(list(self._tools.keys()))


# Global tool registry instance
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get or create global tool registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
        _register_all_tools(_global_registry)
    return _global_registry


def _register_all_tools(registry: ToolRegistry):
    """Register all tools with the registry"""
    from .hcp_tools import register_hcp_tools
    from .interaction_tools import register_interaction_tools
    from .followup_tools import register_followup_tools
    from .context_tools import register_context_tools

    register_hcp_tools(registry)
    register_interaction_tools(registry)
    register_followup_tools(registry)
    register_context_tools(registry)


def get_tool_definitions(tool_names: List[str]) -> List[Dict]:
    """Get tool definitions for specified tools"""
    registry = get_tool_registry()
    return registry.get_definitions_for_tools(tool_names)
