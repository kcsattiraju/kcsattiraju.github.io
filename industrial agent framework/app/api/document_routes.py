import os
import shutil

from pathlib import Path
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.documents.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="File name is missing.",
            )

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported.",
            )

        destination = UPLOAD_DIR / file.filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        file_size = os.path.getsize(destination)

        service = DocumentService(db)

        document = service.process_document(
            file_name=file.filename,
            file_type=file.content_type or "application/pdf",
            file_size=file_size,
            storage_path=str(destination),
        )

        return {
            "id": str(document.id),
            "file_name": document.file_name,
            "status": document.status,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("")
def get_documents(
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    documents = service.repository.get_all_documents()

    return [
        {
            "id": str(document.id),
            "file_name": document.file_name,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "status": document.status,
            "created_at": document.created_at,
        }
        for document in documents
    ]


@router.post(
    "/agents/{agent_id}/assign/{document_id}"
)
def assign_document_to_agent(
    agent_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        service = DocumentService(db)

        assignment = service.assign_document_to_agent(
            agent_id=agent_id,
            document_id=document_id,
        )

        return {
            "id": str(assignment.id),
            "agent_id": str(assignment.agent_id),
            "document_id": str(
                assignment.document_id
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get(
    "/agents/{agent_id}"
)
def get_documents_for_agent(
    agent_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        service = DocumentService(db)

        documents = service.get_agent_documents(
            agent_id=agent_id
        )

        return [
            {
                "id": str(document.id),
                "file_name": document.file_name,
                "status": document.status,
            }
            for document in documents
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )