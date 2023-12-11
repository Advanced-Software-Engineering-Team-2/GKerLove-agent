import time
from datetime import datetime
import pytz

from generate import client


def get_now_str():
    now_utc = datetime.now(pytz.UTC)
    now_bj = now_utc.astimezone(pytz.timezone("Asia/Shanghai"))
    iso_date_bj = now_bj.isoformat(timespec="milliseconds")
    if iso_date_bj.endswith("+00:00"):
        iso_date_bj = iso_date_bj[:-6] + "Z"
    return iso_date_bj


if __name__ == "__main__":
    print(get_now_str())
