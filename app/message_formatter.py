from typing import List
from app.model import MessageReport, PrivateMessage
from app.config import config

class FormattedMessage:
    """格式化后的消息"""
    def __init__(self, raw_message: MessageReport):
        self.raw = raw_message
        self.content = self._extract_content()
        self.at_list = self._extract_at_list()
    
    def _extract_content(self) -> str:
        """提取纯文本内容"""
        text_segments = []
        for segment in self.raw.message:
            if segment.type == "text":
                text_segments.append(segment.data["text"].strip())
        return " ".join(text_segments).strip()
    
    def _extract_at_list(self) -> List[int]:
        """提取@列表"""
        at_list = []
        for segment in self.raw.message:
            if segment.type == "at":
                at_list.append(int(segment.data["qq"]))
        return at_list
    
    def is_private(self) -> bool:
        """是否是私聊消息"""
        return isinstance(self.raw, PrivateMessage)
    
    def is_command(self) -> bool:
        """是否是指令消息"""
        return self.content.startswith(config.command_prefix)
    
    def is_user_allowed(self) -> bool:
        """检查用户是否有权限使用机器人"""
        # 如果是私聊，只检查是否在允许列表中
        if self.is_private():
            return self.raw.sender.user_id in config.allowed_users
            
        # 如果是群聊
        group_config = config.groups.get(self.raw.group_id)
        if group_config:
            # 首先检查是否在群组黑名单中
            if self.raw.sender.user_id in group_config.black_list:
                return False
                
            # 如果是指令，跳过白名单检查
            if self.is_command():
                return True
                
            # 如果群组的允许用户列表为空，表示允许所有非黑名单用户
            if not group_config.allowed_users:
                return True
            # 否则检查用户是否在群组的允许列表中
            return self.raw.sender.user_id in group_config.allowed_users
        
        return False
    
    def should_reply(self) -> bool:
        """检查是否需要回复此消息"""
        # 首先检查用户权限
        if not self.is_user_allowed():
            return False
            
        # 如果是私聊，直接返回True
        if self.is_private():
            return True
            
        # 如果是指令，直接返回True
        if self.is_command():
            return True
            
        # 检查群组配置
        group_config = config.groups.get(self.raw.group_id)
        if group_config and group_config.at_only:
            # 需要@且机器人在@列表中
            return config.bot_id in self.at_list
            
        return True

def format_message(message: MessageReport) -> FormattedMessage:
    """格式化消息"""
    return FormattedMessage(message) 