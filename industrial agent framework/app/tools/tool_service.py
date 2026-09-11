from app.tools.tool_repository import ToolRepository


class ToolService:

    def __init__(self, db):
        self.db = db

        self.tool_repository = ToolRepository(
            db
        )


    # ========================================================
    # GET ALL TOOLS
    # ========================================================

    def get_all_tools(self):

        return (
            self.tool_repository
            .get_all_tools()
        )


    # ========================================================
    # GET AGENT TOOLS
    # ========================================================

    def get_agent_tools(
        self,
        agent_id
    ):

        return (
            self.tool_repository
            .get_agent_tools(
                agent_id
            )
        )


    # ========================================================
    # ASSIGN TOOL
    # ========================================================

    def assign_tool(
        self,
        agent_id,
        tool_name
    ):

        return (
            self.tool_repository
            .assign_tool(
                agent_id=agent_id,
                tool_name=tool_name
            )
        )