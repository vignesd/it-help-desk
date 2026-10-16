from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AnswerDraft(BaseModel):
    """Structured output of the answer LLM call."""

    answer: str = Field(description="The answer to the user, in markdown. Use numbered steps.")
    can_answer: bool = Field(
        description="True only if the provided context actually contains a fix for the issue."
    )
    cited_sources: list[str] = Field(
        description="File names (the `source:` value, e.g. vpn-troubleshooting.md) of the "
        "context passages used in the answer."
    )


class TicketDraft(BaseModel):
    """Structured output of the ticket-drafting LLM call."""

    title: str = Field(description="Short ticket title, under 80 characters.")
    category: str = Field(
        description="One of: network, accounts, email, hardware, software, printing, other."
    )
    priority: Literal["P1", "P2", "P3", "P4"] = Field(
        description="P1 = outage/many users blocked, P2 = one user fully blocked, "
        "P3 = degraded but has a workaround, P4 = request or question."
    )
    summary: str = Field(description="2-4 sentence description of the problem for a technician.")
    steps_tried: list[str] = Field(
        description="Troubleshooting steps the user already tried, from the conversation."
    )
    user_impact: str = Field(description="How this affects the user's work.")


class Ticket(TicketDraft):
    ticket_id: str
    session_id: str
    question: str
    escalation_reason: str
    created_at: datetime


class Source(BaseModel):
    source: str
    title: str
    category: str
    score: float
    snippet: str


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str | None = None


class AskResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[Source]
    escalated: bool
    escalation_reason: str | None = None
    ticket: Ticket | None = None
