import os
import time
import threading

from agent_store import agent_factory
from network import login
from logger import logger

agent_name = os.getenv("AGENT_NAME", "Athena")
agent = agent_factory(agent_name)


def refresh_token():
    logger.info("Refreshing token")
    global agent
    agent.token = login(agent.username, agent.password)
    while not agent.token:
        agent.token = login(agent.username, agent.password)
        time.sleep(1)
    logger.info("Token refreshed", agent.token)


def scheduler():
    time.sleep(60 * 60)
    refresh_token()


refresh_token()
threading.Thread(target=scheduler, daemon=True).start()
