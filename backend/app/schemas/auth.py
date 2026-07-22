"""Authentication request and response schemas."""

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    password: str


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    username: str
    display_name: str
    role: str
