"""Administration command inputs and safe results."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, model_validator

from app.models.enums import Role


class AdministrationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UpdateInput(AdministrationInput):
    @model_validator(mode="after")
    def reject_explicit_null(self) -> Self:
        for name in self.model_fields_set:
            if getattr(self, name) is None:
                if isinstance(self, UpdateRoomRequest) and name == "display_name":
                    continue
                raise ValueError("A supplied required field must not be null.")
        return self


class CreateHotelRequest(AdministrationInput):
    name: StrictStr


class UpdateHotelRequest(UpdateInput):
    name: StrictStr | None = None


class CreateProjectRequest(AdministrationInput):
    hotel_id: StrictInt
    name: StrictStr


class UpdateProjectRequest(UpdateInput):
    name: StrictStr | None = None


class CreateRoomTypeRequest(AdministrationInput):
    hotel_id: StrictInt
    name: StrictStr


class UpdateRoomTypeRequest(UpdateInput):
    name: StrictStr | None = None


class CreateRoomRequest(AdministrationInput):
    hotel_id: StrictInt
    room_type_id: StrictInt
    room_number: StrictStr
    display_name: StrictStr | None = None


class UpdateRoomRequest(UpdateInput):
    room_type_id: StrictInt | None = None
    room_number: StrictStr | None = None
    display_name: StrictStr | None = None


class BootstrapAdminRequest(AdministrationInput):
    username: StrictStr
    display_name: StrictStr
    password: StrictStr = Field(repr=False)


class CreateUserRequest(BootstrapAdminRequest):
    role: Role


class UpdateUserRequest(UpdateInput):
    username: StrictStr | None = None
    display_name: StrictStr | None = None
    role: Role | None = None
    password: StrictStr | None = Field(default=None, repr=False)


class AdministrationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: str
    id: int
    operation: str
