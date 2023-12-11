from queue import Queue
import time

from user import user
from generate import client
from logger import logger
from sio import sio
from task_queue import Task, add_task

message_queue = Queue()
thread_store = {}  # 存储session_id和thread的对应关系，session_id为果壳之恋系统的会话标示，thread代表openai的会话


class Message:
    def __init__(self, session_id, content, sender_id):
        self.session_id = session_id
        self.content = content
        self.sender_id = sender_id


def message_queue_loop():
    logger.info("message_queue_loop start")
    while True:
        message: Message = message_queue.get()
        session_id = message.session_id
        thread = thread_store.get(session_id, None)
        if thread is None:
            thread = client.beta.threads.create()
            thread_store[session_id] = thread
        try:
            trigger_message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message.content,
            )
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=user.assistant.id,
            )
            sio.emit("startTyping", session_id, callback=lambda _: None)
            add_task(Task(run, thread, session_id,
                     trigger_message, message.sender_id))
        except Exception as e:
            # 此会话正在生成消息
            logger.error(e)
            message_queue.put(message)
            time.sleep(1)


def add_message(message):
    message_queue.put(message)
