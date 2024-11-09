from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import Optional
from langgraph.prebuilt import create_react_agent
from tools import get_tools

class AIHandler:
    def __init__(self):
        self.tools = get_tools()
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
    
    def get_response(self, message: str) -> Optional[str]:
        """获取AI响应"""
        try:
            response = self.agent_executor.invoke({"messages": [HumanMessage(content=message)]})
            return response["messages"][-1].content
        except Exception as e:
            print(f"AI处理出错: {e}")
            raise e

# 全局实例
ai_handler: AIHandler = None

def setup_ai_handler():
    """初始化AI处理器"""
    global ai_handler
    ai_handler = AIHandler()

if __name__ == '__main__':
    setup_ai_handler()
    print(f"回答：{ai_handler.get_response('成都和武汉的天气如何')}")


    