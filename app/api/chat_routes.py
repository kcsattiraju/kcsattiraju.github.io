import traceback
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
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

        runtime_service = RuntimeService(
            db
        )

        result = runtime_service.chat(
            agent_id=agent_id,
            message=request.message,
        )

        return ChatResponse(
            response=result
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except HTTPException:

        raise

    except Exception as error:

        # --------------------------------------------
        # Temporary debug logging
        # --------------------------------------------

        print(
            "\n"
            "========================================"
        )

        print(
            "AGENT CHAT ERROR"
        )

        print(
            "========================================"
        )

        traceback.print_exc()

        print(
            "========================================"
            "\n"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"{type(error).__name__}: "
                f"{str(error)}"
            ),
        )