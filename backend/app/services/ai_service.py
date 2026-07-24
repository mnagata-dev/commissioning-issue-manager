"""AI Draft application service."""

from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as PydanticValidationError

from app.clients import OllamaClient, OllamaClientError
from app.core.exceptions import AIServiceError, NotFoundError, ValidationError
from app.models import Category, Project, Room, TargetType
from app.repositories import ProjectRepository, RoomRepository
from app.schemas import GenerateDraftRequest, GenerateDraftResponse


class _DraftOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Category
    description: str = Field(min_length=1)


class AIService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        room_repository: RoomRepository,
        ollama_client: OllamaClient,
        model: str | None,
    ) -> None:
        self.project_repository = project_repository
        self.room_repository = room_repository
        self.ollama_client = ollama_client
        self.model = model

    def generate_issue_draft(
        self, request: GenerateDraftRequest, user_id: int
    ) -> GenerateDraftResponse:
        del user_id
        project = self._require_project(request.project_id)
        target_type = self._parse_target_type(request.target_type)
        target_context = self._validate_target(
            project, target_type, request.room_id, request.target
        )
        if request.input_text == "":
            raise ValidationError("Input text must not be empty.")
        if self.model is None or self.model == "":
            raise AIServiceError()

        messages = self._build_messages(
            target_type, target_context, request.input_text
        )
        try:
            content = self.ollama_client.chat(
                model=self.model,
                messages=messages,
                response_format=_DraftOutput.model_json_schema(),
            )
            output = _DraftOutput.model_validate_json(content)
        except (OllamaClientError, PydanticValidationError, TypeError) as error:
            raise AIServiceError() from error

        return GenerateDraftResponse(
            category=output.category.value,
            description=output.description,
        )

    def _require_project(self, project_id: int) -> Project:
        project = self.project_repository.find_by_id(project_id)
        if project is None:
            raise NotFoundError("Project not found.")
        return project

    @staticmethod
    def _parse_target_type(value: str) -> TargetType:
        try:
            return TargetType(value)
        except ValueError as error:
            raise ValidationError("Invalid target type.") from error

    def _validate_target(
        self,
        project: Project,
        target_type: TargetType,
        room_id: int | None,
        target: str | None,
    ) -> str:
        if target_type is TargetType.ROOM:
            if room_id is None or target is not None:
                raise ValidationError("ROOM requires a room and no target.")
            room = self._require_room(room_id)
            if room.hotel_id != project.hotel_id:
                raise ValidationError("Room does not belong to the Project hotel.")
            return room.room_number
        if room_id is not None or target is None or target == "":
            raise ValidationError("OTHER requires a target and no room.")
        return target

    def _require_room(self, room_id: int) -> Room:
        room = self.room_repository.find_by_id(room_id)
        if room is None:
            raise NotFoundError("Room not found.")
        return room

    @staticmethod
    def _build_messages(
        target_type: TargetType, target_context: str, input_text: str
    ) -> list[dict[str, str]]:
        categories = ", ".join(category.value for category in Category)
        system_message = (
            "Assist with CIM Issue Draft creation. "
            "Return only category and description. "
            f"Category must be one of: {categories}. "
            "Write a natural Issue description based only on the user's input. "
            "Do not invent missing commissioning facts. Do not infer or change Target "
            "Type, Room, or Target. Do not save or register an Issue. "
            "When Category cannot be determined, return OTHER."
        )
        context_label = "Room Number" if target_type is TargetType.ROOM else "Target"
        user_message = (
            f"Target Type: {target_type.value}\n"
            f"{context_label}: {target_context}\n"
            f"Input Text: {input_text}"
        )
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]
