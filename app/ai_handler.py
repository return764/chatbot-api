from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from app.tools import get_tools
from app.config import config

def create_chat_model() -> ChatOpenAI:
    """创建 ChatOpenAI 实例"""
    return ChatOpenAI(
        base_url=config.openai_base_url,
        api_key=config.openai_api_key,
        model=config.openai_model,
        temperature=0
    )

class AIHandler:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 确保初始化代码只运行一次
        if not AIHandler._initialized:
            self.tools = get_tools()
            self.llm = create_chat_model()
            
            self.agent_executor = create_react_agent(
                self.llm, 
                self.tools,
                state_modifier="你是一个AI助手,使用简单,清晰的方式回答用户的问题。"
            )
            AIHandler._initialized = True
    
    def get_response(self, message: str) -> Optional[str]:
        """获取AI响应"""
        try:
            response = self.agent_executor.invoke({"messages": [HumanMessage(content=message)]})
            return response["messages"][-1].content
        except Exception as e:
            print(f"AI处理出错: {e}")
            raise e
    
    @classmethod
    def get_instance(cls) -> 'AIHandler':
        """获取AIHandler实例"""
        if cls._instance is None:
            cls._instance = AIHandler()
        return cls._instance
