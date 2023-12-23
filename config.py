import os


class DevConfig:
    back_server = "http://localhost:8989"
    chat_server = "http://localhost:3000"


class ProdConfig:
    back_server = "https://back.love.gkers.top:1111"
    chat_server = "https://chat.love.gkers.cqupt-gyr.xyz:1111"


env = os.getenv("ENV", "dev")
config = DevConfig if env == "dev" else ProdConfig
