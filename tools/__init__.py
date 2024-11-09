from typing import List
from langchain.tools import BaseTool
from .weather_tool import get_weather
from .time_tool import get_time

def get_tools() -> List[BaseTool]:
    """获取所有可用的工具
    
    Returns:
        List[BaseTool]: 工具列表
    """
    return [
        get_weather,
        get_time,
    ]

__all__ = ['get_tools'] 