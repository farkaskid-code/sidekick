from typing import Annotated, TypedDict

from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from rich.console import Console

from sidekick.config import runtime
from sidekick.tools import web_search


# State
class SearchState(TypedDict):
    messages: Annotated[list, add_messages]


builder = StateGraph(SearchState)


# Nodes
search_model = ChatOllama(
    model=runtime.models.small.name,
    base_url=runtime.models.small.base_url,
    num_ctx=runtime.models.small.num_ctx,
    temperature=runtime.models.small.temperature,
).bind_tools([web_search])

console = Console()


def search(state: SearchState):
    response = search_model.invoke(state["messages"])

    return {"messages": [response]}


builder.add_node("search", search)
builder.add_node("search_tool", ToolNode([web_search]))

# Edges
builder.add_edge(START, "search")
builder.add_conditional_edges(
    "search", tools_condition, {"tools": "search_tool", END: END}
)
builder.add_edge("search_tool", "search")

search_agent = builder.compile(MemorySaver())
