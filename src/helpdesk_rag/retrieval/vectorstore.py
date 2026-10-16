from typing import Protocol

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from helpdesk_rag.config import Settings

ScoredDocs = list[tuple[Document, float]]


class Retriever(Protocol):
    def retrieve(self, query: str) -> ScoredDocs: ...


def get_embeddings(settings: Settings) -> OpenAIEmbeddings:
    # text-embedding-3-* can shorten vectors to match the index; older models cannot.
    dimensions = (
        settings.embedding_dimension
        if settings.openai_embedding_model.startswith("text-embedding-3")
        else None
    )
    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        dimensions=dimensions,
        api_key=settings.openai_api_key or None,
    )


def get_pinecone_client(settings: Settings) -> Pinecone:
    return Pinecone(api_key=settings.pinecone_api_key or None)


def get_vectorstore(settings: Settings) -> PineconeVectorStore:
    return PineconeVectorStore(
        index_name=settings.pinecone_index,
        embedding=get_embeddings(settings),
        namespace=settings.pinecone_namespace,
        pinecone_api_key=settings.pinecone_api_key or None,
    )


class PineconeRetriever:
    """Top-k similarity search that drops chunks below a cosine-similarity threshold."""

    def __init__(self, store: PineconeVectorStore, top_k: int, score_threshold: float):
        self.store = store
        self.top_k = top_k
        self.score_threshold = score_threshold

    def retrieve(self, query: str) -> ScoredDocs:
        results = self.store.similarity_search_with_score(query, k=self.top_k)
        return [(doc, score) for doc, score in results if score >= self.score_threshold]

    @classmethod
    def from_settings(cls, settings: Settings) -> "PineconeRetriever":
        return cls(get_vectorstore(settings), settings.top_k, settings.score_threshold)
