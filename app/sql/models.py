from datetime import datetime
from sqlmodel import SQLModel, Field
from enum import Enum
from app.sql.client import db_client

class MessageRole(str, Enum):
    """消息角色"""
    AI = "ai"
    HUMAN = "human"

class ChatHistory(SQLModel, table=True):
    """聊天历史记录表"""
    __tablename__ = 'chat_history'
    
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now, nullable=False)
    content: str = Field(nullable=False)
    user_id: int = Field(nullable=False, index=True)
    group_id: int = Field(nullable=True, index=True)
    role: MessageRole = Field(nullable=False, default=MessageRole.HUMAN)
    
    def __repr__(self):
        return f"<ChatHistory(id={self.id}, user_id={self.user_id}, group_id={self.group_id}, role={self.role})>"

db_client.create_db_and_tables()