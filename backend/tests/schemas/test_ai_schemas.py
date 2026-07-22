import pytest
from pydantic import ValidationError

from app.schemas import GenerateDraftRequest, GenerateDraftResponse


def test_generate_draft_request_accepts_valid_input() -> None:
    request = GenerateDraftRequest(
        project_id=1,
        target_type="ROOM",
        room_id=2,
        input_text="Light does not turn off.",
    )
    assert request.target is None
    assert request.room_id == 2


def test_generate_draft_request_defaults_optional_fields_to_none() -> None:
    request = GenerateDraftRequest(
        project_id=1, target_type="ARBITRARY", input_text="Input"
    )
    assert request.room_id is None
    assert request.target is None


@pytest.mark.parametrize("missing_field", ["project_id", "target_type", "input_text"])
def test_generate_draft_request_requires_fields(missing_field: str) -> None:
    data = {"project_id": 1, "target_type": "ROOM", "input_text": "Input"}
    data.pop(missing_field)
    with pytest.raises(ValidationError):
        GenerateDraftRequest.model_validate(data)


def test_generate_draft_response_accepts_valid_input() -> None:
    response = GenerateDraftResponse(category="LIGHTING", description="Description")
    assert response.model_dump() == {"category": "LIGHTING", "description": "Description"}


def test_ai_schemas_reject_extra_fields() -> None:
    with pytest.raises(ValidationError):
        GenerateDraftResponse(category="OTHER", description="Description", room_id=1)
