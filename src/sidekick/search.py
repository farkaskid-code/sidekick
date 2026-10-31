from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from rich.console import Console

from sidekick.config import get_model
from sidekick.data import PROMPT, Role
from sidekick.tools import web_search

console = Console()


class SearchState(TypedDict):
    messages: Annotated[list, add_messages]


class SearchAgent:
    def __init__(self, role: Role) -> None:
        self.role = role
        self.model = get_model(role).bind_tools([web_search])

        def search(state: SearchState):
            response = self.model.invoke(state["messages"])

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

    def run(self, query: str):
        messages = [SystemMessage(PROMPT[self.role]), HumanMessage(query)]

        return self.agent.invoke(
            {"messages": messages},
            config={"configurable": {"thread_id": self.role}},
        )
