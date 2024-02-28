import os
import time
import threading

from agents import agent_factory
from network import login
from logger import logger

user_class = os.getenv("USER_CLASS", "Athena")
user = agent_factory(user_class)

token = None


def refresh_token():
    logger.info("Refreshing token")
    global token
    while True:
        token = login(user.username, user.password)
        time.sleep(1)
        if token:
            break
    logger.info("Token refreshed")
    logger.info(token)


def scheduler():
    while True:
        time.sleep(60 * 60)
        refresh_token()


refresh_token()
threading.Thread(target=scheduler, daemon=True).start()
