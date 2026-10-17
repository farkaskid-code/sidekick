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
            "Give me a list of 3-4 topics that should be researched to answer the following question?"
            f"question: {state['question']}"
        )
    return {"planning": response}


def research(state: State):
    topics_info = []
    for topic in state["planning"].topics:
        with console.status(f"[green]Researching: {topic}"):
            response = model.with_structured_output(Information).invoke(
                "Research the following topic and provide a summary of useful facts and information.\n"
                + topic
            )
        topics_info.append(response)
        console.print(f"Researched: {topic}", style="yellow")

    new_research = Research(topics=topics_info)
    existing_research = state.get("research", None)
    if existing_research:
        new_research = Research(topics=existing_research.topics + topics_info)

    return {"research": new_research, "planning": ResearchPlan(topics=[])}


def web_research(state: State):
    research = []
    for topic in state["planning"].topics:
        with console.status(f"[green]Searching on the web: {topic}"):
            response = web_search(topic)
        research.append(Information(topic=topic, content=response))

    return {"research": Research(topics=research)}


def critique(state: State):
    with console.status("[green]Evaluating the answer"):
        response: Critique = model.with_structured_output(Critique).invoke(
            "critique the answer to evaluate if it needs more research\n"
            f"question: {state['question']}\n----\n"
            f"research: {state['research']}\n----\n"
            f"answer: {state['answer']}"
        )
    console.print(
        f"Evaluation: {response.notes}",
        style="green" if len(response.additional_research) == 0 else "red",
    )
    return {
        "critique": response,
        "planning": ResearchPlan(topics=response.additional_research),
    }


def answer(state: State):
    with console.status("[green]Crafting the answer..."):
        response = model.invoke(
            "Answer the following question based on the provided research\n\n"
            f"question: {state['question']}\n\n"
            f"research: {state['research']}"
        )
    return {"answer": response.content}
