from datetime import datetime
from langchain.tools import tool


@tool
def current_datetime_tool() -> datetime:
    """
    Get the current datetime.
    When it comes to time or date (such as today, yesterday, tomorrow, now, etc), you must first use this tool to obtain the current time and date, and then make the next decision based on the current time and date.
    """
    return datetime.now()
