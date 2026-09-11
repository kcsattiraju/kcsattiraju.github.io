import uuid

from sqlalchemy import Column, String, Text, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.connection import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_type = Column(
        String(50),
        nullable=True
    )

    file_size = Column(
        BigInteger,
        nullable=True
    )

    storage_path = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(50),
        nullable=False,
        default="uploaded"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )