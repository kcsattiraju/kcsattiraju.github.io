from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ToolResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    name: str
    description: str | None
    tool_type: str | None
    is_enabled: bool


class ToolAssignmentResponse(BaseModel):

    message: str