from pydantic_settings import BaseSettings
import tomli
import os

class Settings(BaseSettings):
    # OpenAI 配置
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    
    # 和风天气配置
    qweather_key: str
    
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
    
    return Settings(**config_dict)

config = load_config()