import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    Text
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.connection import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    purpose = Column(
        Text,
        nullable=True
    )

    goal = Column(
        Text,
        nullable=False
    )

    system_prompt = Column(
        Text,
        nullable=False
    )

    model_provider = Column(
        String(100),
        nullable=True
    )

    model_name = Column(
        String(150),
        nullable=True
    )

    memory_enabled = Column(
        Boolean,
        default=True,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    version = Column(
        String(30),
        default="1.0"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )