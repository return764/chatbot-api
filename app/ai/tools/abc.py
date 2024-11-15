from abc import ABC, abstractmethod
from langchain.tools import BaseTool


class ToolServiceProvider(ABC):
    @abstractmethod
    def is_tool_available(self) -> bool:
        pass

    @abstractmethod
    def get_tool(self) -> BaseTool:
        pass
