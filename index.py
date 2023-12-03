import os
import time
import socketio

from config import config
from logger import logger
from util import login, fetch_history_messages
from generate import generate_response
from users import user_factory


user_class = os.getenv("USER_CLASS", "Athena")
user = user_factory(user_class)

token = None
while not token:
    token = login(user.username, user.password)
    if not token:
        time.sleep(5)

sio = socketio.Client()


@sio.event
def connect():
    logger.info(f"{user.username} 成功上线")


@sio.on("privateMessage")
def deal_message(payload):
    """
    收到用户的消息，获取历史消息，返回响应
    """
    session_id = payload["sessionId"]
    message = payload["message"]
    if message["type"] == "text":
        history = fetch_history_messages(session_id, token)
        history = list(filter(lambda x: x["type"] == "text", history))  # 只保留文本消息
        context = []
        for history_msg in history:
            from_user = history_msg["senderId"] == message["senderId"]
            context.append(
                {
                    "role": "user" if from_user else "assistant",
                    "content": history_msg["content"],
                }
            )
        sio.emit("startTyping", session_id, callback=lambda _: None)
        response = generate_response(user, context)  # 生成响应内容
        sio.emit("stopTyping", session_id, callback=lambda _: None)

        def handle_callback(res):
            if res["type"] == "SUCCESS":
                logger.info("回复成功")
            else:
                logger.error("回复失败")

        sio.emit(
            "privateMessage",
            {"type": "text", "recipientId": message["senderId"], "content": response},
            callback=handle_callback,
        )


@sio.event
def disconnect():
    logger.info(f"{user.username} 下线")


sio.connect(config.chat_server, auth={"token": token})
sio.wait()
