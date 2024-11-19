from typing import List
import httpx
import logging

logger = logging.getLogger("uvicorn")

class BotClient:
    """Bot HTTP客户端"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not BotClient._initialized:
            self.client = httpx.AsyncClient(
                base_url="http://192.168.2.53:3000",
                timeout=30.0
            )
            BotClient._initialized = True
    
    async def send_group_message(self, group_id: int, message: str, at_list: List[int] = []) -> bool:
        """发送群消息
        
        Args:
            group_id: 群号
            message: 消息内容
            at_list: at数组
            
        Returns:
            bool: 是否发送成功
        """
        try:
            
            at_segments = [
                {
                    "type": "at",
                    "data": {
                        "qq": at_id
                    }
                }
                for at_id in at_list
            ]
            
            response = await self.client.post("/send_group_msg", json={
                "group_id": group_id,
                "message": [
                    *at_segments,
                    {
                        "type": "text",
                        "data": {
                            "text": message
                        }
                    }
                ]
            })
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "ok":
                return True
                
            logger.error(f"发送群消息失败: {data}")
            return False
            
        except Exception as e:
            logger.error(f"发送群消息出错: {str(e)}")
            return False
    
    @classmethod
    def get_instance(cls) -> 'BotClient':
        """获取BotClient实例"""
        if cls._instance is None:
            cls._instance = BotClient()
        return cls._instance
    
    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()

# 创建全局实例
bot_client = BotClient.get_instance()