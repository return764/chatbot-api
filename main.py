import uvicorn
from app.logger import LOGGING_CONFIG
from app.bot_client import bot_client
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from app.model import (
    BasicMessage, 
    GroupMessage, 
    PrivateMessage, 
    RequestReport, 
    NoticeReport, 
    MetaEventReport
)
from app.handler import (
    handle_private_message,
    handle_group_message,
    handle_request,
    handle_notice,
    handle_meta_event
)
import logging
from app.ai.tools.timer_tool_provider import timer_service
from app.sql.client import db_client

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    timer_service.start()
    yield
    timer_service.shutdown()
    await bot_client.close()
    db_client.close()

app = FastAPI(lifespan=lifespan)

@app.post("/onebot")
async def onebotapi(request: Request):
    data = await request.body()
    message = BasicMessage.model_validate_json(data)
    match message:
        case GroupMessage() as group_message:
            await handle_group_message(group_message)
        case PrivateMessage() as private_message:
            await handle_private_message(private_message)
        case RequestReport() as request_report:
            handle_request(request_report)
        case NoticeReport() as notice_report:
            handle_notice(notice_report)
        case MetaEventReport() as meta_event_report:
            handle_meta_event(meta_event_report)
        case _:
            logger.warning(f"未知事件类型: {message}")
    return {}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=5140,
        reload=False,
        log_config=LOGGING_CONFIG
    )
