from uuid import UUID

from app.agents.agent_repository import AgentRepository
from app.tools.tool_repository import ToolRepository
from app.runtime.agent_runtime import build_runtime_agent


class RuntimeService:

    def __init__(self, db):
        self.db = db

        # AgentRepository uses static methods
        self.agent_repository = AgentRepository()

        # ToolRepository takes db in constructor
        self.tool_repository = ToolRepository(db)

    def chat(
        self,
        agent_id: UUID,
        message: str,
    ) -> str:

        # 1. Load agent
        agent = self.agent_repository.get_by_id(
            self.db,
            agent_id,
        )

        if agent is None:
            raise ValueError(
                f"Agent with id {agent_id} was not found."
            )

        print()
        print("======================================")
        print("RUNTIME CHAT")
        print("======================================")
        print("Agent ID:", agent_id)
        print("Agent Name:", agent.name)
        print("User Message:", message)

        # 2. Load assigned tools
        assigned_tools = (
            self.tool_repository
            .get_agent_tools(agent_id)
        )

        tool_names = []

        for tool in assigned_tools:

            if isinstance(tool, str):
                tool_names.append(tool)

            elif hasattr(tool, "name"):
                tool_names.append(
                    tool.name
                )

        print(
            "Assigned Tool Names:",
            tool_names
        )

        # 3. Build runtime agent
        runtime_agent = build_runtime_agent(
            agent=agent,
            tool_names=tool_names,
        )

        # 4. Invoke agent
        result = runtime_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        message,
                    )
                ]
            }
        )

        # 5. Extract response
        if isinstance(result, dict):

            messages = result.get(
                "messages",
                []
            )

            if messages:

                last_message = messages[-1]

                if hasattr(
                    last_message,
                    "content"
                ):
                    return str(
                        last_message.content
                    )

        return str(result)