from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas import (
    AttachmentResponse,
    CommentResponse,
    CreateIssueRequest,
    IssueDetailResponse,
    IssueSummaryResponse,
    UpdateIssueRequest,
    UpdateIssueStatusRequest,
)


def test_create_issue_request_accepts_room_shape() -> None:
    request = CreateIssueRequest(
        room_id=1,
        target_type="ROOM",
        category="LIGHTING",
        description="Light does not turn off.",
    )
    assert request.target is None


def test_create_issue_request_accepts_other_shape() -> None:
    request = CreateIssueRequest(
        target_type="OTHER",
        target="Network",
        category="NETWORK",
        description="No communication.",
    )
    assert request.room_id is None


def test_create_issue_request_defaults_optional_fields_to_none() -> None:
    request = CreateIssueRequest(
        target_type="UNDEFINED", category="UNDEFINED", description=""
    )
    assert request.room_id is None
    assert request.target is None


@pytest.mark.parametrize("missing_field", ["target_type", "category", "description"])
def test_create_issue_request_requires_fields(missing_field: str) -> None:
    data = {"target_type": "ROOM", "category": "LIGHTING", "description": "Description"}
    data.pop(missing_field)
    with pytest.raises(ValidationError):
        CreateIssueRequest.model_validate(data)


def test_create_issue_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        CreateIssueRequest(
            target_type="ROOM", category="LIGHTING", description="Description", status="OPEN"
        )


def test_update_issue_request_accepts_explicit_none_fields() -> None:
    request = UpdateIssueRequest(
        room_id=None,
        target_type="OTHER",
        target=None,
        category="OTHER",
        description="Description",
    )
    assert request.room_id is None
    assert request.target is None


@pytest.mark.parametrize(
    "missing_field", ["room_id", "target_type", "target", "category", "description"]
)
def test_update_issue_request_requires_all_fields(missing_field: str) -> None:
    data = {
        "room_id": None,
        "target_type": "OTHER",
        "target": None,
        "category": "OTHER",
        "description": "Description",
    }
    data.pop(missing_field)
    with pytest.raises(ValidationError):
        UpdateIssueRequest.model_validate(data)


def test_update_issue_status_request_accepts_arbitrary_string() -> None:
    assert UpdateIssueStatusRequest(status="UNDEFINED").status == "UNDEFINED"


def test_issue_summary_response_accepts_room_and_none() -> None:
    updated_at = datetime(2026, 7, 21, 10, 0)
    common = {
        "id": 1,
        "target_type": "ROOM",
        "target": None,
        "category": "LIGHTING",
        "description": "Description",
        "status": "OPEN",
        "updated_at": updated_at,
    }
    with_room = IssueSummaryResponse(room={"id": 2, "room_number": "1203"}, **common)
    without_room = IssueSummaryResponse(room=None, **common)
    assert with_room.room is not None
    assert with_room.room.room_number == "1203"
    assert without_room.room is None


def test_issue_detail_response_serializes_typed_lists_and_datetimes() -> None:
    timestamp = datetime(2026, 7, 21, 10, 30)
    response = IssueDetailResponse(
        id=1,
        project={"id": 2, "name": "Commissioning"},
        room={"id": 3, "room_number": "1203"},
        target_type="ROOM",
        target=None,
        category="LIGHTING",
        description="Description",
        status="OPEN",
        created_by={"id": 4, "display_name": "Creator"},
        updated_by={"id": 5, "display_name": "Updater"},
        created_at=timestamp,
        updated_at=timestamp,
        comments=[
            {
                "id": 6,
                "comment": "Checked",
                "created_by": {"id": 4, "display_name": "Creator"},
                "created_at": timestamp,
            }
        ],
        attachments=[
            {
                "id": 7,
                "file_name": "photo.jpg",
                "mime_type": "image/jpeg",
                "file_size": 2048,
                "uploaded_at": timestamp,
            }
        ],
    )
    assert response.updated_by.display_name == "Updater"
    assert isinstance(response.comments[0], CommentResponse)
    assert isinstance(response.attachments[0], AttachmentResponse)
    serialized = response.model_dump(mode="json")
    assert serialized["created_at"] == "2026-07-21T10:30:00"
    assert serialized["comments"][0]["created_at"] == "2026-07-21T10:30:00"


def test_issue_detail_response_rejects_invalid_nested_structure() -> None:
    timestamp = datetime(2026, 7, 21, 10, 30)
    with pytest.raises(ValidationError):
        IssueDetailResponse(
            id=1,
            project={"id": 2},
            room=None,
            target_type="OTHER",
            target="Network",
            category="NETWORK",
            description="Description",
            status="OPEN",
            created_by={"id": 4, "display_name": "Creator"},
            updated_by={"id": 4, "display_name": "Creator"},
            created_at=timestamp,
            updated_at=timestamp,
            comments=[],
            attachments=[],
        )


def test_issue_response_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        IssueSummaryResponse(
            id=1,
            room=None,
            target_type="OTHER",
            target="Network",
            category="NETWORK",
            description="Description",
            status="OPEN",
            updated_at=datetime(2026, 7, 21, 10, 0),
            project_id=2,
        )
