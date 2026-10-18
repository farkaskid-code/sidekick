from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule

from sidekick.agent import graph
from sidekick.cli import parse_args

console = Console()


def main():
    user_input = parse_args().query.strip()
    config = {"configurable": {"thread_id": "session"}}

    values = list(
        graph.stream(
            input={"question": user_input}, config=config, stream_mode="values"
        )
    )

    answer = values[-1].get("answer", None)
    if answer:
        console.print(Rule())
        console.print("sidekick: ", style="green", end="")
        console.print(Markdown(answer), style="yellow")
        console.print(Rule())
