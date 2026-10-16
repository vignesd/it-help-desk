"""Chat UI. Run from the project root: streamlit run ui/streamlit_app.py"""

import uuid

import streamlit as st

from helpdesk_rag.ingestion.ingest import ingest
from helpdesk_rag.schemas import AskResponse
from helpdesk_rag.service import HelpDeskService

st.set_page_config(page_title="IT Help Desk Assistant", page_icon="🛠️")


@st.cache_resource
def load_service() -> HelpDeskService:
    return HelpDeskService.from_settings()


def render_response(resp: AskResponse) -> None:
    st.markdown(resp.answer)
    if resp.ticket:
        t = resp.ticket
        st.warning(
            f"**Ticket {t.ticket_id}** · {t.priority} · {t.category}\n\n"
            f"**{t.title}**\n\n{t.summary}"
        )
    if resp.sources:
        with st.expander(f"Sources ({len(resp.sources)})"):
            for s in resp.sources:
                st.markdown(f"**{s.title}** — `{s.source}` (score {s.score})")
                st.caption(s.snippet + "…")


if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex
    st.session_state.messages = []  # list of ("user", str) | ("assistant", AskResponse)

try:
    service = load_service()
except Exception as exc:  # usually missing API keys
    st.error(f"Could not start the assistant: {exc}\n\nCheck your `.env` file.")
    st.stop()

with st.sidebar:
    st.header("IT Help Desk")
    if st.button("New conversation", use_container_width=True):
        service.clear_session(st.session_state.session_id)
        st.session_state.session_id = uuid.uuid4().hex
        st.session_state.messages = []
        st.rerun()
    if st.button("Re-ingest knowledge base", use_container_width=True):
        with st.spinner("Ingesting..."):
            stats = ingest()
        st.success(f"Ingested {stats['documents']} documents ({stats['chunks']} chunks).")

st.title("🛠️ IT Help Desk Assistant")
st.caption("Ask about VPN, passwords, email, printers, Wi-Fi, software and more.")

for role, content in st.session_state.messages:
    with st.chat_message(role):
        if role == "assistant":
            render_response(content)
        else:
            st.markdown(content)

if question := st.chat_input("Describe your IT issue..."):
    st.session_state.messages.append(("user", question))
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching the knowledge base..."):
            resp = service.ask(question, st.session_state.session_id)
        render_response(resp)
    st.session_state.messages.append(("assistant", resp))
