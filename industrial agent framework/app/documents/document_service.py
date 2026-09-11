from app.documents.document_processor import DocumentProcessor
from app.documents.document_repository import DocumentRepository
from app.documents.embedding_service import EmbeddingService


class DocumentService:

    def __init__(self, db):
        self.repository = DocumentRepository(db)

    def process_document(
        self,
        file_name: str,
        file_type: str,
        file_size: int,
        storage_path: str,
    ):
        document = self.repository.create_document(
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            storage_path=storage_path,
        )

        text = DocumentProcessor.extract_pdf_text(
            storage_path
        )

        chunks = DocumentProcessor.chunk_text(
            text
        )

        for index, chunk in enumerate(chunks):

            embedding = (
                EmbeddingService.generate_embedding(
                    chunk
                )
            )

            self.repository.add_chunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=embedding,
            )

        document.status = "processed"

        self.repository.commit()

        return document

    def assign_document_to_agent(
        self,
        agent_id,
        document_id,
    ):
        return self.repository.assign_document_to_agent(
            agent_id=agent_id,
            document_id=document_id,
        )

    def get_agent_documents(
        self,
        agent_id,
    ):
        return self.repository.get_agent_documents(
            agent_id=agent_id
        )