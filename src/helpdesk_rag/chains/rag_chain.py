from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser

from helpdesk_rag.chains.prompts import ANSWER_PROMPT, CONDENSE_PROMPT
from helpdesk_rag.retrieval.vectorstore import Retriever, ScoredDocs
from helpdesk_rag.schemas import AnswerDraft


@dataclass
class RagResult:
    standalone_question: str
    retrieved: ScoredDocs
    draft: AnswerDraft | None  # None when nothing relevant was retrieved (LLM not called)


def format_context(retrieved: ScoredDocs) -> str:
    blocks = []
    for i, (doc, _score) in enumerate(retrieved, start=1):
        meta = doc.metadata
        blocks.append(
            f"[{i}] source: {meta.get('source')} | title: {meta.get('title')}\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(blocks)


class RagChain:
    """History-aware retrieval followed by a grounded, structured answer."""

    def __init__(self, llm: BaseChatModel, retriever: Retriever):
        self.retriever = retriever
        self.condense_chain = CONDENSE_PROMPT | llm | StrOutputParser()
        self.answer_chain = ANSWER_PROMPT | llm.with_structured_output(AnswerDraft)

    def standalone_question(self, question: str, history: list[BaseMessage]) -> str:
        if not history:
            return question
        rewritten = self.condense_chain.invoke({"question": question, "history": history})
        return rewritten.strip() or question

    def run(self, question: str, history: list[BaseMessage]) -> RagResult:
        standalone = self.standalone_question(question, history)
        retrieved = self.retriever.retrieve(standalone)
        if not retrieved:
            return RagResult(standalone, retrieved, None)

        draft = self.answer_chain.invoke(
            {"question": question, "history": history, "context": format_context(retrieved)}
        )
        return RagResult(standalone, retrieved, draft)
