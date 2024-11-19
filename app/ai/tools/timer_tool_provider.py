import asyncio
import logging
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from app.ai.tools.abc import ToolServiceProvider
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from app.bot_client import bot_client
from app.sql.client import db_client

logger = logging.getLogger("uvicorn")

async def send_reminder(group_id: int, user_id: int, message: str):
    try:
        logger.info(f"发送提醒{group_id} {message}")
        await bot_client.send_group_message(
            group_id=group_id,
            message=f"⏰ 定时提醒：{message}",
            at_list=[user_id]
        )
    except Exception as e:
        logger.error(f"发送定时提醒失败: {str(e)}")

class TimerToolProvider(ToolServiceProvider):
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not TimerToolProvider._initialized:
            # 配置调度器
            jobstores = {
                'default': SQLAlchemyJobStore(url=db_client.url)
            }
            
            self.scheduler = AsyncIOScheduler(
                jobstores=jobstores,
                timezone='Asia/Shanghai'
            )
            self.status = True
            TimerToolProvider._initialized = True

    def is_tool_available(self) -> bool:
        return self.status

    def get_tool(self) -> BaseTool:
        class TimerInput(BaseModel):
            remind_time: datetime = Field(
                description="发送消息的日期时间"
            )
            message: str = Field(
                description="定时提醒的消息内容"
            )

        @tool(
            "set_timer",
            args_schema=TimerInput,
        )
        def set_timer(remind_time: datetime, message: str, config: RunnableConfig) -> str:
            """当用户的输入中包含提醒、叫我、记得等字样时，设置一个定时提醒，可以在指定的时间发送提醒消息"""
            group_id = config["configurable"].get("group_id")
            user_id = config["configurable"].get("user_id")
            try:
                # 添加定时任务
                job = self.scheduler.add_job(
                    send_reminder,
                    'date',
                    run_date=remind_time,
                    args=[group_id, user_id, message],
                    id=f"timer_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}",
                    replace_existing=True
                )
                
                # 格式化时间
                time_str = remind_time.strftime("%Y-%m-%d %H:%M:%S")
                return f"已设置定时提醒：将在 {time_str} 提醒：{message}"
                
            except Exception as e:
                logger.error(f"设置定时器失败: {str(e)}")
                return f"设置定时器失败: {str(e)}"

        return set_timer
    
    def start(self):
        if not self.scheduler.running:
            logger.info(f"定时任务调度器启动")
            self.scheduler.start()

    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            logger.info(f"定时任务调度器关闭")
            self.scheduler.shutdown()

# 创建全局服务实例
timer_service = TimerToolProvider() 