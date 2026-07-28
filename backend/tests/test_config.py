"""Tests for application settings."""

from pytest import MonkeyPatch

from app.core.config import Settings


def test_settings_can_be_overridden(monkeypatch: MonkeyPatch) -> None:
    """Environment variables override the defaults."""
    monkeypatch.setenv("CIM_APPLICATION_NAME", "Test CIM")
    monkeypatch.setenv("CIM_DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("CIM_STORAGE_ROOT", "/tmp/cim-storage")
    monkeypatch.setenv("CIM_DEBUG", "true")
    monkeypatch.setenv("CIM_OLLAMA_HOST", "http://ollama.test:11434")
    monkeypatch.setenv("CIM_OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("CIM_OLLAMA_TIMEOUT_SECONDS", "15.5")
    monkeypatch.setenv("CIM_SESSION_SECRET", "configured-test-secret")
    settings = Settings.from_environment()
    assert settings.application_name == "Test CIM"
    assert settings.database_url == "sqlite:///test.db"
    assert settings.storage_root == "/tmp/cim-storage"
    assert settings.debug is True
    assert settings.ollama_host == "http://ollama.test:11434"
    assert settings.ollama_model == "test-model"
    assert settings.ollama_timeout_seconds == 15.5
    assert settings.session_secret == "configured-test-secret"


def test_ollama_settings_defaults(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("CIM_OLLAMA_HOST", raising=False)
    monkeypatch.delenv("CIM_OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("CIM_OLLAMA_TIMEOUT_SECONDS", raising=False)
    settings = Settings.from_environment()
    assert settings.ollama_host == "http://localhost:11434"
    assert settings.ollama_model is None
    assert settings.ollama_timeout_seconds == 60.0


def test_storage_root_defaults(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("CIM_STORAGE_ROOT", raising=False)
    settings = Settings.from_environment()
    assert settings.storage_root == "./storage"


def test_session_secret_has_no_default(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("CIM_SESSION_SECRET", raising=False)
    settings = Settings.from_environment()
    assert settings.session_secret is None
