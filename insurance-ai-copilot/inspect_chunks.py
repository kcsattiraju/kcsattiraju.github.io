from rag_config import get_collection

collection = get_collection()

stored = collection.get(
    include=["documents", "metadatas"]
)

print(f"Total indexed chunks: {len(stored['ids'])}")

for doc_id, text, metadata in zip(
    stored["ids"],
    stored["documents"],
    stored["metadatas"]
):
    print("\n-----------------------------")
    print("Chunk ID:", doc_id)
    print("Source:", (metadata or {}).get("source"))
    print("Page:", (metadata or {}).get("page"))
    print("Text:", text[:350])