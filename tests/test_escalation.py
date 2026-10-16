import pytest

from helpdesk_rag.chains.escalation import TicketStore, escalation_reason, new_ticket, wants_human
from tests.conftest import answer, make_doc, ticket_draft


@pytest.mark.parametrize(
    "question",
    [
        "Can I talk to a human?",
        "please open a ticket",
        "Create a support ticket for this",
        "I need a technician",
        "escalate this",
    ],
)
def test_wants_human(question):
    assert wants_human(question)


@pytest.mark.parametrize("question", ["How do I connect to VPN?", "My ticket printer jams"])
def test_does_not_want_human(question):
    assert not wants_human(question)


def test_reason_no_context():
    assert "No relevant" in escalation_reason("badge reader broken", [], None)


def test_reason_cannot_answer():
    reason = escalation_reason("q", [(make_doc("vpn.md"), 0.5)], answer(can_answer=False))
    assert "does not cover" in reason


def test_reason_explicit_request_wins():
    reason = escalation_reason("open a ticket please", [(make_doc("vpn.md"), 0.9)], answer())
    assert "asked for" in reason


def test_no_escalation_when_answered():
    assert escalation_reason("vpn?", [(make_doc("vpn.md"), 0.9)], answer()) is None


def test_ticket_store_roundtrip(tmp_path):
    store = TicketStore(tmp_path / "sub" / "tickets.jsonl")
    assert store.list() == []

    ticket = new_ticket(ticket_draft(), session_id="s1", question="q", reason="r")
    store.save(ticket)

    [loaded] = store.list()
    assert loaded == ticket
    assert loaded.ticket_id.startswith("INC-")
