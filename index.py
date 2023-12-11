import threading

from sio import sio
from config import config
from logger import logger
from agent import agent
from openai_client import client
from thread_store import thread_store
from message_loop import receive_message, message_loop
from task_loop import task_loop
from network import fetch_sessions

lock = threading.Lock()


def init_sessions():
    # 初始化会话，回复下线期间用户发给agent的消息
    sessions = fetch_sessions(agent.token)
    for session in sessions:
        peer = session["peer"]
        messages = session["messages"]
        for message in reversed(messages):
            if message["senderId"] != peer["id"]:
                break
            thread_id = thread_store.get(session["id"])
            if thread_id is None:
                thread_id = client.beta.threads.create().id
                thread_store.set(session["id"], thread_id)
            receive_message(
                session["id"], thread_id, peer["id"], message)


@sio.event
def connect():
    logger.info(f"{agent.username} 成功上线")


@sio.on("privateMessage")
def deal_message(payload):
    session_id = payload["sessionId"]
    message = payload["message"]
    # 只处理文本消息 (Assistant API 目前不支持用户图片消息，未来可能会支持)
    if message["type"] == "text":
        # 获取thread_id (double-checked locking)
        thread_id = thread_store.get(session_id)
        if thread_id is None:
            with lock:
                thread_id = thread_store.get(session_id)
                if thread_id is None:
                    # 确保只有一个线程执行下面的代码
                    thread_id = client.beta.threads.create().id
                    thread_store.set(session_id, thread_id)
        receive_message(session_id, thread_id, message["senderId"], message)


@sio.event
def disconnect():
    logger.info(f"{agent.username} 下线")


init_sessions()
sio.connect(config.chat_server, auth={"token": agent.token})
threading.Thread(target=message_loop, daemon=True).start()
threading.Thread(target=task_loop, daemon=True).start()

sio.wait()
