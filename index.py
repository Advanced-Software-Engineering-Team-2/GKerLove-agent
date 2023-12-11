import threading

from sio import sio
# from generate import client
from config import config
from logger import logger
# from network import fetch_sessions
from user import user
# from task_queue import Task, task_queue_loop, add_task
from task_queue import task_queue_loop
# from message_queue import message_queue_loop, Message, add_message, thread_store
from message_queue import message_queue_loop, Message, add_message


# def init_sessions():
#     sessions = fetch_sessions(user.token)
#     for session in sessions:
#         session_id = session["id"]
#         peer = session["peer"]
#         messages = session["messages"]
#         # 为每个会话创建一个thread
#         thread = client.beta.threads.create()
#         last_openai_message = None
#         for message in messages:
#             if message["type"] == "text":  # 只处理文本消息
#                 openai_message = client.beta.threads.messages.create(
#                     thread_id=thread.id,
#                     role="user" if message["senderId"] == peer["id"] else "assistant",
#                     content=message["content"],
#                 )
#                 last_openai_message = openai_message
#         thread_store[session_id] = thread
#         have_unreaded = messages[-1]["senderId"] == peer["id"]
#         if have_unreaded:
#             run = client.beta.threads.runs.create(
#                 thread_id=thread.id,
#                 assistant_id=user.assistant.id,
#             )
#             add_task(Task(run, thread, session_id, last_openai_message))


@sio.event
def connect():
    logger.info(f"{user.username} 成功上线")


@sio.on("privateMessage")
def deal_message(payload):
    session_id = payload["sessionId"]
    message = payload["message"]
    if message["type"] == "text":  # 只处理文本消息
        add_message(
            Message(session_id, message["content"], message["senderId"]))


@sio.event
def disconnect():
    logger.info(f"{user.username} 下线")


# init_sessions()  # 启动agent时，在openai中同步session
task_queue_loop_thread = threading.Thread(
    target=task_queue_loop, daemon=True).start()

message_queue_loop_thread = threading.Thread(
    target=message_queue_loop, daemon=True).start()

sio.connect(config.chat_server, auth={"token": user.token})
sio.wait()
