import httpx
from typing import Optional, Dict
import logging
from config import config

logger = logging.getLogger("uvicorn")

class WeatherService:
    def __init__(self):
        self.key = config.qweather_key
        if not self.key:
            raise ValueError("未配置和风天气API密钥")

    def get_location_id(self, city_name: str) -> Optional[str]:
        """通过城市名称获取位置ID
        
        Args:
            city_name: 城市名称，如"北京"、"成都"
            
        Returns:
            location_id: 城市ID，如果未找到返回None
        """
        try:
            with httpx.Client(base_url="https://geoapi.qweather.com/v2", timeout=10.0) as client:
                params = {
                    "location": city_name,
                    "key": self.key,
                    "number": 1  # 只返回最匹配的一个结果
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
        """通过位置ID获取实时天气
        
        Args:
            location_id: 城市ID
            
        Returns:
            weather_info: 天气信息字典，包含温度、天气状况等
        """
        try:
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
                        "windScale": data["now"]["windScale"]
                    }
                return None
                
        except Exception as e:
            logger.error(f"获取天气信息失败: {str(e)}")
            return None

# 创建全局服务实例
weather_service = WeatherService()

def get_city_weather(city_name: str) -> str:
    """获取城市天气信息的便捷方法
    
    Args:
        city_name: 城市名称
        
    Returns:
        weather_info: 格式化的天气信息字符串
    """
    location_id = weather_service.get_location_id(city_name)
    if not location_id:
        return f"未找到城市: {city_name}"
        
    weather_info = weather_service.get_weather(location_id)
    if not weather_info:
        return f"获取天气信息失败: {city_name}"
        
    return (
        f"{city_name}天气: {weather_info['text']}, "
        f"温度{weather_info['temp']}℃, "
        f"体感温度{weather_info['feelsLike']}℃, "
        f"湿度{weather_info['humidity']}%, "
        f"{weather_info['windDir']}{weather_info['windScale']}级"
    ) 