from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.clients import OllamaClientError
from app.core.exceptions import AIServiceError, NotFoundError, ValidationError
from app.models import Hotel, Project, Room
from app.schemas import GenerateDraftRequest
from app.services import AIService


@pytest.fixture
def entities() -> dict[str, object]:
    timestamp = datetime(2026, 7, 23, 8, 0)
    hotel = Hotel(id=1, name="Hotel", created_at=timestamp, updated_at=timestamp)
    project = Project(
        id=2,
        hotel_id=1,
        name="Project",
        created_at=timestamp,
        updated_at=timestamp,
    )
    room = Room(
        id=3,
        hotel_id=1,
        room_type_id=4,
        room_number="1203",
        display_name=None,
        created_at=timestamp,
        updated_at=timestamp,
    )
    return {"hotel": hotel, "project": project, "room": room}


@pytest.fixture
def dependencies(entities):
    project_repository = MagicMock()
    room_repository = MagicMock()
    ollama_client = MagicMock()
    project_repository.find_by_id.return_value = entities["project"]
    room_repository.find_by_id.return_value = entities["room"]
    ollama_client.chat.return_value = (
        '{"category":"LIGHTING","description":"Bathroom light remains on."}'
    )
    return project_repository, room_repository, ollama_client


@pytest.fixture
def service(dependencies) -> AIService:
    return AIService(*dependencies, model="test-model")


def room_request(**changes) -> GenerateDraftRequest:
    data = {
        "project_id": 2,
        "target_type": "ROOM",
        "room_id": 3,
        "target": None,
        "input_text": "Bathroom light does not turn off.",
    }
    data.update(changes)
    return GenerateDraftRequest(**data)


def test_generate_issue_draft_returns_only_category_and_description(
    service: AIService, dependencies
) -> None:
    project_repository, room_repository, ollama_client = dependencies

    response = service.generate_issue_draft(room_request(), user_id=99)

    assert response.model_dump() == {
        "category": "LIGHTING",
        "description": "Bathroom light remains on.",
    }
    project_repository.find_by_id.assert_called_once_with(2)
    room_repository.find_by_id.assert_called_once_with(3)
    call = ollama_client.chat.call_args
    assert call.kwargs["model"] == "test-model"
    assert set(call.kwargs["response_format"]["properties"]) == {
        "category",
        "description",
    }
    assert call.kwargs["response_format"]["additionalProperties"] is False


def test_prompt_preserves_selected_room_context(
    service: AIService, dependencies
) -> None:
    service.generate_issue_draft(room_request(), user_id=99)
    messages = dependencies[2].chat.call_args.kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert "category and description" in messages[0]["content"]
    assert (
        "Do not infer or change Target Type, Room, or Target"
        in messages[0]["content"]
    )
    assert "return OTHER" in messages[0]["content"]
    assert "Target Type: ROOM" in messages[1]["content"]
    assert "Room Number: 1203" in messages[1]["content"]
    assert "Input Text: Bathroom light does not turn off." in messages[1]["content"]
    assert "project_id" not in messages[1]["content"]
    assert "99" not in messages[1]["content"]


def test_prompt_preserves_selected_other_target(
    service: AIService, dependencies
) -> None:
    request = room_request(
        target_type="OTHER", room_id=None, target="Network", input_text="No link."
    )
    service.generate_issue_draft(request, user_id=99)
    user_message = dependencies[2].chat.call_args.kwargs["messages"][1]["content"]
    assert "Target Type: OTHER" in user_message
    assert "Target: Network" in user_message
    assert "Room Number" not in user_message


@pytest.mark.parametrize(
    "changes",
    [
        {"target_type": "INVALID"},
        {"room_id": None},
        {"target": "Network"},
        {"target_type": "OTHER", "room_id": 3, "target": "Network"},
        {"target_type": "OTHER", "room_id": None, "target": None},
        {"target_type": "OTHER", "room_id": None, "target": ""},
        {"input_text": ""},
    ],
)
def test_invalid_input_is_rejected_before_provider_call(
    service: AIService, dependencies, changes
) -> None:
    with pytest.raises(ValidationError):
        service.generate_issue_draft(room_request(**changes), user_id=99)
    dependencies[2].chat.assert_not_called()


def test_missing_project_raises_not_found(service: AIService, dependencies) -> None:
    dependencies[0].find_by_id.return_value = None
    with pytest.raises(NotFoundError, match="Project not found"):
        service.generate_issue_draft(room_request(), user_id=99)


def test_missing_room_raises_not_found(service: AIService, dependencies) -> None:
    dependencies[1].find_by_id.return_value = None
    with pytest.raises(NotFoundError, match="Room not found"):
        service.generate_issue_draft(room_request(), user_id=99)


def test_room_project_hotel_mismatch(
    service: AIService, dependencies, entities
) -> None:
    entities["room"].hotel_id = 88
    with pytest.raises(ValidationError, match="Project hotel"):
        service.generate_issue_draft(room_request(), user_id=99)


def test_missing_model_raises_ai_service_error(dependencies) -> None:
    service = AIService(*dependencies, model=None)
    with pytest.raises(AIServiceError, match="AI service failed"):
        service.generate_issue_draft(room_request(), user_id=99)
    dependencies[2].chat.assert_not_called()


def test_provider_failure_becomes_ai_service_error(
    service: AIService, dependencies
) -> None:
    dependencies[2].chat.side_effect = OllamaClientError("private provider detail")
    with pytest.raises(AIServiceError) as error:
        service.generate_issue_draft(room_request(), user_id=99)
    assert error.value.message == "The AI service failed."


@pytest.mark.parametrize(
    "provider_content",
    [
        "not-json",
        "{}",
        '{"category":"INVALID","description":"Draft"}',
        '{"category":"OTHER"}',
        '{"category":"OTHER","description":42}',
        '{"category":"OTHER","description":""}',
        '{"category":"OTHER","description":"Draft","target":"Network"}',
    ],
)
def test_invalid_provider_output_becomes_ai_service_error(
    service: AIService, dependencies, provider_content: str
) -> None:
    dependencies[2].chat.return_value = provider_content
    with pytest.raises(AIServiceError, match="AI service failed"):
        service.generate_issue_draft(room_request(), user_id=99)


def test_other_category_is_accepted(service: AIService, dependencies) -> None:
    dependencies[2].chat.return_value = (
        '{"category":"OTHER","description":"Review required."}'
    )
    response = service.generate_issue_draft(room_request(), user_id=99)
    assert response.category == "OTHER"
