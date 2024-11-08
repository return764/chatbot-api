import asyncio
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from typing import Optional, List
from pydantic import BaseModel, Field
from langgraph.prebuilt import create_react_agent

from service import get_city_weather

# 定义工具的参数模式
class WeatherInput(BaseModel):
    location: str = Field(
        description="城市名称，例如'北京'、'上海'、'成都'等",
        default="北京"
    )

class TimeInput(BaseModel):
    pass

class AIHandler:
    def __init__(self):
        self.tools = self._setup_tools()
        self.llm = ChatOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            model="qwen2.5:7b",
            temperature=0
        )

        self.agent_executor = create_react_agent(
            self.llm, 
            self.tools,
            state_modifier="你是一个AI助手,使用简单,清晰的方式回答用户的问题。"
        )
    
    def _setup_tools(self) -> List[StructuredTool]:
        """设置可用的工具"""
        @tool(
            "get_weather",
            args_schema=WeatherInput,
        )
        def get_weather(location: str) -> str:
            """获取指定位置的天气信息。"""
            return get_city_weather(location)
        
        @tool(
            "get_time",
            args_schema=TimeInput
        )
        def get_time() -> str:
            """获取当前时间"""
            from datetime import datetime
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return [
            get_weather,
            get_time,
        ]
    
    def get_response(self, message: str) -> Optional[str]:
        """获取AI响应"""
        try:
            response = self.agent_executor.invoke({"messages": [HumanMessage(content=message)]})
            return response["messages"][-1].content
        except Exception as e:
            print(f"AI处理出错: {e}")
            raise e;

# 全局实例
ai_handler: AIHandler = None

def setup_ai_handler():
    """初始化AI处理器"""
    global ai_handler
    ai_handler = AIHandler()

if __name__ == '__main__':
    setup_ai_handler()
    print(f"回答：{ai_handler.get_response("成都和武汉的天气如何")}")


    