from datetime import datetime
import logging
from typing import Literal, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, SystemMessage, ToolMessage, filter_messages
from app.ai.state import CustomState
from app.message_formatter import FormattedMessage
from app.model import GroupMessage
from app.ai.tools import get_tools
from app.config import config
from langgraph.graph import StateGraph, END
from langgraph.store.base import BaseStore
from langgraph.prebuilt.tool_node import ToolNode
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver
from app.sql.client import db_client

logger = logging.getLogger("uvicorn")

def create_chat_model() -> ChatOpenAI:
    """创建 ChatOpenAI 实例"""
    return ChatOpenAI(
        base_url=config.openai_base_url,
        api_key=config.openai_api_key,
        model=config.openai_model,
        temperature=0.7
    )

class CustomStore(BaseStore):
    pass


def prepare_model_inputs(state: CustomState, config: RunnableConfig):
    return [{"role": "system", "content": f"""
             你是一个AI助手,
             使用简短的结果回复,
             禁止回复无关问题,
             禁止使用markdown格式,
             请全程使用中文。
             以下是你能利用的系统信息
             当前时间：{state['today']}
             """}] + state["messages"]


def create_agent(checkpointer: SqliteSaver): 
    llm = create_chat_model()
    tools = get_tools();
    bound_model = llm.bind_tools(tools)

    model_runnable = prepare_model_inputs | bound_model

    def call_model(state: CustomState, config: RunnableConfig) -> CustomState: 
        summary = state.get("summary", "")
        if summary:
            system_message = f"以前对话的总结: {summary}"
            state["messages"] = [SystemMessage(content=system_message)] + state["messages"]
        response = model_runnable.invoke(state, config)
        return {"messages": [response]}
    
    def summarize_conversation(state: CustomState):
        summary = state.get("summary", "")
        if summary:
            summary_message = (
                f"这是迄今为止的对话总结: {summary}\n\n"
                "通过简短的方式使用新消息来扩展总结,禁止使用问候语:"
            )
        else:
            summary_message = "使用简短的方式总结以上对话,禁止使用问候语:"

        filtered_message = filter_messages(state['messages'], exclude_types=[ToolMessage])

        messages = filtered_message + [HumanMessage(content=summary_message)]
        response = llm.invoke(messages)
        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
        return {"summary": response.content, "messages": delete_messages}


    def should_continue(state: CustomState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]

        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            if len(messages) > 6:
                return "summarize"
            return "__end__"
        else:
            return "tools"

    tool_nodes = ToolNode(tools)
    workflow = StateGraph(CustomState)
    workflow.set_entry_point("agent")
    workflow.add_node("agent", call_model)
    workflow.add_node("summarize", summarize_conversation)
    workflow.add_node("tools", tool_nodes)
    workflow.add_edge("tools", "agent")
    workflow.add_conditional_edges("agent", should_continue, ['summarize', 'tools', END])
    workflow.set_finish_point('summarize')
    return workflow.compile(
        debug=True,
        checkpointer=checkpointer
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
            checkpointer = SqliteSaver(db_client.get_conn())
            self.agent_executor = create_agent(checkpointer)
            AIHandler._initialized = True
    
    def get_response(self, message: FormattedMessage) -> Optional[str]:
        """获取AI响应"""
        try:
            thread_id = str(message.raw.user_id) + ('-' + str(message.raw.group_id)) if isinstance(message.raw, GroupMessage) else ''

            response = self.agent_executor.invoke(
                input={"messages": [HumanMessage(content=message.content)], "today": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                config={"configurable": {"thread_id": thread_id}}
            )
            return response["messages"][-1].content
        except Exception as e:
            logger.info(f"AI处理出错: {e}")
            raise e
    
    @classmethod
    def get_instance(cls) -> 'AIHandler':
        """获取AIHandler实例"""
        if cls._instance is None:
            cls._instance = AIHandler()
        return cls._instance
