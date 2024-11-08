from model import MessageReport, MessageData
from typing import List
from pydantic import BaseModel

class FormattedMessage(BaseModel):
    """格式化后的消息"""
    content: str  # 文本内容
    at_list: List[int]  # @的用户列表
    raw: MessageReport  # 原始消息对象

def format_message(message: MessageReport) -> FormattedMessage:
    """格式化消息为结构化数据"""
    text_parts = []
    at_list = []
    
    for msg in message.message:
        match msg.type:
            case "text":
                text = msg.data.get("text", "")
                text_parts.append(text)
            case "at":
                qq = msg.data.get("qq", "")
                try:
                    at_list.append(int(qq))
                except (ValueError, TypeError):
                    pass
    
    return FormattedMessage(
        content="".join(text_parts).strip(),
        at_list=at_list,
        raw=message
    ) 