from datetime import datetime

from langchain.tools import tool


@tool
def current_datetime() -> str:
    """
    Return the current server date and time.

    Use this tool when the user asks
    for the current date or current time.
    """

    now = datetime.now()

    return now.strftime(
        "%Y-%m-%d %H:%M:%S"
    )