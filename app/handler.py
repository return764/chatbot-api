import logging
from app.bot_client import BotClient
from app.model import GroupMessage, MetaEventReport, NoticeReport, PrivateMessage, RequestReport
from app.config import config
from app.message_formatter import format_message
from app.ai.ai_handler import AIHandler
from app.sql.chat_history import add_chat_history
from app.sql.models import MessageRole

logger = logging.getLogger("uvicorn")
ai_handler = AIHandler.get_instance()

async def handle_private_message(message: PrivateMessage) -> None:
    formattedMessage = format_message(message)
    """处理私聊消息"""
    if not formattedMessage.should_reply():
        return

    logger.info(f"收到私聊消息: {formattedMessage.raw.raw_message} (纯文本: {formattedMessage.content}, @: {formattedMessage.at_list})")
    
    # 记录用户消息
    add_chat_history(
        content=formattedMessage.content,
        user_id=message.user_id,
        role=MessageRole.HUMAN
    )
    
    try:
        response = ai_handler.get_response(formattedMessage)
        if response:
            logger.info(f"AI响应: {response}")
            await BotClient.get_instance().send_private_message(message.user_id, response)
            # 记录AI响应
            add_chat_history(
                content=response,
                user_id=message.user_id,
                role=MessageRole.AI
            )
    except Exception as e:
        logger.error(f"处理私聊消息出错: {str(e)}")

async def handle_group_message(message: GroupMessage) -> None:
    """处理群聊消息"""
    formattedMessage = format_message(message)
    
    # 检查是否需要回复
    if not formattedMessage.should_reply():
        return
    
    # 记录用户消息
    add_chat_history(
        content=formattedMessage.content,
        user_id=message.user_id,
        group_id=message.group_id,
        role=MessageRole.HUMAN
    )
    
    # try:
        # 获取AI响应
    response = ai_handler.get_response(formattedMessage)
    if response:
        # 发送响应
        await BotClient.get_instance().send_group_message(message.group_id, response)
        # 记录AI响应
        add_chat_history(
            content=response,
            user_id=message.user_id,
            group_id=message.group_id,
            role=MessageRole.AI
        )
    # except Exception as e:
    #     logger.error(f"处理群消息出错: {str(e)}")


def handle_request(message: RequestReport) -> None:
    """处理请求事件"""
    logger.info(f"收到请求事件: {message}")

def handle_notice(message: NoticeReport) -> None:
    """处理通知事件"""
    logger.info(f"收到通知事件: {message}")

def handle_meta_event(message: MetaEventReport) -> None:
    """处理元事件"""
    logger.info(f"收到元事件: {message}") 