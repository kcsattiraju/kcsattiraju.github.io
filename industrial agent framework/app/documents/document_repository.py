from sqlalchemy.orm import Session

from app.documents.document_model import Document
from app.documents.document_chunk_model import DocumentChunk
from app.documents.agent_document_model import AgentDocument


class DocumentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_document(
        self,
        file_name: str,
        file_type: str | None,
        file_size: int | None,
        storage_path: str | None,
    ) -> Document:

        document = Document(
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            storage_path=storage_path,
            status="uploaded",
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def add_chunk(
        self,
        document_id,
        chunk_index: int,
        content: str,
        embedding=None,
    ) -> DocumentChunk:

        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            embedding=embedding,
        )

        self.db.add(chunk)

        return chunk

    def commit(self):
        self.db.commit()

    def get_document(
        self,
        document_id,
    ):
        return (
            self.db.query(Document)
            .filter(
                Document.id == document_id
            )
            .first()
        )

    def get_all_documents(self):
        return (
            self.db.query(Document)
            .order_by(
                Document.created_at.desc()
            )
            .all()
        )

    def assign_document_to_agent(
        self,
        agent_id,
        document_id,
    ):
        existing = (
            self.db.query(AgentDocument)
            .filter(
                AgentDocument.agent_id == agent_id,
                AgentDocument.document_id == document_id,
            )
            .first()
        )

        if existing:
            return existing

        assignment = AgentDocument(
            agent_id=agent_id,
            document_id=document_id,
        )

        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        return assignment

    def get_agent_documents(
        self,
        agent_id,
    ):
        return (
            self.db.query(Document)
            .join(
                AgentDocument,
                AgentDocument.document_id == Document.id,
            )
            .filter(
                AgentDocument.agent_id == agent_id
            )
            .all()
        )