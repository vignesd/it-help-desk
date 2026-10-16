"""REST API. Run from the project root: uvicorn api.main:app --reload"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

from helpdesk_rag.ingestion.ingest import ingest
from helpdesk_rag.schemas import AskRequest, AskResponse, Ticket
from helpdesk_rag.service import HelpDeskService, get_service

app = FastAPI(title="IT Help Desk RAG API", version="0.1.0")

ServiceDep = Annotated[HelpDeskService, Depends(get_service)]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, service: ServiceDep) -> AskResponse:
    return service.ask(req.question, req.session_id)


@app.post("/ingest")
def run_ingest(reset: bool = False) -> dict:
    return ingest(reset=reset)


@app.get("/tickets", response_model=list[Ticket])
def list_tickets(service: ServiceDep) -> list[Ticket]:
    return service.list_tickets()


@app.delete("/sessions/{session_id}")
def clear_session(session_id: str, service: ServiceDep) -> dict:
    if not service.clear_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "cleared": True}
