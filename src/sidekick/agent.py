from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from sidekick.config import runtime
from sidekick.data import State
from sidekick.nodes import answer, critique, factcheck, plan, research


def needs_more_research(state: State):
    return (
        "no"
        if len(state["critique"].additional_research) == 0
        or state["loop_count"] >= runtime.max_loops
        else "yes"
    )


def needs_more_accuracy(state: State):
    return "no" if state["factual_accuracy"] > 80 else "yes"


builder = StateGraph(State)

builder.add_node("plan", plan)
builder.add_node("research", research)
builder.add_node("answer", answer)
builder.add_node("factcheck", factcheck)
builder.add_node("critique", critique)


builder.add_edge(START, "plan")
builder.add_edge("plan", "research")
builder.add_edge("research", "answer")
builder.add_edge("answer", "factcheck")
builder.add_conditional_edges(
    "factcheck", needs_more_accuracy, {"yes": "plan", "no": "critique"}
)
builder.add_conditional_edges(
    "critique", needs_more_research, {"yes": "research", "no": END}
)

memory = MemorySaver()

graph = builder.compile(memory)
