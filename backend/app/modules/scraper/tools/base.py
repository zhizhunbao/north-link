"""LLM Function Calling Tool base class and registry - BE-005."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """Standardized result from a scraper tool execution."""

    success: bool
    data: list[dict] = field(default_factory=list)
    error: str | None = None
    platform: str = ""
    cached: bool = False
    items_count: int = 0


class BaseTool(ABC):
    """Abstract base class for LLM Function Calling tools.

    Each tool represents a scraper for a specific platform.
    The LLM selects the appropriate tool based on name and description,
    and fills parameters based on the JSON Schema.
    """

    name: str = ""
    description: str = ""
    parameters: dict[str, Any] = {}

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the scraping task with given parameters.

        Args:
            **kwargs: Parameters as defined in self.parameters schema.

        Returns:
            ToolResult with scraped data or error info.
        """
        ...

    def to_openai_function(self) -> dict:
        """Convert tool to OpenAI Function Calling format.

        Compatible with both OpenAI API and Ollama (which uses the same format).
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """Central registry for all available scraper tools."""

    _tools: dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool) -> None:
        """Register a tool instance by its name."""
        cls._tools[tool.name] = tool

    @classmethod
    def get_all_tools(cls) -> list[BaseTool]:
        """Get all registered tools."""
        return list(cls._tools.values())

    @classmethod
    def get_tool_by_name(cls, name: str) -> BaseTool | None:
        """Look up a tool by name."""
        return cls._tools.get(name)

    @classmethod
    def get_openai_functions(cls) -> list[dict]:
        """Get all tools in OpenAI function calling format."""
        return [tool.to_openai_function() for tool in cls._tools.values()]
