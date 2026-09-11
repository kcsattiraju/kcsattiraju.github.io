from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:
    """
    Converts text into numerical embedding vectors
    using a Sentence Transformer model.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        print(
            f"Loading embedding model: {model_name}"
        )

        self.model = SentenceTransformer(
            model_name
        )

    def embed_texts(
        self,
        texts: list[str],
    ) -> np.ndarray:
        """
        Generate embeddings for multiple text chunks.
        """

        if not texts:
            raise ValueError(
                "No texts were provided for embedding."
            )

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

        return np.asarray(
            embeddings,
            dtype="float32",
        )

    def embed_query(
        self,
        query: str,
    ) -> np.ndarray:
        """
        Generate an embedding for one search query.
        """

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
        )

        return np.asarray(
            embedding,
            dtype="float32",
        )