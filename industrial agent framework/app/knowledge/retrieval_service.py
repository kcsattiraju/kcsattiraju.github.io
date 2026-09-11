from __future__ import annotations

from app.knowledge.embedding_service import EmbeddingService
from app.knowledge.vector_store import VectorStore


class RetrievalService:
    """
    Reusable semantic retrieval service.

    Responsibilities:
    - Load the persisted FAISS vector store
    - Convert user questions into embeddings
    - Search FAISS
    - Return the most relevant document chunks
    """

    def __init__(
        self,
        top_k: int = 3,
    ):
        self.top_k = top_k

        self.embedding_service = EmbeddingService()

        self.vector_store = VectorStore()

        loaded = self.vector_store.load()

        if not loaded:
            raise RuntimeError(
                "No persisted FAISS index was found. "
                "Build the vector store before using RetrievalService."
            )

    def search(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[dict]:
        """
        Search for document chunks that are semantically
        related to the user's query.
        """

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        query_embedding = (
            self.embedding_service.embed_query(
                query
            )
        )

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k or self.top_k,
        )

        return results

    def retrieve_context(
        self,
        query: str,
        top_k: int | None = None,
    ) -> str:
        """
        Retrieve matching chunks and combine them
        into a single context string.

        This will later be passed to the LLM.
        """

        results = self.search(
            query=query,
            top_k=top_k,
        )

        context_parts = []

        for result in results:

            document = result["document"]

            source = document.get(
                "source",
                "unknown",
            )

            page = document.get(
                "page",
                "unknown",
            )

            text = document.get(
                "text",
                "",
            )

            context_parts.append(
                f"Source: {source}\n"
                f"Page: {page}\n"
                f"Content:\n{text}"
            )

        return "\n\n---\n\n".join(
            context_parts
        )