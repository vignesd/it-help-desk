"""Offline fakes so tests never call OpenAI or Pinecone."""

from typing import Any

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable, RunnableLambda

from helpdesk_rag.chains.escalation import TicketStore
from helpdesk_rag.memory import SessionMemory
from helpdesk_rag.schemas import AnswerDraft, TicketDraft
from helpdesk_rag.service import HelpDeskService


class FakeLLM(Runnable):
    """Stand-in chat model.

    Plain invocations (the condense step) pop from `texts`. `with_structured_output(Schema)`
    pops pre-built objects of that schema from `structured[Schema]`. Every input is recorded.
    """

    def __init__(self, texts: list[str] | None = None, structured: dict | None = None):
        self.texts = list(texts or [])
        self.structured = {k: list(v) for k, v in (structured or {}).items()}
        self.calls: list[tuple[str, Any]] = []

    def invoke(self, input, config=None, **kwargs):
        self.calls.append(("text", input))
        return AIMessage(content=self.texts.pop(0))

    def with_structured_output(self, schema, **kwargs):
        def respond(prompt_value):
            self.calls.append((schema.__name__, prompt_value))
            return self.structured[schema].pop(0)

        return RunnableLambda(respond)


class FakeRetriever:
    def __init__(self, results: list[tuple[Document, float]] | None = None):
        self.results = results or []
        self.queries: list[str] = []

    def retrieve(self, query: str):
        self.queries.append(query)
        return list(self.results)


def make_doc(source: str, text: str = "Restart the GlobalConnect client.") -> Document:
    return Document(
        page_content=text,
        metadata={"source": source, "title": source.removesuffix(".md"), "category": "network"},
    )


def answer(text="1. Restart the client.", can_answer=True, cited=("vpn.md",)) -> AnswerDraft:
    return AnswerDraft(answer=text, can_answer=can_answer, cited_sources=list(cited))


def ticket_draft(**overrides) -> TicketDraft:
    data = {
        "title": "Badge reader broken",
        "category": "hardware",
        "priority": "P3",
        "summary": "Badge reader in building 7 does not respond.",
        "steps_tried": [],
        "user_impact": "Cannot enter the building with badge.",
    }
    return TicketDraft(**{**data, **overrides})


@pytest.fixture
def make_service(tmp_path):
    def _make(llm: FakeLLM, retriever: FakeRetriever) -> HelpDeskService:
        return HelpDeskService(
            llm=llm,
            retriever=retriever,
            memory=SessionMemory(max_turns=6),
            tickets=TicketStore(tmp_path / "tickets.jsonl"),
        )

    return _make
