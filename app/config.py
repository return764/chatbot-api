from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import List, Dict
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
    
    # 指令配置
    command_prefix: str = "/"  # 指令前缀
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

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