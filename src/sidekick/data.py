from typing import TypedDict

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    topics: list[str] = Field(description="List of research topics")


class Information(BaseModel):
    topic: str = Field(description="Title of the research topic")
    content: str = Field(description="Research content")

    def __str__(self) -> str:
        return f"### Topic\n{self.topic}\n\n### Content\n{self.content}"


class Research(BaseModel):
    topics: list[Information] = Field(
        description="A list of research for all the different topics"
    )

    def __str__(self) -> str:
        return "\n---\n".join([str(r) for r in self.topics])


class Critique(BaseModel):
    passed: bool = Field(
        description="If the answer is ok and doesn't need more research"
    )
    notes: str = Field(description="A brief one/two line verdict of the evaluation")
    additional_research: list[str] = Field(
        description="Additional research topics if required"
    )


class State(TypedDict):
    question: str
    planning: ResearchPlan
    research: Research
    answer: str
    critique: Critique
    loop_count: int


PROMPT = {
    "plan": (
        "You are research planner whose job is to provide 3-4 topics"
        " that should be researched to answer the user's query? "
        "Output a simple list with topic names. "
        "Use web_search when you need external information."
        "You may perform multiple searches if necessary"
    ),
    "research": (
        "You are a researcher whose job is to provide a summary of "
        "useful facts and information for the topic given by the user. "
        "Use web_search when you need external information."
        "You may perform multiple searches if necessary"
    ),
    "critic": (
        "You are critic whose job is to critique the answer for a given question "
        "based on the provided research. Tell the user if the answer needs additional research "
        "and provide those research topics as additional research."
    ),
    "answer": (
        "Your job is to craft a detailed answer for the user's "
        "question based on the research provided."
    ),
    "factcheck": (
        "Your job is to factcheck the answer for a given question. "
        "Use web_search when you need external and latest information. "
        "Only output a percentage value for factual accuracy"
    ),
}
