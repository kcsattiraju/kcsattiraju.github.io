from uuid import UUID

from sqlalchemy.orm import Session

from app.tools.tool_model import (
    ToolModel,
    AgentTool,
)


class ToolRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    # ---------------------------------------------------
    # Get all enabled tools
    # ---------------------------------------------------

    def get_all(self):

        return (
            self.db.query(ToolModel)
            .filter(
                ToolModel.is_enabled.is_(True)
            )
            .order_by(
                ToolModel.name
            )
            .all()
        )

    # ---------------------------------------------------
    # Get tool by ID
    # ---------------------------------------------------

    def get_by_id(
        self,
        tool_id: UUID,
    ):

        return (
            self.db.query(ToolModel)
            .filter(
                ToolModel.id == tool_id
            )
            .first()
        )

    # ---------------------------------------------------
    # Get tool by name
    # ---------------------------------------------------

    def get_by_name(
        self,
        tool_name: str,
    ):

        return (
            self.db.query(ToolModel)
            .filter(
                ToolModel.name == tool_name,
                ToolModel.is_enabled.is_(True),
            )
            .first()
        )

    # ---------------------------------------------------
    # Get tools assigned to an agent
    # ---------------------------------------------------

    def get_agent_tools(
        self,
        agent_id: UUID,
    ):

        return (
            self.db.query(ToolModel)
            .join(
                AgentTool,
                AgentTool.tool_id
                == ToolModel.id,
            )
            .filter(
                AgentTool.agent_id
                == agent_id,
                ToolModel.is_enabled.is_(True),
            )
            .order_by(
                ToolModel.name
            )
            .all()
        )

    # ---------------------------------------------------
    # Assign a tool to an agent
    # ---------------------------------------------------

    def assign_tool(
        self,
        agent_id: UUID,
        tool_id: UUID,
    ):

        existing = (
            self.db.query(AgentTool)
            .filter(
                AgentTool.agent_id
                == agent_id,
                AgentTool.tool_id
                == tool_id,
            )
            .first()
        )

        if existing:
            return existing

        assignment = AgentTool(
            agent_id=agent_id,
            tool_id=tool_id,
        )

        self.db.add(
            assignment
        )

        self.db.commit()
        self.db.refresh(
            assignment
        )

        return assignment

    # ---------------------------------------------------
    # Replace all tool assignments for an agent
    # ---------------------------------------------------

    def replace_agent_tools(
        self,
        agent_id: UUID,
        tool_names: list[str],
    ):

        # Remove existing assignments
        (
            self.db.query(AgentTool)
            .filter(
                AgentTool.agent_id
                == agent_id
            )
            .delete(
                synchronize_session=False
            )
        )

        # Add selected tools
        for tool_name in tool_names:

            tool = self.get_by_name(
                tool_name
            )

            if tool is None:
                raise ValueError(
                    f"Tool '{tool_name}' "
                    f"was not found or is disabled."
                )

            assignment = AgentTool(
                agent_id=agent_id,
                tool_id=tool.id,
            )

            self.db.add(
                assignment
            )

        self.db.commit()

    # ---------------------------------------------------
    # Remove one tool
    # ---------------------------------------------------

    def remove_tool(
        self,
        agent_id: UUID,
        tool_id: UUID,
    ):

        assignment = (
            self.db.query(AgentTool)
            .filter(
                AgentTool.agent_id
                == agent_id,
                AgentTool.tool_id
                == tool_id,
            )
            .first()
        )

        if assignment is None:
            return False

        self.db.delete(
            assignment
        )

        self.db.commit()

        return True