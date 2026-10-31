import logging

from langchain_core.messages import HumanMessage, SystemMessage
from rich.console import Console

from sidekick.config import get_model
from sidekick.data import PROMPT, Critique, Information, Research, ResearchPlan, State
from sidekick.search import SearchAgent

console = Console()
log = logging.getLogger(__name__)

plan_agent = SearchAgent("plan")


def plan(state: State):
    log.info(f"Planning started for: {state['question']}")

    with console.status("[green]Planning..."):
        response = plan_agent.run(state["question"])

    content = response.get("messages")[-1].content
    topics = [topic.strip() for topic in content.strip().splitlines()]

    log.info(f"Planned to research topics: {topics}")
    return {
        "planning": ResearchPlan(topics=topics),
        "research": Research(topics=[]),
    }


research_agent = SearchAgent("research")


def research(state: State):
    log.info("Starting Research...")
    topics_info = []

    for topic in state["planning"].topics:
        log.info(f"Researching topic: {topic}")

        with console.status(f"[green]Researching: {topic}"):
            response = research_agent.run(topic)
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


factcheck_agent = SearchAgent("factcheck")


def factcheck(state: State):
    log.info("Factchecking the answer")

    with console.status("[green]Checking facts..."):
        response = factcheck_agent.run(
            f"## Question\n{state['question']}\n---\n### Answer\n{state['answer']}"
        )

    accuracy = int(response["messages"][-1].content[:-1])
    log.info(f"Answer's accuracy: {accuracy}")
    console.print(
        f"Answer's Factual Accuracy: {accuracy}%",
        style="red bold" if accuracy < 80 else "blue",
    )

    return {"factual_accuracy": accuracy}


critic_model = get_model("critic")


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
        response: Critique = critic_model.with_structured_output(Critique).invoke(
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


answer_model = get_model("answer")


def answer(state: State):
    log.info("Drafting the answer")
    messages = [
        SystemMessage(PROMPT.get("answer")),
        HumanMessage(
            f"## Question\n{state['question']}\n\n## Research\n{state['research']}"
        ),
    ]
    with console.status("[green]Drafting the answer..."):
        response = answer_model.invoke(messages)

    log.info("Drafted the answer")
    return {"answer": response.content}
