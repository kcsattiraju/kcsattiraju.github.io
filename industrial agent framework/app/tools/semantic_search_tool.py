from langchain_core.tools import tool

from app.retrieval.semantic_search_service import (
    SemanticSearchService,
)


semantic_search_service = (
    SemanticSearchService()
)

is_indexed = False


def ensure_index_created():
    global is_indexed

    if not is_indexed:

        print()
        print(
            "Creating industrial "
            "document index..."
        )

        semantic_search_service.index_documents(
            "data/documents"
        )

        is_indexed = True


@tool
def semantic_document_search(
    query: str
) -> str:
    """
    Search industrial manuals and technical
    documentation using semantic retrieval.

    Use this tool for equipment troubleshooting,
    maintenance, operating procedures, warnings,
    specifications, faults, and other questions
    that require information from industrial
    documentation.
    """

    ensure_index_created()

    print()
    print(
        "Semantic search query:",
        query
    )

    results = (
        semantic_search_service.search(
            query=query,
            top_k=3,
        )
    )

    if not results:
        return (
            "No relevant information was "
            "found in the industrial documents."
        )

    formatted_results = []

    for number, result in enumerate(
        results,
        start=1
    ):

        formatted_results.append(
            f"""
Result {number}

Source: {result.get('source', 'Unknown')}
Page: {result.get('page', 'Unknown')}
Similarity Score: {result.get('score', 0):.4f}

Content:
{result['text']}
"""
        )

    return "\n".join(
        formatted_results
    )