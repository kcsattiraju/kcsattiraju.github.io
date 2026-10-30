
import re
from collections import defaultdict

from langchain_core.tools import tool
from rank_bm25 import BM25Okapi

from rag_config import generate_embedding, get_collection


SEMANTIC_TOP_K = 8
KEYWORD_TOP_K = 8
FINAL_TOP_K = 4
RRF_K = 60


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def reciprocal_rank_fusion(
    semantic_ids: list[str],
    keyword_ids: list[str]
) -> list[str]:
    scores = defaultdict(float)

    for ranked_ids in (semantic_ids, keyword_ids):
        for rank, doc_id in enumerate(ranked_ids, start=1):
            scores[doc_id] += 1.0 / (RRF_K + rank)

    return sorted(scores, key=scores.get, reverse=True)


def retrieve_documents(
    query: str,
    source: str = "",
    method: str = "hybrid",
    k: int = FINAL_TOP_K
) -> list[dict]:
    """
    Retrieve document chunks using semantic, BM25, or hybrid search.
    Returns IDs, text, and metadata for evaluation and agent use.
    """

    if method not in ("semantic", "bm25", "hybrid"):
        raise ValueError(f"Unsupported retrieval method: {method}")

    if k < 1:
        raise ValueError("k must be at least 1")

    collection = get_collection()

    if collection.count() == 0:
        return []

    where_filter = {"source": source} if source else None

    stored = collection.get(
        where=where_filter,
        include=["documents", "metadatas"]
    )

    ids = stored["ids"]
    documents = stored["documents"]
    metadatas = stored["metadatas"]

    if not ids:
        return []

    records = {
        doc_id: {
            "id": doc_id,
            "text": document,
            "metadata": metadata or {}
        }
        for doc_id, document, metadata in zip(
            ids, documents, metadatas
        )
    }

    semantic_ids = []
    keyword_ids = []

    # Semantic retrieval
    if method in ("semantic", "hybrid"):
        query_embedding = generate_embedding(query)

        semantic_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(max(SEMANTIC_TOP_K, k), len(ids)),
            where=where_filter,
            include=["distances"]
        )

        semantic_ids = semantic_results["ids"][0]

    # BM25 retrieval
    if method in ("bm25", "hybrid"):
        tokenized_corpus = [
            tokenize(document) for document in documents
        ]

        # Avoid BM25 initialization on empty-token documents.
        if any(tokenized_corpus):
            bm25 = BM25Okapi(tokenized_corpus)
            query_tokens = tokenize(query)

            if query_tokens:
                keyword_scores = bm25.get_scores(query_tokens)

                ranked_indices = sorted(
                    range(len(ids)),
                    key=lambda i: keyword_scores[i],
                    reverse=True
                )

                keyword_ids = [
                    ids[i]
                    for i in ranked_indices
                    if keyword_scores[i] > 0
                ][:max(KEYWORD_TOP_K, k)]

    # Choose retrieval method
    if method == "semantic":
        selected_ids = semantic_ids[:k]
    elif method == "bm25":
        selected_ids = keyword_ids[:k]
    else:
        selected_ids = reciprocal_rank_fusion(
            semantic_ids,
            keyword_ids
        )[:k]

    return [records[doc_id] for doc_id in selected_ids]


@tool
def search_insurance_documents(
    query: str,
    source: str = ""
) -> str:
    """
    Search insurance policy documents using hybrid retrieval.

    Use for policy questions about deductibles,
    coverage limits, exclusions, and policy wording.

    Args:
        query: Insurance question.
        source: Optional exact PDF filename.
    """

    print("TOOL EXECUTED: hybrid RAG search")

    passages = retrieve_documents(
        query=query,
        source=source,
        method="hybrid",
        k=FINAL_TOP_K
    )

    if not passages:
        return "No indexed insurance passages were found."

    formatted = []

    for index, passage in enumerate(passages, start=1):
        metadata = passage["metadata"]

        formatted.append(
            f"[Passage {index}]\n"
            f"Chunk ID: {passage['id']}\n"
            f"Source: {metadata.get('source', 'Unknown')}\n"
            f"Page: {metadata.get('page', 'Unknown')}\n"
            f"Content:\n{passage['text']}"
        )

    return "\n\n---\n\n".join(formatted)
