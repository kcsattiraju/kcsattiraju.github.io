from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)

from sqlalchemy.orm import Session

from app.api.schemas.agent_schema import (
    AgentCreate,
    AgentResponse,
    AgentUpdate,
)

from app.agents.agent_service import AgentService
from app.database.connection import get_db


router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


@router.post(
    "",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_agent(
    request: AgentCreate,
    db: Session = Depends(get_db),
):
    return AgentService.create_agent(
        db,
        request,
    )


@router.get(
    "",
    response_model=list[AgentResponse],
)
def get_agents(
    db: Session = Depends(get_db),
):
    return AgentService.get_agents(db)


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
)
def get_agent(
    agent_id: UUID,
    db: Session = Depends(get_db),
):
    return AgentService.get_agent(
        db,
        agent_id,
    )


@router.patch(
    "/{agent_id}",
    response_model=AgentResponse,
)
def update_agent(
    agent_id: UUID,
    request: AgentUpdate,
    db: Session = Depends(get_db),
):
    return AgentService.update_agent(
        db,
        agent_id,
        request,
    )


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_agent(
    agent_id: UUID,
    db: Session = Depends(get_db),
):
    AgentService.delete_agent(
        db,
        agent_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )