"""Load the KB, chunk it, and upsert it into Pinecone.

Usage: python -m helpdesk_rag.ingestion.ingest [--reset]
"""

import argparse
import json

from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import NotFoundException

from helpdesk_rag.config import Settings, get_settings
from helpdesk_rag.ingestion.loaders import load_documents
from helpdesk_rag.ingestion.splitter import chunk_id, split_documents
from helpdesk_rag.retrieval.vectorstore import get_pinecone_client, get_vectorstore


def ensure_index(pc: Pinecone, settings: Settings) -> None:
    if not pc.has_index(settings.pinecone_index):
        pc.create_index(
            name=settings.pinecone_index,
            dimension=settings.embedding_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud=settings.pinecone_cloud, region=settings.pinecone_region),
        )
        return

    existing = pc.describe_index(settings.pinecone_index).dimension
    if existing != settings.embedding_dimension:
        raise SystemExit(
            f"Index '{settings.pinecone_index}' has dimension {existing} but "
            f"EMBEDDING_DIMENSION is {settings.embedding_dimension}. "
            "Set EMBEDDING_DIMENSION to match, or use a different PINECONE_INDEX."
        )


def ingest(settings: Settings | None = None, reset: bool = False) -> dict:
    """Ingest `settings.kb_dir`. `reset` wipes the namespace first, removing stale chunks."""
    settings = settings or get_settings()
    docs = load_documents(settings.kb_dir)
    chunks = split_documents(docs, settings.chunk_size, settings.chunk_overlap)

    ensure_index(get_pinecone_client(settings), settings)
    store = get_vectorstore(settings)
    if reset:
        try:
            store.delete(delete_all=True, namespace=settings.pinecone_namespace)
        except NotFoundException:
            pass  # namespace doesn't exist yet

    if chunks:
        store.add_documents(chunks, ids=[chunk_id(c) for c in chunks])

    return {
        "documents": len(docs),
        "chunks": len(chunks),
        "index": settings.pinecone_index,
        "namespace": settings.pinecone_namespace,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest the IT knowledge base into Pinecone.")
    parser.add_argument(
        "--reset", action="store_true", help="delete all vectors in the namespace first"
    )
    args = parser.parse_args()
    print(json.dumps(ingest(reset=args.reset), indent=2))


if __name__ == "__main__":
    main()
