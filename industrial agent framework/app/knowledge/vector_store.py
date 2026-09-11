from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import faiss
import numpy as np


VECTOR_STORE_DIR = Path("data/vector_store")
INDEX_PATH = VECTOR_STORE_DIR / "documents.faiss"
METADATA_PATH = VECTOR_STORE_DIR / "documents.pkl"


class VectorStore:
    """
    Persistent FAISS vector store.

    FAISS stores vectors.
    Pickle stores the metadata/text associated with each vector.
    """

    def __init__(self):
        self.index: faiss.Index | None = None
        self.documents: list[dict[str, Any]] = []

        VECTOR_STORE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create_index(
        self,
        embeddings: np.ndarray,
        documents: list[dict[str, Any]],
    ) -> None:
        """
        Create a new FAISS index from embeddings.
        """

        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        if len(embeddings) == 0:
            raise ValueError(
                "Cannot create FAISS index: embeddings are empty."
            )

        if len(embeddings) != len(documents):
            raise ValueError(
                "Number of embeddings must match number of documents."
            )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)

        self.index.add(embeddings)

        self.documents = documents

        print(
            f"FAISS index created with "
            f"{self.index.ntotal} vectors."
        )

    def save(self) -> None:
        """
        Save FAISS index and document metadata.
        """

        if self.index is None:
            raise ValueError(
                "No FAISS index exists to save."
            )

        faiss.write_index(
            self.index,
            str(INDEX_PATH),
        )

        with open(
            METADATA_PATH,
            "wb",
        ) as file:
            pickle.dump(
                self.documents,
                file,
            )

        print(
            f"FAISS index saved to: {INDEX_PATH}"
        )

        print(
            f"Document metadata saved to: {METADATA_PATH}"
        )

    def load(self) -> bool:
        """
        Load an existing FAISS index.

        Returns:
            True if successfully loaded.
            False if saved files do not exist.
        """

        if not self.exists():
            return False

        self.index = faiss.read_index(
            str(INDEX_PATH)
        )

        with open(
            METADATA_PATH,
            "rb",
        ) as file:
            self.documents = pickle.load(file)

        print(
            f"FAISS index loaded with "
            f"{self.index.ntotal} vectors."
        )

        return True

    def exists(self) -> bool:
        """
        Check whether persisted vector-store files exist.
        """

        return (
            INDEX_PATH.exists()
            and METADATA_PATH.exists()
        )

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Search FAISS and return the closest documents.
        """

        if self.index is None:
            raise ValueError(
                "FAISS index has not been loaded or created."
            )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32",
        )

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(
                1,
                -1,
            )

        distances, indices = self.index.search(
            query_embedding,
            top_k,
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0],
        ):
            if index == -1:
                continue

            document = self.documents[index]

            results.append(
                {
                    "score": float(distance),
                    "document": document,
                }
            )

        return results