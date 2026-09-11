import faiss
import numpy as np


class VectorStore:

    def __init__(self):
        self.index = None
        self.documents = []

    def build_index(
        self,
        embeddings: np.ndarray,
        documents: list[str],
    ):
        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(embeddings)

        self.documents = documents

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 3,
    ):
        if self.index is None:
            raise ValueError(
                "Vector index has not been created."
            )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        scores, indexes = self.index.search(
            query_embedding,
            top_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indexes[0]
        ):
            if index == -1:
                continue

            results.append(
                {
                    "text": self.documents[index],
                    "score": float(score),
                }
            )

        return results