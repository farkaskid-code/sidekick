from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from rich.console import Console

from sidekick.config import runtime
from sidekick.data import PROMPT
from sidekick.tools import web_search


# State
class SearchState(TypedDict):
    messages: Annotated[list, add_messages]


# Nodes
search_model = ChatOllama(
    model=runtime.models.small.name,
    base_url=str(runtime.models.small.base_url),
    num_ctx=40960,
    temperature=0.7,
).bind_tools([web_search])

console = Console()


class SearchAgent:
    def __init__(self, model: ChatOllama) -> None:
        def search(state: SearchState):
            response = model.invoke(state["messages"])

            return {"messages": [response]}

        builder = StateGraph(SearchState)
        builder.add_node("search", search)
        builder.add_node("search_tool", ToolNode([web_search]))

        # Edges
        builder.add_edge(START, "search")
        builder.add_conditional_edges(
            "search", tools_condition, {"tools": "search_tool", END: END}
        )
        builder.add_edge("search_tool", "search")

        self.agent = builder.compile(MemorySaver())

    def run(self, system_prompt: str, query: str):
        messages = [SystemMessage(system_prompt), HumanMessage(query)]

        return self.agent.invoke(
            {"messages": messages}, config={"configurable": {"thread_id": "factcheck"}}
        )
