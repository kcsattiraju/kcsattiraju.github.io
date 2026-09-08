from app.database.connection import Base, engine

from app.agents.agent_model import Agent

from app.tools.tool_model import (
    ToolModel,
    AgentTool,
)

from app.datasources.datasource_model import (
    DataSource,
    AgentDataSource,
    DataSourceSchema,
)

from app.conversations.conversation_model import (
    Conversation,
    Message,
)

from app.executions.execution_model import (
    AgentExecution,
    ToolExecution,
)


def setup_database():
    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully.")