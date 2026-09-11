from langchain_core.tools import tool

from app.knowledge.retrieval_service import RetrievalService


# --------------------------------------------------
# CREATE RETRIEVAL SERVICE
# --------------------------------------------------
# We initialize it once when this module is loaded.
# It will load the persisted FAISS vector store.

retrieval_service = RetrievalService(
    top_k=3
)


# --------------------------------------------------
# DOCUMENT SEARCH TOOL
# --------------------------------------------------

@tool
def search_documents(query: str) -> str:
    """
    Search industrial documents and maintenance manuals
    for information relevant to the user's question.

    Use this tool when the user asks about equipment,
    troubleshooting, maintenance, operating procedures,
    safety instructions, or information contained in
    technical manuals.
    """

    if not query.strip():
        return "No search query was provided."

    context = retrieval_service.retrieve_context(
        query=query,
        top_k=3,
    )

    if not context:
        return (
            "No relevant information was found "
            "in the available documents."
        )

    return context
