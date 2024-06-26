import os

from langchain_openai import ChatOpenAI

from config import config
from .prompt import prompt_template
from tools import (
    bing_search_tool,
    weather_tool,
    current_datetime_tool,
    create_experience_tool,
    tavily_search_tool,
)
from ..base import BaseAgent


class Athena(BaseAgent):
    def __init__(self):
        self.username = "Athena"
        self.password = os.getenv("PASSWORD_ATHENA")
        self.prompt = prompt_template
        self.llm = ChatOpenAI(
            model="gpt-4o",
            base_url=config.openai_base_url,
            max_tokens=400,
        )
        self.tools = [
            tavily_search_tool,
            # bing_search_tool,
            weather_tool,
            current_datetime_tool,
            # create_experience_tool("assets/experiences/Athena.txt"),
        ]
        super().__init__(self.llm, self.tools, self.prompt)
