import sys

from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule

from sidekick.agent import graph

console = Console()


def main():
    console.print(f"Discussion Topic: {sys.argv[1]}", style="yellow")
    console.print(Rule())
    config = {"configurable": {"thread_id": sys.argv[1]}}

    while True:
        try:
            console.print("You: ", style="green", end="")
            user_input = input().strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                console.print("Goodbye!", "yellow")
                break

            # Execute graph stream
            events = graph.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="values",
            )

            # Retrieve final message output
            for event in events:
                latest_msg = event["messages"][-1]

            if latest_msg.type == "ai" and latest_msg.content:
                console.print(Rule())
                console.print("sidekick: ", style="green", end="")
                console.print(Markdown(latest_msg.content), style="yellow")
                console.print(Rule())

        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat loop...")
            break
