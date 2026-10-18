from typing import TypedDict

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    topics: list[str] = Field(description="List of research topics")


class Information(BaseModel):
    topic: str = Field(description="Title of the research topic")
    content: str = Field(description="Research content")

    def __str__(self) -> str:
        return f"Topic: {self.topic}\n----\nContent: {self.content}"


class Research(BaseModel):
    topics: list[Information] = Field(
        description="A list of research for all the different topics"
    )

    def __str__(self) -> str:
        return "\n\n====\n\n".join([str(r) for r in self.topics])


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
