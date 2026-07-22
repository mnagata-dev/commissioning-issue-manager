from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas import CommentResponse, CreateCommentRequest, UserReferenceResponse


def test_create_comment_request_accepts_empty_string() -> None:
    request = CreateCommentRequest(comment="")
    assert request.comment == ""


def test_create_comment_request_requires_comment() -> None:
    with pytest.raises(ValidationError):
        CreateCommentRequest.model_validate({})


def test_comment_response_uses_typed_user() -> None:
    created_at = datetime(2026, 7, 21, 10, 0)
    response = CommentResponse(
        id=1,
        comment="Checked",
        created_by={"id": 2, "display_name": "Engineer"},
        created_at=created_at,
    )
    assert isinstance(response.created_by, UserReferenceResponse)
    assert response.created_at == created_at


def test_comment_schemas_reject_extra_fields() -> None:
    with pytest.raises(ValidationError):
        CreateCommentRequest(comment="Checked", issue_id=1)
