import os
import time
import threading
import schedule

from generate import client
from agents import agent_factory
from network import login
from logger import logger

user_class = os.getenv("USER_CLASS", "Athena")
user = agent_factory(user_class)
user.token = None
user.assistant = client.beta.assistants.create(
    name=user.username,
    instructions=user.prompt,
    model="gpt-4-1106-preview",
)


def refresh_token():
    logger.info("Refreshing token")
    global user
    user.token = login(user.username, user.password)
    while not user.token:
        user.token = login(user.username, user.password)
        time.sleep(5)
    logger.info("Token refreshed", user.token)


def scheduler():
    schedule.every().hour.do(refresh_token)
    while True:
        schedule.run_pending()
        time.sleep(1)


refresh_token()
threading.Thread(target=scheduler, daemon=True).start()
