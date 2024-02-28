from logger import logger
from user import user


def disconnect():
    logger.info(f"{user.username} 下线")
