from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.connection import Base


# ===================================================
# TOOL TABLE
# ===================================================

class ToolModel(Base):
    __tablename__ = "tools"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    name = Column(
        String,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    tool_type = Column(
        String,
        nullable=True,
    )

    is_enabled = Column(
        Boolean,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


# ===================================================
# AGENT <-> TOOL RELATIONSHIP TABLE
# ===================================================

class AgentTool(Base):
    __tablename__ = "agent_tools"

    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    tool_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "tools.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )


# ===================================================
# BACKWARD COMPATIBILITY
# ===================================================

ToolDefinition = ToolModel