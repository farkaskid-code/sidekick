import logging

from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule

from sidekick.agent import graph
from sidekick.cli import parse_args

console = Console()
log = logging.getLogger(__name__)


def main():
    user_input = parse_args().query.strip()
    log.info(f"User query: {user_input}")
    config = {"configurable": {"thread_id": "session"}}

    result = graph.invoke(
        input={"question": user_input, "loop_count": 0},
        config=config,
    )

    answer = result.get("answer", None)
    log.info(f"Answer: {answer}")
    if answer:
        console.print(Rule())
        console.print("sidekick: ", style="green", end="")
        console.print(Markdown(answer), style="yellow")
        console.print(Rule())
