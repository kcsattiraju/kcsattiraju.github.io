from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.tools.tool_service import ToolService


router = APIRouter(
    tags=["Tools"],
)


# ---------------------------------------------------
# Get all available tools
# ---------------------------------------------------

@router.get("/tools")
def get_tools(
    db: Session = Depends(get_db),
):

    service = ToolService(db)

    return service.get_all_tools()


# ---------------------------------------------------
# Get tools assigned to an Agent
# ---------------------------------------------------

@router.get(
    "/agents/{agent_id}/tools"
)
def get_agent_tools(
    agent_id: UUID,
    db: Session = Depends(get_db),
):

    service = ToolService(db)

    return service.get_agent_tools(
        agent_id
    )


# ---------------------------------------------------
# Assign Tool to Agent
# ---------------------------------------------------

@router.post(
    "/agents/{agent_id}/tools/{tool_id}",
    status_code=status.HTTP_201_CREATED,
)
def assign_tool(
    agent_id: UUID,
    tool_id: UUID,
    db: Session = Depends(get_db),
):

    service = ToolService(db)

    return service.assign_tool(
        agent_id,
        tool_id,
    )


# ---------------------------------------------------
# Remove Tool from Agent
# ---------------------------------------------------

@router.delete(
    "/agents/{agent_id}/tools/{tool_id}"
)
def remove_tool(
    agent_id: UUID,
    tool_id: UUID,
    db: Session = Depends(get_db),
):

    service = ToolService(db)

    return service.remove_tool(
        agent_id,
        tool_id,
    )