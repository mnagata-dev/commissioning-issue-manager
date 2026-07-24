"""Application configuration."""

import os
from dataclasses import dataclass


def _read_bool(name: str, default: bool) -> bool:
    """Read a boolean environment variable."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    """Typed application settings."""

    application_name: str = "Commissioning Issue Manager API"
    database_url: str = "sqlite:///./cim.db"
    debug: bool = False
    ollama_host: str = "http://localhost:11434"
    ollama_model: str | None = None
    ollama_timeout_seconds: float = 60.0

    @classmethod
    def from_environment(cls) -> "Settings":
        """Build settings with environment overrides."""
        defaults = cls()
        return cls(
            application_name=os.getenv("CIM_APPLICATION_NAME", defaults.application_name),
            database_url=os.getenv("CIM_DATABASE_URL", defaults.database_url),
            debug=_read_bool("CIM_DEBUG", defaults.debug),
            ollama_host=os.getenv("CIM_OLLAMA_HOST", defaults.ollama_host),
            ollama_model=os.getenv("CIM_OLLAMA_MODEL"),
            ollama_timeout_seconds=float(
                os.getenv(
                    "CIM_OLLAMA_TIMEOUT_SECONDS",
                    str(defaults.ollama_timeout_seconds),
                )
            ),
        )


settings = Settings.from_environment()
