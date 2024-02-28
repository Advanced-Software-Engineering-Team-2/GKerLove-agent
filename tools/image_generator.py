from typing import Optional
from config import config

from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper


class ImageGenerator(BaseTool):
    """Tool used to generate images from a text-prompt."""

    name: str = "image_generator"
    description: str = (
        "Useful for when you need to generate an image."
        "Input: A detailed text-2-image prompt describing an image"
        "Output: the url of a generated image"
    )
    api_wrapper: DallEAPIWrapper

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return self.api_wrapper.run(query)


image_generator = ImageGenerator(
    api_wrapper=DallEAPIWrapper(base_url=config.openai_base_url)
)
