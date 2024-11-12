import logging
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.service import get_city_weather

logger = logging.getLogger("uvicorn")

class WeatherInput(BaseModel):
    location: str = Field(
        description="城市名称，例如'北京'、'上海'、'成都'等",
        default="北京"
    )

@tool(
    "get_weather",
    args_schema=WeatherInput,
)
def get_weather(location: str) -> str:
    """获取指定位置的天气信息。
    
    Args:
        location: 城市名称，如"北京"、"成都"等
        
    Returns:
        str: 天气信息
    """
    return get_city_weather(location) 