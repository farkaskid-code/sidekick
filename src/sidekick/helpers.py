import requests
from langchain_ollama import ChatOllama
from rich.console import Console

from sidekick.config import runtime

console = Console()


def web_search(query: str) -> str:
    with console.status(f"[green]Researching: {query}"):
        response = requests.post(
            url=runtime.web.url,
            json={"api_key": runtime.web.api_key, "query": query, "max_results": 3},
        )

    output = f"Topic: {query}\n\n====\n"

    for result in response.json()["results"]:
        output = f"{output}Title: {result['title']}\n"
        output = f"{output}URL: {result['url']}\n"
        output = f"{output}Content: {result['content']}\n"
        output = f"{output}----\n"

    return output


def llm_search(model: ChatOllama, query: str) -> str:
    with console.status(f"[green]Researching: {query}"):
        response = model.invoke(
            "Research the following topic and provide useful facts and information.\n"
            + query
        )

    return f"Topic: {query}\n====\nResearch: {response.content}"
