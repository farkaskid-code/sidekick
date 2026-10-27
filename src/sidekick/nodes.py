import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from rich.console import Console

from sidekick.config import runtime
from sidekick.data import PROMPT, Critique, Information, Research, ResearchPlan, State
from sidekick.search import search_agent
from sidekick.tools import web_search

small_model = ChatOllama(
    model=runtime.models.small.name,
    base_url=str(runtime.models.small.base_url),
    num_ctx=runtime.models.small.num_ctx,
    temperature=runtime.models.small.temperature,
)

large_model = ChatOllama(
    model=runtime.models.large.name,
    base_url=str(runtime.models.large.base_url),
    num_ctx=runtime.models.large.num_ctx,
    temperature=runtime.models.large.temperature,
)

research_model = large_model.bind_tools([web_search])

console = Console()
log = logging.getLogger(__name__)


def plan(state: State):
    log.info(f"Planning started for: {state['question']}")
    messages = [
        SystemMessage(PROMPT.get("plan")),
        HumanMessage(f"question: {state['question']}"),
    ]
    with console.status("[green]Planning..."):
        response = search_agent.invoke(
            {"messages": messages},
            config={"configurable": {"thread_id": "planning_search"}},
        )

    content = response.get("messages")[-1].content
    topics = [topic.strip() for topic in content.strip().splitlines()]
    log.info(f"Planned to research topics: {topics}")
    return {
        "planning": ResearchPlan(topics=topics),
        "research": Research(topics=[]),
    }


def research(state: State):
    log.info("Starting Research...")
    system_msg = SystemMessage(PROMPT.get("research"))
    topics_info = []
    for topic in state["planning"].topics:
        log.info(f"Researching topic: {topic}")
        with console.status(f"[green]Researching: {topic}"):
            response = search_agent.invoke(
                {"messages": [system_msg, HumanMessage(topic)]},
                config={"configurable": {"thread_id": "search"}},
            )
            info = Information(topic=topic, content=response["messages"][-1].content)
            log.debug(f"Info from research: {info}")
        topics_info.append(info)
        log.info(f"Completed research for: {topic}")
        console.print(f"Researched: {topic}", style="yellow")

    new_research = Research(topics=topics_info)
    existing_research = state.get("research", None)
    if existing_research:
        log.info("Adding new information to the previous research")
        new_research = Research(topics=existing_research.topics + topics_info)

    return {"research": new_research, "planning": ResearchPlan(topics=[])}


def factcheck(state: State):
    log.info("Factchecking the answer")
    messages = [
        SystemMessage(PROMPT.get("factcheck")),
        HumanMessage(
            f"## Question\n{state['question']}\n---\n### Answer\n{state['answer']}"
        ),
    ]

    with console.status("[green]Checking facts..."):
        response = search_agent.invoke(
            {"messages": messages}, config={"configurable": {"thread_id": "factcheck"}}
        )

    accuracy = int(response["messages"][-1].content[:-1])
    log.info(f"Answer's accuracy: {accuracy}")
    console.print(
        f"Answer's Factual Accuracy: {accuracy}%",
        style="red bold" if accuracy < 80 else "blue",
    )

    return {"factual_accuracy": accuracy}


def critique(state: State):
    log.info("Critiquing the answer")
    messages = [
        SystemMessage(PROMPT.get("critic")),
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

    log.info(f"Answer's critique: {response.notes}")
    log.info(f"Additional research topics: {response.additional_research}")

    return {
        "critique": response,
        "loop_count": state["loop_count"] + 1,
        "planning": ResearchPlan(topics=response.additional_research),
    }


def answer(state: State):
    log.info("Drafting the answer")
    messages = [
        SystemMessage(PROMPT.get("answer")),
        HumanMessage(
            f"## Question\n{state['question']}\n\n## Research\n{state['research']}"
        ),
    ]
    with console.status("[green]Drafting the answer..."):
        response = small_model.invoke(messages)

    log.info("Drafted the answer")
    return {"answer": response.content}
