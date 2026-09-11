from app.retrieval.embedding_service import EmbeddingService


service = EmbeddingService()

sentences = [
    "Pump pressure is low.",
    "The inlet pipe may be blocked.",
    "Today is a sunny day.",
]

vectors = service.embed_documents(sentences)

print("Embedding shape:", vectors.shape)

print()
print("First embedding values:")
print(vectors[0][:10])