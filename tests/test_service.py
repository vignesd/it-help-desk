from langchain_core.messages import HumanMessage

from helpdesk_rag.schemas import AnswerDraft, TicketDraft
from tests.conftest import FakeLLM, FakeRetriever, answer, make_doc, ticket_draft


def test_answer_from_kb(make_service):
    llm = FakeLLM(structured={AnswerDraft: [answer()]})
    retriever = FakeRetriever([(make_doc("vpn.md"), 0.8), (make_doc("wifi.md"), 0.5)])
    service = make_service(llm, retriever)

    resp = service.ask("How do I connect to VPN?", session_id="s1")

    assert resp.answer == "1. Restart the client."
    assert not resp.escalated and resp.ticket is None
    # Only the cited source is returned.
    assert [s.source for s in resp.sources] == ["vpn.md"]
    assert retriever.queries == ["How do I connect to VPN?"]
    assert service.list_tickets() == []


def test_sources_resolve_numeric_citations(make_service):
    # Models often cite the passage number from the context ("[2]") instead of the file name.
    llm = FakeLLM(structured={AnswerDraft: [answer(cited=["[2]"])]})
    retriever = FakeRetriever([(make_doc("vpn.md"), 0.8), (make_doc("wifi.md"), 0.5)])

    resp = make_service(llm, retriever).ask("wifi?", session_id="s1")

    assert [s.source for s in resp.sources] == ["wifi.md"]


def test_unresolvable_citations_fall_back_to_all_sources(make_service):
    llm = FakeLLM(structured={AnswerDraft: [answer(cited=["something else"])]})
    retriever = FakeRetriever([(make_doc("vpn.md"), 0.8), (make_doc("wifi.md"), 0.5)])

    resp = make_service(llm, retriever).ask("vpn?", session_id="s1")

    assert [s.source for s in resp.sources] == ["vpn.md", "wifi.md"]


def test_follow_up_uses_memory_and_condensed_question(make_service):
    llm = FakeLLM(
        texts=["VPN shows certificate expired error"],
        structured={AnswerDraft: [answer(), answer("1. Renew the certificate.")]},
    )
    retriever = FakeRetriever([(make_doc("vpn.md"), 0.8)])
    service = make_service(llm, retriever)

    service.ask("How do I connect to VPN?", session_id="s1")
    resp = service.ask("it says certificate expired", session_id="s1")

    assert resp.answer == "1. Renew the certificate."
    assert retriever.queries[-1] == "VPN shows certificate expired error"
    # The condense prompt received the first turn as history.
    condense_input = next(inp for kind, inp in llm.calls if kind == "text")
    assert any(
        isinstance(m, HumanMessage) and m.content == "How do I connect to VPN?"
        for m in condense_input.to_messages()
    )


def test_new_session_has_no_history(make_service):
    llm = FakeLLM(structured={AnswerDraft: [answer(), answer()]})
    service = make_service(llm, FakeRetriever([(make_doc("vpn.md"), 0.8)]))

    first = service.ask("vpn?")
    second = service.ask("vpn again?")

    assert first.session_id != second.session_id
    assert not any(kind == "text" for kind, _ in llm.calls)  # no condense call needed


def test_escalates_when_nothing_retrieved(make_service):
    llm = FakeLLM(structured={TicketDraft: [ticket_draft()]})
    service = make_service(llm, FakeRetriever([]))

    resp = service.ask("My badge reader in building 7 is broken", session_id="s1")

    assert resp.escalated
    assert resp.ticket.priority == "P3"
    assert resp.ticket.ticket_id in resp.answer
    assert resp.sources == []
    # The answer LLM is skipped when there is no context.
    assert [kind for kind, _ in llm.calls] == ["TicketDraft"]
    assert [t.ticket_id for t in service.list_tickets()] == [resp.ticket.ticket_id]


def test_escalates_but_keeps_answer_when_user_asks_for_human(make_service):
    llm = FakeLLM(structured={AnswerDraft: [answer()], TicketDraft: [ticket_draft()]})
    service = make_service(llm, FakeRetriever([(make_doc("vpn.md"), 0.8)]))

    resp = service.ask("VPN broken, please open a ticket", session_id="s1")

    assert resp.escalated
    assert resp.answer.startswith("1. Restart the client.")
    assert "technician can follow up" in resp.answer


def test_clear_session(make_service):
    llm = FakeLLM(structured={AnswerDraft: [answer()]})
    service = make_service(llm, FakeRetriever([(make_doc("vpn.md"), 0.8)]))

    service.ask("vpn?", session_id="s1")

    assert service.clear_session("s1")
    assert not service.clear_session("s1")
