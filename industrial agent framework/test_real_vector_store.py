from app.knowledge.document_loader import load_pdf
from app.knowledge.text_splitter import split_documents
from app.knowledge.embedding_service import EmbeddingService
from app.knowledge.vector_store import VectorStore


PDF_PATH = "data/documents/pump_manual.pdf"


# --------------------------------------------------
# 1. LOAD REAL PDF
# --------------------------------------------------

print("\n================================")
print("1. LOADING PDF")
print("================================")

documents = load_pdf(
    PDF_PATH
)

print(
    f"Pages loaded: {len(documents)}"
)


# --------------------------------------------------
# 2. SPLIT DOCUMENT INTO CHUNKS
# --------------------------------------------------

print("\n================================")
print("2. SPLITTING DOCUMENT")
print("================================")

chunks = split_documents(
    documents,
    chunk_size=800,
    chunk_overlap=100,
)

print(
    f"Chunks created: {len(chunks)}"
)


# --------------------------------------------------
# 3. EXTRACT TEXT FOR EMBEDDING
# --------------------------------------------------

texts = [
    chunk["text"]
    for chunk in chunks
]


# --------------------------------------------------
# 4. CREATE REAL EMBEDDINGS
# --------------------------------------------------

print("\n================================")
print("3. CREATING EMBEDDINGS")
print("================================")

embedding_service = EmbeddingService()

embeddings = (
    embedding_service.embed_texts(
        texts
    )
)

print(
    "Embedding shape:",
    embeddings.shape,
)


# --------------------------------------------------
# 5. BUILD FAISS INDEX
# --------------------------------------------------

print("\n================================")
print("4. BUILDING FAISS INDEX")
print("================================")

vector_store = VectorStore()

vector_store.create_index(
    embeddings=embeddings,
    documents=chunks,
)


# --------------------------------------------------
# 6. SAVE FAISS INDEX
# --------------------------------------------------

print("\n================================")
print("5. SAVING VECTOR STORE")
print("================================")

vector_store.save()


# --------------------------------------------------
# 7. LOAD SAVED INDEX AGAIN
# --------------------------------------------------

print("\n================================")
print("6. RELOADING VECTOR STORE")
print("================================")

loaded_store = VectorStore()

loaded = loaded_store.load()

print(
    "Loaded:",
    loaded,
)


# --------------------------------------------------
# 8. REAL USER QUESTION
# --------------------------------------------------

question = (
    "What can cause problems with the pump?"
)

print("\n================================")
print("7. SEMANTIC SEARCH")
print("================================")

print(
    "Question:",
    question,
)


# --------------------------------------------------
# 9. EMBED QUESTION
# --------------------------------------------------

query_embedding = (
    embedding_service.embed_query(
        question
    )
)


# --------------------------------------------------
# 10. SEARCH FAISS
# --------------------------------------------------

results = loaded_store.search(
    query_embedding=query_embedding,
    top_k=3,
)


# --------------------------------------------------
# 11. DISPLAY RESULTS
# --------------------------------------------------

print("\n================================")
print("TOP MATCHING CHUNKS")
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
        "\nText:"
    )

    print(
        document["text"][:700]
    )

    print(
        "\n--------------------------------"
    )


print(
    "\nCheckpoint 26 completed."
)