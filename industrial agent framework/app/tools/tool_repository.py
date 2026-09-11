from sqlalchemy.orm import Session

from app.tools.tool_model import AgentTool, ToolModel


class ToolRepository:
    """Database access for tools and agent-tool assignments."""

    def __init__(self, db: Session):
        self.db = db

    # ========================================================
    # GET ALL ENABLED TOOLS
    # ========================================================

    def get_all_tools(self):
        return (
            self.db.query(ToolModel)
            .filter(ToolModel.is_enabled.is_(True))
            .order_by(ToolModel.name.asc())
            .all()
        )

    # ========================================================
    # GET TOOL BY NAME
    # ========================================================

    def get_tool_by_name(self, tool_name: str):
        return (
            self.db.query(ToolModel)
            .filter(ToolModel.name == tool_name)
            .first()
        )

    # ========================================================
    # GET TOOLS ASSIGNED TO AGENT
    # ========================================================

    def get_agent_tools(self, agent_id):
        return (
            self.db.query(ToolModel)
            .join(
                AgentTool,
                AgentTool.tool_id == ToolModel.id,
            )
            .filter(AgentTool.agent_id == agent_id)
            .order_by(ToolModel.name.asc())
            .all()
        )

    # ========================================================
    # ASSIGN ONE TOOL TO AGENT
    # ========================================================

    def assign_tool(self, agent_id, tool_name: str):
        tool = self.get_tool_by_name(tool_name)

        if tool is None:
            raise ValueError(
                f"Tool '{tool_name}' does not exist."
            )

        existing = (
            self.db.query(AgentTool)
            .filter(
                AgentTool.agent_id == agent_id,
                AgentTool.tool_id == tool.id,
            )
            .first()
        )

        if existing is not None:
            return existing

        assignment = AgentTool(
            agent_id=agent_id,
            tool_id=tool.id,
        )

        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        return assignment

    # ========================================================
    # REPLACE ALL TOOLS ASSIGNED TO AGENT
    # ========================================================

    def replace_agent_tools(
        self,
        agent_id,
        tool_names: list[str],
    ):
        """
        Replace all current tool assignments for an agent
        with the supplied tool names.

        This method is used by AgentService during both
        agent creation and agent update.
        """

        # Validate all tool names first so a bad name does not
        # delete the agent's existing assignments.
        tools = []

        for tool_name in tool_names:
            tool = self.get_tool_by_name(tool_name)

            if tool is None:
                raise ValueError(
                    f"Tool '{tool_name}' does not exist."
                )

            tools.append(tool)

        try:
            (
                self.db.query(AgentTool)
                .filter(AgentTool.agent_id == agent_id)
                .delete(synchronize_session=False)
            )

            for tool in tools:
                self.db.add(
                    AgentTool(
                        agent_id=agent_id,
                        tool_id=tool.id,
                    )
                )

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

    # ========================================================
    # REMOVE ALL TOOLS FROM AGENT
    # ========================================================

    def remove_agent_tools(self, agent_id):
        try:
            (
                self.db.query(AgentTool)
                .filter(AgentTool.agent_id == agent_id)
                .delete(synchronize_session=False)
            )

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise
