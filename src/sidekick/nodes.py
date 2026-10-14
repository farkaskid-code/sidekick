from typing import TypedDict

from langchain_ollama import ChatOllama
from rich.console import Console

from sidekick.config import runtime

model = ChatOllama(
    model=runtime.model.name,
    base_url=runtime.model.base_url,
    num_ctx=runtime.model.num_ctx,
    temperature=runtime.model.temperature,
)

console = Console()


class State(TypedDict):
    question: str
    research: str
    answer: str


def research(state: State):
    response = model.invoke(
        "Research the following question and provide useful facts\n\n"
        f"question: {state['question']}"
    )
    return {"research": response.content}


def answer(state: State):
    response = model.invoke(
        "Answer the following question based on the provided research\n\n"
        f"question: {state['question']}\n\n"
        f"research: {state['research']}"
    )
    return {"answer": response.content}
