from typing import TypedDict

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    topics: list[str] = Field(description="List of research topics")


class Research(BaseModel):
    topic: str = Field(description="Title of the research topic")
    content: str = Field(description="Research content")

    def __str__(self) -> str:
        return f"Topic: {self.topic}\n----\nContent: {self.content}"


class ResearchResult(BaseModel):
    research: list[Research] = Field(
        description="A list of research for all the different topics"
    )

    def __str__(self) -> str:
        return "\n\n====\n\n".join([str(r) for r in self.research])


class State(TypedDict):
    question: str
    planning: ResearchPlan
    research: ResearchResult
    answer: str
