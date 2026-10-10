import os
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


OLLAMA_BASE_URL = os.getenv("OLLAMA_API_BASE")

llm = ChatOllama(
    model="qwen3:14b",  # Change to your target model
    base_url=OLLAMA_BASE_URL,
    temperature=0.5,
)


def call_model(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(AgentState)

builder.add_node("agent", call_model)

builder.add_edge(START, "agent")
builder.add_edge("agent", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)


def main():
    print("=" * 60)
    print(f"Ollama LangGraph Chat Loop Started via {OLLAMA_BASE_URL}")
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
