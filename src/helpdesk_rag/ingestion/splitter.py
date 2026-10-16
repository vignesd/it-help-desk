import hashlib
from collections import defaultdict

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(docs: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
    """Chunk documents, preferring markdown section boundaries, and number chunks per source."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    counters: dict[tuple[str, int], int] = defaultdict(int)
    for chunk in chunks:
        key = (chunk.metadata["source"], chunk.metadata.get("page", 0))
        chunk.metadata["chunk_index"] = counters[key]
        counters[key] += 1
    return chunks


def chunk_id(chunk: Document) -> str:
    """Stable vector ID so re-ingesting overwrites a chunk instead of duplicating it."""
    meta = chunk.metadata
    raw = f"{meta['source']}:{meta.get('page', 0)}:{meta['chunk_index']}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()
