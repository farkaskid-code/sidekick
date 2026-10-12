from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage, trim_messages
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from rich.console import Console

from sidekick.config import runtime

model = ChatOllama(
    model=runtime.model.name,
    base_url=runtime.model.base_url,
    num_ctx=runtime.model.num_ctx,
    temperature=runtime.model.temperature,
)

console = Console()

SYSTEM_PROMPT = SystemMessage(content=(Path(__file__).parent / "prompt.md").read_text())

trimmer = trim_messages(
    max_tokens=int(runtime.model.num_ctx * 0.9),
    token_counter="approximate",
    strategy="last",
    include_system=True,
    start_on="human",
)


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def call_model(state: State):
    messages = state["messages"]
    if not any(msg == SYSTEM_PROMPT for msg in messages):
        state["messages"] = [SYSTEM_PROMPT] + messages

    with console.status("[green]Thinking..."):
        response = model.invoke(trimmer.invoke(state["messages"]))
    return {"messages": [response]}
