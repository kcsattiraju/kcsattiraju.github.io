from app.retrieval.document_loader import load_pdf
from app.retrieval.text_splitter import split_text
from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.vector_store import VectorStore


class SemanticSearchService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def index_pdf(
        self,
        file_path: str
    ):
        print(f"Loading PDF: {file_path}")

        text = load_pdf(file_path)

        chunks = split_text(text)

        print(
            f"Created {len(chunks)} chunks"
        )

        embeddings = (
            self.embedding_service
            .embed_documents(chunks)
        )

        self.vector_store.build_index(
            embeddings,
            chunks,
        )

        print("FAISS index created successfully")

    def search(
        self,
        query: str,
        top_k: int = 3,
    ):
        query_embedding = (
            self.embedding_service
            .embed_query(query)
        )

        return self.vector_store.search(
            query_embedding,
            top_k,
        )