from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.agent_repository import AgentRepository
from app.tools.tool_repository import ToolRepository


class ToolService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db
        self.repository = ToolRepository(db)

    # ---------------------------------------------------
    # Get available tools
    # ---------------------------------------------------

    def get_all_tools(self):

        tools = self.repository.get_all()

        return [
            {
                "id": str(tool.id),
                "name": tool.name,
                "description": tool.description,
                "tool_type": tool.tool_type,
                "is_enabled": tool.is_enabled,
            }
            for tool in tools
        ]

    # ---------------------------------------------------
    # Get tools assigned to Agent
    # Reads agent_tools
    # ---------------------------------------------------

    def get_agent_tools(
        self,
        agent_id: UUID,
    ):

        agent = AgentRepository.get_by_id(
            self.db,
            agent_id,
        )

        if agent is None:
            raise HTTPException(
                status_code=404,
                detail="Agent not found.",
            )

        tools = self.repository.get_agent_tools(
            agent_id
        )

        return [
            {
                "id": str(tool.id),
                "name": tool.name,
                "description": tool.description,
                "tool_type": tool.tool_type,
                "is_enabled": tool.is_enabled,
            }
            for tool in tools
        ]

    # ---------------------------------------------------
    # Assign Tool
    # Writes agent_tools
    # ---------------------------------------------------

    def assign_tool(
        self,
        agent_id: UUID,
        tool_id: UUID,
    ):

        agent = AgentRepository.get_by_id(
            self.db,
            agent_id,
        )

        if agent is None:
            raise HTTPException(
                status_code=404,
                detail="Agent not found.",
            )

        tool = self.repository.get_by_id(
            tool_id
        )

        if tool is None:
            raise HTTPException(
                status_code=404,
                detail="Tool not found.",
            )

        self.repository.assign_tool(
            agent_id,
            tool_id,
        )

        return {
            "message": (
                f"Tool '{tool.name}' assigned "
                f"to agent '{agent.name}'."
            )
        }

    # ---------------------------------------------------
    # Remove Tool
    # Deletes agent_tools relationship
    # ---------------------------------------------------

    def remove_tool(
        self,
        agent_id: UUID,
        tool_id: UUID,
    ):

        agent = AgentRepository.get_by_id(
            self.db,
            agent_id,
        )

        if agent is None:
            raise HTTPException(
                status_code=404,
                detail="Agent not found.",
            )

        removed = self.repository.remove_tool(
            agent_id,
            tool_id,
        )

        if not removed:
            raise HTTPException(
                status_code=404,
                detail="Tool assignment not found.",
            )

        return {
            "message": "Tool removed from agent."
        }