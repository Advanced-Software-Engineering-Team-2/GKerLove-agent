import os


class DevConfig:
    back_server = "https://back.love.gkers.cqupt-gyr.xyz:1111"
    chat_server = "https://chat.love.gkers.cqupt-gyr.xyz:1111"


class ProdConfig:
    back_server = "https://back.love.gkers.cqupt-gyr.xyz:1111"
    chat_server = "https://chat.love.gkers.cqupt-gyr.xyz:1111"


env = os.getenv("ENV", "dev")
config = DevConfig if env == "dev" else ProdConfig
