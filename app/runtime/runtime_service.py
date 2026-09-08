from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.agent_repository import AgentRepository
from app.runtime.agent_runtime import build_runtime_agent
from app.tools.tool_repository import ToolRepository


class RuntimeService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def chat(
        self,
        agent_id: UUID,
        message: str,
    ) -> str:

        # ------------------------------------------------
        # Load Agent Configuration
        # ------------------------------------------------

        agent_definition = (
            AgentRepository.get_by_id(
                self.db,
                agent_id,
            )
        )

        if agent_definition is None:

            raise ValueError(
                f"Agent '{agent_id}' "
                f"was not found."
            )

        # ------------------------------------------------
        # Load Agent Tool Assignments
        # ------------------------------------------------

        tool_repository = ToolRepository(
            self.db
        )

        assigned_tools = (
            tool_repository.get_agent_tools(
                agent_id
            )
        )

        # ------------------------------------------------
        # Convert Tool Models to Tool Names
        # ------------------------------------------------

        tool_names = [
            tool.name
            for tool in assigned_tools
        ]

        # ------------------------------------------------
        # Build Runtime Agent
        # ------------------------------------------------

        runtime_agent = (
            build_runtime_agent(
                agent_definition,
                tool_names,
            )
        )

        # ------------------------------------------------
        # Execute Agent
        # ------------------------------------------------

        result = runtime_agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            }
        )

        # ------------------------------------------------
        # Extract Response
        # ------------------------------------------------

        messages = result.get(
            "messages",
            [],
        )

        if not messages:

            return (
                "No response from agent."
            )

        last_message = messages[-1]

        if hasattr(
            last_message,
            "content",
        ):

            return last_message.content

        return str(
            last_message
        )