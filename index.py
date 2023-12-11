import time

from sio import sio
from config import config
from logger import logger
from agent import agent
from openai_client import client

thread_store = {}
thread_lock = {}


@sio.event
def connect():
    logger.info(f"{agent.username} 成功上线")


@sio.on("privateMessage")
def deal_message(payload):
    session_id = payload["sessionId"]
    message = payload["message"]
    if message["type"] == "text":  # 只处理文本消息
        thread_id = thread_store.get(session_id, None)
        if thread_id is None:
            thread_id = client.beta.threads.create().id
            thread_store[session_id] = thread_id
        while thread_lock.get(thread_id, False):
            time.sleep(1)
        thread_lock[thread_id] = True
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
        while run.status == "queued" or run.status == "in_progress":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )
            time.sleep(1)
        response_messages = client.beta.threads.messages.list(
            thread_id=thread_id, order="asc", after=trigger_message.id
        )
        logger.info(response_messages)
        sio.emit("stopTyping", session_id, callback=lambda _: None)

        def callback(res):
            if res["type"] == "SUCCESS":
                logger.info("回复成功")
            else:
                logger.error("回复失败")
        for response_message in response_messages:
            if response_message.role == "assistant":
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
        thread_lock[thread_id] = False


@sio.event
def disconnect():
    logger.info(f"{agent.username} 下线")


sio.connect(config.chat_server, auth={"token": agent.token})
sio.wait()
