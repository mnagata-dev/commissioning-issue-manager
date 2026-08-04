"""AI Draft API integration tests."""

from collections.abc import Generator
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_ai_service, get_current_user
from app.core.config import Settings
from app.core.exceptions import AIServiceError, NotFoundError, ValidationError
from app.main import create_app
from app.schemas import CurrentUserResponse, GenerateDraftResponse

CURRENT_USER = CurrentUserResponse(
    id=7,
    username="engineer@example.com",
    display_name="Engineer",
    role="ENGINEER",
)

ROOM_PAYLOAD = {
    "project_id": 1,
    "target_type": "ROOM",
    "room_id": 2,
    "target": None,
    "input_text": "Bathroom light does not turn off.",
}


@pytest.fixture
def ai_service() -> MagicMock:
    service = MagicMock()
    service.generate_issue_draft.return_value = GenerateDraftResponse(
        category="LIGHTING",
        description="Bathroom light remains on after operation.",
    )
    return service


@pytest.fixture
def client(ai_service: MagicMock) -> Generator[TestClient, None, None]:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    application.dependency_overrides[get_current_user] = lambda: CURRENT_USER
    application.dependency_overrides[get_ai_service] = lambda: ai_service
    with TestClient(application) as test_client:
        yield test_client


@pytest.mark.parametrize(
    "payload",
    [
        ROOM_PAYLOAD,
        {
            "project_id": 1,
            "target_type": "OTHER",
            "room_id": None,
            "target": "Network",
            "input_text": "Processor cannot communicate with gateway.",
        },
    ],
)
def test_generate_draft_forwards_exact_request_and_user_id(
    client: TestClient, ai_service: MagicMock, payload: dict[str, object]
) -> None:
    response = client.post("/api/ai/issue-draft", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "category": "LIGHTING",
        "description": "Bathroom light remains on after operation.",
    }
    call = ai_service.generate_issue_draft.call_args
    assert call.kwargs["request"].model_dump() == payload
    assert call.kwargs["user_id"] == 7


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {**ROOM_PAYLOAD, "project_id": "not-an-integer"},
    ],
)
def test_invalid_request_uses_common_safe_400_without_calling_service(
    client: TestClient, ai_service: MagicMock, payload: object
) -> None:
    response = client.post("/api/ai/issue-draft", json=payload)

    assert response.status_code == 400
    assert response.json() == {
        "error": {"code": "VALIDATION_ERROR", "message": "Validation failed."}
    }
    ai_service.generate_issue_draft.assert_not_called()


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        ({**ROOM_PAYLOAD, "target_type": "INVALID"}, ValidationError()),
        ({**ROOM_PAYLOAD, "room_id": None}, ValidationError()),
        (
            {
                **ROOM_PAYLOAD,
                "target_type": "OTHER",
                "room_id": 2,
                "target": "Network",
            },
            ValidationError(),
        ),
        ({**ROOM_PAYLOAD, "input_text": ""}, ValidationError()),
        (ROOM_PAYLOAD, NotFoundError("Project not found.")),
        (ROOM_PAYLOAD, NotFoundError("Room not found.")),
    ],
)
def test_business_errors_use_common_safe_response(
    client: TestClient,
    ai_service: MagicMock,
    payload: dict[str, object],
    error: Exception,
) -> None:
    ai_service.generate_issue_draft.side_effect = error

    response = client.post("/api/ai/issue-draft", json=payload)

    assert response.status_code == error.status_code
    assert set(response.json()) == {"error"}


@pytest.mark.parametrize(
    "failure",
    [
        "model missing",
        "connection failure",
        "timeout",
        "invalid structured output",
        "invalid category",
        "missing description",
        "empty description",
    ],
)
def test_ai_failures_use_common_safe_500(
    client: TestClient,
    ai_service: MagicMock,
    failure: str,
) -> None:
    ai_service.generate_issue_draft.side_effect = AIServiceError()

    response = client.post("/api/ai/issue-draft", json=ROOM_PAYLOAD)

    assert response.status_code == 500, failure
    assert response.json() == {
        "error": {
            "code": "AI_SERVICE_ERROR",
            "message": "The AI service failed.",
        }
    }
    assert "Ollama" not in response.text
    assert "provider" not in response.text


def test_ai_draft_requires_authentication(ai_service: MagicMock) -> None:
    application = create_app(Settings(session_secret="test-only-session-secret"))
    application.dependency_overrides[get_ai_service] = lambda: ai_service
    with TestClient(application) as unauthenticated_client:
        response = unauthenticated_client.post(
            "/api/ai/issue-draft", json=ROOM_PAYLOAD
        )

    assert response.status_code == 401
    ai_service.generate_issue_draft.assert_not_called()
