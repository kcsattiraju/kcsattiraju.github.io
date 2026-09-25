from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "The pump has low pressure.",
    "The pump output pressure is reduced.",
    "I like eating pizza."
]

embeddings = model.encode(sentences)

similarity = cosine_similarity(embeddings)

print(similarity)