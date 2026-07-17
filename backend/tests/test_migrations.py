"""Alembic migration chain tests."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def _config(database_path: Path) -> Config:
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")
    return config


def test_upgrade_downgrade_and_reupgrade(tmp_path: Path) -> None:
    database_path = tmp_path / "migration.db"
    config = _config(database_path)

    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database_path}")
    assert set(inspect(engine).get_table_names()) >= {
        "attachments", "comments", "hotels", "issues", "projects", "rooms",
        "room_types", "users",
    }
    engine.dispose()

    command.downgrade(config, "-1")
    engine = create_engine(f"sqlite:///{database_path}")
    assert "issues" not in inspect(engine).get_table_names()
    engine.dispose()

    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database_path}")
    assert "issues" in inspect(engine).get_table_names()
    engine.dispose()
