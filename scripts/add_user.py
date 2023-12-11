import hashlib
from datetime import datetime
from pymongo import MongoClient
import uuid

client = MongoClient("mongodb://gkers:gkers111666@server.cqupt-gyr.xyz:30572")
# client = MongoClient("mongodb://gkers:gkers111666@server.cqupt-gyr.xyz:27017/test")

db = client["GKerLove"]


def generate_password(orginal: str):
    return hashlib.md5(orginal.encode("utf-8")).hexdigest()


def add_user(username: str, password: str):
    collection = db["users"]
    user = {
        "_id": str(uuid.uuid4()),
        "username": username,
        "password": generate_password(password),
        "email": "fake@fake.com",
        "avatar": "https://gker-love.oss-cn-beijing.aliyuncs.com/default-avatar",
        "create_time": datetime.now(),
    }
    collection.insert_one(user)


if __name__ == "__main__":
    add_user("Athena", "myLover")
