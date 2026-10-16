import uuid
from functools import lru_cache

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from helpdesk_rag.chains.escalation import (
    USER_REQUESTED,
    TicketDrafter,
    TicketStore,
    escalation_reason,
    new_ticket,
)
from helpdesk_rag.chains.rag_chain import RagChain
from helpdesk_rag.config import Settings, get_settings
from helpdesk_rag.memory import SessionMemory
from helpdesk_rag.retrieval.vectorstore import PineconeRetriever, Retriever, ScoredDocs
from helpdesk_rag.schemas import AnswerDraft, AskResponse, Source, Ticket


def resolve_citations(cited: list[str], retrieved: ScoredDocs) -> set[str]:
    """Map LLM citations to source names. Models cite either the file name or the
    passage number from the context (`[2]`), so accept both."""
    names = {doc.metadata.get("source") for doc, _ in retrieved}
    resolved = set()
    for ref in cited:
        ref = ref.strip().strip("[]")
        if ref in names:
            resolved.add(ref)
        elif ref.isdigit() and 1 <= int(ref) <= len(retrieved):
            resolved.add(retrieved[int(ref) - 1][0].metadata.get("source"))
    return resolved


def build_sources(retrieved: ScoredDocs, draft: AnswerDraft | None) -> list[Source]:
    """One Source per KB file (best score wins), limited to cited files when citations resolve."""
    cited = (
        resolve_citations(draft.cited_sources, retrieved) if draft and draft.can_answer else set()
    )
    best: dict[str, Source] = {}
    for doc, score in retrieved:
        meta = doc.metadata
        name = meta.get("source", "unknown")
        if cited and name not in cited:
            continue
        if name not in best or score > best[name].score:
            best[name] = Source(
                source=name,
                title=meta.get("title", name),
                category=meta.get("category", "general"),
                score=round(float(score), 3),
                snippet=doc.page_content[:200],
            )
    return sorted(best.values(), key=lambda s: s.score, reverse=True)


def escalation_answer(draft: AnswerDraft | None, ticket: Ticket) -> str:
    ref = f"**{ticket.ticket_id}** (priority {ticket.priority})"
    if draft and draft.can_answer:
        return f"{draft.answer}\n\nI've also opened ticket {ref} so a technician can follow up."
    if ticket.escalation_reason == USER_REQUESTED:
        return f"I've opened ticket {ref} as requested. A technician will contact you."
    return (
        "I couldn't find a documented fix for this in the IT knowledge base, so I've opened "
        f"ticket {ref} for the support team. A technician will contact you."
    )


class HelpDeskService:
    """Single entry point used by both the FastAPI app and the Streamlit UI."""

    def __init__(
        self,
        llm: BaseChatModel,
        retriever: Retriever,
        memory: SessionMemory,
        tickets: TicketStore,
    ):
        self.rag = RagChain(llm, retriever)
        self.drafter = TicketDrafter(llm)
        self.memory = memory
        self.tickets = tickets

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "HelpDeskService":
        settings = settings or get_settings()
        llm = ChatOpenAI(
            model=settings.openai_chat_model,
            temperature=0,
            api_key=settings.openai_api_key or None,
        )
        return cls(
            llm=llm,
            retriever=PineconeRetriever.from_settings(settings),
            memory=SessionMemory(settings.memory_max_turns),
            tickets=TicketStore(settings.tickets_file),
        )

    def ask(self, question: str, session_id: str | None = None) -> AskResponse:
        session_id = session_id or uuid.uuid4().hex
        history = self.memory.get_messages(session_id)

        result = self.rag.run(question, history)
        reason = escalation_reason(question, result.retrieved, result.draft)

        ticket = None
        if reason:
            draft = self.drafter.draft(result.standalone_question, history, reason)
            ticket = new_ticket(draft, session_id=session_id, question=question, reason=reason)
            self.tickets.save(ticket)
            answer = escalation_answer(result.draft, ticket)
        else:
            answer = result.draft.answer

        self.memory.add_turn(session_id, question, answer)
        return AskResponse(
            session_id=session_id,
            answer=answer,
            sources=build_sources(result.retrieved, result.draft),
            escalated=ticket is not None,
            escalation_reason=reason,
            ticket=ticket,
        )

    def clear_session(self, session_id: str) -> bool:
        return self.memory.clear(session_id)

    def list_tickets(self) -> list[Ticket]:
        return self.tickets.list()


@lru_cache
def get_service() -> HelpDeskService:
    return HelpDeskService.from_settings()
