from langchain_core.documents import Document

from helpdesk_rag.config import get_settings
from helpdesk_rag.ingestion.loaders import load_documents, parse_front_matter
from helpdesk_rag.ingestion.splitter import chunk_id, split_documents


def test_parse_front_matter():
    meta, body = parse_front_matter("---\ntitle: VPN\ncategory: network\n---\n# Body\ntext")
    assert meta == {"title": "VPN", "category": "network"}
    assert body.startswith("# Body")


def test_parse_front_matter_absent():
    meta, body = parse_front_matter("# Just text")
    assert meta == {} and body == "# Just text"


def test_load_documents_uses_front_matter_and_defaults(tmp_path):
    (tmp_path / "vpn-guide.md").write_text("---\ncategory: network\n---\nConnect it.")
    (tmp_path / "notes.txt").write_text("Plain notes.")
    (tmp_path / "ignored.docx").write_text("nope")

    docs = {d.metadata["source"]: d for d in load_documents(tmp_path)}

    assert set(docs) == {"vpn-guide.md", "notes.txt"}
    assert docs["vpn-guide.md"].metadata["category"] == "network"
    assert docs["vpn-guide.md"].metadata["title"] == "Vpn Guide"
    assert docs["notes.txt"].metadata["category"] == "general"


def test_sample_kb_loads():
    docs = load_documents(get_settings().kb_dir)
    assert len(docs) >= 8
    assert all(d.metadata["category"] != "general" for d in docs)


def test_split_keeps_metadata_and_numbers_chunks():
    doc = Document(page_content="word " * 1000, metadata={"source": "a.md", "title": "A"})
    chunks = split_documents([doc], chunk_size=200, chunk_overlap=20)

    assert len(chunks) > 1
    assert [c.metadata["chunk_index"] for c in chunks] == list(range(len(chunks)))
    assert all(c.metadata["source"] == "a.md" for c in chunks)


def test_chunk_ids_are_stable_and_unique():
    docs = [
        Document(page_content="x " * 500, metadata={"source": "a.md"}),
        Document(page_content="y " * 500, metadata={"source": "b.md"}),
    ]
    first = [chunk_id(c) for c in split_documents(docs, 200, 20)]
    second = [chunk_id(c) for c in split_documents(docs, 200, 20)]

    assert first == second
    assert len(set(first)) == len(first)
