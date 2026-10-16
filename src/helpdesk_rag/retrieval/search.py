"""Query Pinecone directly to check what the retriever returns (no LLM call).

Usage: python -m helpdesk_rag.retrieval.search "How do I connect to VPN?" [--k 4] [--all]
"""

import argparse

from helpdesk_rag.config import get_settings
from helpdesk_rag.retrieval.vectorstore import get_vectorstore


def main() -> None:
    parser = argparse.ArgumentParser(description="Search the ingested knowledge base.")
    parser.add_argument("query")
    parser.add_argument("--k", type=int, help="number of results (default: TOP_K)")
    parser.add_argument(
        "--all", action="store_true", help="also show results below SCORE_THRESHOLD"
    )
    args = parser.parse_args()

    settings = get_settings()
    results = get_vectorstore(settings).similarity_search_with_score(
        args.query, k=args.k or settings.top_k
    )
    print(f"threshold = {settings.score_threshold}\n")
    for doc, score in results:
        passed = score >= settings.score_threshold
        if not passed and not args.all:
            continue
        marker = "PASS" if passed else "drop"
        snippet = " ".join(doc.page_content.split())[:150]
        print(f"[{marker}] {score:.3f}  {doc.metadata.get('source')}\n        {snippet}\n")
    if not any(score >= settings.score_threshold for _, score in results):
        print("No chunks passed the threshold; this question would be escalated.")


if __name__ == "__main__":
    main()
