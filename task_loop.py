from queue import Queue

from logger import logger
from sio import sio
from openai_client import client
from util import get_now_str
from flag import mark_session_idle

task_queue = Queue()


class Task:
    def __init__(self, run, session, offset):
        self.run = run
        self.session = session
        self.offset = offset


def task_loop():
    logger.info("task_queue_loop started")
    while True:
        task = task_queue.get()
        run = client.beta.threads.runs.retrieve(
            thread_id=task.session.thread_id, run_id=task.run.id)
        if run.status == "queued" or run.status == "in_progress":
            task_queue.put(task)
        else:
            response_messages = client.beta.threads.messages.list(
                thread_id=task.session.thread_id, order="asc", after=task.offset
            )
            sio.emit("stopTyping", task.session.session_id, callback=lambda _: None)

            def handle_callback(res):
                if res["type"] == "SUCCESS":
                    logger.info("回复成功")
                else:
                    logger.error("回复失败")
            for message in response_messages:
                sio.emit(
                    "privateMessage",
                    {
                        "type": "text",
                        "recipientId": task.session.peer_id,
                        "content": message.content[0].text.value,
                        "timestamp": get_now_str(),
                    },
                    callback=handle_callback,
                )
            mark_session_idle(task.session.session_id)


def add_task(task):
    task_queue.put(task)
