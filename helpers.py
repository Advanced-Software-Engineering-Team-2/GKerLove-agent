from datetime import datetime
import pytz
import base64
import requests


def get_now_str():
    now_utc = datetime.now(pytz.UTC)
    now_bj = now_utc.astimezone(pytz.timezone("Asia/Shanghai"))
    iso_date_bj = now_bj.isoformat(timespec="milliseconds")
    if iso_date_bj.endswith("+00:00"):
        iso_date_bj = iso_date_bj[:-6] + "Z"
    return iso_date_bj


def encode_image(image_url):
    res = requests.get(image_url)
    return base64.b64encode(res.content).decode("utf-8")


if __name__ == "__main__":
    # print(get_now_str())
    b64 = encode_image(
        "https://gker-love.oss-cn-beijing.aliyuncs.com/Naive/messages/b4a84c88-aa92-4302-9b0b-11d6a402b8bb/7aa16bde-0f8a-406a-82e2-5d1bfc15f9aa.jpeg"
    )
    print(len(b64))
