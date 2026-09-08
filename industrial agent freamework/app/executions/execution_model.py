import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.connection import Base


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agents.id"),
        nullable=False
    )

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id"),
        nullable=True
    )

    user_input = Column(
        Text,
        nullable=False
    )

    final_response = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(50),
        default="started"
    )

    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )


class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    agent_execution_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "agent_executions.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    tool_name = Column(
        String(150),
        nullable=False
    )

    tool_input = Column(
        JSON,
        nullable=True
    )

    tool_output = Column(
        JSON,
        nullable=True
    )

    status = Column(
        String(50),
        default="started"
    )

    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )