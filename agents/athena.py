import os

from langchain_openai import ChatOpenAI

from config import config
from prompts import athena_prompt_template
from tools import bing_search_tool, weather_tool, current_datetime_tool
from .base import BaseAgent


class Athena(BaseAgent):
    def __init__(self):
        self.username = "Athena"
        self.password = os.getenv("GKerLove_agent_password")
        self.prompt = athena_prompt_template
        self.llm = ChatOpenAI(
            model="gpt-4", temperature=0, base_url=config.openai_base_url
        )
        self.tools = [bing_search_tool, weather_tool, current_datetime_tool]
        super().__init__(self.llm, self.tools, self.prompt)
