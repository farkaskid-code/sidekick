from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages

from sidekick.config import runtime

model = ChatOllama(model=runtime.model.name, base_url=runtime.model.base_url)


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def call_model(state: State):
    response = model.invoke(state["messages"])
    return {"messages": [response]}
