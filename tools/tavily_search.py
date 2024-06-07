from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

api_wrapper = TavilySearchAPIWrapper()
tavily_search_tool = TavilySearchResults(api_wrapper=api_wrapper)
