from logger import logger
from user import user


def connect():
    logger.info(f"{user.username} 成功上线")
