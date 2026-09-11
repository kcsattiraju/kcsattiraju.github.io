import numpy as np

from app.knowledge.vector_store import VectorStore


# --------------------------------------------------
# 1. CREATE SAMPLE EMBEDDINGS
# --------------------------------------------------
# These are fake 3-dimensional embeddings.
# We are using them only to test FAISS persistence.
#
# In the next checkpoint, these will be replaced
# with real Sentence Transformer embeddings.

embeddings = np.array(
    [
        [1.0, 1.0, 1.0],
        [5.0, 5.0, 5.0],
        [9.0, 9.0, 9.0],
    ],
    dtype="float32",
)


# --------------------------------------------------
# 2. CREATE DOCUMENT METADATA
# --------------------------------------------------
# Each document corresponds to one embedding above.

documents = [
    {
        "text": "Low suction pressure may cause pump cavitation.",
        "source": "pump_manual.pdf",
        "page": 10,
    },
    {
        "text": "Check motor voltage if the pump fails to start.",
        "source": "pump_manual.pdf",
        "page": 20,
    },
    {
        "text": "Replace lubricant after scheduled operating hours.",
        "source": "pump_manual.pdf",
        "page": 30,
    },
]


# --------------------------------------------------
# 3. CREATE FAISS VECTOR STORE
# --------------------------------------------------

print("\nCreating FAISS index...")

store = VectorStore()

store.create_index(
    embeddings=embeddings,
    documents=documents,
)


# --------------------------------------------------
# 4. SAVE FAISS INDEX
# --------------------------------------------------

print("\nSaving FAISS index...")

store.save()

print("\nIndex saved successfully.")


# --------------------------------------------------
# 5. CREATE A NEW VECTOR STORE OBJECT
# --------------------------------------------------
# This simulates restarting our application.
#
# The new object does NOT have the original
# in-memory FAISS index.

print("\nCreating new VectorStore instance...")

new_store = VectorStore()


# --------------------------------------------------
# 6. LOAD SAVED FAISS INDEX
# --------------------------------------------------

print("\nLoading saved FAISS index...")

loaded = new_store.load()

print("Index loaded:", loaded)


# --------------------------------------------------
# 7. CREATE SAMPLE QUERY EMBEDDING
# --------------------------------------------------
# This vector is intentionally close to:
#
# [1.0, 1.0, 1.0]
#
# Therefore FAISS should return the cavitation
# document as the best result.

query_embedding = np.array(
    [1.1, 1.1, 1.1],
    dtype="float32",
)


# --------------------------------------------------
# 8. SEARCH FAISS
# --------------------------------------------------

print("\nSearching FAISS...")

results = new_store.search(
    query_embedding=query_embedding,
    top_k=2,
)


# --------------------------------------------------
# 9. DISPLAY RESULTS
# --------------------------------------------------

print("\n==============================")
print("SEARCH RESULTS")
print("==============================")


for number, result in enumerate(
    results,
    start=1,
):

    document = result["document"]

    print(f"\nResult #{number}")

    print(
        "FAISS Score:",
        result["score"],
    )

    print(
        "Text:",
        document["text"],
    )

    print(
        "Source:",
        document["source"],
    )

    print(
        "Page:",
        document["page"],
    )


print("\nCheckpoint 25 test completed.")