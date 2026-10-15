from json import loads
from typing import TypedDict

from langchain_ollama import ChatOllama
from rich.console import Console

from sidekick.config import runtime
from sidekick.helpers import llm_search, web_search

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
    passed: bool
    notes: str


def plan(state: State):
    with console.status("[green]Planning..."):
        response = model.invoke(
            "What topics should be researched to answer the following question?"
            "Respond with a list of topics.\n\n"
            f"question: {state['question']}"
        )
    return {"research_topics": response.content.splitlines()}


def research(state: State):
    return {
        "research": [llm_search(model, topic) for topic in state["research_topics"]]
    }


def critique(state: State):
    response = model.invoke(
        "critique the following answer generated for the question based on the given research"
        " to decide if it passes or fails as an answer and requires additional research. "
        "Return a JSON response with the following information: "
        "'passed': a boolean indicating if the answer passes\n"
        "'notes': Your notes for passing or failing the answer\n"
        "'additional_research': A list of strings containing additional research topics to incorporate if required\n\n\n"
        "====\n"
        f"question: {state['question']}\n----\n"
        f"research: {'\n####\n'.join(state['research'])}\n----\n"
        f"answer: {state['answer']}"
    )
    print(response.content)
    data = loads(response.content)
    return {
        "passed": data["passed"],
        "notes": data["notes"],
        "research_topics": state["research_topics"] + data["additional_research"],
    }


def answer(state: State):
    with console.status("[green]Putting togather all the pieces..."):
        response = model.invoke(
            "Answer the following question based on the provided research\n\n"
            f"question: {state['question']}\n\n"
            f"research: {'\n\n'.join(state['research'])}"
        )
    return {"answer": response.content}
