from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_db
from app.tools.tool_service import ToolService


router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
)


@router.get("")
def get_tools(db=Depends(get_db)):
    """Return all enabled tools."""
    try:
        service = ToolService(db)
        return service.get_all_tools()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get("/agent/{agent_id}")
def get_agent_tools(
    agent_id: UUID,
    db=Depends(get_db),
):
    """Return tools assigned to a particular agent."""
    try:
        service = ToolService(db)
        return service.get_agent_tools(agent_id)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post("/agent/{agent_id}/{tool_name}")
def assign_tool(
    agent_id: UUID,
    tool_name: str,
    db=Depends(get_db),
):
    """Assign an existing tool to an agent."""
    try:
        service = ToolService(db)

        result = service.assign_tool(
            agent_id=agent_id,
            tool_name=tool_name,
        )

        return {
            "message": (
                f"Tool '{tool_name}' assigned "
                f"to agent '{agent_id}'."
            ),
            "result": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
