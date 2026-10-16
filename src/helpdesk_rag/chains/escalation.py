import json
import re
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from helpdesk_rag.chains.prompts import TICKET_PROMPT
from helpdesk_rag.retrieval.vectorstore import ScoredDocs
from helpdesk_rag.schemas import AnswerDraft, Ticket, TicketDraft

_HANDOFF = re.compile(
    r"\b(human|real person|technician|someone from it|escalate"
    r"|(open|create|raise|log|file|submit)\s+(a\s+|an\s+)?(support\s+|it\s+)?ticket)\b",
    re.IGNORECASE,
)


USER_REQUESTED = "User asked for a technician or a ticket"


def wants_human(question: str) -> bool:
    return bool(_HANDOFF.search(question))


def escalation_reason(
    question: str, retrieved: ScoredDocs, draft: AnswerDraft | None
) -> str | None:
    """Return why the conversation must be escalated, or None if self-service is enough."""
    if wants_human(question):
        return USER_REQUESTED
    if not retrieved:
        return "No relevant knowledge base articles found"
    if draft is not None and not draft.can_answer:
        return "Knowledge base does not cover this issue"
    return None


class TicketDrafter:
    def __init__(self, llm: BaseChatModel):
        self.chain = TICKET_PROMPT | llm.with_structured_output(TicketDraft)

    def draft(self, question: str, history: list[BaseMessage], reason: str) -> TicketDraft:
        return self.chain.invoke({"question": question, "history": history, "reason": reason})


def new_ticket(draft: TicketDraft, *, session_id: str, question: str, reason: str) -> Ticket:
    return Ticket(
        **draft.model_dump(),
        ticket_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
        session_id=session_id,
        question=question,
        escalation_reason=reason,
        created_at=datetime.now(UTC),
    )


class TicketStore:
    """Append-only JSONL file of escalated tickets."""

    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()

    def save(self, ticket: Ticket) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, self.path.open("a", encoding="utf-8") as f:
            f.write(ticket.model_dump_json() + "\n")

    def list(self) -> list[Ticket]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as f:
            return [Ticket(**json.loads(line)) for line in f if line.strip()]
