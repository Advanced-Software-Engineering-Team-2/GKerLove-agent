import threading
import time
from collections import UserDict

from logger import logger
from task_loop import Task, add_task
from openai_client import client
from agent import agent


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


sessions = ThreadSafeDict()
sessions_lock = {}


def message_loop():
    logger.info("message_loop started")
    while True:
        for session_id in sessions:
            if sessions_lock.get(session_id, False):
                continue
            logger.info(f"deal with session {session_id}")
            _submit_task(sessions[session_id])
        time.sleep(1)


def receive_message(session_id, thread_id, sender_id, message):
    if session_id not in sessions:
        sessions[session_id] = Session(
            session_id, thread_id, sender_id, [message])
    else:
        sessions[session_id].messages.append(message)


def _submit_task(session):
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
    sessions_lock[session.id] = True
    task = Task(run, session, offset)
    add_task(task)
    sessions.pop(session.id)
