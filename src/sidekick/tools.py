import logging

import requests
from langchain_core.tools import tool
from rich.console import Console

from sidekick.config import runtime

console = Console()
log = logging.getLogger(__name__)


@tool
def web_search(query: str) -> str:
    """Search the web for current and factual information"""

    log.info(f"Web Search for: {query}")
    response = requests.post(
        url=str(runtime.web.url),
        json={"api_key": runtime.web.api_key, "query": query, "max_results": 3},
    )

    console.print(f"\nWeb Search: {query}", style="blue")
    log.info(f"Web Search completed with: {response.status_code} code")

    results = []

    for result in response.json()["results"]:
        results.append(
            f"### Source: [{result['title']}]({result['url']})\n"
            f"**Content**: {result['content']}"
        )

    return "\n---\n".join(results)
