import logging
from model import GroupMessage, MetaEventReport, NoticeReport, PrivateMessage, RequestReport
from config import config
from message_formatter import format_message
from ai_handler import ai_handler

logger = logging.getLogger("uvicorn")

async def handle_private_message(message: PrivateMessage) -> None:
    """处理私聊消息"""
    if message.sender.user_id in config.target_users:
        formatted = format_message(message)
        logger.info(f"收到私聊消息: {formatted.raw.raw_message} (纯文本: {formatted.content}, @: {formatted.at_list})")
        
        # 获取AI响应
        response = await ai_handler.get_response(formatted.content)
        if response:
            logger.info(f"AI响应: {response}")

async def handle_group_message(message: GroupMessage) -> None:
    """处理群聊消息"""
    if message.sender.user_id in config.target_users:
        formatted = format_message(message)
        logger.info(f"收到群聊消息 [群:{message.group_id}]: {formatted.raw.raw_message} (纯文本: {formatted.content}, @: {formatted.at_list})")
        
        # 获取AI响应
        response = await ai_handler.get_response(formatted.content)
        if response:
            logger.info(f"AI响应: {response}")

def handle_request(message: RequestReport) -> None:
    """处理请求事件"""
    logger.info(f"收到请求事件: {message}")

def handle_notice(message: NoticeReport) -> None:
    """处理通知事件"""
    logger.info(f"收到通知事件: {message}")

def handle_meta_event(message: MetaEventReport) -> None:
    """处理元事件"""
    logger.info(f"收到元事件: {message}") 