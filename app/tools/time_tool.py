from langchain_core.tools import tool
from pydantic import BaseModel
from datetime import datetime

class TimeInput(BaseModel):
    pass

@tool(
    "get_time",
    args_schema=TimeInput
)
def get_time() -> str:
    """获取当前时间。
    
    Returns:
        str: 当前时间的字符串表示
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 