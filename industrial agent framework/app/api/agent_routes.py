from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from app.database.connection import get_db
from app.agents.agent_service import AgentService


router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)


# ============================================================
# REQUEST MODELS
# ============================================================

class AgentCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    goal: str
    system_prompt: str

    tools: List[str] = Field(
        default_factory=list
    )


class AgentUpdateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    goal: str
    system_prompt: str

    tools: List[str] = Field(
        default_factory=list
    )


# ============================================================
# CREATE AGENT
# ============================================================

@router.post("")
def create_agent(
    request: AgentCreateRequest,
    db: Session = Depends(get_db)
):
    try:

        return AgentService.create_agent(
            db,
            request
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        print(
            "CREATE AGENT ERROR:",
            repr(e)
        )

        raise


# ============================================================
# GET ALL AGENTS
# ============================================================

@router.get("")
def get_agents(
    db: Session = Depends(get_db)
):
    try:

        return AgentService.get_agents(
            db
        )

    except Exception as e:

        print(
            "GET AGENTS ERROR:",
            repr(e)
        )

        raise


# ============================================================
# GET AGENT BY ID
# ============================================================

@router.get("/{agent_id}")
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    try:

        agent = AgentService.get_agent(
            db,
            agent_id
        )

        if agent is None:

            raise HTTPException(
                status_code=404,
                detail="Agent not found"
            )

        return agent

    except HTTPException:
        raise

    except Exception as e:

        print(
            "GET AGENT ERROR:",
            repr(e)
        )

        raise


# ============================================================
# UPDATE AGENT
# ============================================================

@router.put("/{agent_id}")
def update_agent(
    agent_id: str,
    request: AgentUpdateRequest,
    db: Session = Depends(get_db)
):
    try:

        agent = AgentService.update_agent(
            db,
            agent_id,
            request
        )

        if agent is None:

            raise HTTPException(
                status_code=404,
                detail="Agent not found"
            )

        return agent

    except HTTPException:
        raise

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        print(
            "UPDATE AGENT ERROR:",
            repr(e)
        )

        raise


# ============================================================
# DELETE AGENT
# ============================================================

@router.delete("/{agent_id}")
def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    try:

        deleted = AgentService.delete_agent(
            db,
            agent_id
        )

        if not deleted:

            raise HTTPException(
                status_code=404,
                detail="Agent not found"
            )

        return {
            "message": "Agent deleted successfully"
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            "DELETE AGENT ERROR:",
            repr(e)
        )

        raise