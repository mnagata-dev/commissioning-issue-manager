"""Speech API and non-persistence integration tests."""

from datetime import datetime
from unittest.mock import Mock

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import event, select
from sqlalchemy.orm import Session

from app.api import deps
from app.clients import SpeechClient, SpeechClientError
from app.core.config import Settings
from app.core.security import hash_password
from app.db.base import Base
from app.main import create_app
from app.models import Attachment, Comment, Hotel, Issue, Project, User
from app.schemas import CurrentUserResponse
from app.services import AIService, AttachmentService, StorageService


@pytest.fixture
def speech_client(monkeypatch) -> Mock:
    client = Mock(spec=SpeechClient)
    client.transcribe_audio.return_value = "ロビーの照明が点滅している"
    monkeypatch.setattr(deps, "SpeechClient", lambda *args: client)
    return client


@pytest.fixture
def application(speech_client):
    return create_app(Settings(session_secret="test-only-session-secret"))


@pytest.fixture
def client(application):
    application.dependency_overrides[deps.get_current_user] = lambda: CurrentUserResponse(
        id=1, username="engineer", display_name="Engineer", role="ENGINEER"
    )
    with TestClient(application) as client:
        yield client


def test_transcription_response(client, speech_client) -> None:
    response = client.post(
        "/api/speech/transcriptions", files={"audio": ("input", b"audio")}
    )
    assert response.status_code == 200
    assert response.json() == {"text": "ロビーの照明が点滅している"}
    speech_client.transcribe_audio.assert_called_once()


@pytest.mark.parametrize("payload", [
    {}, {"data": {"audio": "not a file"}},
    {"files": {"wrong": ("audio", b"data")}},
    {"files": {"audio": ("audio", b"")}},
])
def test_invalid_audio(client, speech_client, payload) -> None:
    response = client.post("/api/speech/transcriptions", **payload)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    speech_client.transcribe_audio.assert_not_called()


@pytest.mark.parametrize("result", [None, "", " \n", 42, {}])
def test_unusable_text(client, speech_client, result) -> None:
    speech_client.transcribe_audio.return_value = result
    response = client.post(
        "/api/speech/transcriptions", files={"audio": ("input", b"audio")}
    )
    assert response.status_code == 500
    assert response.json() == {"error": {
        "code": "SPEECH_RECOGNITION_ERROR", "message": "Speech recognition failed."
    }}


def test_unauthenticated(application, speech_client) -> None:
    with TestClient(application) as client:
        response = client.post(
            "/api/speech/transcriptions", files={"audio": ("input", b"audio")}
        )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"
    speech_client.transcribe_audio.assert_not_called()


def test_speech_uses_no_database_or_other_services(client, monkeypatch) -> None:
    def forbidden(*args, **kwargs):
        pytest.fail("Speech must not access persistence, AI or Attachment storage")

    client.app.dependency_overrides[deps.get_db_session] = forbidden
    for service in (AIService, AttachmentService, StorageService):
        monkeypatch.setattr(service, "__init__", forbidden)
    response = client.post(
        "/api/speech/transcriptions", files={"audio": ("input", b"audio")}
    )
    assert response.status_code == 200


@pytest.mark.parametrize("role", ["ENGINEER", "ADMINISTRATOR"])
@pytest.mark.parametrize("outcome,status", [
    ("success", 200), ("failure", 500), ("empty", 500), ("invalid", 400)
])
def test_authenticated_speech_preserves_business_data(
    application, speech_client, database_engine, role, outcome, status, monkeypatch
) -> None:
    """Exercise real authentication and compare every table before/after speech."""
    Base.metadata.create_all(database_engine)
    timestamp = datetime(2026, 9, 30)
    with database_engine.begin() as connection:
        connection.execute(User.__table__.insert(), dict(
            id=1, username="user", password_hash=hash_password("password"),
            display_name="User", role=role, created_at=timestamp, updated_at=timestamp,
        ))
        connection.execute(Hotel.__table__.insert(), dict(
            id=1, name="Hotel", created_at=timestamp, updated_at=timestamp,
        ))
        connection.execute(Project.__table__.insert(), dict(
            id=1, hotel_id=1, name="Project", created_at=timestamp, updated_at=timestamp,
        ))
        connection.execute(Issue.__table__.insert(), dict(
            id=1, project_id=1, target_type="OTHER", target="Lobby", category="OTHER",
            description="Original", status="OPEN", created_by=1, updated_by=1,
            created_at=timestamp, updated_at=timestamp,
        ))
        connection.execute(Comment.__table__.insert(), dict(
            id=1, issue_id=1, comment="Original", created_by=1, created_at=timestamp,
        ))
        connection.execute(Attachment.__table__.insert(), dict(
            id=1, issue_id=1, file_name="original", original_file_name="original",
            file_path="original", mime_type="image/png", file_size=1,
            uploaded_by=1, uploaded_at=timestamp,
        ))

    def database_session():
        with Session(database_engine) as session:
            yield session

    def snapshot():
        with database_engine.connect() as connection:
            return {
                table.name: connection.execute(select(table)).all()
                for table in Base.metadata.sorted_tables
            }

    application.dependency_overrides[deps.get_db_session] = database_session
    forbidden_ai = Mock(side_effect=AssertionError("AI must not be called"))
    forbidden_storage = Mock(side_effect=AssertionError("Storage must not be called"))
    monkeypatch.setattr(AIService, "generate_issue_draft", forbidden_ai)
    monkeypatch.setattr(StorageService, "__init__", forbidden_storage)
    if outcome == "failure":
        speech_client.transcribe_audio.side_effect = SpeechClientError("private path")
    elif outcome == "empty":
        speech_client.transcribe_audio.return_value = ""
    with TestClient(application) as client:
        assert client.post("/api/auth/login", json={
            "username": "user", "password": "password"
        }).status_code == 200
        before = snapshot()
        statements = []

        def record_sql(connection, cursor, statement, parameters, context, many):
            statements.append(statement)

        event.listen(database_engine, "before_cursor_execute", record_sql)
        try:
            response = client.post("/api/speech/transcriptions", files={
                "audio": ("input", b"" if outcome == "invalid" else b"audio")
            })
        finally:
            event.remove(database_engine, "before_cursor_execute", record_sql)
        assert response.status_code == status
        assert snapshot() == before
        # Only the existing authentication dependency may query the database.
        assert len(statements) == 1
        assert statements[0].lstrip().upper().startswith("SELECT")
        assert "FROM users" in statements[0]
        assert "private path" not in response.text
        forbidden_ai.assert_not_called()
        forbidden_storage.assert_not_called()
