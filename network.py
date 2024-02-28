import requests
import ddddocr
import json

from logger import logger
from config import config
from beans import Message

ocr = ddddocr.DdddOcr(show_ad=False)


def login(username, password):
    session = requests.session()
    captcha = session.get(f"{config.back_server}/common/captcha")
    payload = {
        "username": username,
        "password": password,
        "captcha": ocr.classification(captcha.content),
    }
    res = session.post(
        f"{config.back_server}/user/login",
        headers={
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    res = res.json()
    if res["code"] == "SUCCESS":
        logger.info("登录成功")
        logger.info("token: " + res["data"]["token"])
        return res["data"]["token"]
    else:
        logger.error("登录失败")
        return None


def fetch_history_messages(session_id, token) -> list[Message]:
    try:
        res = requests.get(
            f"{config.back_server}/message/{session_id}", headers={"token": token}
        )
        return res.json()["data"]["session"]["messages"]
    except Exception as e:
        logger.error(res.json())
        logger.error(e)
        return []


if __name__ == "__main__":
    token = login("gyr679", "2023111")
    res = fetch_history_messages("fd9b07f8-ebaa-444a-83fe-ccabff3807a3", token)
    print(res)
