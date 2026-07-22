import pytest
from pydantic import ValidationError

from app.schemas import HotelReferenceResponse, ProjectListResponse, ProjectResponse


def test_project_response_uses_typed_hotel() -> None:
    response = ProjectResponse(id=1, name="Commissioning", hotel={"id": 2, "name": "Hotel"})
    assert isinstance(response.hotel, HotelReferenceResponse)
    assert response.model_dump() == {
        "id": 1,
        "name": "Commissioning",
        "hotel": {"id": 2, "name": "Hotel"},
    }


def test_project_list_response_accepts_nested_projects() -> None:
    response = ProjectListResponse(
        projects=[{"id": 1, "name": "Commissioning", "hotel": {"id": 2, "name": "Hotel"}}]
    )
    assert isinstance(response.projects[0], ProjectResponse)


def test_project_response_rejects_invalid_hotel() -> None:
    with pytest.raises(ValidationError):
        ProjectResponse(id=1, name="Commissioning", hotel={"id": 2})


def test_project_schemas_reject_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ProjectResponse(
            id=1,
            name="Commissioning",
            hotel={"id": 2, "name": "Hotel", "code": "H"},
        )
