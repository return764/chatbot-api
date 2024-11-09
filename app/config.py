from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import List, Optional, Dict
import tomli
import os

class GroupConfig(BaseModel):
    """群组配置"""
    id: int
    at_only: bool = True
    allowed_users: List[int] = []
    black_list: List[int] = []  # 群组黑名单列表

class Settings(BaseSettings):
    # OpenAI 配置
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    
    # 和风天气配置
    qweather_key: str
    
    # 用户配置
    bot_id: int
    allowed_users: List[int] = []  # 允许私聊的用户列表
    
    # 群组配置
    groups: Dict[int, GroupConfig] = {}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def is_user_allowed(self, user_id: int, group_id: Optional[int] = None) -> bool:
        """检查用户是否有权限使用机器人
        
        Args:
            user_id: 用户ID
            group_id: 群组ID,如果是私聊则为None
            
        Returns:
            bool: 是否允许使用
        """
        # 如果是私聊，只检查是否在允许列表中
        if group_id is None:
            return user_id in self.allowed_users
            
        # 如果是群聊
        group_config = self.groups.get(group_id)
        if group_config:
            # 首先检查是否在群组黑名单中
            if user_id in group_config.black_list:
                return False
                
            # 如果群组的允许用户列表为空，表示允许所有非黑名单用户
            if not group_config.allowed_users:
                return True
            # 否则检查用户是否在群组的允许列表中
            return user_id in group_config.allowed_users
        
        return False
    
    def need_at(self, group_id: int) -> bool:
        """检查群组是否需要@才响应"""
        group_config = self.groups.get(group_id)
        return group_config.at_only if group_config else True

def load_config() -> Settings:
    config_dict = {}
    
    # 尝试读取 config.toml
    if os.path.exists("config.toml"):
        with open("config.toml", "rb") as f:
            toml_config = tomli.load(f)
            
            # OpenAI 配置
            if "openai" in toml_config:
                config_dict["openai_api_key"] = toml_config["openai"].get("api_key")
                config_dict["openai_base_url"] = toml_config["openai"].get("base_url")
                config_dict["openai_model"] = toml_config["openai"].get("model")
            
            # 和风天气配置
            if "api" in toml_config:
                config_dict["qweather_key"] = toml_config["api"].get("qweather_key")
            
            # 用户配置
            if "users" in toml_config:
                config_dict["bot_id"] = toml_config["users"].get("bot_id")
                config_dict["allowed_users"] = toml_config["users"].get("allowed_users", [])
            
            # 群组配置
            if "groups" in toml_config:
                groups_dict = {}
                for group in toml_config["groups"]:
                    group_id = group["id"]
                    groups_dict[group_id] = GroupConfig(
                        id=group_id,
                        at_only=group.get("at_only", True),
                        allowed_users=group.get("allowed_users", []),
                        black_list=group.get("black_list", [])
                    )
                config_dict["groups"] = groups_dict
    
    return Settings(**config_dict)

config = load_config()