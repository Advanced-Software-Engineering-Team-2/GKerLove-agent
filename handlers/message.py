from chatsocket import sio
from user import user, token
from logger import logger
from beans import MessagePayload

from network import fetch_history_messages
from helpers import get_now_str


def message(payload: MessagePayload):
    """
    收到用户的消息，获取历史消息，返回响应
    """
    session_id = payload["sessionId"]
    message = payload["message"]
    history = fetch_history_messages(session_id, token)
    # history = list(filter(lambda x: x["type"] == "text", history))  # 历史只保留文本消息
    sio.emit("startTyping", session_id, callback=lambda _: None)
    response = user.respond(message, history)

    def handle_callback(res):
        if res["type"] == "SUCCESS":
            logger.info("回复成功")
        else:
            logger.error("回复失败")

    # 在发送回复之前再看一眼聊天记录，如果用户有新的输入，则不进行回复
    history = fetch_history_messages(session_id, token)
    if history[-1]["_id"] == message["_id"]:
        sio.emit("stopTyping", session_id, callback=lambda _: None)
        sio.emit(
            "privateMessage",
            (
                session_id,
                {
                    "type": "text",
                    "recipientId": message["senderId"],
                    "content": response,
                    "timestamp": get_now_str(),
                },
            ),
            callback=handle_callback,
        )
