from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from rich.console import Console

from sidekick.config import runtime
from sidekick.data import Critique, Information, Research, ResearchPlan, State
from sidekick.search import search_agent
from sidekick.tools import web_search

small_model = ChatOllama(
    model=runtime.models.small.name,
    base_url=runtime.models.small.base_url,
    num_ctx=runtime.models.small.num_ctx,
    temperature=runtime.models.small.temperature,
)

large_model = ChatOllama(
    model=runtime.models.large.name,
    base_url=runtime.models.large.base_url,
    num_ctx=runtime.models.large.num_ctx,
    temperature=runtime.models.large.temperature,
)

research_model = large_model.bind_tools([web_search])

console = Console()


def plan(state: State):
    messages = [
        SystemMessage(
            "You are research planner whose job is to provide 3-4 topics"
            " that should be researched to answer the user's query?"
        ),
        HumanMessage(f"question: {state['question']}"),
    ]
    with console.status("[green]Planning..."):
        response = large_model.with_structured_output(ResearchPlan).invoke(messages)

    return {"planning": response}


def research(state: State):
    system_msg = SystemMessage(
        "You are a researcher whose job is to provide a summary of "
        "useful facts and information for the topic given by the user. "
        "Use web_search when you need external information."
        "You may perform multiple searches if necessary"
    )
    topics_info = []
    for topic in state["planning"].topics:
        with console.status(f"[green]Researching: {topic}"):
            response = search_agent.invoke(
                {"messages": [system_msg, HumanMessage(topic)]},
                config={"configurable": {"thread_id": "search"}},
            )
        topics_info.append(
            Information(topic=topic, content=response["messages"][-1].content)
        )
        console.print(f"Researched: {topic}", style="yellow")

    new_research = Research(topics=topics_info)
    existing_research = state.get("research", None)
    if existing_research:
        new_research = Research(topics=existing_research.topics + topics_info)

    return {"research": new_research, "planning": ResearchPlan(topics=[])}


def critique(state: State):
    messages = [
        SystemMessage(
            "You are critic whose job is to critique the answer for a given question "
            "based on the provided research. Tell the user if the answer needs additional research "
            "and provide those research topics as additional research."
        ),
        HumanMessage(
            f"## Question\n{state['question']}\n\n"
            f"## Answer\n{state['answer']}\n\n"
            f"## Research:\n{state['research']}"
        ),
    ]
    with console.status("[green]Evaluating the answer"):
        response: Critique = small_model.with_structured_output(Critique).invoke(
            messages
        )

    console.print(
        f"Evaluation: {response.notes}",
        style="green" if len(response.additional_research) == 0 else "red",
    )

    return {
        "critique": response,
        "loop_count": state["loop_count"] + 1,
        "planning": ResearchPlan(topics=response.additional_research),
    }


def answer(state: State):
    messages = [
        SystemMessage(
            "Your job is to craft a detailed answer based to the user "
            "question based on the research provided."
        ),
        HumanMessage(
            f"## Question\n{state['question']}\n\n## Research\n{state['research']}"
        ),
    ]
    with console.status("[green]Crafting the answer..."):
        response = small_model.invoke(messages)
    return {"answer": response.content}
