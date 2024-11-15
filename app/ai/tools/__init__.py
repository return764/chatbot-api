from typing import List
import inspect
import importlib
import pkgutil
from langchain.tools import BaseTool
from app.ai.tools.abc import ToolServiceProvider

def get_tools() -> List[BaseTool]:

    tools = []
    
    # 获取所有 service 目录下的模块
    service_package = importlib.import_module("app.ai.tools")
    for _, module_name, _ in pkgutil.iter_modules(service_package.__path__):
        # 导入模块
        module = importlib.import_module(f"app.ai.tools.{module_name}")
        
        # 遍历模块中的所有类
        for name, obj in inspect.getmembers(module):
            # 检查是否是 ToolServiceProvider 的子类（排除基类本身）
            if (inspect.isclass(obj) and 
                issubclass(obj, ToolServiceProvider) and 
                obj != ToolServiceProvider):
                
                # 获取类的实例（假设使用了单例模式）
                if hasattr(module, name.lower()):
                    instance = getattr(module, name.lower())
                else:
                    instance = obj()
                
                # 检查服务是否可用
                if instance.is_tool_available():
                    # 获取工具并添加到列表
                    tool = instance.get_tool()
                    if tool:
                        tools.append(tool)
    
    return tools
