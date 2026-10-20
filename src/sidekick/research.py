from typing import Annotated, TypedDict

from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from rich.console import Console

from sidekick.config import runtime
from sidekick.tools import web_search


# State
class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]


builder = StateGraph(ResearchState)


# Nodes
research_model = ChatOllama(
    model=runtime.models.small.name,
    base_url=runtime.models.small.base_url,
    num_ctx=runtime.models.small.num_ctx,
    temperature=runtime.models.small.temperature,
).bind_tools([web_search])

console = Console()


def research(state: ResearchState):
    response = research_model.invoke(state["messages"])

    return {"messages": [response]}


builder.add_node("research", research)
builder.add_node("search_tool", ToolNode([web_search]))

# Edges
builder.add_edge(START, "research")
builder.add_conditional_edges(
    "research", tools_condition, {"tools": "search_tool", END: END}
)
builder.add_edge("search_tool", "research")

agent = builder.compile(MemorySaver())
