from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule

from sidekick.agent import graph

console = Console()


def main():
    config = {"configurable": {"thread_id": "session"}}

    while True:
        try:
            console.print("Question: ", style="green", end="")
            user_input = input().strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                console.print("Goodbye!", style="yellow")
                break

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

        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat loop...")
            break
