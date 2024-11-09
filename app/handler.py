import logging
from app.bot_client import BotClient
from app.model import GroupMessage, MetaEventReport, NoticeReport, PrivateMessage, RequestReport
from app.config import config
from app.message_formatter import format_message
from app.ai_handler import AIHandler
from app.sql.chat_history import add_chat_history

logger = logging.getLogger("uvicorn")

async def handle_private_message(message: PrivateMessage) -> None:
    """处理私聊消息"""
    if config.is_user_allowed(message.sender.user_id):
        formatted = format_message(message)
        logger.info(f"收到私聊消息: {formatted.raw.raw_message} (纯文本: {formatted.content}, @: {formatted.at_list})")

        response = AIHandler.get_instance().get_response(formatted.content)
        if response:
            logger.info(f"AI响应: {response}")

async def handle_group_message(message: GroupMessage) -> None:
    """处理群聊消息"""
    if config.is_user_allowed(message.sender.user_id, message.group_id):
        formatted = format_message(message)
        logger.info(f"收到群聊消息 [群:{message.group_id}]: {formatted.raw.raw_message} (纯文本: {formatted.content}, @: {formatted.at_list})")
        
        if config.need_at(message.group_id) and config.bot_id not in formatted.at_list:
            return
        
        add_chat_history(formatted.content, message.sender.user_id, message.group_id)
        response = AIHandler.get_instance().get_response(formatted.content)
        if response:
            logger.info(f"AI响应: {response}")
            add_chat_history(response, message.sender.user_id, message.group_id)
            await BotClient.get_instance().send_group_message(message.group_id, response)


def handle_request(message: RequestReport) -> None:
    """处理请求事件"""
    logger.info(f"收到请求事件: {message}")

def handle_notice(message: NoticeReport) -> None:
    """处理通知事件"""
    logger.info(f"收到通知事件: {message}")

def handle_meta_event(message: MetaEventReport) -> None:
    """处理元事件"""
    logger.info(f"收到元事件: {message}") 