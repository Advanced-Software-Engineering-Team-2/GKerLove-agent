import requests
import ddddocr
import json

from logger import logger
from config import config

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


def fetch_history_messages(session_id, token):
    return requests.get(
        f"{config.back_server}/message/{session_id}", headers={"token": token}
    ).json()["data"]["session"]["messages"]

def fetch_sessions(token):
    return requests.get(
        f"{config.back_server}/message", headers={"token": token}
    ).json()["data"]["sessions"]


if __name__ == "__main__":
    token = login("Athena", "myLover")
    # res = fetch_history_messages("fd9b07f8-ebaa-444a-83fe-ccabff3807a3", token)
    res = fetch_sessions(token)
    json.dump(res, open("sessions.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(res)
