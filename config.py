import os


class BaseConfig:
    openai_base_url = "https://api2.aigcbest.top/v1"


class DevConfig(BaseConfig):
    back_server = "http://localhost:30901"
    chat_server = "http://localhost:30101"


class ProdConfig(BaseConfig):
    back_server = "https://back.love.gkers.top:1111"
    chat_server = "https://chat.love.gkers.top:1111"


env = os.getenv("ENV", "dev")
config = DevConfig if env == "dev" else ProdConfig
