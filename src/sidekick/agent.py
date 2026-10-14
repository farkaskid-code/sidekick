from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from sidekick.nodes import State, answer, research

builder = StateGraph(State)

builder.add_node("research", research)
builder.add_node("answer", answer)

builder.add_edge(START, "research")
builder.add_edge("research", "answer")
builder.add_edge("answer", END)


memory = MemorySaver()

graph = builder.compile(memory)
