# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from the project root with the venv active (`.venv\Scripts\activate`).

```bash
pip install -e ".[dev]"                          # install (src layout, editable)
pytest                                           # all tests (offline, no keys needed)
pytest tests/test_service.py::test_answer_from_kb   # single test
ruff check . && ruff format .                    # lint / format
python -m helpdesk_rag.ingestion.ingest [--reset]   # load data/kb into Pinecone
python -m helpdesk_rag.retrieval.search "query" [--all]   # inspect raw retrieval scores (no LLM)
uvicorn api.main:app --reload                    # REST API (/docs for Swagger)
streamlit run ui/streamlit_app.py                # chat UI
```

Ingestion and the running apps need `OPENAI_API_KEY` and `PINECONE_API_KEY` in `.env`. Tests do not.

## Architecture

RAG assistant for IT help desk: LangChain + OpenAI (chat and embeddings) + Pinecone.

- **`HelpDeskService` (`src/helpdesk_rag/service.py`) is the single entry point.** Both `api/main.py` and `ui/streamlit_app.py` call `service.ask()`. Streamlit imports the service directly, not through the API, so the two interfaces have **separate in-process memory**. Put new behavior in the service or chains, not in either interface.
- **The `ask()` flow:** `RagChain.run` (condense the question with history, then `Retriever.retrieve`, then a structured `AnswerDraft`) → `escalation_reason()` → if escalating, `TicketDrafter` returns a `TicketDraft`, which is wrapped into a `Ticket` and appended to `data/tickets/tickets.jsonl` → `SessionMemory.add_turn`.
- **Escalation triggers** (`chains/escalation.py`): no chunks passed the score threshold (the answer LLM is skipped entirely), `AnswerDraft.can_answer` is false, or the user asked for a human or ticket (`_HANDOFF` regex). When the user asks for a human but the KB has an answer, the reply contains both the answer and the ticket reference.
- **LLM outputs are Pydantic models** (`schemas.py`) used via `llm.with_structured_output(...)`. Field descriptions in `AnswerDraft` and `TicketDraft` act as prompt instructions, so changing them changes model behavior. Prompts are in `chains/prompts.py`.
- **Retrieval** sits behind the `Retriever` protocol (`retrieve(query) -> list[(Document, score)]`). `PineconeRetriever` filters by `score_threshold` (cosine similarity, default 0.45, tuned for `text-embedding-3-small`, whose scores run low).
- **Ingestion** (`ingestion/`): loaders read `.md`/`.txt`/`.pdf`, and YAML front matter supplies `title`/`category`. Metadata must stay Pinecone-safe (str/number/bool). Vector IDs are `sha1(source:page:chunk_index)`, so re-ingesting overwrites chunks. A doc that shrinks leaves stale chunks behind unless you use `--reset`.
- **Config:** `config.py` `Settings` (pydantic-settings, reads `.env` at the project root), with a cached `get_settings()`. pydantic-settings does **not** export values to `os.environ`, so API keys are passed explicitly to the OpenAI/Pinecone clients.
- **TLS:** `helpdesk_rag/__init__.py` calls `truststore.inject_into_ssl()` so HTTPS verifies against the OS certificate store. The dev machine is behind a corporate proxy, and without this every OpenAI/Pinecone call fails with `CERTIFICATE_VERIFY_FAILED`.
- **Embedding dimension:** `get_embeddings` passes `EMBEDDING_DIMENSION` to `text-embedding-3-*` models. `ensure_index` refuses to ingest into an existing index whose dimension differs. The local `.env` uses the existing 512-dimension `it-help-desk` index, because the Pinecone project is at its 5-index limit.

## Testing conventions

- Tests never hit the network. `tests/conftest.py` provides `FakeLLM`, which queues plain-text replies for the condense step and queues Pydantic objects per schema for `with_structured_output`. It also provides `FakeRetriever` and a `make_service` fixture that writes tickets to `tmp_path`.
- API tests swap the service via `app.dependency_overrides[get_service]`.
- Each `FakeLLM` queue must hold exactly as many items as the code path will consume. The condense step only runs when the session already has history.
