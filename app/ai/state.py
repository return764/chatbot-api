from langgraph.prebuilt.chat_agent_executor import AgentState

class CustomState(AgentState):
    today: str
    has_tool_call: bool
    summary: str