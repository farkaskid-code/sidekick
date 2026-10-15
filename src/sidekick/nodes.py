from json import loads

from langchain_ollama import ChatOllama
from rich.console import Console

from sidekick.config import runtime
from sidekick.data import Research, ResearchPlan, ResearchResult, State
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
            response = model.with_structured_output(Research).invoke(
                "Research the following topic and provide useful facts and information.\n"
                + topic
            )
        research.append(response)

    return {"research": ResearchResult(research=research)}


def web_research(state: State):
    research = []
    for topic in state["planning"].topics:
        with console.status(f"[green]Searching on the web: {topic}"):
            response = web_search(topic)
        research.append(Research(topic=topic, content=response))

    return {"research": ResearchResult(research=research)}


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
            f"research: {state['research']}"
        )
    return {"answer": response.content}
