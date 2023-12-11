from queue import Queue

from logger import logger
from sio import sio
from generate import client
from util import get_now_str

task_queue = Queue()


class Task:
    def __init__(self, run, thread, session_id, trigger_message, sender_id):
        self.run = run
        self.thread = thread
        self.session_id = session_id
        self.trigger_message = trigger_message
        self.sender_id = sender_id


def task_queue_loop():
    logger.info("task_queue_loop start")
    while True:
        task: Task = task_queue.get()
        run = client.beta.threads.runs.retrieve(
            thread_id=task.thread.id, run_id=task.run.id)
        if run.status == "queued" or run.status == "in_progress":
            task_queue.put(task)
        else:
            response_messages = client.beta.threads.messages.list(
                thread_id=task.thread.id, order="asc", after=task.trigger_message.id
            )
            sio.emit("stopTyping", task.session_id, callback=lambda _: None)

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
                        "recipientId": task.sender_id,
                        "content": message.content[0].text.value,
                        "timestamp": get_now_str(),
                    },
                    callback=handle_callback,
                )


def add_task(task):
    task_queue.put(task)
