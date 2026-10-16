import pytest
from fastapi.testclient import TestClient

from api.main import app
from helpdesk_rag.schemas import AnswerDraft, TicketDraft
from helpdesk_rag.service import get_service
from tests.conftest import FakeLLM, FakeRetriever, answer, make_doc, ticket_draft


@pytest.fixture
def client(make_service):
    llm = FakeLLM(structured={AnswerDraft: [answer()], TicketDraft: [ticket_draft()]})
    service = make_service(llm, FakeRetriever([(make_doc("vpn.md"), 0.8)]))
    app.dependency_overrides[get_service] = lambda: service
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_ask_and_clear_session(client):
    resp = client.post("/ask", json={"question": "How do I connect to VPN?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"] == "1. Restart the client."
    assert body["escalated"] is False
    assert body["sources"][0]["source"] == "vpn.md"

    session_id = body["session_id"]
    assert client.delete(f"/sessions/{session_id}").status_code == 200
    assert client.delete(f"/sessions/{session_id}").status_code == 404


def test_ask_validates_question(client):
    assert client.post("/ask", json={"question": ""}).status_code == 422


def test_escalated_ticket_is_listed(client):
    body = client.post("/ask", json={"question": "I need a technician for my VPN"}).json()
    assert body["escalated"] is True

    tickets = client.get("/tickets").json()
    assert [t["ticket_id"] for t in tickets] == [body["ticket"]["ticket_id"]]
