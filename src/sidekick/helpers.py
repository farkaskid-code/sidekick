import requests
from rich.console import Console

from sidekick.config import runtime

console = Console()


def web_search(query: str) -> str:
    response = requests.post(
        url=runtime.web.url,
        json={"api_key": runtime.web.api_key, "query": query, "max_results": 3},
    )

    output = ""

    for result in response.json()["results"]:
        output = f"{output}Title: {result['title']}\n"
        output = f"{output}URL: {result['url']}\n"
        output = f"{output}Info: {result['content']}\n"

    return output
