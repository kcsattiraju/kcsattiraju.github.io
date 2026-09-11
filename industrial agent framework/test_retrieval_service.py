from app.knowledge.retrieval_service import RetrievalService


print("\n================================")
print("CHECKPOINT 27")
print("RETRIEVAL SERVICE TEST")
print("================================")


# --------------------------------------------------
# 1. CREATE RETRIEVAL SERVICE
# --------------------------------------------------

print("\nCreating RetrievalService...")

retrieval_service = RetrievalService(
    top_k=3
)


# --------------------------------------------------
# 2. USER QUESTION
# --------------------------------------------------

question = (
    "What should I check if the pump "
    "has low discharge pressure?"
)

print(
    "\nQuestion:",
    question,
)


# --------------------------------------------------
# 3. RUN SEMANTIC SEARCH
# --------------------------------------------------

print("\nSearching knowledge base...")

results = retrieval_service.search(
    query=question
)


# --------------------------------------------------
# 4. DISPLAY STRUCTURED RESULTS
# --------------------------------------------------

print("\n================================")
print("SEARCH RESULTS")
print("================================")


for number, result in enumerate(
    results,
    start=1,
):

    document = result[
        "document"
    ]

    print(
        f"\nResult #{number}"
    )

    print(
        "FAISS Score:",
        result["score"],
    )

    print(
        "Source:",
        document["source"],
    )

    print(
        "Page:",
        document["page"],
    )

    print(
        "Text:"
    )

    print(
        document["text"][:500]
    )

    print(
        "\n--------------------------------"
    )


# --------------------------------------------------
# 5. CREATE LLM-READY CONTEXT
# --------------------------------------------------

print("\n================================")
print("LLM READY CONTEXT")
print("================================")


context = (
    retrieval_service.retrieve_context(
        query=question,
        top_k=2,
    )
)


print(context)


print(
    "\nCheckpoint 27 completed."
)