from langchain_core.messages import HumanMessage

from sidekick.agent import graph
from sidekick.config import runtime


def main():
    print("=" * 60)
    print(f"Ollama LangGraph Chat Loop Started via {runtime.model.base_url}")
    print("Type 'exit' or 'quit' to end.")
    print("=" * 60)

    config = {"configurable": {"thread_id": "session-1"}}

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
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
                print(f"\nAgent: {latest_msg.content}")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat loop...")
            break
