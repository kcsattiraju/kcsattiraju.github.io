from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    name: str
    description: str | None = None
    purpose: str | None = None
    goal: str
    system_prompt: str

    model_provider: str | None = None
    model_name: str | None = None

    memory_enabled: bool = True

    # Tool names selected from Streamlit
    tools: list[str] = Field(default_factory=list)


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    purpose: str | None = None
    goal: str | None = None
    system_prompt: str | None = None

    model_provider: str | None = None
    model_name: str | None = None

    memory_enabled: bool | None = None
    is_active: bool | None = None

    # If supplied, replace current tool assignments
    tools: list[str] | None = None


class AgentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    name: str
    description: str | None
    purpose: str | None
    goal: str
    system_prompt: str

    model_provider: str | None
    model_name: str | None

    memory_enabled: bool
    is_active: bool

    version: str | None

    created_at: datetime
    updated_at: datetime

    # Returned from agent_tools relationship
    tools: list[str] = Field(
        default_factory=list
    )