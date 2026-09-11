from app.retrieval.semantic_search_service import (
    SemanticSearchService,
)


service = SemanticSearchService()

service.index_pdf(
    "data/documents/pump_manual.pdf"
)


question = (
    "Why is the pump output pressure low?"
)


results = service.search(
    question,
    top_k=3,
)


print()
print("QUESTION:")
print(question)

print()
print("SEMANTIC SEARCH RESULTS:")


for number, result in enumerate(
    results,
    start=1
):
    print()
    print(
        f"===== RESULT {number} ====="
    )

    print(
        f"Score: {result['score']:.4f}"
    )

    print(result["text"])