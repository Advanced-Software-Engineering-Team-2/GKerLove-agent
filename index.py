from config import config
from chatsocket import sio
from user import token
from handlers import connect, message, disconnect

sio.on("connect", connect)
sio.on("privateMessage", message)
sio.on("disconnect", disconnect)

if __name__ == "__main__":
    sio.connect(config.chat_server, auth={"token": token})
    sio.wait()
