import threading
import time

from sio import sio
from config import config
from logger import logger
from agent import agent
from openai_client import client
from thread_store import thread_store

thread_lock = {}
lock = threading.Lock()


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

        while True:
            is_locked = thread_lock.get(thread_id, False)
            if not is_locked:
                with lock:
                    is_locked = thread_lock.get(thread_id, False)
                    if not is_locked:
                        thread_lock[thread_id] = True
                        break
            time.sleep(1)

        # 对同一个session，只允许一个线程执行下面的代码
        # 创建消息，并提交一个run
        trigger_message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message["content"],
        )
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=agent.assistant.id,
        )
        sio.emit("startTyping", session_id, callback=lambda _: None)
        # 阻塞线程，等待run执行完毕
        while run.status == "queued" or run.status == "in_progress":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )
            time.sleep(1)
        # run执行完毕，获取run的结果
        response_messages = client.beta.threads.messages.list(
            thread_id=thread_id, order="asc", after=trigger_message.id
        )
        sio.emit("stopTyping", session_id, callback=lambda _: None)

        def callback(res):
            if res["type"] == "SUCCESS":
                logger.info("回复成功")
            else:
                logger.error("回复失败")
        for response_message in response_messages:
            sio.emit(
                "privateMessage",
                {
                    "type": "text",
                    "recipientId": message["senderId"],
                    "content": response_message.content[0].text.value,
                    "timestamp": response_message.created_at,
                },
                callback=callback,
            )

        # 释放会话锁
        with lock:
            thread_lock[thread_id] = False


@sio.event
def disconnect():
    logger.info(f"{agent.username} 下线")


sio.connect(config.chat_server, auth={"token": agent.token})
sio.wait()
