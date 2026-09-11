from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.runtime.runtime_service import RuntimeService


router = APIRouter(
    prefix="/agents",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post(
    "/{agent_id}/chat",
    response_model=ChatResponse,
)
def chat_with_agent(
    agent_id: UUID,
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    try:
        runtime_service = RuntimeService(db)

        result = runtime_service.chat(
            agent_id=agent_id,
            message=request.message,
        )

        return ChatResponse(response=result)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        import traceback

        print()
        print("=" * 60)
        print("AGENT CHAT ERROR")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {str(exc)}",
        ) from exc
