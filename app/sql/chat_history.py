from app.sql.client import db_client
from app.sql.models import ChatHistory, MessageRole
from typing import Optional, List
from datetime import datetime
from sqlmodel import select

def add_chat_history(
    content: str,
    user_id: int,
    role: MessageRole = MessageRole.HUMAN,
    group_id: Optional[int] = None
) -> ChatHistory:
    """添加聊天记录
    
    Args:
        content: 聊天内容
        user_id: 用户ID
        role: 消息角色(ai/human)
        group_id: 群组ID,私聊为None
        
    Returns:
        ChatHistory: 创建的聊天记录
    """
    with db_client.get_session() as session:
        chat_history = ChatHistory(
            content=content,
            user_id=user_id,
            group_id=group_id,
            role=role,
            created_at=datetime.now()
        )
        session.add(chat_history)
        session.commit()
        return chat_history

def get_user_history(
    user_id: int,
    group_id: Optional[int] = None,
    limit: int = 10,
    role: Optional[MessageRole] = None
) -> List[ChatHistory]:
    """获取用户的聊天历史
    
    Args:
        user_id: 用户ID
        group_id: 群组ID,私聊为None
        limit: 返回的记录数量
        role: 筛选特定角色的消息
        
    Returns:
        List[ChatHistory]: 聊天记录列表
    """
    with db_client.get_session() as session:
        query = select(ChatHistory).where(
            ChatHistory.user_id == user_id,
            ChatHistory.group_id == group_id
        )
        
        if role:
            query = query.where(ChatHistory.role == role)
            
        query = query.order_by(ChatHistory.created_at.desc()).limit(limit)
        
        result = session.exec(query)
        return result.all()

def get_group_history(
    group_id: int,
    limit: int = 10,
    role: Optional[MessageRole] = None
) -> List[ChatHistory]:
    """获取群组的聊天历史
    
    Args:
        group_id: 群组ID
        limit: 返回的记录数量
        role: 筛选特定角色的消息
        
    Returns:
        List[ChatHistory]: 聊天记录列表
    """
    with db_client.get_session() as session:
        query = select(ChatHistory).where(
            ChatHistory.group_id == group_id
        )
        
        if role:
            query = query.where(ChatHistory.role == role)
            
        query = query.order_by(ChatHistory.created_at.desc()).limit(limit)
        
        result = session.exec(query)
        return result.all() 