from ai_handler import AIHandler

# 全局实例
ai_handler: AIHandler = None

def setup_ai_handler():
    """初始化AI处理器"""
    global ai_handler
    ai_handler = AIHandler()