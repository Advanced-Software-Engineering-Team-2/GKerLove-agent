import threading
import time
from collections import UserDict

from logger import logger
from task_loop import Task, add_task
from openai_client import client
from agent import agent
from sio import sio
from flag import mark_session_busy, get_session_busy


class ThreadSafeDict(UserDict):
    def __init__(self, *args, **kwargs):
        self.lock = threading.Lock()
        super(ThreadSafeDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        with self.lock:
            super(ThreadSafeDict, self).__setitem__(key, value)

    def __getitem__(self, key):
        with self.lock:
            return super(ThreadSafeDict, self).__getitem__(key)

    def __delitem__(self, key):
        with self.lock:
            super(ThreadSafeDict, self).__delitem__(key)


class Session:
    def __init__(self, session_id, thread_id, peer_id, messages):
        self.session_id = session_id
        self.thread_id = thread_id
        self.peer_id = peer_id
        self.messages = messages
        self.lock = threading.Lock()


# 需要保证线程安全，在以下几种情况下会使用该数据结构：
# 1. 在消息循环线程中，会循环读取该数据结构
# 2. 在消息循环线程中，会删除该数据结构中的元素
# 3. 在事件处理线程中（多线程），会调用receive_message，向该数据结构中添加元素
sessions = ThreadSafeDict()


def message_loop():
    logger.info("message_loop started")
    while True:
        session_ids = list(sessions.keys())  # 创建sessions的快照
        for session_id in session_ids:
            if session_id not in sessions:
                continue  # 确保session_id仍然存在于原始sessions中
            if len(sessions[session_id].messages) == 0:
                continue
            if get_session_busy(session_id):
                continue
            _submit_task(sessions[session_id])
        time.sleep(1)  # 每1秒查看一下有没有新消息


def receive_message(session_id, thread_id, sender_id, message):
    if session_id not in sessions:
        sessions[session_id] = Session(
            session_id, thread_id, sender_id, [message])
    else:
        with sessions[session_id].lock:
            sessions[session_id].messages.append(message)


def _submit_task(session):
    with session.lock:  # 锁住session，防止在创建run的过程中，有新消息进来
        mark_session_busy(session.session_id)
        offset = -1
        for message in session.messages:
            offset = client.beta.threads.messages.create(
                thread_id=session.thread_id,
                role="user",
                content=message["content"],
            ).id
        run = client.beta.threads.runs.create(
            thread_id=session.thread_id,
            assistant_id=agent.assistant.id,
        )
        sio.emit("startTyping", session.session_id, callback=lambda _: None)
        task = Task(run, session, offset)
        add_task(task)
        session.messages.clear()
