"""Tests for application settings."""

from pytest import MonkeyPatch

from app.core.config import Settings


def test_settings_can_be_overridden(monkeypatch: MonkeyPatch) -> None:
    """Environment variables override the defaults."""
    monkeypatch.setenv("CIM_APPLICATION_NAME", "Test CIM")
    monkeypatch.setenv("CIM_DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("CIM_DEBUG", "true")
    settings = Settings.from_environment()
    assert settings.application_name == "Test CIM"
    assert settings.database_url == "sqlite:///test.db"
    assert settings.debug is True
