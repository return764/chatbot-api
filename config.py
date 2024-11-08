import tomli
from typing import Set
from pathlib import Path

class Config:
    def __init__(self):
        self.target_users: Set[int] = set()
        self.qweather_key: str = ""
        self.load_config()
    
    def load_config(self) -> None:
        """加载TOML配置文件"""
        try:
            config_path = Path("config.toml")
            with open(config_path, "rb") as f:
                config = tomli.load(f)
                self.target_users = set(config.get("users", {}).get("target_users", [543851436]))
                self.qweather_key = config.get("api", {}).get("qweather_key", "")
        except FileNotFoundError:
            # 如果配置文件不存在，使用默认值
            self.target_users = {543851436}
            self.qweather_key = ""

# 创建全局配置实例
config = Config() 