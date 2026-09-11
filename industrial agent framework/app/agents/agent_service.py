from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.agent_model import Agent
from app.agents.agent_repository import AgentRepository
from app.tools.tool_repository import ToolRepository


class AgentService:

    # ========================================================
    # CONVERT AGENT ID
    # ========================================================

    @staticmethod
    def _to_uuid(agent_id) -> UUID:
        """
        Convert string agent IDs coming from FastAPI/Streamlit
        into UUID objects used by PostgreSQL/SQLAlchemy.
        """

        if isinstance(agent_id, UUID):
            return agent_id

        return UUID(str(agent_id))


    # ========================================================
    # EXTRACT TOOL NAME
    # ========================================================

    @staticmethod
    def _get_tool_name(tool):
        """
        Supports tools returned as:

        Dictionary:
            {"name": "search_documents"}

        String:
            "search_documents"

        ORM object:
            tool.name
        """

        if isinstance(tool, dict):

            return (
                tool.get("name")
                or tool.get("tool_name")
            )

        if isinstance(tool, str):

            return tool

        return getattr(
            tool,
            "name",
            None
        )


    # ========================================================
    # BUILD AGENT RESPONSE
    # ========================================================

    @staticmethod
    def _build_agent_response(
        db: Session,
        agent: Agent,
    ):

        tool_repository = ToolRepository(
            db
        )

        tools = tool_repository.get_agent_tools(
            agent.id
        )

        tool_names = []

        for tool in tools:

            tool_name = (
                AgentService._get_tool_name(
                    tool
                )
            )

            if tool_name:

                tool_names.append(
                    tool_name
                )


        return {
            "id": str(agent.id),
            "name": agent.name,
            "description": agent.description,
            "goal": agent.goal,
            "system_prompt": agent.system_prompt,
            "tools": tool_names,
        }


    # ========================================================
    # CREATE AGENT
    # ========================================================

    @staticmethod
    def create_agent(
        db: Session,
        agent_data,
    ):

        # ----------------------------------------------------
        # CREATE ORM AGENT OBJECT
        # ----------------------------------------------------

        agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            goal=agent_data.goal,
            system_prompt=agent_data.system_prompt,
        )


        # ----------------------------------------------------
        # SAVE AGENT
        # ----------------------------------------------------

        created_agent = (
            AgentRepository.create(
                db,
                agent,
            )
        )


        # ----------------------------------------------------
        # ASSIGN TOOLS
        # ----------------------------------------------------

        tools = (
            agent_data.tools
            if agent_data.tools
            else []
        )


        tool_repository = ToolRepository(
            db
        )


        tool_repository.replace_agent_tools(
            created_agent.id,
            tools,
        )


        # ----------------------------------------------------
        # RETURN RESPONSE
        # ----------------------------------------------------

        return (
            AgentService._build_agent_response(
                db,
                created_agent,
            )
        )


    # ========================================================
    # GET ALL AGENTS
    # ========================================================

    @staticmethod
    def get_agents(
        db: Session,
    ):

        agents = (
            AgentRepository.get_all(
                db
            )
        )


        results = []


        for agent in agents:

            results.append(
                AgentService._build_agent_response(
                    db,
                    agent,
                )
            )


        return results


    # ========================================================
    # GET AGENT BY ID
    # ========================================================

    @staticmethod
    def get_agent(
        db: Session,
        agent_id,
    ):

        agent_uuid = (
            AgentService._to_uuid(
                agent_id
            )
        )


        agent = (
            AgentRepository.get_by_id(
                db,
                agent_uuid,
            )
        )


        if agent is None:

            return None


        return (
            AgentService._build_agent_response(
                db,
                agent,
            )
        )


    # ========================================================
    # UPDATE AGENT
    # ========================================================

    @staticmethod
    def update_agent(
        db: Session,
        agent_id,
        agent_data,
    ):

        agent_uuid = (
            AgentService._to_uuid(
                agent_id
            )
        )


        # ----------------------------------------------------
        # FIND AGENT
        # ----------------------------------------------------

        agent = (
            AgentRepository.get_by_id(
                db,
                agent_uuid,
            )
        )


        if agent is None:

            return None


        # ----------------------------------------------------
        # UPDATE FIELDS
        # ----------------------------------------------------

        agent.name = (
            agent_data.name
        )

        agent.description = (
            agent_data.description
        )

        agent.goal = (
            agent_data.goal
        )

        agent.system_prompt = (
            agent_data.system_prompt
        )


        # ----------------------------------------------------
        # SAVE CHANGES
        # ----------------------------------------------------

        updated_agent = (
            AgentRepository.save(
                db,
                agent,
            )
        )


        # ----------------------------------------------------
        # UPDATE TOOLS
        # ----------------------------------------------------

        tools = (
            agent_data.tools
            if agent_data.tools
            is not None
            else []
        )


        tool_repository = ToolRepository(
            db
        )


        tool_repository.replace_agent_tools(
            updated_agent.id,
            tools,
        )


        # ----------------------------------------------------
        # RETURN UPDATED AGENT
        # ----------------------------------------------------

        return (
            AgentService._build_agent_response(
                db,
                updated_agent,
            )
        )


    # ========================================================
    # DELETE AGENT
    # ========================================================

    @staticmethod
    def delete_agent(
        db: Session,
        agent_id,
    ):

        agent_uuid = (
            AgentService._to_uuid(
                agent_id
            )
        )


        agent = (
            AgentRepository.get_by_id(
                db,
                agent_uuid,
            )
        )


        if agent is None:

            return False


        AgentRepository.delete(
            db,
            agent,
        )


        return True