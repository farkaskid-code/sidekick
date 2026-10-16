from json import loads

from langchain_ollama import ChatOllama
from rich.console import Console

from sidekick.config import runtime
from sidekick.data import Critique, Information, Research, ResearchPlan, State
from sidekick.helpers import web_search

model = ChatOllama(
    model=runtime.model.name,
    base_url=runtime.model.base_url,
    num_ctx=runtime.model.num_ctx,
    temperature=runtime.model.temperature,
)

console = Console()


def plan(state: State):
    with console.status("[green]Planning..."):
        response = model.with_structured_output(ResearchPlan).invoke(
            "Give me a list of topics that should be researched to answer the following question?"
            f"question: {state['question']}"
        )
    return {"planning": response}


def research(state: State):
    research = []
    for topic in state["planning"].topics:
        with console.status(f"[green]Researching: {topic}"):
            response = model.with_structured_output(Information).invoke(
                "Research the following topic and provide useful facts and information.\n"
                + topic
            )
        research.append(response)

    return {"research": Research(topics=research)}


def web_research(state: State):
    research = []
    for topic in state["planning"].topics:
        with console.status(f"[green]Searching on the web: {topic}"):
            response = web_search(topic)
        research.append(Information(topic=topic, content=response))

    return {"research": Research(topics=research)}


def critique(state: State):
    response = model.with_structured_output(Critique).invoke(
        "critique the following answer for the question based on the given research"
        " to decide if it passes or fails as an answer and does it require additional research. "
        f"question: {state['question']}\n----\n"
        f"research: {state['research']}\n----\n"
        f"answer: {state['answer']}"
    )
    return {"critique": response}


def answer(state: State):
    with console.status("[green]Putting togather all the pieces..."):
        response = model.invoke(
            "Answer the following question based on the provided research\n\n"
            f"question: {state['question']}\n\n"
            f"research: {state['research']}"
        )
    return {"answer": response.content}
