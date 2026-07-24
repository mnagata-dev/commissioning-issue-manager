"""Tests for application settings."""

from pytest import MonkeyPatch

from app.core.config import Settings


def test_settings_can_be_overridden(monkeypatch: MonkeyPatch) -> None:
    """Environment variables override the defaults."""
    monkeypatch.setenv("CIM_APPLICATION_NAME", "Test CIM")
    monkeypatch.setenv("CIM_DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("CIM_DEBUG", "true")
    monkeypatch.setenv("CIM_OLLAMA_HOST", "http://ollama.test:11434")
    monkeypatch.setenv("CIM_OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("CIM_OLLAMA_TIMEOUT_SECONDS", "15.5")
    settings = Settings.from_environment()
    assert settings.application_name == "Test CIM"
    assert settings.database_url == "sqlite:///test.db"
    assert settings.debug is True
    assert settings.ollama_host == "http://ollama.test:11434"
    assert settings.ollama_model == "test-model"
    assert settings.ollama_timeout_seconds == 15.5


def test_ollama_settings_defaults(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("CIM_OLLAMA_HOST", raising=False)
    monkeypatch.delenv("CIM_OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("CIM_OLLAMA_TIMEOUT_SECONDS", raising=False)
    settings = Settings.from_environment()
    assert settings.ollama_host == "http://localhost:11434"
    assert settings.ollama_model is None
    assert settings.ollama_timeout_seconds == 60.0
