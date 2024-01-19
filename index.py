import os
import time
import socketio
import threading

from config import config
from logger import logger
from network import login, fetch_history_messages
from util import get_now_str
from generate import generate_response
from users import user_factory


user_class = os.getenv("USER_CLASS", "Athena")
user = user_factory(user_class)

token = None
# while not token:
#     token = login(user.username, user.password)
#     if not token:
#         time.sleep(5)

def refresh_token():
    logger.info("Refreshing token")
    global token
    while not token:
        token = login(user.username, user.password)
        time.sleep(1)
    logger.info("Token refreshed", token)


def scheduler():
    time.sleep(60 * 60)
    refresh_token()


refresh_token()
threading.Thread(target=scheduler, daemon=True).start()

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
    # if message["type"] == "text":  # 只处理文本消息
    history = fetch_history_messages(session_id, token)
    # history = list(filter(lambda x: x["type"] == "text", history))  # 只保留文本消息
    history = history[-10:]  # 只保留最近的10条消息，节省花费，同时避免token数量超限
    context = []
    for history_msg in history:
        from_user = history_msg["senderId"] == message["senderId"]
        if history_msg["type"] == "text":
            context.append(
                {
                    "role": "user" if from_user else "assistant",
                    "content": history_msg["content"],
                }
            )
        elif history_msg["type"] == "image":
            context.append(
                {
                    "role": "user" if from_user else "assistant",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": history_msg["content"],
                            },
                        }
                    ],
                }
            )
    sio.emit("startTyping", session_id, callback=lambda _: None)
    response = generate_response(user, context)  # 生成响应内容

    def handle_callback(res):
        if res["type"] == "SUCCESS":
            logger.info("回复成功")
        else:
            logger.error("回复失败")

    history = fetch_history_messages(session_id, token)
    if history[-1]["_id"] == message["_id"]:  # 在发送回复之前再看一眼聊天记录，如果用户有新的输入，则不进行回复
        sio.emit("stopTyping", session_id, callback=lambda _: None)
        sio.emit(
            "privateMessage",
            {
                "type": "text",
                "recipientId": message["senderId"],
                "content": response,
                "timestamp": get_now_str(),
            },
            callback=handle_callback,
        )


@sio.event
def disconnect():
    logger.info(f"{user.username} 下线")


sio.connect(config.chat_server, auth={"token": token})
sio.wait()
