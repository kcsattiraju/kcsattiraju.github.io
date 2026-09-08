import uuid

from sqlalchemy import (
    Boolean,
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


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String(200),
        nullable=False
    )

    source_type = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    configuration = Column(
        JSON,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class AgentDataSource(Base):
    __tablename__ = "agent_data_sources"

    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    data_source_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "data_sources.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )


class DataSourceSchema(Base):
    __tablename__ = "data_source_schemas"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    data_source_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "data_sources.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    schema_name = Column(
        String(200),
        nullable=True
    )

    schema_definition = Column(
        JSON,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )