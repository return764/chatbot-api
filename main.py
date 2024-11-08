from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from ai_handler import ai_handler, setup_ai_handler
from model import (
    BasicMessage, 
    GroupMessage, 
    PrivateMessage, 
    RequestReport, 
    NoticeReport, 
    MetaEventReport
)
from handler import (
    handle_private_message,
    handle_group_message,
    handle_request,
    handle_notice,
    handle_meta_event
)
import logging


logger = logging.getLogger("uvicorn")
setup_ai_handler()

app = FastAPI()

@app.get("/")
async def root():
    return await ai_handler.get_response("成都的天气怎么样?")

@app.post("/onebot")
async def onebotapi(request: Request):
    data = await request.body()  # 获取事件数据
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
    import uvicorn
    from logger import LOGGING_CONFIG
    
    uvicorn.run(
        "main:app", 
        host="192.168.2.7", 
        port=5140,
        reload=True,
        log_config=LOGGING_CONFIG
    )

