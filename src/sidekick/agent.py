from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from sidekick.config import runtime
from sidekick.data import State
from sidekick.nodes import answer, critique, plan, research, web_research

builder = StateGraph(State)

builder.add_node("research", research)
builder.add_node("plan", plan)
builder.add_node("answer", answer)
builder.add_node("critique", critique)


def needs_more_research(state: State):
    return (
        "no"
        if len(state["critique"].additional_research) == 0
        or state["loop_count"] >= runtime.max_loops
        else "yes"
    )


builder.add_edge(START, "plan")
builder.add_edge("plan", "research")
builder.add_edge("research", "answer")
builder.add_edge("answer", "critique")
builder.add_conditional_edges(
    "critique", needs_more_research, {"yes": "research", "no": END}
)

memory = MemorySaver()

graph = builder.compile(memory)
