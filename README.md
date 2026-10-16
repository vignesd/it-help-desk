# IT Help Desk RAG Assistant

A retrieval-augmented generation (RAG) assistant for IT support. It answers employee questions
from an IT knowledge base, cites the articles it used, remembers the conversation, and drafts a
support ticket when the knowledge base can't solve the problem.

**Stack:** LangChain · OpenAI (chat + embeddings) · Pinecone · FastAPI · Streamlit

## How it works

```
INGEST (once, or whenever data/kb changes)
  data/kb/*.md|txt|pdf ──► load + front matter ──► split into chunks
                        ──► OpenAI embeddings ──► upsert into Pinecone index

ASK (every question)
  question ──► rewrite as standalone question (uses chat history)
           ──► Pinecone similarity search (top-k, drop scores below threshold)
           ──► OpenAI answer grounded in the retrieved chunks, with citations
           ──► escalate?  no relevant chunks / KB can't answer / user asked for a human
                   └─► OpenAI drafts a ticket ──► data/tickets/tickets.jsonl
```

### Escalation rules

A ticket is created when **any** of these is true:

| Trigger | Example | Reply |
|---|---|---|
| No chunk scores above `SCORE_THRESHOLD` (the answer LLM is skipped) | "My badge reader in building 7 is broken" | "I couldn't find a documented fix… opened ticket INC-XXXX" |
| The LLM decides the retrieved articles don't solve the issue (`can_answer = false`) | A question near a KB topic that the KB doesn't actually cover | Same as above |
| The user asks for a human or a ticket ("open a ticket", "technician", "escalate"…) | "VPN still fails after renewing, please open a ticket" | The KB answer (if any) **plus** the ticket, or "I've opened ticket INC-XXXX as requested" |

Tickets include a title, category, priority (P1–P4), summary, steps already tried (taken from the
conversation) and user impact. They are appended to `data/tickets/tickets.jsonl`.

### Project layout

```
src/helpdesk_rag/
  config.py            settings (from .env)
  ingestion/           load → split → embed → upsert   (CLI: ingestion.ingest)
  retrieval/           Pinecone vector store, retriever (CLI: retrieval.search)
  chains/              prompts, RAG chain, escalation + ticket store
  memory.py            per-session chat history
  service.py           HelpDeskService.ask() — used by both the API and the UI
api/main.py            FastAPI app
ui/streamlit_app.py    Streamlit chat UI
data/kb/               knowledge base articles (8 samples included)
tests/                 offline tests (fake LLM and retriever)
```

---

## Getting started

Run every command from the project root folder (`it-help-desk/`).

**Already set up?** If `.venv` exists, the package is installed and the keys are configured, skip to:
```powershell
.venv\Scripts\Activate.ps1                       # macOS/Linux: source .venv/bin/activate
pytest                                           # sanity check, offline
python -m helpdesk_rag.ingestion.ingest          # safe to re-run
streamlit run ui/streamlit_app.py                # chat UI (Step 5)
uvicorn api.main:app --reload                    # REST API (Step 6), in a second terminal
```

### Prerequisites

- Python 3.11 or newer (3.13 recommended)
- An **OpenAI API key**: https://platform.openai.com/api-keys
- A **Pinecone API key**: https://app.pinecone.io → *API Keys*. The free Starter plan is enough.
  You don't need to create an index yourself; ingest creates one if it's missing.

### Step 1 — Create a virtual environment and install

Windows (PowerShell):
```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Check the install (offline, no keys needed):
```bash
pytest        # expect: 30 passed
```

### Step 2 — Configure API keys

```powershell
copy .env.example .env      # macOS/Linux: cp .env.example .env
```

Open `.env` and set:
```ini
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pcsk_...
```

If either key is already set as an environment variable, you can leave it out of `.env`.

**Choosing the Pinecone index.** By default ingest creates an index named `it-helpdesk`
(1536 dimensions, AWS `us-east-1`) and writes to the `kb` namespace. To **reuse an existing
index** instead, for example because your plan's index limit is reached, point to it and match its
dimension. `text-embedding-3-small` can produce 512- or 1536-dimension vectors:
```ini
PINECONE_INDEX=it-help-desk
EMBEDDING_DIMENSION=512
```
Find an index's dimension in the Pinecone console. Ingest stops with a clear message if the two
don't match.

### Step 3 — Ingest the knowledge base into Pinecone

```bash
python -m helpdesk_rag.ingestion.ingest
```

This command:
1. Loads every `.md`, `.txt` and `.pdf` file in `data/kb/` (8 sample IT articles are included).
2. Splits them into chunks of about 800 characters, preferring `##` heading boundaries.
3. Creates the Pinecone serverless index (cosine metric) if it doesn't exist. Creating it can
   take a minute on the first run.
4. Embeds the chunks with `text-embedding-3-small` and upserts them.

Output with the sample KB:
```json
{
  "documents": 8,
  "chunks": 22,
  "index": "it-help-desk",
  "namespace": "kb"
}
```

Re-running ingest is safe because each chunk has a fixed ID, so it overwrites instead of
duplicating. If you **edit or delete** KB files, use `--reset` to wipe the namespace first so
old chunks don't linger:
```bash
python -m helpdesk_rag.ingestion.ingest --reset
```

To confirm the vector count, open the Pinecone console: *Indexes → your index → Namespaces → kb*.

### Step 4 — Check retrieval

Before involving the chat LLM, confirm that searches return the right KB chunks. This calls only
the embeddings API and Pinecone:

```bash
python -m helpdesk_rag.retrieval.search "How do I connect to VPN?"
```

```
threshold = 0.45

[PASS] 0.661  vpn-troubleshooting.md
        ## VPN will not connect 1. Check that your normal internet connection works by ...

[PASS] 0.637  vpn-troubleshooting.md
        # VPN Connection Troubleshooting The company uses the GlobalConnect VPN client ...
```

Then try a question the KB doesn't cover. Nothing should pass, which means the assistant
would escalate it:
```bash
python -m helpdesk_rag.retrieval.search "My badge reader in building 7 is broken" --all
```

Options: `--all` also shows chunks below the threshold, which helps with tuning. `--k 8` returns
more results.

Measured scores with the sample KB (512-dimension embeddings):

| Question | Top match | Score |
|---|---|---|
| How do I connect to VPN? | vpn-troubleshooting.md | 0.661 |
| VPN says certificate expired | vpn-troubleshooting.md | 0.620 |
| my account keeps getting locked | account-lockout.md | 0.650 |
| outlook stuck on loading profile | outlook-email-issues.md | 0.664 |
| how do I print to the office printer | printer-setup.md | 0.606 |
| My badge reader in building 7 is broken | *(printer-setup.md)* | 0.391 → escalated |
| what is the cafeteria menu today | *(outlook-email-issues.md)* | 0.221 → escalated |

Relevant chunks scored **0.48–0.66** and off-topic ones **0.39 or lower**, which is why the
default threshold is **0.45**. Re-check these numbers when you add your own articles or change
the embedding model or dimension.

### Step 5 — Run the chat UI

```bash
streamlit run ui/streamlit_app.py
```

This opens http://localhost:8501. Try this conversation:

1. `outlook stuck on loading profile` → four numbered steps (close Outlook, safe mode, disable
   add-ins, Repair Office) and a **Sources (1)** expander citing `outlook-email-issues.md`.
2. `safe mode also fails` → a follow-up that uses the earlier messages. It skips the steps
   already tried and goes straight to **Run Repair Office from the Software Center**.
3. `My badge reader in building 7 is broken` → an escalation message and a yellow ticket card,
   e.g. **Ticket INC-DE4BD88E · P2 · hardware**.

The sidebar has **New conversation** (clears the memory) and **Re-ingest knowledge base**.

### Step 6 — Run the REST API (optional)

```bash
uvicorn api.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive Swagger docs, or call the API directly:

```powershell
# PowerShell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/ask `
  -ContentType "application/json" `
  -Body '{"question": "outlook stuck on loading profile"}'
```
```bash
# bash / curl
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "outlook stuck on loading profile"}'
```

Response (shortened):
```json
{
  "session_id": "d7b72ecd307040a2bd80b3dd027a4010",
  "answer": "1. Close Outlook completely ...\n2. Start Outlook in safe mode ...",
  "sources": [
    {"source": "outlook-email-issues.md", "title": "Outlook and Email Issues",
     "category": "email", "score": 0.664, "snippet": "..."}
  ],
  "escalated": false,
  "escalation_reason": null,
  "ticket": null
}
```

To ask a follow-up, send the returned `session_id` with the next question:
```json
{"question": "safe mode also fails", "session_id": "d7b72ecd307040a2bd80b3dd027a4010"}
```

| Endpoint                   | Purpose                                                 |
|----------------------------|---------------------------------------------------------|
| `POST /ask`                | `{"question": "...", "session_id": "optional"}`         |
| `POST /ingest?reset=false` | Re-ingest `data/kb`                                     |
| `GET /tickets`             | List escalated tickets                                  |
| `DELETE /sessions/{id}`    | Clear one conversation's memory (404 if it doesn't exist) |
| `GET /health`              | Health check                                            |

The API and the Streamlit UI keep **separate** conversation memory. Memory is held in the
process and is lost on restart. Both write escalated tickets to `data/tickets/tickets.jsonl`;
delete that file to start with no tickets.

---

## Adding your own knowledge base articles

Put `.md`, `.txt` or `.pdf` files in `data/kb/` (subfolders are fine), then run ingest again
(with `--reset` if you changed or removed files). Markdown files can start with front matter,
which is stored as metadata and shown in citations:

```markdown
---
title: VPN Connection Troubleshooting
category: network
---

# VPN Connection Troubleshooting
...
```

Without front matter, the title comes from the file name and the category is `general`.

Tips for good retrieval:
- Use a `##` heading per problem. The splitter prefers to break at headings.
- Include exact error messages ("Certificate expired"), since users search with them.
- Re-run Step 4 for a few typical questions and adjust `SCORE_THRESHOLD` if needed.

## Configuration

Settings live in `src/helpdesk_rag/config.py`. Override any of them in `.env` (see `.env.example`).

| Variable                 | Default                  | Notes                                        |
|--------------------------|--------------------------|----------------------------------------------|
| `OPENAI_CHAT_MODEL`      | `gpt-4o-mini`            | Answer, question-rewrite and ticket model    |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Changing it requires a new index + re-ingest |
| `EMBEDDING_DIMENSION`    | `1536`                   | Must equal the index dimension (512 also works for `text-embedding-3-*`) |
| `PINECONE_INDEX`         | `it-helpdesk`            | Created if missing                           |
| `PINECONE_NAMESPACE`     | `kb`                     |                                              |
| `PINECONE_CLOUD` / `PINECONE_REGION` | `aws` / `us-east-1` | Used only when the index is created |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `800` / `120`      | Re-ingest with `--reset` after changing      |
| `TOP_K`                  | `4`                      | Chunks retrieved per question                |
| `SCORE_THRESHOLD`        | `0.45`                   | Raise if off-topic answers appear; lower if too much escalates |
| `MEMORY_MAX_TURNS`       | `6`                      | Question/answer pairs kept per conversation  |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `SSL: CERTIFICATE_VERIFY_FAILED` | A corporate proxy is re-signing HTTPS. The package uses `truststore` so Python trusts the Windows/macOS certificate store; make sure your company root CA is installed there, and re-run `pip install -e .` |
| Pinecone `403 ... max serverless indexes` | Your plan's index limit is reached. Reuse an existing index by setting `PINECONE_INDEX` and a matching `EMBEDDING_DIMENSION` (see Step 2) |
| `Index '...' has dimension X but EMBEDDING_DIMENSION is Y` | Set `EMBEDDING_DIMENSION=X` in `.env`, or use a different `PINECONE_INDEX` |
| `Could not start the assistant` in Streamlit / auth errors | Check the keys in `.env` and start from the project root |
| OpenAI auth errors only in a new terminal | The key was set as an environment variable that this shell doesn't see. Put `OPENAI_API_KEY` in `.env` instead (uncomment the line) |
| `ModuleNotFoundError: helpdesk_rag` | Activate the venv and run `pip install -e ".[dev]"` |
| Every question escalates | Make sure Step 3 ran, then check scores with Step 4 `--all`; lower `SCORE_THRESHOLD` if relevant chunks score just under it |
| Old answers after editing KB files | `python -m helpdesk_rag.ingestion.ingest --reset` |
| `UnicodeEncodeError` in scripts on Windows | Set `PYTHONIOENCODING=utf-8` (the console can't print the emoji in the UI title) |

## Development

```bash
pytest                                              # all tests (offline, fakes for OpenAI/Pinecone)
pytest tests/test_service.py::test_answer_from_kb   # one test
ruff check . && ruff format .                       # lint + format
```
