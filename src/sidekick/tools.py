import requests
from langchain_core.tools import tool
from rich.console import Console

from sidekick.config import runtime

console = Console()


@tool
def web_search(query: str) -> str:
    """Search the web for current and factual information"""

    response = requests.post(
        url=runtime.web.url,
        json={"api_key": runtime.web.api_key, "query": query, "max_results": 3},
    )

    console.print(f"\nWeb Search: {query}", style="blue")

    results = []

    for result in response.json()["results"]:
        results.append(
            f"### Source: [{result['title']}]({result['url']})\n"
            f"**Content**: {result['content']}"
        )

    return "\n---\n".join(results)
