from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.agent_model import Agent
from app.agents.agent_repository import AgentRepository
from app.api.schemas.agent_schema import (
    AgentCreate,
    AgentUpdate,
)
from app.tools.tool_repository import ToolRepository


class AgentService:

    # ---------------------------------------------------
    # Build API response using database relationship
    # ---------------------------------------------------

    @staticmethod
    def _build_agent_response(
        db: Session,
        agent: Agent,
    ) -> dict:

        tool_repository = ToolRepository(db)

        assigned_tools = tool_repository.get_agent_tools(
            agent.id
        )

        return {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "purpose": agent.purpose,
            "goal": agent.goal,
            "system_prompt": agent.system_prompt,
            "model_provider": agent.model_provider,
            "model_name": agent.model_name,
            "memory_enabled": agent.memory_enabled,
            "is_active": agent.is_active,
            "version": agent.version,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,

            # IMPORTANT:
            # Loaded from agent_tools -> tools
            "tools": [
                tool.name
                for tool in assigned_tools
            ],
        }

    # ---------------------------------------------------
    # Create Agent
    # ---------------------------------------------------

    @staticmethod
    def create_agent(
        db: Session,
        request: AgentCreate,
    ) -> dict:

        agent = Agent(
            name=request.name,
            description=request.description,
            purpose=request.purpose,
            goal=request.goal,
            system_prompt=request.system_prompt,
            model_provider=request.model_provider,
            model_name=request.model_name,
            memory_enabled=request.memory_enabled,
        )

        agent = AgentRepository.create(
            db,
            agent,
        )

        tool_repository = ToolRepository(db)

        try:

            # Save selected tools in agent_tools
            tool_repository.replace_agent_tools(
                agent.id,
                request.tools,
            )

        except ValueError as error:

            # Remove the newly created agent
            # if tool assignment failed
            AgentRepository.delete(
                db,
                agent,
            )

            raise HTTPException(
                status_code=400,
                detail=str(error),
            )

        return AgentService._build_agent_response(
            db,
            agent,
        )

    # ---------------------------------------------------
    # Get one Agent
    # ---------------------------------------------------

    @staticmethod
    def get_agent(
        db: Session,
        agent_id: UUID,
    ) -> dict:

        agent = AgentRepository.get_by_id(
            db,
            agent_id,
        )

        if agent is None:
            raise HTTPException(
                status_code=404,
                detail="Agent not found.",
            )

        return AgentService._build_agent_response(
            db,
            agent,
        )

    # ---------------------------------------------------
    # Get all Agents
    # ---------------------------------------------------

    @staticmethod
    def get_agents(
        db: Session,
    ) -> list[dict]:

        agents = AgentRepository.get_all(db)

        return [
            AgentService._build_agent_response(
                db,
                agent,
            )
            for agent in agents
        ]

    # ---------------------------------------------------
    # Update Agent
    # ---------------------------------------------------

    @staticmethod
    def update_agent(
        db: Session,
        agent_id: UUID,
        request: AgentUpdate,
    ) -> dict:

        agent = AgentRepository.get_by_id(
            db,
            agent_id,
        )

        if agent is None:
            raise HTTPException(
                status_code=404,
                detail="Agent not found.",
            )

        update_data = request.model_dump(
            exclude_unset=True
        )

        # tools is relationship data,
        # not a column on agents
        tools = update_data.pop(
            "tools",
            None,
        )

        for field, value in update_data.items():
            setattr(
                agent,
                field,
                value,
            )

        agent = AgentRepository.save(
            db,
            agent,
        )

        if tools is not None:

            tool_repository = ToolRepository(db)

            try:
                tool_repository.replace_agent_tools(
                    agent.id,
                    tools,
                )

            except ValueError as error:
                raise HTTPException(
                    status_code=400,
                    detail=str(error),
                )

        return AgentService._build_agent_response(
            db,
            agent,
        )

    # ---------------------------------------------------
    # Delete Agent
    # ---------------------------------------------------

    @staticmethod
    def delete_agent(
        db: Session,
        agent_id: UUID,
    ) -> None:

        agent = AgentRepository.get_by_id(
            db,
            agent_id,
        )

        if agent is None:
            raise HTTPException(
                status_code=404,
                detail="Agent not found.",
            )

        tool_repository = ToolRepository(db)

        # Explicitly remove agent-tool relationships
        tool_repository.replace_agent_tools(
            agent.id,
            [],
        )

        AgentRepository.delete(
            db,
            agent,
        )