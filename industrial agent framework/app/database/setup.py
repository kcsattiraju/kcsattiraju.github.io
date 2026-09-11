from app.database.connection import Base, engine

# Agent models
from app.agents.agent_model import Agent

# Tool models
from app.tools.tool_model import (
    ToolModel,
    AgentTool,
)

# Data source models
from app.datasources.datasource_model import (
    DataSource,
    AgentDataSource,
    DataSourceSchema,
)

# Conversation models
from app.conversations.conversation_model import (
    Conversation,
    Message,
)

# Execution models
from app.executions.execution_model import (
    AgentExecution,
    ToolExecution,
)

# Phase 2 document models
from app.documents.document_model import Document
from app.documents.document_chunk_model import DocumentChunk
from app.documents.agent_document_model import AgentDocument


def setup_database():
    print("Creating database tables...")

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully.")


if __name__ == "__main__":
    setup_database()