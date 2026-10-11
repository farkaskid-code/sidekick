from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from sidekick.nodes import State, call_model

builder = StateGraph(State)

builder.add_node("model", call_model)

builder.add_edge(START, "model")
builder.add_edge("model", END)

memory = MemorySaver()

graph = builder.compile(memory)
