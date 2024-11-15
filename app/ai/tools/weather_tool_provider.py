import httpx
import logging
from typing import Annotated, Optional, Dict, List

from langchain.tools import BaseTool
from langgraph.prebuilt import InjectedState

from app.config import config
from app.ai.tools.abc import ToolServiceProvider
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.ai.state import CustomState


logger = logging.getLogger("uvicorn")

class WeatherToolProvider(ToolServiceProvider):
    def __init__(self):
        self.key = config.qweather_key
        result = self.get_location_id('成都');
        self.status = result is not None

    def get_location_id(self, city_name: str) -> Optional[str]:
        """通过城市名称获取位置ID"""
        try:
            with httpx.Client(base_url="https://geoapi.qweather.com/v2", timeout=10.0) as client:
                params = {
                    "location": city_name,
                    "key": self.key,
                    "number": 1
                }
                response = client.get("/city/lookup", params=params)
                response.raise_for_status()

                data = response.json()
                if data["code"] == "200" and data["location"]:
                    return data["location"][0]["id"]
                return None

        except Exception as e:
            logger.error(f"获取城市ID失败: {str(e)}")
            return None

    def get_weather(self, location_id: str) -> Optional[Dict]:
        """获取7天天气预报

        Args:
            location_id: 城市ID

        Returns:
            Dict: 包含实时天气和未来7天预报的字典
        """
        try:
            # 获取实时天气
            current_weather = self._get_current_weather(location_id)
            if not current_weather:
                return None

            # 获取7天预报
            daily_forecast = self._get_daily_forecast(location_id)
            if not daily_forecast:
                return None

            return {
                "current": current_weather,
                "daily": daily_forecast
            }

        except Exception as e:
            logger.error(f"获取天气信息失败: {str(e)}")
            return None

    def _get_current_weather(self, location_id: str) -> Optional[Dict]:
        """获取实时天气"""
        with httpx.Client(base_url="https://devapi.qweather.com/v7", timeout=10.0) as client:
            params = {
                "location": location_id,
                "key": self.key
            }
            response = client.get("/weather/now", params=params)
            response.raise_for_status()

            data = response.json()
            if data["code"] == "200":
                return {
                    "temp": data["now"]["temp"],
                    "text": data["now"]["text"],
                    "feelsLike": data["now"]["feelsLike"],
                    "humidity": data["now"]["humidity"],
                    "windDir": data["now"]["windDir"],
                    "windScale": data["now"]["windScale"],
                    "time": "现在"
                }
            return None

    def _get_daily_forecast(self, location_id: str) -> Optional[List[Dict]]:
        """获取7天预报"""
        with httpx.Client(base_url="https://devapi.qweather.com/v7", timeout=10.0) as client:
            params = {
                "location": location_id,
                "key": self.key
            }
            response = client.get("/weather/7d", params=params)
            response.raise_for_status()

            data = response.json()
            if data["code"] == "200":
                return [{
                    "date": day["fxDate"],
                    "tempMax": day["tempMax"],
                    "tempMin": day["tempMin"],
                    "textDay": day["textDay"],
                    "textNight": day["textNight"],
                    "uvIndex": day["uvIndex"],
                    "windDirDay": day["windDirDay"],
                    "windScaleDay": day["windScaleDay"],
                    "humidity": day["humidity"]
                } for day in data["daily"]]
            return None

    def is_tool_available(self) -> bool:
        return self.status

    def get_tool(self) -> BaseTool:
        class WeatherInput(BaseModel):
            location: str = Field(
                description="城市名称，例如'北京'、'上海'、'成都'等",
                default="北京"
            )

        @tool(
            "get_weather",
            args_schema=WeatherInput,
        )
        def get_weather(location: str, state: Annotated[CustomState, InjectedState]) -> str:
            """获取指定位置的天气信息。

            Args:
                location: 城市名称，如"北京"、"成都"等

            Returns:
                str: 天气信息
            """
            state["has_tool_call"] = True
            return get_city_weather(location)

        return get_weather



# 创建全局服务实例
weather_service = WeatherToolProvider()

# 天气工具存在的问题是ai会回复历史问题
def get_city_weather(city_name: str) -> str:
    """获取城市天气信息

    Args:
        city_name: 城市名称

    Returns:
        str: 格式化的天气信息字符串
    """
    location_id = weather_service.get_location_id(city_name)
    if not location_id:
        logger.error(f"未找到城市: {city_name}")
        return f"未找到城市: {city_name}"

    weather_info = weather_service.get_weather(location_id)
    if not weather_info:
        logger.error(f"获取天气信息失败: {city_name}")
        return f"获取天气信息失败: {city_name}"

    # 格式化当前天气
    try:
        current = weather_info["current"]
        result = [
            f"{city_name} 实时天气: {current['text']}, "
            f"温度{current['temp']}℃, "
            f"体感温度{current['feelsLike']}℃, "
            f"湿度{current['humidity']}%, "
            f"{current['windDir']}{current['windScale']}级"
        ]

        # 添加未来天气预报
        result.append("\n未来天气预报:")
        for day in weather_info["daily"][1:]:
            result.append(
                f"{day['date']}: {day['textDay']}转{day['textNight']}, "
                f"气温{day['tempMin']}-{day['tempMax']}℃, "
                f"湿度{day['humidity']}%, "
                f"紫外线强度{day.get('uvIndex', '未知')}, "
                f"{day['windDirDay']}{day['windScaleDay']}级"
            )
    except Exception as e:
        logger.error(f"格式化天气信息失败: {str(e)}")

    return "".join(result)
