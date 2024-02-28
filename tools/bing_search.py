from langchain.tools.bing_search import BingSearchRun
from langchain_community.utilities import BingSearchAPIWrapper

bing_search_tool = BingSearchRun(api_wrapper=BingSearchAPIWrapper())
