from fastapi import FastAPI, Request
from app.ai_handler import AIHandler
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


logger = logging.getLogger("uvicorn")
app = FastAPI()


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
    from app.logger import LOGGING_CONFIG
    
    uvicorn.run(
        "main:app", 
        host="192.168.2.7", 
        port=5140,
        reload=True,
        log_config=LOGGING_CONFIG
    )


