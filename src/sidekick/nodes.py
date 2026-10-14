from typing import TypedDict

from langchain_ollama import ChatOllama
from rich.console import Console

from sidekick.config import runtime
from sidekick.helpers import web_search

model = ChatOllama(
    model=runtime.model.name,
    base_url=runtime.model.base_url,
    num_ctx=runtime.model.num_ctx,
    temperature=runtime.model.temperature,
)

console = Console()


class State(TypedDict):
    question: str
    research_topics: list[str]
    research: list[str]
    answer: str


def plan(state: State):
    response = model.invoke(
        "What topics should be researched to answer the following question?"
        "Respond with a list of topics.\n\n"
        f"question: {state['question']}"
    )
    return {"research_topics": response.content.splitlines()}


def research(state: State):
    return {"research": [web_search(topic) for topic in state["research_topics"]]}


def answer(state: State):
    print("\n\n==========\n\n".join(state["research"]))
    response = model.invoke(
        "Answer the following question based on the provided research\n\n"
        f"question: {state['question']}\n\n"
        f"research: {'\n\n'.join(state['research'])}"
    )
    return {"answer": response.content}
