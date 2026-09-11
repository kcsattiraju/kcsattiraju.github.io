from app.tools.semantic_search_tool import (
    semantic_document_search,
)


result = semantic_document_search.invoke(
    {
        "query": (
            "What can cause low pump output pressure?"
        )
    }
)


print()
print("SEMANTIC TOOL RESULT:")
print()
print(result)