from loguru import logger


# def color_sink(message):
#     record = message.record
#     level = record["level"].name
#     time = record["time"].strftime("%Y-%m-%d %H:%M:%S")
#     msg = record["message"]

#     if level == "INFO":
#         print(f"\033[32m[{time}] [INFO]    - {msg}\033[0m")
#     elif level == "WARNING":
#         print(f"\033[33m[{time}] [WARNING] - {msg}\033[0m")
#     elif level == "ERROR":
#         print(f"\033[31m[{time}] [ERROR]   - {msg}\033[0m")


# logger.remove()
# logger.add(color_sink)


if __name__ == "__main__":
    logger.info("这是一条info信息")
    logger.warning("这是一条warning信息")
    logger.error("这是一条error信息")
